"""Main application entry point for the PoC7 Orchestrator."""
import logging
from omegaconf import OmegaConf, MissingMandatoryValue
from pydantic import ValidationError
from langgraph.graph import StateGraph, END

from src.config import AppConfig
from src.state import WorkflowState
from src.utils.logging_setup import setup_logging
from src.services import AiderService, ChangelogService
from src.nodes import initialize_workflow_node, error_path_node, success_path_node
from src.graph_builder import build_graph


import traceback

# Configure logging using the utility function
setup_logging()
logger = logging.getLogger(__name__)

def load_app_config(config_path: str = "config.yml") -> AppConfig:
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
        logger.info(f"Attempting to load configuration from: {config_path}")
        raw_config = OmegaConf.load(config_path)

        config_dict = OmegaConf.to_container(raw_config, resolve=True)
        app_config = AppConfig(**config_dict)
        logger.info("Application configuration loaded successfully.")
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


def main():
    logger.info("PoC7 LangGraph Orchestrator Starting...")

    try:
        app_config = load_app_config()
        # You can now use app_config throughout your application
        logger.info(f"Workspace root: {app_config.workspace_root_path}")
        logger.info(f"Goal root: {app_config.goal_root_path}")

        # Instantiate Services
        aider_service = AiderService(app_config=app_config)
        changelog_service = ChangelogService(app_config=app_config)
        logger.info("Services instantiated.")

    except Exception as e:
        logger.critical(f"Failed to initialize application due to configuration error: {e}")
        logger.critical(f"Callstack:\n{traceback.format_exc()}")
        return  # Exit if configuration fails

    # NOTE: Everything below here should be in separate functions

    # Define LangGraph graph
    graph_builder = build_graph()
    logger.info("Graph builder created.")
    
    # Compile graph
    app_graph = graph_builder.compile()
    logger.info("Graph compiled.")

    # TODO: Prepare initial WorkflowState and RunnableConfig
    # TODO: Invoke graph execution
    logger.info("PoC7 LangGraph Orchestrator Finished (placeholder for graph execution).")

if __name__ == "__main__":
    main()
