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

logger = logging.getLogger(__name__)

def manifest_create_node(state: WorkflowState, config) -> WorkflowState:
    """
    Generates the goal manifest file. It extracts data using LlmPromptService,
    populates a ManifestData Pydantic model, stores this model in the workflow state,
    and then renders the manifest file using WriteFileFromTemplateService.
    Records the event in the changelog upon success.
    """
    state['current_step_name'] = "Create Manifest"
    logger.info(f"Executing node: {state['current_step_name']}")

    manifest_config_llm: ManifestConfigLLM | None = None
    manifest_data_instance: ManifestData | None = None

    try:
        services_config = config["configurable"]
        app_config: AppConfig = services_config["app_config"]
        llm_prompt_service: LlmPromptService = services_config["llm_prompt_service"]
        write_file_service: WriteFileFromTemplateService = services_config["write_file_service"]
        changelog_service: ChangelogService = services_config["changelog_service"]
        git_service: GitService = services_config["git_service"]

        task_description_content = state.get('task_description_content')
        manifest_template_path_str = state.get('manifest_template_path')
        manifest_output_path_str = state.get('manifest_output_path')

        if not all([task_description_content, manifest_template_path_str, manifest_output_path_str]):
            error_msg = "[ManifestCreate] Critical information missing in state for manifest generation (task_description_content, manifest_template_path, or manifest_output_path)."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Missing critical info for manifest generation."
            state['is_manifest_generated'] = False
            state['manifest_data'] = None
            return state

        logger.info("Attempting to extract structured data from task description using LLM.")

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

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            manifest_config_llm = asyncio.run(llm_prompt_service.get_structured_output(
                messages=messages,
                output_pydantic_model_type=ManifestConfigLLM,
                llm_model_name=app_config.gemini_weak_model_name
            ))
        except Exception as e:
            error_msg = f"[ManifestCreate] Error during LLM call: {e}"
            logger.error(error_msg, exc_info=True)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: LLM call failed during manifest creation."
            state['is_manifest_generated'] = False
            state['manifest_data'] = None
            return state

        if not manifest_config_llm:
            error_msg = "[ManifestCreate] LLM did not return structured data (ManifestConfigLLM is None)."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: LLM failed to parse task description for manifest."
            state['is_manifest_generated'] = False
            state['manifest_data'] = None
            return state

        logger.info(f"LLM successfully extracted data: {manifest_config_llm.goal_title}")
        state['last_event_summary'] = f"LLM extracted manifest data for: {manifest_config_llm.goal_title}"
        state['small_tweak_file_path'] = manifest_config_llm.small_tweak_file_path

        # Populate ManifestData Pydantic model
        current_timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        initial_artifact = Artifact(
            status="[in-progress]",
            path=manifest_config_llm.small_tweak_file_path
        )
        manifest_data_instance = ManifestData(
            goal_title=manifest_config_llm.goal_title,
            task_description_for_manifest=manifest_config_llm.task_description,
            last_updated_timestamp=current_timestamp,
            overall_status="New",
            current_focus=task_description_content, # Full content of task-description.md
            artifacts=[initial_artifact],
            ai_questions_list=[],
            human_responses_content="NONE",
        )
        state['manifest_data'] = manifest_data_instance
        logger.info("ManifestData model populated and stored in state.")

        # Render and write goal-manifest.md using ManifestData
        logger.info("Attempting to render and write goal-manifest.md from ManifestData.")
        template_context = {"manifest_data": manifest_data_instance.model_dump()}

        # Avoid logging full task description from manifest_data if it's too verbose
        debug_context_summary = {
            k: (v if k != "manifest_data" else "{...manifest_data_details...}") 
            for k, v in template_context.items()
        }
        logger.debug(f"Template context prepared with ManifestData: {debug_context_summary}")

        try:
            success_write = write_file_service.render_and_write_file(
                template_abs_path_str=manifest_template_path_str,
                context=template_context,
                output_abs_path_str=manifest_output_path_str
            )
        except Exception as e:
            error_msg = f"[ManifestCreate] Error during template rendering or file writing from ManifestData: {e}"
            logger.error(error_msg, exc_info=True)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Failed to write manifest file from ManifestData."
            state['is_manifest_generated'] = False
            # state['manifest_data'] is already set, no need to change it here
            return state

        if success_write:
            logger.info(f"Successfully generated manifest file from ManifestData: {manifest_output_path_str}")
            state['is_manifest_generated'] = True
            state['last_event_summary'] = f"Goal Manifest '{manifest_data_instance.goal_title}' generated from ManifestData."
        else:
            error_msg = f"[ManifestCreate] WriteFileFromTemplateService failed to write manifest from ManifestData to '{manifest_output_path_str}'."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Failed to write manifest file from ManifestData (service reported failure)."
            state['is_manifest_generated'] = False
            return state

        # Record manifest creation in changelog
        if state['is_manifest_generated']:
            logger.info("Attempting to record manifest creation in changelog.")
            changelog_summary = f"Goal Manifest Created: {manifest_data_instance.goal_title}"
            try:
                success_changelog = changelog_service.record_event_in_changelog(
                    current_workflow_state=state,
                    preceding_event_summary=changelog_summary
                )
            except Exception as e:
                error_msg = f"[ManifestCreate] Error during changelog service call: {e}"
                logger.error(error_msg, exc_info=True)
                state['is_changelog_entry_added'] = False
                current_error = state.get('error_message', "")
                state['error_message'] = f"{current_error} [ChangelogError] {error_msg}".strip()
                state['last_event_summary'] = f"Manifest '{manifest_data_instance.goal_title}' generated, but changelog update failed."
                return state

            if success_changelog:
                logger.info("Successfully recorded manifest creation in changelog.")
                state['is_changelog_entry_added'] = True
                state['last_event_summary'] = f"Manifest '{manifest_data_instance.goal_title}' created and changelog updated."
            else:
                error_msg = "[ManifestCreate] ChangelogService failed to record event."
                logger.error(error_msg)
                state['is_changelog_entry_added'] = False
                current_error = state.get('error_message', "")
                state['error_message'] = f"{current_error} [ChangelogError] {error_msg}".strip()
                state['last_event_summary'] = f"Manifest '{manifest_data_instance.goal_title}' generated, but changelog update failed (service reported failure)."

            # Attempt to commit changes
            commit_message = f"AI Army Man - Created goal manifest for: {manifest_data_instance.goal_title}"
            logger.info(f"Attempting to commit changes with message: '{commit_message}'")
            try:
                commit_success = git_service.commit_changes(commit_message)
                if commit_success:
                    logger.info("Successfully committed manifest and changelog changes.")
                else:
                    logger.error("Failed to commit manifest and changelog changes.")
                    state['last_event_summary'] += ", but git commit failed."
            except Exception as e:
                logger.error(f"Error during git commit: {e}", exc_info=True)
                state['last_event_summary'] += f", but git commit failed: {e}"

    except Exception as e:
        error_msg = f"[ManifestCreate] Unexpected error during manifest creation: {e}"
        logger.error(error_msg, exc_info=True)
        state['is_manifest_generated'] = False
        state['is_changelog_entry_added'] = False
        state['manifest_data'] = None # Clear manifest_data on unexpected error
        state['error_message'] = error_msg
        state['last_event_summary'] = f"Unexpected error in manifest creation: {e}"
        if state.get('aider_last_exit_code') is None:
            state['aider_last_exit_code'] = -1

    return state
