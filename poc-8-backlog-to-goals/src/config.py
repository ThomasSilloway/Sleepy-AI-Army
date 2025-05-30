# poc-8-backlog-to-goals/src/config.py
"""
Manages application configuration loading and validation.

This module defines the AppConfig class, which is responsible for loading
configuration settings from a YAML file (config.yaml) and environment
variables (.env file). It also validates the loaded configuration to ensure
all necessary parameters are present and valid.
"""

import os
import yaml
import logging

from dotenv import load_dotenv
from typing import Optional, Any # Added Any for yaml_config values

class AppConfig:
    """
    Loads, stores, and validates application configuration settings.
    
    Attributes:
        project_git_path (Optional[str]): Absolute path to the target git repository.
        backlog_file_name (Optional[str]): Name of the backlog markdown file.
        ai_goals_directory_name (Optional[str]): Name of the directory for AI-generated goals.
        default_llm_model_name (str): Default LLM model name to be used.
        gemini_api_key (Optional[str]): API key for Google Gemini services.
    """
    project_git_path: Optional[str]
    backlog_file_name: Optional[str]
    ai_goals_directory_name: Optional[str]
    default_llm_model_name: str
    gemini_api_key: Optional[str]
    task_description_filename: str # Standardized name
    default_log_directory: str # New attribute for logging
    default_log_filename: str # New attribute for logging

    def __init__(self) -> None:
        """
        Initializes AppConfig by loading settings from config.yaml and .env file.
        It then validates the loaded configuration.
        """
        # base_dir is 'poc-8-backlog-to-goals', containing src/ and config.yaml
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_yaml_path = os.path.join(base_dir, "config.yaml")

        if not os.path.exists(config_yaml_path):
            raise FileNotFoundError(f"Configuration file not found: {config_yaml_path}. It should be in the 'poc-8-backlog-to-goals' directory.")

        yaml_config: dict[str, Any] = {}
        with open(config_yaml_path, 'r') as f:
            loaded_yaml = yaml.safe_load(f)
            if isinstance(loaded_yaml, dict):
                yaml_config = loaded_yaml
            else:
                # Handle cases where YAML is valid but not a dictionary (e.g. just a string)
                logger.warning(f"config.yaml at {config_yaml_path} did not load as a dictionary. Using empty config.")


        self.project_git_path = yaml_config.get("project_git_path")
        self.backlog_file_name = yaml_config.get("backlog_file_name")
        self.ai_goals_directory_name = yaml_config.get("ai_goals_directory_name")
        self.default_llm_model_name = yaml_config.get("default_llm_model_name", "gemini-1.5-flash-latest")
        self.task_description_filename = yaml_config.get("task_description_filename", "task-description.md") # Standardized name and YAML key
        self.default_log_directory = yaml_config.get("default_log_directory", "logs") # Initialize new logging attribute
        self.default_log_filename = yaml_config.get("default_log_filename", "backlog-to-goals.log") # Initialize new logging attribute

        load_dotenv()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        self.validate()

    @property
    def backlog_file_path(self) -> str:
        """
        Constructs the full path to the backlog file.
        Returns an empty string if components are missing.
        """
        if not self.project_git_path or not self.backlog_file_name:
            return "" 
        return os.path.join(self.project_git_path, self.backlog_file_name)

    @property
    def goals_output_directory(self) -> str:
        """
        Constructs the full path to the AI goals output directory.
        Returns an empty string if components are missing.
        """
        if not self.project_git_path or not self.ai_goals_directory_name:
            return ""
        return os.path.join(self.project_git_path, self.ai_goals_directory_name)

    def validate(self) -> None:
        """
        Validates the loaded configuration settings.

        Raises:
            ValueError: If any required configuration is missing or invalid.
        """
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set. Please set it in the .env file.")
        if not self.project_git_path:
            raise ValueError("project_git_path is not set in config.yaml.")
        if not os.path.isdir(self.project_git_path):
            raise ValueError(f"project_git_path '{self.project_git_path}' set in config.yaml is not a valid directory.")
        if not self.backlog_file_name:
            raise ValueError("backlog_file_name is not set in config.yaml.")
        if not self.ai_goals_directory_name:
            raise ValueError("ai_goals_directory_name is not set in config.yaml.")
        if not self.default_llm_model_name or not isinstance(self.default_llm_model_name, str):
            raise ValueError("default_llm_model_name must be a non-empty string in config.yaml or defaults will apply.")
        if not self.task_description_filename or not isinstance(self.task_description_filename, str): # Validate standardized name
            raise ValueError("task_description_filename must be a non-empty string in config.yaml or use the default value.")
        if not self.default_log_directory or not isinstance(self.default_log_directory, str): # Validate new logging attribute
            raise ValueError("default_log_directory must be a non-empty string in config.yaml or use the default value 'logs'.")
        if not self.default_log_filename or not isinstance(self.default_log_filename, str): # Validate new logging attribute
            raise ValueError("default_log_filename must be a non-empty string in config.yaml or use the default value 'backlog-to-goals.log'.")

        # Validate constructed paths
        if not self.backlog_file_path:
            # This case should ideally be caught by individual component checks,
            # but as a safeguard for the property itself:
            raise ValueError("Could not construct backlog_file_path. Ensure project_git_path and backlog_file_name are valid in config.yaml.")
        if not os.path.isfile(self.backlog_file_path):
            raise ValueError(f"backlog_file_path '{self.backlog_file_path}' (from config.yaml) does not exist or is not a file.")
        
        if not self.goals_output_directory:
            # Similar safeguard for goals_output_directory property
            raise ValueError("Could not construct goals_output_directory. Ensure project_git_path and ai_goals_directory_name are valid in config.yaml.")
        # We don't validate if goals_output_directory exists, as it might be created by the application.
        # However, its parent (project_git_path) is validated to be a directory.

logger = logging.getLogger(__name__)
