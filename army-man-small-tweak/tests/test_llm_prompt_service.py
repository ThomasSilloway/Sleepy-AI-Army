import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from src.config import AppConfig
from src.services.llm_prompt_service import LlmPromptService
from src.utils.logging_setup import setup_logging

# Get a logger for this test script
logger = logging.getLogger(__name__)

# Define a simple Pydantic model for testing structured output
class TestItemInfo(BaseModel):
    item_name: str = Field(description="The name of the item mentioned in the text.")
    sentiment: str = Field(description="The sentiment expressed towards the item (e.g., positive, negative, neutral).")

async def run_llm_service_tests(app_config: AppConfig, llm_service: LlmPromptService):
    """
    Executes a test call to LlmPromptService.get_structured_output and logs results.
    """
    logger.overview("--- Starting LlmPromptService Method Execution Test ---")

    # Prepare test input messages
    messages_input = [
        {
            "role": "system", 
            "content": f"Extract the item and sentiment. Respond in JSON matching this schema: {TestItemInfo.model_json_schema()}"
        },
        {
            "role": "user", 
            "content": "I really love apples, they are delicious and make me happy!"
        },
    ]

    # Get the model name from AppConfig
    # The LlmPromptService itself requires the model name to be passed to get_structured_output
    llm_model_to_use = app_config.task_description_extraction_model
    if not llm_model_to_use:
        logger.error("`task_description_extraction_model` is not configured in AppConfig. Cannot run LLM test.")
        logger.overview("--- LlmPromptService Method Execution Test Aborted ---")
        return

    logger.info(f"Attempting to call llm_service.get_structured_output with model: {llm_model_to_use}")
    logger.info(f"Input messages: {messages_input}")
    logger.info(f"Expected output Pydantic model: {TestItemInfo.__name__}")

    try:
        structured_result: TestItemInfo | None = await llm_service.get_structured_output(
            messages=messages_input,
            output_pydantic_model_type=TestItemInfo,
            llm_model_name=llm_model_to_use
        )

        if structured_result:
            logger.info("Successfully received structured output from LlmPromptService.")
            logger.info(f"  Result (Pydantic model): {structured_result}")
            logger.info(f"  Item Name: {structured_result.item_name}")
            logger.info(f"  Sentiment: {structured_result.sentiment}")
            # You can also log the JSON representation
            # logger.debug(f"  Result (JSON): {structured_result.model_dump_json(indent=2)}")
        else:
            logger.warning("LlmPromptService returned None. This might indicate an issue with the LLM call or parsing.")
            logger.warning("Check previous logs from LlmPromptService for more details (e.g., API errors, empty response).")

    except Exception as e:
        logger.error(f"An error occurred during LlmPromptService.get_structured_output call: {e}", exc_info=True)

    logger.overview("--- LlmPromptService Method Execution Test Finished ---")
    logger.overview("*** IMPORTANT: This test interacted with the Google Gemini API. ***")
    logger.overview("*** Please MANUALLY VERIFY the console and log file output for correctness. ***")
    logger.overview("*** Ensure your GEMINI_API_KEY environment variable is set and valid. ***")

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
    except Exception as e:
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
        asyncio.run(run_llm_service_tests(app_config, llm_service))
    except Exception as e:
        main_logger.error(f"An error occurred while running the async test function: {e}", exc_info=True)


    main_logger.overview("====== LlmPromptService Test Suite Finished ======")
