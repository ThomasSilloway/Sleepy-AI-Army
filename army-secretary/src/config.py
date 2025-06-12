# poc-8-backlog-to-goals/src/config.py
"""
Manages application configuration loading and validation.

This module defines the AppConfig class, which is responsible for loading
configuration settings from a YAML file (config.yaml) and environment
variables (.env file). It also validates the loaded configuration to ensure
all necessary parameters are present and valid.
"""

import logging
import os
from typing import Any, Optional

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__) # Define logger at module level

class AppConfig:
    """
    Loads, stores, and validates application configuration settings.
    """
    project_git_path: Optional[str]
    backlog_file_name: Optional[str]
    ai_missions_directory_name: Optional[str] # Renamed
    default_llm_model_name: str
    gemini_api_key: Optional[str]
    mission_spec_filename: str # Renamed from task_description_filename
    default_log_directory: str
    default_log_filename: str
    new_mission_folders_filename: str # Renamed
    delete_backlog_file_on_completion: bool

    def __init__(self, command_line_git_path: Optional[str] = None) -> None:
        """
        Initializes AppConfig by loading settings from config.yaml and .env file.
        It then validates the loaded configuration.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_yaml_path = os.path.join(base_dir, "config.yaml")

        if not os.path.exists(config_yaml_path):
            raise FileNotFoundError(f"Configuration file not found: {config_yaml_path}. It should be in the 'poc-8-backlog-to-goals' directory.")

        yaml_config: dict[str, Any] = {}
        with open(config_yaml_path) as f:
            loaded_yaml = yaml.safe_load(f)
            if isinstance(loaded_yaml, dict):
                yaml_config = loaded_yaml
            else:
                logger.warning(f"config.yaml at {config_yaml_path} did not load as a dictionary. Using empty config.")

        if command_line_git_path:
            self.project_git_path = command_line_git_path
            logger.info(f"Using command line override for project_git_path: {command_line_git_path}")
        else:
            self.project_git_path = yaml_config.get("project_git_path")

        self.backlog_file_name = yaml_config.get("backlog_file_name")
        self.ai_missions_directory_name = yaml_config.get("ai_missions_directory_name") # Renamed field, will read new key from YAML
        self.default_llm_model_name = yaml_config.get("default_llm_model_name")
        self.mission_spec_filename = yaml_config.get("mission_spec_filename") # Renamed field
        self.default_log_directory = yaml_config.get("default_log_directory")
        self.default_log_filename = yaml_config.get("default_log_filename") # This will read the new default log filename from YAML
        self.new_mission_folders_filename = yaml_config.get("new_mission_folders_filename") # Renamed field, will read new key from YAML
        self.delete_backlog_file_on_completion = yaml_config.get("delete_backlog_file_on_completion", False)

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
    def missions_output_directory(self) -> str: # Renamed property
        """
        Constructs the full path to the AI missions output directory.
        Returns an empty string if components are missing.
        """
        if not self.project_git_path or not self.ai_missions_directory_name: # Logic uses renamed field
            return ""
        return os.path.join(self.project_git_path, self.ai_missions_directory_name) # Logic uses renamed field

    @property
    def new_mission_folders_file_path(self) -> str: # Renamed property
        """
        Constructs the full path to the file that will contain the list of new mission folders.
        Returns an empty string if components are missing.
        """
        if not self.project_git_path:
            return ""
        if not self.missions_output_directory or not self.new_mission_folders_filename: # Logic uses renamed property and field
             return ""
        return os.path.join(self.missions_output_directory, self.new_mission_folders_filename) # Logic uses renamed property and field

    def validate(self) -> None:
        """
        Validates the loaded configuration settings.

        Raises:
            ValueError: If any required configuration is missing or invalid.
        """
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set. Please set it in the .env file.")
        if not self.project_git_path:
            raise ValueError("project_git_path is not set in config.yaml and not provided via command line.")
        if not os.path.isdir(self.project_git_path):
            raise ValueError(f"project_git_path '{self.project_git_path}' is not a valid directory.")
        if not self.backlog_file_name:
            raise ValueError("backlog_file_name is not set in config.yaml.")
        if not self.ai_missions_directory_name: # Validates renamed field
            raise ValueError("ai_missions_directory_name is not set in config.yaml.") # Updated error message
        if not self.default_llm_model_name or not isinstance(self.default_llm_model_name, str):
            raise ValueError("default_llm_model_name must be a non-empty string in config.yaml or defaults will apply.")
        if not self.mission_spec_filename or not isinstance(self.mission_spec_filename, str): # Renamed field
            raise ValueError("mission_spec_filename must be a non-empty string in config.yaml.") # Updated error message
        if not self.default_log_directory or not isinstance(self.default_log_directory, str):
            raise ValueError("default_log_directory must be a non-empty string in config.yaml or use the default value 'logs'.")
        if not self.default_log_filename or not isinstance(self.default_log_filename, str):
            raise ValueError("default_log_filename must be a non-empty string in config.yaml or use the default value 'backlog-to-missions.log'.") # Updated example log name

        # Validate constructed paths
        if not self.backlog_file_path:
            raise ValueError("Could not construct backlog_file_path. Ensure project_git_path (command-line or config) and backlog_file_name are valid in config.yaml.")
        if not os.path.isfile(self.backlog_file_path):
            raise ValueError(f"backlog_file_path '{self.backlog_file_path}' (from config.yaml) does not exist or is not a file.")

        if not self.missions_output_directory: # Validates renamed property
            raise ValueError("Could not construct missions_output_directory. Ensure project_git_path (command-line or config) and ai_missions_directory_name are valid in config.yaml.") # Updated error message
