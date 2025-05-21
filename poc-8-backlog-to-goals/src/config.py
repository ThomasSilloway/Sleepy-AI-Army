# poc-8-backlog-to-goals/src/config.py
import os
from dotenv import load_dotenv

class AppConfig:
    def __init__(self):
        load_dotenv() # Load environment variables from .env file
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        # Add any other configurations LlmPromptService might expect,
        # or that might be useful for PoC 8.
        # For now, GEMINI_API_KEY is the primary concern.

        if not self.gemini_api_key:
            print("Warning: GEMINI_API_KEY environment variable not set. LLM calls will fail.")

# Example of how it might be instantiated, not for execution here
# if __name__ == '__main__':
#     app_conf = AppConfig()
#     if app_conf.gemini_api_key:
#         print("AppConfig loaded, GEMINI_API_KEY is set.")
#     else:
#         print("AppConfig loaded, but GEMINI_API_KEY is NOT set.")
