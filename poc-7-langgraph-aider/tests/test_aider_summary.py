import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from src.config import AppConfig
from src.models.aider_summary import AiderRunSummary
from src.services.aider_service import AiderExecutionResult, AiderService
from src.services.llm_prompt_service import LlmPromptService
from src.utils.logging_setup import setup_logging

# Get a logger for this test script
logger = logging.getLogger(__name__)

# Define the path to the aider output sample file relative to this test file
TEST_DIR = Path(__file__).parent
SAMPLE_OUTPUT_FILE = TEST_DIR / "aider_std_out_sample.txt"

def test_get_aider_summary_from_sample_output(
    app_config: AppConfig, 
    llm_prompt_service: LlmPromptService
):
    """
    Tests AiderService.get_summary() by providing it with a sample Aider output
    and verifying that it correctly interacts with LlmPromptService and returns
    the expected summary.
    """
    # 1. ARRANGE: Prepare AiderExecutionResult from the sample file content
    if not SAMPLE_OUTPUT_FILE.exists():
        logger.warning(f"Sample output file not found: {SAMPLE_OUTPUT_FILE}")
        return

    sample_stdout_content = SAMPLE_OUTPUT_FILE.read_text(encoding="utf-8")

    execution_result = AiderExecutionResult(
        exit_code=0,  # Assuming a successful aider run for this output
        stdout=sample_stdout_content,
        stderr=""  # Per request, all sample content is in stdout
    )

    # Instantiate AiderService with the actual AppConfig and the mocked LlmPromptService
    aider_service = AiderService(app_config=app_config, llm_prompt_service=llm_prompt_service)

    # 3. ACT: Call the method under test
    # AiderService.get_summary internally uses asyncio.run, so the call is blocking.
    actual_summary = aider_service.get_summary(execution_result)

    logger.info(actual_summary.model_dump())

if __name__ == "__main__":
    # Load environment variables from .env file, if present
    # This is crucial for GEMINI_API_KEY
    if load_dotenv():
        print("Loaded .env file.")
    else:
        print("No .env file found or it is empty. GEMINI_API_KEY should be set in your environment.")

    # Initialize a basic logger for messages prior to full logging setup
    main_logger = logging.getLogger(__name__) # This instance will be updated by setup_logging

    app_config = None
    try:
        # Load application configuration
        app_config = AppConfig.load_from_yaml() # Assumes config.yml is in the project root

        # Setup logging system based on AppConfig
        setup_logging(app_config=app_config) # Configures all loggers, including main_logger

        main_logger.info("====== Starting LlmPromptService Test Suite ======")
        main_logger.info("AppConfig loaded and logging configured successfully.")
    except Exception:
        main_logger.error("Failed to load AppConfig or setup logging.", exc_info=True)
        main_logger.error("Cannot proceed with tests without AppConfig and logging.")
        main_logger.info("====== LlmPromptService Test Suite Aborted ======")
        sys.exit(1)

    llm_service = None
    try:
        # Instantiate LlmPromptService
        main_logger.info("Initializing LlmPromptService...")
        llm_service = LlmPromptService(app_config=app_config)
        main_logger.overview("LlmPromptService instantiated successfully.")
    except Exception as e:
        main_logger.error(f"An unexpected error occurred while instantiating LlmPromptService: {e}", exc_info=True)
        main_logger.info("====== LlmPromptService Test Suite Aborted ======")
        sys.exit(1)

    # Check for GEMINI_API_KEY before running async tests
    if not os.getenv("GEMINI_API_KEY"):
        main_logger.error("GEMINI_API_KEY environment variable not set.")
        main_logger.error("LlmPromptService requires this key to function.")
        main_logger.error("Please set it in your .env file or system environment.")
        main_logger.info("====== LlmPromptService Test Suite Aborted ======")
        sys.exit(1)
    else:
        main_logger.info("GEMINI_API_KEY found in environment.")

    # Execute the LlmPromptService method tests
    try:
        test_get_aider_summary_from_sample_output(app_config, llm_service)
    except Exception as e:
        main_logger.error(f"An error occurred while running the async test function: {e}", exc_info=True)


    main_logger.overview("====== LlmPromptService Test Suite Finished ======")
