"""Contains logic for the manifest_create_node."""
import asyncio
import logging
from datetime import datetime

from src.config import AppConfig
from src.pydantic_models.core_schemas import Artifact, ManifestConfigLLM, ManifestData
from src.services.changelog_service import ChangelogService
from src.services.git_service import GitService
from src.services.llm_prompt_service import LlmPromptService
from src.services.write_file_from_template_service import WriteFileFromTemplateService
from src.state import WorkflowState
# Import the new error handler utility
from src.utils.node_error_handler import NodeOperation, handle_operation_error

# Initialize logger for this module if not already configured by the application
# This logger instance might be overridden by one passed in config if available
logger = logging.getLogger(__name__)

def manifest_create_node(state: WorkflowState, config: dict) -> WorkflowState:
    """
    Generates the goal manifest file. It extracts data using LlmPromptService,
    populates a ManifestData Pydantic model, stores this model in the workflow state,
    and then renders the manifest file using WriteFileFromTemplateService.
    Records the event in the changelog upon success.
    """
    state['current_step_name'] = "Create Manifest"
    # Node-specific logger can be fetched from config if passed, otherwise use module logger
    node_logger = config.get("logger", logger) 
    node_logger.info(f"Executing node: {state['current_step_name']}")

    manifest_config_llm: ManifestConfigLLM | None = None
    # manifest_data_instance is created later, so no need to initialize to None here if it's always set before use or handled if not.

    try:
        services_config = config.get("configurable", {}) # Ensure configurable exists
        app_config: AppConfig = services_config.get("app_config")
        llm_prompt_service: LlmPromptService = services_config.get("llm_prompt_service")
        write_file_service: WriteFileFromTemplateService = services_config.get("write_file_service")
        changelog_service: ChangelogService = services_config.get("changelog_service")
        git_service: GitService = services_config.get("git_service")

        # Ensure essential services are present
        if not all([app_config, llm_prompt_service, write_file_service, changelog_service, git_service]):
            # This is a configuration error, should be handled
            # Create a generic exception for this type of configuration issue
            config_exception = ValueError("Essential services are missing from configuration.")
            # Use custom_error_message_override for a clear, concise summary.
            # is_manifest_generated and manifest_data are likely relevant here.
            if handle_operation_error(
                state, config, NodeOperation.GENERAL_VALIDATION, config_exception,
                custom_error_message_override="[ManifestCreate] Essential services missing from configuration.",
                custom_state_updates={"is_manifest_generated": False, "manifest_data": None}
            ):
                return state


        task_description_content = state.get('task_description_content')
        manifest_template_path_str = state.get('manifest_template_path')
        manifest_output_path_str = state.get('manifest_output_path')

        if not all([task_description_content, manifest_template_path_str, manifest_output_path_str]):
            err_msg = "Critical information missing in state for manifest generation (task_description_content, manifest_template_path, or manifest_output_path)."
            # Use custom_error_message_override for precise control over the logged message and summary.
            # Default state updates for GENERAL_VALIDATION might be okay, but explicitly setting manifest related fields.
            if handle_operation_error(
                state, config, NodeOperation.GENERAL_VALIDATION, ValueError(err_msg),
                custom_error_message_override=f"[ManifestCreate] {err_msg}",
                custom_state_updates={"is_manifest_generated": False, "manifest_data": None} # Explicitly ensure these are set
            ):
                return state

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

        try:
            manifest_config_llm = asyncio.run(llm_prompt_service.get_structured_output(
                messages=messages,
                output_pydantic_model_type=ManifestConfigLLM,
                llm_model_name=app_config.gemini_weak_model_name
            ))
        except Exception as e:
            # Custom state updates are handled by NodeOperation.LLM_CALL defaults in _apply_state_updates
            if handle_operation_error(state, config, NodeOperation.LLM_CALL, e,
                                      additional_error_info="LLM service call failed"):
                return state
        
        if not manifest_config_llm:
            app_err_msg = "LLM did not return structured data (ManifestConfigLLM is None)."
            # Custom state updates are handled by NodeOperation.LLM_CALL defaults
            if handle_operation_error(
                state, config, NodeOperation.LLM_CALL, ValueError(app_err_msg),
                additional_error_info=app_err_msg
            ):
                return state

        node_logger.info(f"LLM successfully extracted data: {manifest_config_llm.goal_title}")
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
        
        # Debug logging for context summary (can remain as is)
        debug_context_summary = {k: (v if k != "manifest_data" else "{...manifest_data_details...}") for k, v in template_context.items()}
        node_logger.debug(f"Template context prepared with ManifestData: {debug_context_summary}")

        try:
            success_write = write_file_service.render_and_write_file(
                template_abs_path_str=manifest_template_path_str,
                context=template_context,
                output_abs_path_str=manifest_output_path_str
            )
            if not success_write:
                err_msg = f"WriteFileFromTemplateService failed to write manifest from ManifestData to '{manifest_output_path_str}'."
                # NodeOperation.FILE_WRITE defaults handle is_manifest_generated=False
                if handle_operation_error(
                    state, config, NodeOperation.FILE_WRITE, RuntimeError(err_msg), # Using RuntimeError for service failure
                    custom_error_message_override=f"[ManifestCreate] {err_msg}"
                ):
                    return state
        except Exception as e:
            # NodeOperation.FILE_WRITE defaults handle is_manifest_generated=False
            if handle_operation_error(
                state, config, NodeOperation.FILE_WRITE, e,
                additional_error_info="Template rendering or file writing from ManifestData failed."
            ):
                return state

        # If success_write was True, we reach here.
        node_logger.info(f"Successfully generated manifest file from ManifestData: {manifest_output_path_str}")
        state['is_manifest_generated'] = True # Explicitly set to True on success
        state['last_event_summary'] = f"Goal Manifest '{manifest_data_instance.goal_title}' generated from ManifestData."

        if state['is_manifest_generated']: # This check is somewhat redundant now but fine to keep
            node_logger.info("Attempting to record manifest creation in changelog.")
            changelog_summary = f"Goal Manifest Created: {manifest_data_instance.goal_title}"
            try:
                success_changelog = changelog_service.record_event_in_changelog(
                    current_workflow_state=state,
                    preceding_event_summary=changelog_summary
                )
                if not success_changelog:
                    err_msg = "ChangelogService failed to record event (service reported failure)."
                    # NodeOperation.CHANGELOG_UPDATE defaults handle is_changelog_entry_added=False
                    if handle_operation_error(
                        state, config, NodeOperation.CHANGELOG_UPDATE, RuntimeError(err_msg),
                        custom_error_message_override=f"[ManifestCreate] {err_msg}",
                        # We want to keep the manifest as generated, so override the default for is_manifest_generated
                        custom_state_updates={"is_manifest_generated": True} 
                    ):
                        # Even if changelog fails, we don't necessarily stop the whole flow if manifest is written.
                        # The original code returned state, so we maintain that.
                        return state 
            except Exception as e:
                # NodeOperation.CHANGELOG_UPDATE defaults handle is_changelog_entry_added=False
                if handle_operation_error(
                    state, config, NodeOperation.CHANGELOG_UPDATE, e,
                    additional_error_info="Changelog service call failed.",
                    custom_state_updates={"is_manifest_generated": True} # Keep manifest as generated
                ):
                    return state # Original code returned state.

            if success_changelog: # Implies no exception was caught, and service reported true
                state['is_changelog_entry_added'] = True
                # This summary assumes manifest was also successful.
                # If manifest could fail but changelog succeed (unlikely here), this would need adjustment.
                state['last_event_summary'] = f"Manifest '{manifest_data_instance.goal_title}' created and changelog updated."
            # If success_changelog is False or an exception occurred, 
            # handle_operation_error has already set is_changelog_entry_added to False
            # and updated last_event_summary appropriately.


            commit_message = f"Create Goal Manifest for [{manifest_data_instance.goal_title}]"
            node_logger.info(f"Attempting to commit changes with message: '{commit_message}'")
            try:
                commit_success = git_service.commit_changes(commit_message)
                if commit_success:
                    node_logger.info("Successfully committed manifest and changelog changes.")
                    current_summary = state.get('last_event_summary', "Operations successful") 
                    state['last_event_summary'] = f"{current_summary}, and changes committed."
                else:
                    # This is an application-level error for git commit.
                    # We don't return state here, just log and update summary.
                    git_err_msg = "Failed to commit manifest and changelog changes (service reported failure)."
                    handle_operation_error(
                        state, config, NodeOperation.GIT_COMMIT, RuntimeError(git_err_msg),
                        custom_error_message_override=f"[ManifestCreate] {git_err_msg}",
                        set_aider_exit_code=False, # A git commit failure might not be a critical workflow error
                        custom_state_updates={ # Preserve previous successes
                            "is_manifest_generated": state.get('is_manifest_generated', False),
                            "is_changelog_entry_added": state.get('is_changelog_entry_added', False),
                            "manifest_data": state.get("manifest_data")
                        }
                    )
                    # Do not return state, original code continued.
            except Exception as e:
                # We don't return state here, just log and update summary.
                handle_operation_error(
                    state, config, NodeOperation.GIT_COMMIT, e,
                    additional_error_info="Git commit operation failed.",
                    set_aider_exit_code=False,
                    custom_state_updates={ # Preserve previous successes
                        "is_manifest_generated": state.get('is_manifest_generated', False),
                        "is_changelog_entry_added": state.get('is_changelog_entry_added', False),
                        "manifest_data": state.get("manifest_data")
                    }
                )
                # Do not return state, original code continued.

    except Exception as e:
        # This is the outermost catch-all.
        # It should ideally not be reached if specific handlers are correct.
        # Default state updates for UNEXPECTED_ERROR will apply.
        if handle_operation_error(
            state, config, NodeOperation.UNEXPECTED_ERROR, e,
            custom_error_message_override="[ManifestCreate] Unexpected error during manifest creation process."
            # custom_state_updates can be used here if UNEXPECTED_ERROR defaults are not sufficient
            # For example, ensuring all key flags are False and data is None.
            # The _apply_state_updates for UNEXPECTED_ERROR handles resetting common flags.
        ):
            return state

    return state
