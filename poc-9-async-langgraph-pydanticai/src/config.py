import logging
import os

from dotenv import load_dotenv

class AppConfig:
    """
    Application configuration class.
    Loads settings from environment variables.
    """
    def __init__(self):
        # Load .env file first to ensure environment variables are available
        load_dotenv()

        # Mandatory: GEMINI_API_KEY
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        if not self.gemini_api_key:
            # This error should ideally be caught by the application's entry point
            # to prevent execution without the key.
            logging.critical("GEMINI_API_KEY environment variable not set or empty.")
            raise ValueError("GEMINI_API_KEY environment variable not set or empty.")

        # Gemini model for summarization tasks
        # Default to a known valid and generally available model if not set
        self.gemini_summarizer_model_name: str = os.getenv("GEMINI_SUMMARIZER_MODEL_NAME", "gemini-1.5-flash-latest")
        
        # Logging configuration
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_to_file: bool = os.getenv("LOG_TO_FILE", "false").lower() == "true"
        self.log_file_path: str = os.getenv("LOG_FILE_PATH", "app.log")

        # Input text for PoC-9
        self.poc9_input_text: str = os.getenv("POC9_INPUT_TEXT", "LangGraph is a library for building stateful, multi-actor applications with LLMs. It is part of the LangChain ecosystem and allows for more complex, cyclical data flows than are easily achievable with standard LangChain Expressions alone.")
        
        # You can add more configuration parameters here as needed
        # For example, paths, other API keys, feature flags, etc.

        logging.debug("AppConfig initialized.")
        logging.debug(f"  GEMINI_SUMMARIZER_MODEL_NAME: {self.gemini_summarizer_model_name}")
        logging.debug(f"  LOG_LEVEL: {self.log_level}")
        logging.debug(f"  POC9_INPUT_TEXT: {self.poc9_input_text[:100]}...") # Log a snippet

# Example of how to use it (optional, for testing this file directly)
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG) # Setup basic logging for direct test
    try:
        config = AppConfig()
        logging.info("AppConfig loaded successfully.")
        logging.info(f"Summarizer Model: {config.gemini_summarizer_model_name}")
        logging.info(f"Log Level: {config.log_level}")
        logging.info(f"Input Text: {config.poc9_input_text}")
        if not config.gemini_api_key:
            logging.warning("GEMINI_API_KEY is not set in the environment.")
        else:
            logging.info("GEMINI_API_KEY is set.")
            # print(f"GEMINI_API_KEY: {config.gemini_api_key}") # Avoid printing actual key
            
    except ValueError as e:
        logging.error(f"Error initializing AppConfig: {e}")
