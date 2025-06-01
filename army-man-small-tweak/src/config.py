"""Pydantic model for application configuration."""
import logging
import os
from typing import Optional

from omegaconf import MissingMandatoryValue, OmegaConf
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class AppConfig(BaseModel):
    goal_root_path: str
    goal_git_path: str # Path to the root of the Git repo that contains the goal_root_path
    task_description_filename: str
    manifest_output_filename: str
    changelog_output_filename: str
    log_subdirectory_name: str
    overview_log_filename: str
    detailed_log_filename: str
    # Example of a more complex field if needed later:
    # aider_model: Optional[str] = None 
    manifest_template_filename: str

    aider_code_model: str
    aider_summary_model: str
    task_description_extraction_model: str

    @property
    def workspace_root_path(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @classmethod
    def load_from_yaml(cls, config_path: str = "config.yml", root_git_path: Optional[str] = None, goal_path: Optional[str] = None) -> "AppConfig":
        """
        Loads application configuration from a YAML file using OmegaConf
        and instantiates an AppConfig object.

        Args:
            config_path: Path to the configuration file.
            root_git_path: Optional path to the root of the Git repo. If provided, overrides `goal_git_path` from YAML.
            goal_path: Optional path to the goal root. If provided, overrides `goal_root_path` from YAML.

        Returns:
            An instance of AppConfig.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            OmegaConf.errors.OmegaConfBaseException: For issues during OmegaConf loading (e.g., malformed YAML).
            pydantic.ValidationError: If loaded data fails AppConfig validation.
            ValueError: For other configuration-related errors.
        """
        try:
            logger.debug(f"Attempting to load configuration from: {config_path}")
            raw_config = OmegaConf.load(config_path)

            config_dict = OmegaConf.to_container(raw_config, resolve=True)

            # Override with provided arguments if they exist
            if root_git_path is not None:
                config_dict['goal_git_path'] = root_git_path
                logger.debug(f"Overriding goal_git_path with provided argument: {root_git_path}")

            if goal_path is not None:
                config_dict['goal_root_path'] = goal_path
                logger.debug(f"Overriding goal_root_path with provided argument: {goal_path}")

            app_config = cls(**config_dict)
            logger.debug("Application configuration loaded successfully.")
            return app_config
        except FileNotFoundError:
            logger.error(f"Configuration file not found at: {config_path}")
            raise
        except MissingMandatoryValue as e:
            logger.error(f"Missing mandatory value in configuration: {e}")
            # Ensure this error message clearly indicates which key is missing.
            # OmegaConf's MissingMandatoryValue exception __str__ usually includes the key.
            raise ValueError(f"Missing mandatory value in configuration: {e}") from e

        # TODO: Fix me - AttributeError: type object 'OmegaConf' has no attribute 'errors'
        # except OmegaConf.errors.OmegaConfBaseException as e: # Catches various OmegaConf errors
        #     logger.error(f"Error loading or parsing configuration file ({config_path}): {e}")
        #     raise
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            raise
        except Exception as e: # Catch any other unexpected errors during loading
            logger.error(f"An unexpected error occurred while loading configuration: {e}")
            raise ValueError(f"An unexpected error occurred while loading configuration: {e}")
