"""
Main execution script for the Secretary

This script initializes the application configuration, sets up logging,
instantiates necessary services (like LlmPromptService and BacklogProcessor),
and then starts the backlog processing. It includes global error handling
to catch and log any unhandled exceptions during execution.
"""

import argparse  # Added for command-line argument parsing
import asyncio
import logging
from datetime import datetime

# Project-specific imports
from config import AppConfig
from services.backlog_processor import BacklogProcessor
from services.git_service import GitService
from services.llm_prompt_service import LlmPromptService
from utils.logging_setup import LoggingSetup

# 1. Initialize ArgumentParser
parser = argparse.ArgumentParser(description="Army Secretary - Backlog to Goals Processor")
parser.add_argument(
    "--root_git_path",
    type=str,
    help="Override the project_git_path from config.yaml with the provided path.",
    required=False
)
args = parser.parse_args()

# 2. Initialize AppConfig first, passing the command line argument if provided
app_config = AppConfig(command_line_git_path=args.root_git_path)

# 3. Initialize and setup logging using AppConfig
logging_setup = LoggingSetup(app_config=app_config)
logging_setup.setup_logging()

# Get the logger instance
logger = logging.getLogger(__name__)


# Initial log message to confirm setup and show date
logger.info(f"\n\n======== Logging initialized via LoggingSetup & AppConfig. Date: {datetime.now().strftime('%Y-%m-%d')} =========\n\n")
if args.root_git_path:
    logger.info(f"Overriding project_git_path with command line argument: {args.root_git_path}")
logger.debug("Debug level test message for detailed log from main.py.")

async def run() -> None:
    """
    Main asynchronous function to run the PoC 8 backlog processing.
    Initializes services and processes the backlog file.
    """
    logger.info("Starting PoC 8: Backlog to Goals Processor.")
    try:

        # Get paths from AppConfig
        backlog_file_path: str = app_config.backlog_file_path
        goals_output_directory: str = app_config.goals_output_directory
        logger.info(f"Using backlog file path: {backlog_file_path}")
        logger.info(f"Using goals output directory: {goals_output_directory}")

        # 2. Initialize LlmPromptService
        llm_service = LlmPromptService(app_config=app_config)
        logger.info("LlmPromptService initialized.")

        # 3. Initialize BacklogProcessor
        backlog_processor = BacklogProcessor(
            llm_service=llm_service,
            output_dir=goals_output_directory,
            app_config=app_config 
        )
        logger.info(f"BacklogProcessor initialized. Output will be in: {goals_output_directory}")

        # 4. Process the backlog file
        logger.info(f"Attempting to process backlog file: {backlog_file_path}")
        await backlog_processor.process_backlog_file(backlog_file_path)

        created_folders = backlog_processor.created_folders
        if created_folders:
            logger.info(f"Created folders: {created_folders}")

            # Write new folders to a file specified in appconfig in the variable: new_goal_folders_file_path
            new_goal_folders_file_path: str = app_config.new_goal_folders_file_path
            if new_goal_folders_file_path:
                with open(new_goal_folders_file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(created_folders) + "\n")
                logger.info(f"Wrote created folders to file: {new_goal_folders_file_path}")

            git_service = GitService(repo_path=app_config.project_git_path)
            commit_message = "AI Army Secretary - Added new goals"
            if git_service.commit_changes(commit_message):
                logger.info(f"Committed changes to git with message: {commit_message}")
            else:
                logger.warning("Failed to commit changes to git.")

        logger.info("PoC 8 processing finished successfully.")
    except ValueError as ve:
        logger.critical(f"Configuration error: {ve}. Please check your .env, config.yaml files, or command line arguments. Exiting.", exc_info=False)
    except Exception:
        logger.error("An unhandled error occurred during PoC 8 execution:", exc_info=True)

if __name__ == "__main__":
    asyncio.run(run())
