# poc-8-backlog-to-goals/src/config.py
import os

from dotenv import load_dotenv


class AppConfig:
    def __init__(self):
        load_dotenv() # Load environment variables from .env file
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        self.validate()

    def validate(self):
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set. Please set it in the .env file.")
