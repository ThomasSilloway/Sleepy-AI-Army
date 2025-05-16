"""Contains logic for the execute_small_tweak_node."""
import logging
import os
from pathlib import Path

from src.state import WorkflowState
from src.config import AppConfig
from src.services.aider_service import AiderService
from src.services.git_service import GitService
from src.services.changelog_service import ChangelogService

logger = logging.getLogger(__name__)

def execute_small_tweak_node(state: WorkflowState, config) -> WorkflowState:
    """
    Executes a "Small Tweak" using AiderService based on instructions in
    task_description_path. Records git information and changelog on success.
    Updates WorkflowState with the outcome.
    """
    state['current_step_name'] = "execute_small_tweak_node"
    logger.info(f"Executing node: {state['current_step_name']}")

    try:
        services_config = config["configurable"]
        app_config: AppConfig = services_config["app_config"]
        aider_service: AiderService = services_config["aider_service"]
        git_service: GitService = services_config["git_service"]
        changelog_service: ChangelogService = services_config["changelog_service"]

        task_description_path_str = state.get('task_description_path')

        if not task_description_path_str:
            error_msg = "[SmallTweakExecution] Critical information missing: task_description_path not found in state."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Missing task_description_path for Small Tweak."
            state['is_code_change_committed'] = False
            return state
        
        if not os.path.exists(task_description_path_str):
            error_msg = f"[SmallTweakExecution] Task description file not found at: {task_description_path_str}"
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = f"Error: Task description file missing at {task_description_path_str}."
            state['is_code_change_committed'] = False
            return state

        task_desc_filename = Path(task_description_path_str).name
        aider_prompt = f"""Please apply the changes described in the file '{task_desc_filename}'.
This file has been provided to you as read-only context.
Please ensure to commit the changes with a descriptive message if successful.
The changes should be applied to the files in the current Git repository.
"""
        logger.debug(f"Constructed aider prompt for small tweak:\n\n{aider_prompt}\n\n")

        # Aider will determine files to edit from the instructions in task_description_path_str
        # The task_description_path_str itself is provided as read-only context.
        # Aider is expected to run in the context of the app_config.goal_git_path.
        # AiderService should be configured to use app_config.goal_git_path as cwd.
        # For now, we assume AiderService is correctly set up or aider CLI can find the repo.
        files_to_edit_or_add_to_context = [] # No files explicitly added for editing by default
        command_args = [
            "-m", aider_prompt,
            "--read", task_description_path_str,
            # Using goal_manifest_aider_model as a general purpose model for now.
            # Ideally, a specific model for tweaks could be configured in AppConfig.
            "--model", app_config.goal_manifest_aider_model,
        ]

        logger.info("Invoking AiderService to execute small tweak.")
        # Assuming AiderService runs with cwd = app_config.goal_git_path
        exit_code = aider_service.execute(command_args=command_args, files_to_add=files_to_edit_or_add_to_context)
        state['aider_last_exit_code'] = exit_code

        if exit_code == 0:
            logger.info("Aider successfully executed the small tweak.")
            state['is_code_change_committed'] = True
            
            commit_hash = git_service.get_last_commit_hash()
            commit_summary_raw = git_service.get_last_commit_summary()
            file_stats_raw = git_service.get_last_commit_file_stats()

            state['last_change_commit_hash'] = commit_hash
            state['tweak_file_change_stats'] = file_stats_raw

            combined_summary = commit_summary_raw or "N/A"
            if file_stats_raw:
                combined_summary += f"\n\nFile Stats:\n{file_stats_raw}"
            state['last_change_commit_summary'] = combined_summary
            
            event_summary = f"Small Tweak applied. Commit: {commit_hash or 'N/A'} - {commit_summary_raw or 'N/A'}"
            state['last_event_summary'] = event_summary
            state['error_message'] = None

            logger.info("Attempting to record small tweak event in changelog.")
            changelog_success = changelog_service.record_event_in_changelog(
                current_workflow_state=state,
                preceding_event_summary=event_summary 
            )
            state['is_changelog_entry_added'] = changelog_success
            if changelog_success:
                logger.info("Changelog entry successfully added for small tweak.")
            else:
                logger.warning("Failed to add changelog entry for small tweak. This is non-critical for the tweak itself.")

        else:
            error_msg = f"Failed to apply Small Tweak. Aider exit code: {exit_code}."
            logger.error(error_msg)
            state['is_code_change_committed'] = False
            state['error_message'] = error_msg
            state['last_event_summary'] = f"Failed to apply Small Tweak. Aider exit code: {exit_code}"
            # Clear git info fields on failure
            state['last_change_commit_hash'] = None
            state['last_change_commit_summary'] = None
            state['tweak_file_change_stats'] = None

    except Exception as e:
        error_msg = f"[SmallTweakExecution] Unexpected error during small tweak execution: {e}"
        logger.error(error_msg, exc_info=True)
        state['is_code_change_committed'] = False
        state['error_message'] = error_msg
        state['last_event_summary'] = f"Unexpected error during Small Tweak: {e}"
        if state.get('aider_last_exit_code') is None:
            state['aider_last_exit_code'] = -1 
        state['last_change_commit_hash'] = None
        state['last_change_commit_summary'] = None
        state['tweak_file_change_stats'] = None
            
    return state
