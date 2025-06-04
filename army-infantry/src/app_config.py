"""
Manages application configuration loading and validation.

This module defines the AppConfig class, which is responsible for loading
configuration settings from a yml file (config.yml) and environment
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
    root_git_path: str
    mission_folder_path: str # Path to the mission folder. Should be relative to root_git_path
    gemini_api_key: str

    mission_description_filename: str
    mission_report_filename: str
    mission_report_template_filename: str # Just the filename.ext

    aider_code_model: str
    aider_summary_model: str

    mission_title_extraction_model: str

    # Paths for code modification node
    conventions_file_path: str
    aider_config_file_path: str

    log_subdirectory_name: str
    overview_log_filename: str
    detailed_log_filename: str

    # Branch naming configuration
    default_branch_prefix: str
    max_branch_name_length: int
    max_branch_description_length: int
    valid_branch_types: list[str]
    branch_hash_length: int # For the suffix

    def __init__(self, command_line_git_path: Optional[str] = None, command_line_mission_folder_path: Optional[str] = None) -> None:
        """
        Initializes AppConfig by loading settings from config.yml and .env file.
        It then validates the loaded configuration.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_yml_path = os.path.join(base_dir, "config.yml")

        if not os.path.exists(config_yml_path):
            raise FileNotFoundError(f"Configuration file not found: {config_yml_path}.")

        yml_config: dict[str, Any] = {}
        with open(config_yml_path) as f:
            loaded_yml = yaml.safe_load(f)
            if isinstance(loaded_yml, dict):
                yml_config = loaded_yml
            else:
                logger.warning(f"config.yml at {config_yml_path} did not load as a dictionary. Using empty config.")

        if command_line_git_path:
            self.root_git_path = command_line_git_path
            logger.info(f"Using command line override for root_git_path: {command_line_git_path}")
        else:
            self.root_git_path = yml_config.get("root_git_path")

        if command_line_mission_folder_path:
            self.mission_folder_path = command_line_mission_folder_path
            logger.info(f"Using command line override for mission_folder_path: {command_line_mission_folder_path}")
        else:
            self.mission_folder_path = yml_config.get("mission_folder_path")

        self.mission_report_filename = yml_config.get("mission_report_filename")
        self.mission_description_filename = yml_config.get("mission_description_filename")

        self.log_subdirectory_name = yml_config.get("log_subdirectory_name")
        self.overview_log_filename = yml_config.get("overview_log_filename")
        self.detailed_log_filename = yml_config.get("detailed_log_filename")

        self.mission_report_template_filename = yml_config.get("mission_report_template_filename")

        self.aider_code_model = yml_config.get("aider_code_model")
        self.aider_summary_model = yml_config.get("aider_summary_model")
        self.mission_title_extraction_model = yml_config.get("mission_title_extraction_model")

        # Load paths for code modification
        self.conventions_file_path = yml_config.get("conventions_file_path", "ai-docs/CONVENTIONS.md")
        self.aider_config_file_path = yml_config.get("aider_config_file_path", ".aider.sleepy.conf.yml")

        # Load branch naming config
        branch_config = yml_config.get("branch_naming", {})
        self.default_branch_prefix = branch_config.get("default_branch_prefix", "ai-mission/")
        self.max_branch_name_length = branch_config.get("max_branch_name_length", 60)
        self.max_branch_description_length = branch_config.get("max_branch_description_length", 40)
        self.valid_branch_types = branch_config.get("valid_branch_types", ["feature", "fix", "polish", "docs", "refactor", "chore"])
        self.branch_hash_length = branch_config.get("branch_hash_length", 7)

        load_dotenv()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        self.validate()

    @property
    def mission_folder_path_absolute(self) -> str:
        """
        Constructs the full absolute path to the mission folder.
        Returns an empty string if components are missing.
        """
        if not self.root_git_path or not self.mission_folder_path:
            return ""
        return os.path.join(self.root_git_path, self.mission_folder_path)

    @property
    def mission_report_path(self) -> str:
        """
        Constructs the full path to the mission report file.
        Returns an empty string if components are missing.
        """
        if not self.mission_folder_path or not self.mission_report_filename:
            return ""
        return os.path.join(self.mission_folder_path_absolute, self.mission_report_filename)

    @property
    def mission_description_path(self) -> str:
        """
        Constructs the full path to the mission description file.
        Returns an empty string if components are missing.
        """
        if not self.mission_folder_path or not self.mission_description_filename:
            return ""
        return os.path.join(self.mission_folder_path_absolute, self.mission_description_filename)

    @property
    def mission_report_template_abs_path(self) -> str:
        """
        Constructs the full absolute path to the mission report template file.
        Returns an empty string if components are missing.
        """
        # Create variable with current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        templates_base_dir = current_dir + "/templates"

        return os.path.join(templates_base_dir, self.mission_report_template_filename)

    def validate(self) -> None:
        """
        Validates the loaded configuration settings.

        Raises:
            ValueError: If any required configuration is missing or invalid.
        """
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set. Please set it in the .env file.")
        if not self.root_git_path:
            raise ValueError("root_git_path is not set in config.yml and not provided via command line.")
        if not os.path.isdir(self.root_git_path):
            raise ValueError(f"root_git_path '{self.root_git_path}' is not a valid directory.")

        if not self.mission_folder_path:
            raise ValueError("mission_folder_path is not set in config.yml and not provided via command line.")
        if not self.mission_report_filename:
            raise ValueError("mission_report_filename is not set in config.yml.")
        if not self.mission_report_template_filename: # Check for the filename itself
            raise ValueError("mission_report_template_filename (the filename part) is not set in config.yml.")

        if not self.aider_code_model:
            raise ValueError("aider_code_model is not set in config.yml.")
        if not self.aider_summary_model:
            raise ValueError("aider_summary_model is not set in config.yml.")
        if not self.mission_title_extraction_model:
            raise ValueError("mission_title_extraction_model is not set in config.yml.")

        if not self.conventions_file_path:
            raise ValueError("conventions_file_path is not set in config.yml.")
        if not self.aider_config_file_path:
            raise ValueError("aider_config_file_path is not set in config.yml.")

        if not self.log_subdirectory_name:
            raise ValueError("log_subdirectory_name is not set in config.yml.")
        if not self.overview_log_filename:
            raise ValueError("overview_log_filename is not set in config.yml.")
        if not self.detailed_log_filename:
            raise ValueError("detailed_log_filename is not set in config.yml.")

        # Validate branch naming config
        if not self.default_branch_prefix:
            raise ValueError("branch_naming.default_branch_prefix is not set in config.yml.")
        if not isinstance(self.max_branch_name_length, int) or self.max_branch_name_length <= 0:
            raise ValueError("branch_naming.max_branch_name_length must be a positive integer.")
        if not isinstance(self.max_branch_description_length, int) or self.max_branch_description_length <= 0:
            raise ValueError("branch_naming.max_branch_description_length must be a positive integer.")
        if not isinstance(self.valid_branch_types, list) or not all(isinstance(item, str) for item in self.valid_branch_types):
            raise ValueError("branch_naming.valid_branch_types must be a list of strings.")
        if not self.valid_branch_types: # Must not be empty
            raise ValueError("branch_naming.valid_branch_types cannot be empty.")
        if not isinstance(self.branch_hash_length, int) or self.branch_hash_length <= 0:
            raise ValueError("branch_naming.branch_hash_length must be a positive integer.")

        # Validate constructed paths
        if not os.path.isdir(self.mission_folder_path_absolute):
            raise ValueError(f"mission_folder_path '{self.mission_folder_path_absolute}' is not a valid directory.")

        if not os.path.isfile(self.mission_description_path):
            raise ValueError(f"mission_description_path '{self.mission_description_path}' does not exist or is not a file.")

        if not os.path.isfile(self.mission_report_template_abs_path):
            raise ValueError(f"mission_report_template_path '{self.mission_report_template_abs_path}' does not exist or is not a file.")

