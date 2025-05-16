"""Contains logic for the generate_manifest_node."""
import logging
import os
from pathlib import Path

from src.state import WorkflowState
from src.config import AppConfig
from src.services.aider_service import AiderService
from src.services.changelog_service import ChangelogService

logger = logging.getLogger(__name__)

def generate_manifest_node(state: WorkflowState, config) -> WorkflowState:
    """
    Generates the goal manifest file using AiderService based on the task
    description and templates. Records the event in the changelog upon success.
    Updates WorkflowState with the outcome.
    """
    state['current_step_name'] = "generate_manifest_node"
    logger.info(f"Executing node: {state['current_step_name']}")

    try:
        services_config = config["configurable"]
        app_config: AppConfig = services_config["app_config"]
        aider_service: AiderService = services_config["aider_service"]
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
        
        spec_file_abs_path = r"C:\GithubRepos\Sleepy-AI-Army\poc-7-langgraph-aider\src\ai-specs\goal-manifest-creation-spec.md"

        # Construct the aider prompt
        # Using state['manifest_template_path'] as it's resolved in initialize_workflow_node
        # Using state['manifest_output_path'] as it's resolved in initialize_workflow_node

        
        aider_prompt = f"""
You are being tasked with generating a goal manifest file.

Primary Instructions File:
You MUST follow the detailed instructions located in the file named `{spec_file_abs_path}`. This file has been provided to you for reading.

Key File Paths for Your Task:
1.  **Output Manifest File:** The file you are to create or update is located at `{manifest_output_path_str}` (relative to the Git project root). This is your SOLE target for writing.
2.  **Manifest Template File:** You MUST use the structure and guidance from the file named `{manifest_template_path_str}`. This file has also been provided to you for reading.

Task Description Context:
The content for the manifest should be based on the following task description:
=========================
{task_description_content}
=========================

CRITICAL DIRECTIVES:
-   Your ONLY objective is to generate and write to the specified Output Manifest File (`{manifest_output_path_str}`).
-   You MUST NOT, under any circumstances, modify, analyze, or even suggest adding any other files.
-   You MUST NOT attempt to execute or implement any coding tasks mentioned in the Task Description Context. Your role is strictly limited to generating the manifest document.
-   After successfully generating and writing the manifest, you MUST stop all further actions.

Proceed by strictly adhering to the instructions in `{spec_file_abs_path}` using the information defined above.
"""
        logger.debug(f"Constructed aider prompt for manifest generation:\n\n{aider_prompt}\n\n")

        # Prepare arguments for AiderService.execute()
        # The manifest_output_path_str is the file aider will create/edit.
        files_to_edit = [manifest_output_path_str]
        # The manifest_template_path_str is a read-only context file.
        command_args = [
            "-m", aider_prompt,
            "--read", manifest_template_path_str,
            "--read", spec_file_abs_path,
            "--model", app_config.goal_manifest_aider_model,
        ]

        logger.info(f"Invoking AiderService to generate manifest: {manifest_output_path_str}")
        exit_code = aider_service.execute(command_args=command_args, files_to_add=files_to_edit)
        state['aider_last_exit_code'] = exit_code

        # Handle successful manifest generation
        if exit_code == 0 and os.path.exists(manifest_output_path_str):
            logger.info(f"Aider successfully generated manifest file: {manifest_output_path_str}")
            state['is_manifest_generated'] = True
            # Using manifest_output_path as per WorkflowState and initialization node.
            state['last_event_summary'] = f"Goal Manifest generated: {manifest_output_path_str}"
            
            logger.info("Attempting to record manifest generation event in changelog.")
            changelog_success = changelog_service.record_event_in_changelog(
                current_workflow_state=state,
                preceding_event_summary=state['last_event_summary']
            )
            state['is_changelog_entry_added'] = changelog_success

            if changelog_success:
                logger.info("Changelog entry successfully added for manifest generation.")
            else:
                logger.warning("Failed to add changelog entry for manifest generation. This is a non-critical error for manifest generation itself.")
            
            state['error_message'] = None # Clear any previous error if successful now

        # Handle manifest generation failure
        else:
            error_msg = f"Failed to generate Goal Manifest. Aider exit code: {exit_code}."
            if exit_code == 0 and not os.path.exists(manifest_output_path_str):
                error_msg += f" Manifest file not found at {manifest_output_path_str} despite aider success exit code."
            
            logger.error(error_msg)
            state['is_manifest_generated'] = False
            state['error_message'] = error_msg
            state['last_event_summary'] = "Failed to generate Goal Manifest."
            # is_changelog_entry_added remains as it was (likely False or not set if manifest failed)

    except Exception as e:
        error_msg = f"[ManifestGeneration] Unexpected error during manifest generation: {e}"
        logger.error(error_msg, exc_info=True)
        state['is_manifest_generated'] = False
        state['error_message'] = error_msg
        state['last_event_summary'] = f"Unexpected error: {e}"
        # Ensure aider_last_exit_code is set if exception occurs before aider call or if it's not set by aider_service
        if state.get('aider_last_exit_code') is None:
            state['aider_last_exit_code'] = -1 # Generic error code

    return state
