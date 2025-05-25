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
import sys # For potential sys.exit

# Project-specific imports
from config import AppConfig
from services.backlog_processor import BacklogProcessor
from services.llm_prompt_service import LlmPromptService

# Define log directory (e.g., poc-8-backlog-to-goals/logs/) and file path
LOG_DIR_PATH: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
LOG_FILE_PATH: str = os.path.join(LOG_DIR_PATH, "backlog-to-goals.log")
os.makedirs(LOG_DIR_PATH, exist_ok=True)

# Setup basic logging
# More sophisticated logging can be added to a dedicated logging_setup.py if needed
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE_PATH)
    ]
)
logger: logging.Logger = logging.getLogger(__name__)

async def run() -> None:
    """
    Main asynchronous function to run the PoC 8 backlog processing.
    Initializes services and processes the backlog file.
    """
    logger.info("Starting PoC 8: Backlog to Goals Processor")
    try:
        # 1. Initialize AppConfig (loads .env, including GEMINI_API_KEY and paths from config.yaml)
        app_config = AppConfig()
        # Validate essential configurations from AppConfig
        # These checks are now primarily handled by AppConfig.validate(), 
        # but keeping them here as an early exit mechanism if AppConfig itself fails to initialize
        # or if specific critical values are None (though validate() should catch that).
        if not app_config.gemini_api_key: # AppConfig.validate() already checks this
            logger.critical("GEMINI_API_KEY is not available after AppConfig initialization. Exiting.")
            return # Or sys.exit(1)
        if not app_config.backlog_file_path: # AppConfig.validate() already checks this
            logger.critical("backlog_file_path is not available after AppConfig initialization. Exiting.")
            return
        if not app_config.goals_output_directory: # AppConfig.validate() already checks this
            logger.critical("goals_output_directory is not available after AppConfig initialization. Exiting.")
            return
    
        logger.info("AppConfig initialized successfully.")
    
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
        # sys.exit(1) # Optional: exit with error code
    except Exception as e:
        logger.error("An unhandled error occurred during PoC 8 execution:", exc_info=True)
        # sys.exit(1) # Optional: exit with error code

if __name__ == "__main__":
    # Python 3.7+
    asyncio.run(run())
