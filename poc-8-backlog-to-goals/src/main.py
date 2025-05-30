# poc-8-backlog-to-goals/src/main.py
"""
Main execution script for the PoC 8 application.

This script initializes the application configuration, sets up logging,
instantiates necessary services (like LlmPromptService and BacklogProcessor),
and then starts the backlog processing. It includes global error handling
to catch and log any unhandled exceptions during execution.
"""

import asyncio
import logging
from datetime import datetime

# Project-specific imports
from config import AppConfig
from services.backlog_processor import BacklogProcessor
from services.llm_prompt_service import LlmPromptService
from src.utils.logging_setup import LoggingSetup

# 1. Initialize AppConfig first
app_config = AppConfig()

# 2. Initialize and setup logging using AppConfig
logging_setup = LoggingSetup(app_config=app_config)
logging_setup.setup_logging()

# Get the logger instance
logger = logging.getLogger(__name__)


# Initial log message to confirm setup and show date
logger.info(f"\n\n======== Logging initialized via LoggingSetup & AppConfig. Date: {datetime.now().strftime('%Y-%m-%d')} =========\n\n")
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

        logger.info("PoC 8 processing finished successfully.")
    except ValueError as ve: # Catch validation errors from AppConfig specifically
        logger.critical(f"Configuration error: {ve}. Please check your .env and config.yaml files. Exiting.", exc_info=False) # No need for full exc_info for expected ValueErrors
    except Exception as e:
        logger.error("An unhandled error occurred during PoC 8 execution:", exc_info=True)

if __name__ == "__main__":
    # Python 3.7+
    asyncio.run(run())
