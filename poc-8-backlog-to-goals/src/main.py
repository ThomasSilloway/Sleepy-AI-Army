# poc-8-backlog-to-goals/src/main.py
import asyncio
import logging
import os

# Project-specific imports
from config import AppConfig
from services.backlog_processor import BacklogProcessor
from services.llm_prompt_service import LlmPromptService

# Configuration
# Assumes backlog.md is in the root directory of the entire project,
# two levels up from src/
BACKLOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "backlog.md")
# Output directory will be created inside poc-8-backlog-to-goals/
GOALS_OUTPUT_DIRECTORY = os.path.join(os.path.dirname(__file__), "..", "ai-goals")


# Setup basic logging
# More sophisticated logging can be added to a dedicated logging_setup.py if needed
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s - %(message)s',
    handlers=[
        logging.StreamHandler(), # To output to console
        # Optional: Add a FileHandler here if you want to log to a file
        # logging.FileHandler("poc8_debug.log") 
    ]
)
logger = logging.getLogger(__name__)

async def run():
    """
    Main asynchronous function to run the PoC 8 backlog processing.
    Initializes services and processes the backlog file.
    """
    logger.info("Starting PoC 8: Backlog to Goals Processor")

    # 1. Initialize AppConfig (loads .env, including GEMINI_API_KEY)
    app_config = AppConfig()
    if not app_config.gemini_api_key:
        logger.error("GEMINI_API_KEY is not set. Please set it in the .env file in the 'poc-8-backlog-to-goals' directory.")
        print("Error: GEMINI_API_KEY is not configured. Exiting.")
        return

    logger.info("AppConfig initialized.")

    # 2. Initialize LlmPromptService
    # LlmPromptService expects AppConfig
    llm_service = LlmPromptService(app_config=app_config)
    logger.info("LlmPromptService initialized.")

    # 3. Initialize BacklogProcessor
    # BacklogProcessor needs the LlmPromptService, output directory, and AppConfig
    backlog_processor = BacklogProcessor(
        llm_service=llm_service,
        output_dir=GOALS_OUTPUT_DIRECTORY,
        app_config=app_config 
    )
    logger.info(f"BacklogProcessor initialized. Output will be in: {GOALS_OUTPUT_DIRECTORY}")

    # 4. Process the backlog file
    logger.info(f"Attempting to process backlog file: {BACKLOG_FILE_PATH}")
    await backlog_processor.process_backlog_file(BACKLOG_FILE_PATH)

    logger.info("PoC 8 processing finished.")

if __name__ == "__main__":

    # Python 3.7+
    asyncio.run(run())
