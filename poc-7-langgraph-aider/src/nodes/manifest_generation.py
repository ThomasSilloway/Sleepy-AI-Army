"""Contains logic for the generate_manifest_node."""
import logging
from datetime import datetime
from typing import Any  # Any will be replaced by any if used

from src.config import AppConfig
from src.pydantic_models.core_schemas import ManifestConfigLLM
from src.services.changelog_service import ChangelogService
from src.services.llm_prompt_service import LlmPromptService
from src.services.write_file_from_template_service import WriteFileFromTemplateService
from src.state import WorkflowState

logger = logging.getLogger(__name__)

# This node needs to be async if LlmPromptService.get_structured_output is async
# and we want to await it properly.
async def generate_manifest_node(state: WorkflowState, config) -> WorkflowState:
    """
    Generates the goal manifest file using LlmPromptService for data extraction
    and WriteFileFromTemplateService for rendering. Records the event in the
    changelog upon success. Updates WorkflowState with the outcome.
    """
    state['current_step_name'] = "generate_manifest_node"
    logger.info(f"Executing node: {state['current_step_name']}")

    manifest_config_llm: ManifestConfigLLM | None = None

    try:
        services_config = config["configurable"]
        app_config: AppConfig = services_config["app_config"]
        llm_prompt_service: LlmPromptService = services_config["llm_prompt_service"]
        write_file_service: WriteFileFromTemplateService = services_config["write_file_service"]
        changelog_service: ChangelogService = services_config["changelog_service"]

        task_description_content = state.get('task_description_content')
        manifest_template_path_str = state.get('manifest_template_path')
        manifest_output_path_str = state.get('manifest_output_path')

        if not all([task_description_content, manifest_template_path_str, manifest_output_path_str]):
            error_msg = "[ManifestGeneration] Critical information missing in state for manifest generation (task_description_content, manifest_template_path, or manifest_output_path)."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Missing critical info for manifest generation."
            state['is_manifest_generated'] = False
            return state

        # Task 2: Integrate LLM Interaction
        logger.info("Attempting to extract structured data from task description using LLM.")

        # Construct prompts for LlmPromptService
        # Referring to tests/test_llm_prompt_service.py for guidance
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
            # Invoke llm_prompt_service.get_structured_output asynchronously
            manifest_config_llm = await llm_prompt_service.get_structured_output(
                messages=messages,
                output_pydantic_model_type=ManifestConfigLLM,
                llm_model_name=app_config.gemini_weak_model_name
            )
        except Exception as e:
            error_msg = f"[ManifestGeneration] Error during LLM call: {e}"
            logger.error(error_msg, exc_info=True)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: LLM call failed during manifest generation."
            state['is_manifest_generated'] = False
            return state

        if not manifest_config_llm:
            error_msg = "[ManifestGeneration] LLM did not return structured data (ManifestConfigLLM is None)."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: LLM failed to parse task description for manifest."
            state['is_manifest_generated'] = False
            return state

        logger.info(f"LLM successfully extracted data: {manifest_config_llm.goal_title}")
        state['last_event_summary'] = f"LLM extracted manifest data for: {manifest_config_llm.goal_title}"

        # Task 3: Integrate Template-Based File Writing
        logger.info("Attempting to render and write goal-manifest.md.")

        # Prepare context for Jinja2 template
        current_timestamp_iso = datetime.now().isoformat()
        artifacts_section_content = f"* [in-progress] {manifest_config_llm.small_tweak_file_path}"

        template_context: dict[str, Any] = {
            "goal_title": manifest_config_llm.goal_title,
            "task_description_for_manifest": manifest_config_llm.task_description, # Using task_description from Pydantic model
            "last_updated_timestamp": current_timestamp_iso,
            "overall_status": "New",
            "current_focus": task_description_content, # Full content of task-description.md
            "artifacts_section_content": artifacts_section_content,
            "ai_questions_list": [], # Empty list as per PRD
            "default_ai_questions_placeholder": "",
            "human_responses_content": "NONE" # As per PRD
        }

        # Avoid logging full task description
        logger.debug(f"Template context prepared: { {k:v for k,v in template_context.items() if k != 'current_focus'} }") 

        try:
            success_write = write_file_service.render_and_write_file(
                template_abs_path_str=manifest_template_path_str,
                context=template_context,
                output_abs_path_str=manifest_output_path_str
            )
        except Exception as e:
            error_msg = f"[ManifestGeneration] Error during template rendering or file writing: {e}"
            logger.error(error_msg, exc_info=True)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Failed to write manifest file."
            state['is_manifest_generated'] = False
            return state

        if success_write:
            logger.info(f"Successfully generated manifest file: {manifest_output_path_str}")
            state['is_manifest_generated'] = True
            state['last_event_summary'] = f"Goal Manifest '{manifest_config_llm.goal_title}' generated."
        else:
            error_msg = f"[ManifestGeneration] WriteFileFromTemplateService failed to write manifest to '{manifest_output_path_str}'."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Failed to write manifest file (service reported failure)."
            state['is_manifest_generated'] = False
            return state # Stop if manifest writing failed

        # Task 4: Integrate Changelog Service Invocation
        if state['is_manifest_generated']:
            logger.info("Attempting to record manifest creation in changelog.")
            changelog_summary = f"Goal Manifest Created: {manifest_config_llm.goal_title}"

            try:
                success_changelog = changelog_service.record_event_in_changelog(
                    current_workflow_state=state,
                    preceding_event_summary=changelog_summary
                )
            except Exception as e:
                error_msg = f"[ManifestGeneration] Error during changelog service call: {e}"
                logger.error(error_msg, exc_info=True)
                # Manifest was generated, but changelog failed. Update state accordingly.
                state['is_changelog_entry_added'] = False
                # Append to error message, don't overwrite manifest success summary yet
                current_error = state.get('error_message', "")
                state['error_message'] = f"{current_error} [ChangelogError] {error_msg}".strip()
                state['last_event_summary'] = f"Manifest '{manifest_config_llm.goal_title}' generated, but changelog update failed."
                return state


            if success_changelog:
                logger.info("Successfully recorded manifest creation in changelog.")
                state['is_changelog_entry_added'] = True
                state['last_event_summary'] = f"Manifest '{manifest_config_llm.goal_title}' created and changelog updated."
            else:
                error_msg = "[ManifestGeneration] ChangelogService failed to record event."
                logger.error(error_msg)
                # Manifest was generated, but changelog failed.
                state['is_changelog_entry_added'] = False
                current_error = state.get('error_message', "")
                state['error_message'] = f"{current_error} [ChangelogError] {error_msg}".strip()
                state['last_event_summary'] = f"Manifest '{manifest_config_llm.goal_title}' generated, but changelog update failed (service reported failure)."
                # Do not return error for the whole node if only changelog failed, but reflect in summary.

    except Exception as e:
        error_msg = f"[ManifestGeneration] Unexpected error during manifest generation: {e}"
        logger.error(error_msg, exc_info=True)
        state['is_manifest_generated'] = False # Ensure it's false if an overarching error occurs
        state['is_changelog_entry_added'] = False
        state['error_message'] = error_msg
        state['last_event_summary'] = f"Unexpected error in manifest generation: {e}"
        if state.get('aider_last_exit_code') is None: # Aider not directly used here, but good practice
            state['aider_last_exit_code'] = -1 

    return state
