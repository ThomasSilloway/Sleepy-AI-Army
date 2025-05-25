import logging
import os
import re  # Added for regex verification
import sys
import uuid

from dotenv import load_dotenv
from src.config import AppConfig
from src.services.changelog_service import ChangelogService
from src.state import WorkflowState
from src.utils.logging_setup import setup_logging

logger = logging.getLogger(__name__)
load_dotenv()

def run_changelog_update_test(app_config: AppConfig, changelog_service: ChangelogService):
    """
    Tests the ChangelogService's ability to record an event in the changelog
    using direct f-string formatting and verifies the output.
    """
    logger.overview("--- Starting ChangelogService Update Test (Direct Formatting) ---")

    changelog_file_path = os.path.join(app_config.goal_root_path, app_config.changelog_output_filename)

    # Ensure a clean state by removing the changelog file if it exists
    if os.path.exists(changelog_file_path):
        try:
            os.remove(changelog_file_path)
            logger.info(f"Removed existing changelog file: {changelog_file_path}")
        except OSError as e:
            logger.error(f"Error removing existing changelog file {changelog_file_path}: {e}")
            # If we can't remove the file, we should not proceed as assertions might be incorrect
            return

    # 1. Prepare a minimal WorkflowState instance
    mock_workflow_state: WorkflowState = {
        "current_step_name": "TestChangelogStep",
        "goal_folder_path": app_config.goal_root_path,
        "workspace_folder_path": app_config.workspace_root_path,
        "task_description_path": None,
        "task_description_content": None,
        "manifest_template_path": None,
        "changelog_template_path": None, # No longer used by the service
        "manifest_output_path": "data/output/placeholder_manifest.md",
        "changelog_output_path": changelog_file_path,
        "last_event_summary": "Initial state before any test events.", # Not used by current service version
        "aider_last_exit_code": 0,
        "error_message": None,
        "is_manifest_generated": True,
        "is_changelog_entry_added": False
    }
    logger.debug(f"Mock WorkflowState prepared: {mock_workflow_state}")

    # Timestamp pattern for regex verification
    timestamp_pattern = r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2} [AP]M [A-Z]{3,}\]"

    # --- First Entry ---
    event_summary_text_1 = f"Test Event 1: First direct formatted entry {uuid.uuid4()}"
    logger.info(f"Recording first event: '{event_summary_text_1}'")

    success1 = changelog_service.record_event_in_changelog(
        current_workflow_state=mock_workflow_state,
        preceding_event_summary=event_summary_text_1
    )

    if not success1:
        logger.error("Failed to record the first changelog entry. Test cannot proceed.")
        return

    logger.info("Verifying content after first entry...")
    try:
        with open(changelog_file_path, encoding='utf-8') as f:
            actual_content_1 = f.read()

        # Expected structure for the first entry
        # Escaping regex special characters in summary if any (though uuid shouldn't have them)
        escaped_summary_1 = re.escape(event_summary_text_1)
        expected_pattern_1 = rf"^# {escaped_summary_1}\n{timestamp_pattern}\n\n\* {escaped_summary_1}\n$"

        match_1 = re.search(expected_pattern_1, actual_content_1, re.MULTILINE)
        if match_1:
            logger.info("First entry format and content VERIFIED.")
        else:
            logger.error(f"First entry format MISMATCH. Expected pattern:\n{expected_pattern_1}\nActual content:\n{actual_content_1}")
            # Log more details for debugging
            logger.debug(f"Header check: '# {event_summary_text_1}' in actual_content_1: {'# ' + event_summary_text_1 in actual_content_1}")
            logger.debug(f"Timestamp check: regex search for {timestamp_pattern} in actual_content_1: {bool(re.search(timestamp_pattern, actual_content_1))}")
            logger.debug(f"Bullet check: '* {event_summary_text_1}' in actual_content_1: {'* ' + event_summary_text_1 in actual_content_1}")

    except FileNotFoundError:
        logger.error(f"Changelog file not found after first write: {changelog_file_path}")
        return
    except Exception as e:
        logger.error(f"Error reading or verifying changelog after first entry: {e}", exc_info=True)
        return

    # --- Second Entry ---
    event_summary_text_2 = f"Test Event 2: Second direct formatted entry {uuid.uuid4()}"
    logger.info(f"Recording second event: '{event_summary_text_2}'")

    # Update mock state if necessary (e.g., if last_event_summary was used by service)
    # mock_workflow_state["last_event_summary"] = event_summary_text_1 

    success2 = changelog_service.record_event_in_changelog(
        current_workflow_state=mock_workflow_state,
        preceding_event_summary=event_summary_text_2
    )

    if not success2:
        logger.error("Failed to record the second changelog entry.")
        return

    logger.info("Verifying content after second entry...")
    try:
        with open(changelog_file_path, encoding='utf-8') as f:
            actual_content_2 = f.read()

        # Expected structure for the second entry, appended to the first
        escaped_summary_1 = re.escape(event_summary_text_1) # Re-escape for clarity
        escaped_summary_2 = re.escape(event_summary_text_2)

        # Pattern for first entry (already verified, but used for context)
        # Note: the $ at the end of expected_pattern_1 ensures it was the end of the string at that time.
        # Now we look for it, followed by newlines and the second entry.
        # The service should add \n\n between entries if current_content is not empty.
        # The first entry itself ends with a \n. So, current_content.strip() + \n\n + new_entry
        # new_entry_content from service: "# summary\n[timestamp]\n\n* summary\n"
        # So, after strip(), first entry is: "# summary1\n[timestamp1]\n\n* summary1"
        # Then combined: "# summary1\n[timestamp1]\n\n* summary1\n\n# summary2\n[timestamp2]\n\n* summary2\n"

        expected_pattern_combined = (
            rf"^# {escaped_summary_1}\n"
            rf"{timestamp_pattern}\n\n"
            rf"\* {escaped_summary_1}\n\n"  # Two newlines separating entries
            rf"# {escaped_summary_2}\n"
            rf"{timestamp_pattern}\n\n"
            rf"\* {escaped_summary_2}\n$"
        )

        match_combined = re.search(expected_pattern_combined, actual_content_2, re.MULTILINE)
        if match_combined:
            logger.info("Second entry appended correctly, format and content VERIFIED.")
        else:
            logger.error(f"Second entry append or format MISMATCH. Expected combined pattern:\n{expected_pattern_combined}\nActual content:\n{actual_content_2}")

    except FileNotFoundError:
        logger.error(f"Changelog file not found after second write: {changelog_file_path}")
    except Exception as e:
        logger.error(f"Error reading or verifying changelog after second entry: {e}", exc_info=True)

    logger.overview("--- ChangelogService Update Test (Direct Formatting) Finished ---")
    logger.overview(f"*** IMPORTANT: This test attempted to modify '{changelog_file_path}'. ***")
    logger.overview("*** Please MANUALLY VERIFY its content if automated checks show errors. ***")


if __name__ == "__main__":
    app_config = None
    main_logger = logging.getLogger(__name__) 
    try:
        app_config = AppConfig.load_from_yaml()
        setup_logging(app_config=app_config) 
        main_logger = logging.getLogger(__name__) 
        main_logger.info("====== Starting ChangelogService Test Suite ======")
        main_logger.info("AppConfig loaded successfully")
    except Exception:
        main_logger.error("Failed to load AppConfig or setup logging", exc_info=True)
        main_logger.error("Cannot proceed with tests.")
        main_logger.info("====== ChangelogService Test Suite Aborted ======")
        sys.exit(1)

    changelog_service = None
    try:
        changelog_service = ChangelogService(app_config=app_config)
        main_logger.overview("ChangelogService instantiated successfully.")
    except Exception as e:
        main_logger.error(f"Failed to instantiate ChangelogService: {e}", exc_info=True)
        main_logger.error("Cannot proceed with tests without ChangelogService.")
        main_logger.info("====== ChangelogService Test Suite Aborted ======")
        sys.exit(1)

    if app_config and changelog_service:
        main_logger.info("All services initialized. Running test...")
        try:
            run_changelog_update_test(app_config, changelog_service)
        except Exception as e:
            main_logger.error(f"An error occurred while running the test: {e}", exc_info=True)
    else:
        main_logger.error("One or more services not initialized. Skipping test execution.")

    main_logger.overview("====== ChangelogService Test Suite Finished ======")
