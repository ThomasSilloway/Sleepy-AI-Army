"""Contains logic for the manifest_create_node."""
import asyncio
import logging # Keep for AppConfig and other service initializations if they use it
from datetime import datetime

from src.config import AppConfig
from src.pydantic_models.core_schemas import Artifact, ManifestConfigLLM, ManifestData
from src.services.changelog_service import ChangelogService
from src.services.git_service import GitService
from src.services.llm_prompt_service import LlmPromptService
from src.services.write_file_from_template_service import WriteFileFromTemplateService
from src.state import WorkflowState

# Import from the new exception handling framework
from src.utils.custom_exceptions import (
    NodeOperation, # Though NodeOperation might not be directly used in node after refactor
    NodeConfigError,
    ValidationError,
    LLMError,
    FileError,
    ChangelogError,
    GitError
)
from src.utils.node_exception_handler import handle_node_exceptions, _get_logger

# Module-level logger is not typically used directly in nodes if logger is passed via config or state
# However, it can be kept for any module-level activities if necessary.
# For node-specific logging, _get_logger will be used.

@handle_node_exceptions # Apply the decorator
def manifest_create_node(state: WorkflowState, config: dict) -> WorkflowState:
    """
    Generates the goal manifest file. It extracts data using LlmPromptService,
    populates a ManifestData Pydantic model, stores this model in the workflow state,
    and then renders the manifest file using WriteFileFromTemplateService.
    Records the event in the changelog upon success.
    Errors are handled by the @handle_node_exceptions decorator.
    """
    state['current_step_name'] = "Create Manifest"
    node_logger = _get_logger(state, config, __name__) # Use utility to get logger
    node_logger.info(f"Executing node: {state['current_step_name']}")

    services_config = config.get("configurable", {})
    app_config: AppConfig = services_config.get("app_config")
    llm_prompt_service: LlmPromptService = services_config.get("llm_prompt_service")
    write_file_service: WriteFileFromTemplateService = services_config.get("write_file_service")
    changelog_service: ChangelogService = services_config.get("changelog_service")
    git_service: GitService = services_config.get("git_service")

    if not all([app_config, llm_prompt_service, write_file_service, changelog_service, git_service]):
        raise NodeConfigError("Essential services (app_config, llm_prompt_service, etc.) are missing from node configuration.")

    task_description_content = state.get('task_description_content')
    manifest_template_path_str = state.get('manifest_template_path')
    manifest_output_path_str = state.get('manifest_output_path')

    if not all([task_description_content, manifest_template_path_str, manifest_output_path_str]):
        raise ValidationError("Critical information missing in state for manifest generation (task_description_content, manifest_template_path, or manifest_output_path).")

    node_logger.info("Attempting to extract structured data from task description using LLM.")
    system_prompt = f"""
You are an expert in analyzing software development task descriptions.
Your goal is to extract specific pieces of information and structure them according to the provided JSON schema.
The JSON schema to use for your response is:
{ManifestConfigLLM.model_json_schema()}
Ensure your output is a valid JSON object that conforms to this schema.
From the user's task description, extract:
1.  `goal_title`: A concise title for the overall goal or task.
2.  `task_description`: The full, original task description provided by the user.
3.  `small_tweak_file_path`: The specific file path, relative to the git repository root, that is the target of this task.
"""
    user_prompt = task_description_content
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    manifest_config_llm: ManifestConfigLLM | None = None
    try:
        manifest_config_llm = asyncio.run(llm_prompt_service.get_structured_output(
            messages=messages,
            output_pydantic_model_type=ManifestConfigLLM,
            llm_model_name=app_config.gemini_weak_model_name
        ))
    except Exception as e: # Catch specific exceptions from the LLM service if known, else generic Exception
        raise LLMError(f"LLM service call failed during get_structured_output: {e}", original_exception=e)
    
    if not manifest_config_llm:
        raise LLMError("LLM did not return structured data (ManifestConfigLLM is None).")

    node_logger.info(f"LLM successfully extracted data: {manifest_config_llm.goal_title}")
    # Happy path state updates directly
    state['last_event_summary'] = f"LLM extracted manifest data for: {manifest_config_llm.goal_title}"
    state['small_tweak_file_path'] = manifest_config_llm.small_tweak_file_path

    current_timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    initial_artifact = Artifact(status="[in-progress]", path=manifest_config_llm.small_tweak_file_path)
    manifest_data_instance = ManifestData(
        goal_title=manifest_config_llm.goal_title,
        task_description_for_manifest=manifest_config_llm.task_description,
        last_updated_timestamp=current_timestamp,
        overall_status="New",
        current_focus=task_description_content,
        artifacts=[initial_artifact],
        ai_questions_list=[],
        human_responses_content="NONE",
    )
    state['manifest_data'] = manifest_data_instance
    node_logger.info("ManifestData model populated and stored in state.")

    node_logger.info("Attempting to render and write goal-manifest.md from ManifestData.")
    template_context = {"manifest_data": manifest_data_instance.model_dump()}
    
    debug_context_summary = {k: (v if k != "manifest_data" else "{...manifest_data_details...}") for k, v in template_context.items()}
    node_logger.debug(f"Template context prepared with ManifestData: {debug_context_summary}")

    try:
        success_write = write_file_service.render_and_write_file(
            template_abs_path_str=manifest_template_path_str,
            context=template_context,
            output_abs_path_str=manifest_output_path_str
        )
        if not success_write:
            raise FileError(f"WriteFileFromTemplateService failed to write manifest to '{manifest_output_path_str}' (service reported failure).")
    except Exception as e: # Catch specific exceptions from the service if known
        if not isinstance(e, FileError): # Avoid re-wrapping if already a FileError
             raise FileError(f"Error during template rendering or file writing: {e}", original_exception=e)
        raise # Re-raise if it's already the correct custom type

    # Happy path for file writing
    node_logger.info(f"Successfully generated manifest file: {manifest_output_path_str}")
    state['is_manifest_generated'] = True
    state['last_event_summary'] = f"Goal Manifest '{manifest_data_instance.goal_title}' generated." # Keep it concise

    # Record manifest creation in changelog
    node_logger.info("Attempting to record manifest creation in changelog.")
    changelog_summary = f"Goal Manifest Created: {manifest_data_instance.goal_title}"
    try:
        success_changelog = changelog_service.record_event_in_changelog(
            current_workflow_state=state,
            preceding_event_summary=changelog_summary
        )
        if not success_changelog:
            raise ChangelogError("ChangelogService failed to record event (service reported failure).")
    except Exception as e:
        if not isinstance(e, ChangelogError):
            raise ChangelogError(f"Error during changelog service call: {e}", original_exception=e)
        raise
    
    # Happy path for changelog
    node_logger.info("Successfully recorded manifest creation in changelog.")
    state['is_changelog_entry_added'] = True
    state['last_event_summary'] = f"Manifest '{manifest_data_instance.goal_title}' created and changelog updated."

    # Attempt to commit changes
    commit_message = f"Create Goal Manifest for [{manifest_data_instance.goal_title}]"
    node_logger.info(f"Attempting to commit changes with message: '{commit_message}'")
    try:
        commit_success = git_service.commit_changes(commit_message)
        if not commit_success:
            # This will be caught by the decorator. NODE_ERROR_CONFIG for GIT_COMMIT
            # specifies set_aider_exit_code=False, so it won't halt the graph,
            # but error_message and last_event_summary will be updated.
            raise GitError("Failed to commit manifest and changelog changes (service reported failure).")
    except Exception as e:
        if not isinstance(e, GitError):
             raise GitError(f"Error during git commit: {e}", original_exception=e)
        raise

    # Happy path for git commit
    node_logger.info("Successfully committed manifest and changelog changes.")
    state['last_event_summary'] += ", and changes committed." # Append to previous summary

    return state
