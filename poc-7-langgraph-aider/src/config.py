"""Pydantic model for application configuration."""
import logging
from pydantic import BaseModel, ValidationError
from typing import List, Optional
from omegaconf import OmegaConf, MissingMandatoryValue

logger = logging.getLogger(__name__)

class AppConfig(BaseModel):
    workspace_root_path: str
    goal_root_path: str
    task_description_filename: str
    manifest_output_filename: str
    changelog_output_filename: str
    log_subdirectory_name: str
    overview_log_filename: str
    detailed_log_filename: str
    # Example of a more complex field if needed later:
    # aider_model: Optional[str] = None 
    manifest_template_filename: str
    changelog_template_filename: str

    changelog_aider_model: str

    @classmethod
    def load_from_yaml(cls, config_path: str = "config.yml") -> "AppConfig":
        """
        Loads application configuration from a YAML file using OmegaConf
        and instantiates an AppConfig object.

        Args:
            config_path: Path to the configuration file.

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
            app_config = cls(**config_dict)
            logger.debug("Application configuration loaded successfully.")
            return app_config
        except FileNotFoundError:
            logger.error(f"Configuration file not found at: {config_path}")
            raise
        except MissingMandatoryValue as e:
            logger.error(f"Missing mandatory value in configuration: {e}")
            raise ValueError(f"Missing mandatory value in configuration: {e}") from e
        except OmegaConf.errors.OmegaConfBaseException as e: # Catches various OmegaConf errors
            logger.error(f"Error loading or parsing configuration file ({config_path}): {e}")
            raise
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            raise
        except Exception as e: # Catch any other unexpected errors during loading
            logger.error(f"An unexpected error occurred while loading configuration: {e}")
            raise ValueError(f"An unexpected error occurred while loading configuration: {e}")
