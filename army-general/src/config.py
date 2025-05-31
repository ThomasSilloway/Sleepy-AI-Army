"""
Manages application configuration loading and validation.

This module defines the AppConfig class, which is responsible for loading
configuration settings from a YAML file (config.yaml) and environment
variables (.env file). It also validates the loaded configuration to ensure
all necessary parameters are present and valid.
"""

import logging
import os
from typing import Any

import yaml


class AppConfig:
    """
    Loads, stores, and validates application configuration settings.
    """
    root_git_path: str

    # Default path for Secretary output if it writes to a file
    secretary_output_file: str

    # Full command templates
    secretary_run_command_template: str
    army_man_run_command_template: str

    # Logging
    default_log_directory: str
    default_log_filename: str

    log_level: str

    def __init__(self) -> None:
        """
        Initializes AppConfig by loading settings from config.yaml and .env file.
        It then validates the loaded configuration.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_yaml_path = os.path.join(base_dir, "config.yml")

        if not os.path.exists(config_yaml_path):
            raise FileNotFoundError(f"Configuration file not found: {config_yaml_path}")

        yaml_config: dict[str, Any] = {}
        with open(config_yaml_path) as f:
            loaded_yaml = yaml.safe_load(f)
            if isinstance(loaded_yaml, dict):
                yaml_config = loaded_yaml
            else:
                # Handle cases where YAML is valid but not a dictionary (e.g. just a string)
                logger.warning(f"config.yaml at {config_yaml_path} did not load as a dictionary. Using empty config.")

        self.root_git_path = yaml_config.get("root_git_path")
        self.secretary_output_file = yaml_config.get("secretary_output_file")
        self.secretary_run_command_template = yaml_config.get("secretary_run_command_template")
        self.army_man_run_command_template = yaml_config.get("army_man_run_command_template")
        self.default_log_directory = yaml_config.get("default_log_directory") 
        self.default_log_filename = yaml_config.get("default_log_filename") 
        self.log_level = yaml_config.get("log_level")

        self.validate()

    @property
    def secretary_output_file_path(self) -> str: 
        """
        Constructs the full path to the Secretary output file.
        Returns an empty string if components are missing.
        """
        if not self.root_git_path or not self.secretary_output_file:
            return "" 
        return os.path.join(self.root_git_path, self.secretary_output_file)

    def validate(self) -> None:
        """
        Validates the loaded configuration settings.

        Raises:
            ValueError: If any required configuration is missing or invalid.
        """
        if not self.root_git_path:
            raise ValueError("root_git_path is not set in config.yaml.")
        if not self.secretary_output_file:
            raise ValueError("secretary_output_file is not set in config.yaml.")
        if not self.secretary_run_command_template:
            raise ValueError("secretary_run_command_template is not set in config.yaml.")
        if not self.army_man_run_command_template:
            raise ValueError("army_man_run_command_template is not set in config.yaml.")
        if not self.default_log_directory:
            raise ValueError("default_log_directory is not set in config.yaml.")
        if not self.default_log_filename:
            raise ValueError("default_log_filename is not set in config.yaml.")
        if not self.log_level:
            raise ValueError("log_level is not set in config.yaml.")

        # Validate all paths
        if not os.path.isdir(self.root_git_path):
            raise ValueError(f"root_git_path '{self.root_git_path}' set in config.yaml is not a valid directory.")

logger = logging.getLogger(__name__)
