
import sys
import os
import logging
import uuid # For generating random text

# Adjust sys.path to allow imports from the 'src' directory
# This assumes the script is in 'poc-7-langgraph-aider/tests/'
# and 'src' is in 'poc-7-langgraph-aider/'
# Also assumes 'config.yml' is in 'poc-7-langgraph-aider/'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.config import AppConfig
    from src.services.aider_service import AiderService
    from src.utils.logging_setup import setup_logging
except ImportError as e:
    print(f"Error importing necessary modules. This script expects to be in a 'tests' subdirectory of the project root.")
    print(f"Ensure 'src' directory is at the project root and contains the required modules.")
    print(f"Details: {e}")
    sys.exit(1)

# Get a logger for this test script
# The logger name will be 'test_aider_service_command' due to __name__
logger = logging.getLogger(__name__)

def run_aider_version_test(app_config: AppConfig, aider_service: AiderService):
    """
    Runs a basic test of the AiderService by executing 'aider --version'.
    """
    logger.info("--- Starting AiderService Version Command Test ---")

    command_to_run = ["--version"]
    files_for_context = []

    logger.info(f"Attempting to execute aider command: aider {' '.join(command_to_run)}")
    
    try:
        exit_code = aider_service.execute(command_args=command_to_run, files_to_add=files_for_context)
    except Exception as e:
        logger.error(f"An unexpected error occurred during AiderService.execute() for version test: {e}", exc_info=True)
        exit_code = -99 
        
    logger.info("Aider version command execution attempt finished.")
    logger.info(f"  Command executed: 'aider {' '.join(command_to_run)}'")
    logger.info(f"  Reported exit code: {exit_code}")

    if exit_code == 0:
        logger.info("Version Test Result: SUCCESS - Aider command ran successfully.")
    elif exit_code == -1:
        logger.warning("Version Test Result: FAILED - AiderService reported an issue (e.g., 'aider' not found).")
    else:
        logger.warning(f"Version Test Result: FAILED or UNCERTAIN - Aider command returned non-zero exit code: {exit_code}.")
    
    logger.info("--- AiderService Version Command Test Finished ---")


def run_aider_edit_readme_test_simplified(app_config: AppConfig, aider_service: AiderService):
    """
    Simplified test for AiderService: attempts to edit README.md to add a random line.
    Does NOT backup, verify content, or restore README.md. Manual check required.
    """
    logger.info("--- Starting AiderService Simplified Edit README.md Test ---")
    config_file_path = os.path.join(project_root, "config.yml")
    try:
        app_config = AppConfig.load_from_yaml(config_file_path)
        logger.info(f"AppConfig loaded successfully from '{config_file_path}'.")
    except FileNotFoundError:
        logger.error(f"Failed to load AppConfig: 'config.yml' not found at '{config_file_path}'.")
        logger.error("Please ensure 'config.yml' exists in the project root.")
        logger.info("--- AiderService Test Aborted ---")
        return
    except Exception as e:
        logger.error(f"Failed to load AppConfig from '{config_file_path}': {e}", exc_info=True)
    readme_path = os.path.join(project_root, "README.md")

    if not os.path.exists(readme_path):
        logger.error(f"README.md not found at {readme_path}. Skipping simplified edit test.")
        logger.info("--- AiderService Simplified Edit README.md Test Aborted ---")
        return

    try:
        # 1. Prepare command to add a random line
        random_line_text = f"Automated test line (simplified test): {uuid.uuid4()}"
        # Prompt to append the line
        prompt = (
            f"UPDATE the Readme.md file with the following text at the end: \ "
            f"{random_line_text}"
        )
        
        command_args = ["--no-auto-commits", "-m", prompt]
        files_to_edit = [readme_path] 

        logger.info(f"Attempting to execute aider command to edit {readme_path} (simplified)")
        logger.debug(f"  Aider arguments: {files_to_edit + command_args}")

        # 2. Execute the aider command
        exit_code = aider_service.execute(command_args=command_args, files_to_add=files_to_edit)
        
        logger.info(f"Aider edit command (simplified) finished with exit code: {exit_code}")

        # 7. (Implicit) Use uuid module - already done by generating random_line_text

        if exit_code == 0:
            logger.info("Simplified Edit Test: Aider command executed successfully (exit code 0).")
            logger.info(f"  Line intended to be added: '{random_line_text}'")
            logger.info("  Please MANUALLY VERIFY the content of README.md.")
        elif exit_code == -1:
            logger.warning("Simplified Edit Test: FAILED - AiderService reported an issue (e.g., 'aider' not found or subprocess error).")
        else:
            logger.warning(f"Simplified Edit Test: FAILED or UNCERTAIN - Aider command returned non-zero exit code: {exit_code}.")
            logger.info("  README.md may not have been modified as expected.")

    except FileNotFoundError:
        # This might occur if README.md disappears between the os.path.exists check and usage.
        logger.error(f"Error during simplified edit test: README.md not found at {readme_path}.", exc_info=True)
    except Exception as e:
        logger.error(f"An unexpected error occurred during the simplified README edit test: {e}", exc_info=True)
            
    logger.info("--- AiderService Simplified Edit README.md Test Finished ---")
    logger.info("*** IMPORTANT: If this test ran, README.md may have been modified. ***")
    logger.info("*** Please check its content manually. ***")


if __name__ == "__main__":
    setup_logging(log_level=logging.INFO) 
    
    main_logger = logging.getLogger(__name__)
    main_logger.info("====== Starting AiderService Test Suite ======")

    config_file_path = os.path.join(project_root, "config.yml")
    app_config = None
    try:
        app_config = AppConfig.load_from_yaml(config_file_path)
        main_logger.info(f"AppConfig loaded successfully from '{config_file_path}'.")
    except Exception as e:
        main_logger.error(f"Failed to load AppConfig from '{config_file_path}': {e}", exc_info=True)
        main_logger.error("Cannot proceed with tests without AppConfig.")
        main_logger.info("====== AiderService Test Suite Aborted ======")
        sys.exit(1)

    aider_service = None
    try:
        aider_service = AiderService(app_config=app_config)
        main_logger.info("AiderService instantiated successfully.")
    except Exception as e:
        main_logger.error(f"Failed to instantiate AiderService: {e}", exc_info=True)
        main_logger.error("Cannot proceed with tests without AiderService.")
        main_logger.info("====== AiderService Test Suite Aborted ======")
        sys.exit(1)

    # run_aider_version_test(app_config, aider_service)
    
    # main_logger.info("\n") 

    # Call the new simplified edit test
    run_aider_edit_readme_test_simplified(app_config, aider_service)
    
    main_logger.info("====== AiderService Test Suite Finished ======")
