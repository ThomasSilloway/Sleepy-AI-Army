"""Defines the ChangelogService class."""
import logging
import os
from datetime import datetime

from src.config import AppConfig
from src.state import WorkflowState

logger = logging.getLogger(__name__)

class ChangelogService:
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config

    def record_event_in_changelog(self, current_workflow_state: WorkflowState, preceding_event_summary: str) -> bool:
        """
        Records an event in the changelog.md file by direct f-string formatting.

        Args:
            current_workflow_state: The current state of the workflow.
            preceding_event_summary: A summary of the event to be logged.

        Returns:
            True if the event was successfully recorded, False otherwise.
        """
        logger.info(f"Attempting to record event in changelog: {preceding_event_summary}")

        try:
            timestamp_str = datetime.now().astimezone().strftime('%Y-%m-%d %I:%M %p %Z')
            logger.debug(f"Generated timestamp for changelog: {timestamp_str}")

            changelog_file_path = os.path.join(
                self.app_config.goal_root_path,
                self.app_config.changelog_output_filename
            )
            os.makedirs(os.path.dirname(changelog_file_path), exist_ok=True)
            logger.debug(f"Target changelog file path: {changelog_file_path}")

            # 3. Manually Format Changelog Entry using f-strings
            # preceding_event_summary comes from the method arguments
            new_entry_content = f"# {preceding_event_summary}\n"
            new_entry_content += f"[{timestamp_str}]\n\n"  # Double newline for a blank line
            new_entry_content += f"* {preceding_event_summary}\n"
            
            logger.debug(f"Formatted new changelog entry:\n{new_entry_content}")

            # 4. Write to file using refined logic
            current_content = ""
            if os.path.exists(changelog_file_path):
                with open(changelog_file_path, 'r', encoding='utf-8') as f:
                    current_content = f.read().strip() # Read and strip trailing newlines

            if current_content: # If there's existing content
                # Add two newlines to ensure a blank line before the new entry
                combined_content = current_content + "\n\n" + new_entry_content
            else: # If file is empty or new
                combined_content = new_entry_content

            with open(changelog_file_path, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            
            logger.info(f"Changelog entry successfully added to '{changelog_file_path}'.")
            return True

        except Exception as e:
            logger.error(f"An unexpected error occurred in record_event_in_changelog: {e}", exc_info=True)
            return False
