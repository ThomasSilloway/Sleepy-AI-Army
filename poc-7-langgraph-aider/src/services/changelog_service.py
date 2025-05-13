"""Defines the ChangelogService class."""
import logging
import os
from datetime import datetime

from src.config import AppConfig
from src.services.aider_service import AiderService  # Corrected import path
from src.state import WorkflowState

logger = logging.getLogger(__name__)

class ChangelogService:
    def __init__(self, app_config: AppConfig, aider_service: AiderService):
        self.app_config = app_config
        self.aider_service = aider_service

    def record_event_in_changelog(self, current_workflow_state: WorkflowState, preceding_event_summary: str) -> bool:
        """
        Records an event in the changelog.md file using AiderService.

        Args:
            current_workflow_state: The current state of the workflow.
            preceding_event_summary: A summary of the event to be logged.

        Returns:
            True if the event was successfully recorded, False otherwise.
        """
        logger.info(f"Attempting to record event in changelog: {preceding_event_summary}")

        try:
            # 1. Generate timestamp
            # Format: [YYYY-MM-DD HH:MM AM/PM TZ] e.g., [2024-07-16 03:45 PM PDT]
            timestamp = datetime.now().astimezone().strftime('%Y-%m-%d %I:%M %p %Z')
            logger.debug(f"Generated timestamp for changelog: {timestamp}")

            # 2. Determine changelog file path
            changelog_file_path = os.path.join(
                self.app_config.goal_root_path,
                self.app_config.changelog_output_filename
            )
            # Ensure the directory exists, Aider might not create it
            os.makedirs(os.path.dirname(changelog_file_path), exist_ok=True)
            logger.debug(f"Target changelog file path: {changelog_file_path}")

            # 3. Construct sophisticated prompt for aider
            # Details from workflow state for context            
            last_event_summary_state = current_workflow_state.get('last_event_summary', 'N/A')
            changelog_template_file_path = os.path.join(
                self.app_config.workspace_root_path,
                self.app_config.changelog_template_filename
            )

            aider_prompt = f"""UPDATE the file '{changelog_file_path}' by appending a new changelog entry.

GENERATE the new changelog entry strictly following the format in `{changelog_template_file_path}` using the data below:

- Timestamp: {timestamp}
- Preceeding Event Summary: {preceding_event_summary}
- Workflow state's last recorded event: "{last_event_summary_state}"

Ensure this new entry is appended to the end of the file.
If the file '{changelog_file_path}' is empty or does not exist, create it and add this as the first entry.
The title and bullet points should be concise and accurately reflect the event.
Do not add any other commentary before or after the changelog entry itself.
"""
            logger.debug(f"Constructed aider prompt:\n\n{aider_prompt}\n\n")

            # 4. Execute aider command
            # Files to add (aider will edit this file)
            files_to_edit = [changelog_file_path]
            # Aider command arguments
            command_args = [
                "-m", aider_prompt, 
                "--read", changelog_template_file_path,
                "--model", self.app_config.changelog_aider_model,
            ]

            logger.info(f"Executing AiderService to update changelog: {changelog_file_path}")
            exit_code = self.aider_service.execute(command_args=command_args, files_to_add=files_to_edit)

            # 5. Handle exit status
            if exit_code == 0:
                logger.info(f"Changelog entry successfully added/updated in '{changelog_file_path}'. Aider exit code: {exit_code}")
                return True
            else:
                logger.error(f"Failed to add/update changelog entry in '{changelog_file_path}'. Aider exit code: {exit_code}")
                return False

        except Exception as e:
            logger.error(f"An unexpected error occurred in record_event_in_changelog: {e}", exc_info=True)
            return False
