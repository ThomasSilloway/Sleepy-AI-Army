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
import os
import sys
from datetime import datetime

# Project-specific imports
from config import AppConfig
from services.backlog_processor import BacklogProcessor
from services.llm_prompt_service import LlmPromptService

# Define log directory (e.g., poc-8-backlog-to-goals/logs/) and file path
LOG_DIR_PATH: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
LOG_FILE_PATH: str = os.path.join(LOG_DIR_PATH, "backlog-to-goals.log")
os.makedirs(LOG_DIR_PATH, exist_ok=True)



# Setup basic logging
# TODO - Move logging setup into its own class under src\utils\logging_setup.py
class LowercaseLevelnameFormatter(logging.Formatter):
    def format(self, record):
        record.levelname = record.levelname.lower()
        return super().format(record)

# Spec mentioned: fmt="[%(asctime)s.%(msecs)03d] (%(levelname)s) [%(name)s] %(message)s", datefmt="%H:%M:%S"
# Adding [%(name)s] to file_formatter as per typical detailed logging.
file_formatter = LowercaseLevelnameFormatter(     
    fmt="[%(asctime)s.%(msecs)03d]: (%(levelname)s): %(message)s",
    datefmt="%H:%M:%S"
)

console_formatter = LowercaseLevelnameFormatter(
    fmt="%(asctime)s.%(msecs)03d: (%(levelname)s): %(message)s", # Keeping console simpler
    datefmt="%M:%S" # Console uses MM:SS for brevity as per your current code
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

if logger.hasHandlers():
    logger.handlers.clear()
    
# Configure Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Configure Overview File Handler
file_handler = logging.FileHandler(LOG_FILE_PATH, mode='a') # Use 'a' for append
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Initial log message to confirm setup and show date
# Changed to use the newly defined logger.overview for this prominent message
logger.info(f"\n\n======== Logging initialized. Date: {datetime.now().strftime('%Y-%m-%d')} =========\n\n")
logger.info("Detailed logging started (includes INFO, DEBUG, OVERVIEW, etc.).")
logger.debug("Debug level test message for detailed log.")

async def run() -> None:
    """
    Main asynchronous function to run the PoC 8 backlog processing.
    Initializes services and processes the backlog file.
    """
    logger.info("Starting PoC 8: Backlog to Goals Processor.")
    try:
        # 1. Initialize AppConfig (loads .env, including GEMINI_API_KEY and paths from config.yaml)
        app_config = AppConfig()
    
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
