import logging
import os
import sys
import uuid  # For generating random text for the changelog entry

from src.config import AppConfig
from src.services.aider_service import AiderService
from src.services.changelog_service import ChangelogService
from src.state import WorkflowState  # TypedDict for workflow state
from src.utils.logging_setup import setup_logging

# Get a logger for this test script
logger = logging.getLogger(__name__)

def run_changelog_update_test(app_config: AppConfig, changelog_service: ChangelogService):
    """
    Tests the ChangelogService's ability to record an event in the changelog.
    This test will modify the changelog file specified in config.yml.
    Manual verification of the changelog file is required.
    """
    logger.info("--- Starting ChangelogService Update Test ---")

    # 1. Prepare a minimal WorkflowState instance
    # Only populate fields directly used by ChangelogService or essential for state structure
    mock_workflow_state: WorkflowState = {
        "current_step_name": "TestChangelogStep",
        "goal_folder_path": app_config.goal_root_path, # For context, though not directly used by service
        "workspace_folder_path": app_config.workspace_root_path, # For context
        "task_description_path": None,
        "task_description_content": None,
        "manifest_template_path": None, # Not directly used by changelog service
        "changelog_template_path": os.path.join(app_config.workspace_root_path, app_config.changelog_template_filename),
        "manifest_output_path": "data/output/placeholder_manifest.md", # Example path
        "changelog_output_path": os.path.join(app_config.goal_root_path, app_config.changelog_output_filename),
        "last_event_summary": "Placeholder: Previous workflow step completed successfully.",
        "aider_last_exit_code": 0,
        "error_message": None,
        "is_manifest_generated": True, # Test with manifest generated
        "is_changelog_entry_added": False # Initial state
    }
    logger.debug(f"Mock WorkflowState prepared: {mock_workflow_state}")

    # 2. Define a preceding_event_summary for the new changelog entry
    event_summary_text = "Updated fake file `fake.txt` to have more babies in it"
    logger.info(f"Event summary for changelog: '{event_summary_text}'")

    # 3. Execute the changelog service
    changelog_file_path = os.path.join(
        app_config.goal_root_path,
        app_config.changelog_output_filename
    )
    logger.info(f"Attempting to update changelog file: {changelog_file_path}")

    try:
        success = changelog_service.record_event_in_changelog(
            current_workflow_state=mock_workflow_state,
            preceding_event_summary=event_summary_text
        )
        
        if success:
            logger.info("ChangelogService.record_event_in_changelog reported SUCCESS.")
            logger.info(f"  An entry for '{event_summary_text}' should have been added to '{changelog_file_path}'.")
        else:
            logger.warning("ChangelogService.record_event_in_changelog reported FAILURE.")
            logger.warning(f"  The changelog file '{changelog_file_path}' may not have been updated as expected.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during ChangelogService.record_event_in_changelog(): {e}", exc_info=True)
        success = False # Ensure failure is noted

    logger.info("--- ChangelogService Update Test Finished ---")
    logger.info(f"*** IMPORTANT: This test attempted to modify '{changelog_file_path}'. ***")
    logger.info("*** Please MANUALLY VERIFY its content. ***")

if __name__ == "__main__":
    # Setup logging with a default level (e.g., INFO)
    # The actual log level can be further configured in AppConfig if needed
    setup_logging(log_level=logging.INFO) 
    
    main_logger = logging.getLogger(__name__) # Logger for the main script execution
    main_logger.info("====== Starting ChangelogService Test Suite ======")

    # Load AppConfig
    app_config = None
    try:
        app_config = AppConfig.load_from_yaml()
        main_logger.info("AppConfig loaded successfully")
    except Exception as e:
        main_logger.error("Failed to load AppConfig", exc_info=True)
        main_logger.error("Cannot proceed with tests without AppConfig.")
        main_logger.info("====== ChangelogService Test Suite Aborted ======")
        sys.exit(1)

    # Instantiate AiderService
    aider_service = None
    try:
        aider_service = AiderService(app_config=app_config)
        main_logger.info("AiderService instantiated successfully.")
    except Exception as e:
        main_logger.error(f"Failed to instantiate AiderService: {e}", exc_info=True)
        main_logger.error("Cannot proceed with tests without AiderService.")
        main_logger.info("====== ChangelogService Test Suite Aborted ======")
        sys.exit(1)

    # Instantiate ChangelogService
    changelog_service = None
    try:
        # Assumes ChangelogService __init__ takes app_config and aider_service
        changelog_service = ChangelogService(app_config=app_config, aider_service=aider_service)
        main_logger.info("ChangelogService instantiated successfully.")
    except Exception as e:
        main_logger.error(f"Failed to instantiate ChangelogService: {e}", exc_info=True)
        main_logger.error("Cannot proceed with tests without ChangelogService.")
        main_logger.info("====== ChangelogService Test Suite Aborted ======")
        sys.exit(1)

    # Run the test
    run_changelog_update_test(app_config, changelog_service)

    main_logger.info("====== ChangelogService Test Suite Finished ======")
