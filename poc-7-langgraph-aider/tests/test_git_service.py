import logging
import sys
from dotenv import load_dotenv

from src.config import AppConfig
from src.services.git_service import GitService
from src.utils.logging_setup import setup_logging

# Get a logger for this test script
# This logger will be configured by setup_logging later
logger = logging.getLogger(__name__)

def run_git_service_tests(app_config: AppConfig, git_service: GitService):
    """
    Executes core GitService methods and prints their outputs for manual verification.
    """
    logger.overview("--- Starting GitService Method Execution Test ---")

    # Test get_last_commit_hash
    try:
        logger.info("Calling git_service.get_last_commit_hash()...")
        commit_hash = git_service.get_last_commit_hash()
        logger.info(f"  Method: get_last_commit_hash()")
        logger.info(f"  Result: {commit_hash}")
    except Exception as e:
        logger.error(f"  Error calling get_last_commit_hash(): {e}", exc_info=True)

    # Test get_last_commit_summary
    try:
        logger.info("Calling git_service.get_last_commit_summary()...")
        commit_summary = git_service.get_last_commit_summary()
        logger.info(f"  Method: get_last_commit_summary()")
        logger.info(f"  Result: {commit_summary}")
    except Exception as e:
        logger.error(f"  Error calling get_last_commit_summary(): {e}", exc_info=True)

    # Test get_last_commit_file_stats
    try:
        logger.info("Calling git_service.get_last_commit_file_stats()...")
        file_stats = git_service.get_last_commit_file_stats()
        logger.info(f"  Method: get_last_commit_file_stats()")
        # File stats can be multi-line, so adding a newline for better readability
        logger.info(f"  Result:\n{file_stats}")
    except Exception as e:
        logger.error(f"  Error calling get_last_commit_file_stats(): {e}", exc_info=True)

    logger.overview("--- GitService Method Execution Test Finished ---")
    logger.overview(f"*** IMPORTANT: This test interacted with the Git repository at '{git_service.repo_path}'. ***")
    logger.overview("*** Please MANUALLY VERIFY the console output for correctness. ***")

if __name__ == "__main__":
    # Load environment variables from .env file, if present
    load_dotenv()

    # Initialize a basic logger for messages prior to full logging setup
    # This logger instance will be updated by setup_logging
    main_logger = logging.getLogger(__name__)

    app_config = None
    try:
        # Load application configuration
        app_config = AppConfig.load_from_yaml() # Assumes config.yml is in the root
        
        # Setup logging system based on AppConfig
        # This will configure handlers and formatters for all loggers, including main_logger
        setup_logging(app_config=app_config)
        
        main_logger.info("====== Starting GitService Test Suite ======")
        main_logger.info("AppConfig loaded and logging configured successfully.")
    except Exception as e:
        # Use basic print if logger is not configured, or logger if it is partially.
        main_logger.error("Failed to load AppConfig or setup logging.", exc_info=True)
        main_logger.error("Cannot proceed with tests without AppConfig and logging.")
        main_logger.info("====== GitService Test Suite Aborted ======")
        sys.exit(1)

    git_service = None
    try:
        # Instantiate GitService
        # The spec mandates using app_config.goal_git_path for the repo_path
        repo_path = app_config.goal_git_path
        main_logger.info(f"Initializing GitService with repo_path: {repo_path}")
        
        git_service = GitService(repo_path=repo_path)
        main_logger.overview("GitService instantiated successfully.")
    except ValueError as e: # Specific error from GitService if repo_path is not a Git repo
        main_logger.error(f"Failed to instantiate GitService: {e}", exc_info=True)
        main_logger.error(f"Ensure the configured 'goal_root_path' ('{repo_path}') is a valid Git repository.")
        main_logger.info("====== GitService Test Suite Aborted ======")
        sys.exit(1)
    except Exception as e: # Catch any other unexpected errors during GitService instantiation
        main_logger.error(f"An unexpected error occurred while instantiating GitService: {e}", exc_info=True)
        main_logger.info("====== GitService Test Suite Aborted ======")
        sys.exit(1)

    # Execute the GitService method tests
    run_git_service_tests(app_config, git_service)

    main_logger.overview("====== GitService Test Suite Finished ======")
