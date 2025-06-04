"""
Main execution script for the Army Infantry

This script initializes the application configuration, sets up logging,
instantiates necessary services (like LlmPromptService),
and then starts working on the mission
"""

import argparse  # Added for command-line argument parsing
import asyncio
import logging

# Project-specific imports
from src.app_config import AppConfig
from src.graph_builder import build_graph
from src.graph_state import MissionContext, WorkflowState
from src.services.aider_service import AiderService
from src.services.git_service import GitService
from src.services.llm_prompt_service import LlmPromptService
from src.services.write_file_from_template_service import WriteFileFromTemplateService
from src.utils.logging_setup import setup_logging

# 1. Initialize ArgumentParser
parser = argparse.ArgumentParser(description="Army Infantry - Coding Mission Executor")
parser.add_argument(
    "--root_git_path",
    type=str,
    help="Override the root_git_path from config.yaml with the provided path.",
    required=False
)
# Add argument for the mission_folder_path
parser.add_argument(
    "--mission_folder_path",
    type=str,
    help="Path to the mission folder. Should be relative to the root_git_path.",
    required=False
)
args = parser.parse_args()

# 2. Initialize AppConfig first, passing the command line argument if provided
app_config = AppConfig(command_line_git_path=args.root_git_path)

# 3. Initialize and setup logging using AppConfig
setup_logging(app_config)

# Get the logger instance
logger = logging.getLogger(__name__)


# Initial log message to confirm setup and show date
if args.root_git_path:
    logger.info(f"Overriding project_git_path with command line argument: {args.root_git_path}")
logger.debug("Debug level test message for detailed log from main.py.")

async def run() -> None:
    """
    Main asynchronous function to run the Army Infantry mission.
    """
    logger.info("Starting Army Infantry: Coding Mission Executor.")
    try:
        logger.info(f"Mission Folder Path: {app_config.mission_folder_path_absolute}")

        # Instantiate services
        logger.debug("Instantiating services...")
        llm_prompt_service = LlmPromptService(app_config=app_config)
        aider_service = AiderService(app_config=app_config, llm_prompt_service=llm_prompt_service)
        git_service = GitService(app_config.root_git_path)
        write_file_from_template_service = WriteFileFromTemplateService() # Does not require app_config
        logger.info("Services instantiated.")

        # Define LangGraph graph
        app_graph = build_graph()

        # Prepare initial WorkflowState
        initial_state: WorkflowState = {
            "mission_context": MissionContext(),
            "current_step_name": None,
            "critical_error_message": None
        }

        # Prepare RunnableConfig
        runnable_config = {
            "configurable": {
                "app_config": app_config,
                "llm_prompt_service": llm_prompt_service,
                "aider_service": aider_service,
                "git_service": git_service,
                "write_file_from_template_service": write_file_from_template_service,
            }
        }
        logger.debug("RunnableConfig prepared with services.")

        # Invoke graph execution
        logger.overview("Invoking graph execution...")
        final_state = await app_graph.ainvoke(initial_state, config=runnable_config)
        logger.overview(f"  - Final Step Name: {final_state.get('current_step_name', 'N/A')}")

        logger.info("Army Infantry Mission Complete")
    except ValueError as ve:
        logger.critical(f"Configuration error: {ve}. Please check your .env, config.yaml files, or command line arguments. Exiting.", exc_info=False)
    except Exception:
        logger.error("An unhandled error occurred during Army Infantry execution:", exc_info=True)

if __name__ == "__main__":
    asyncio.run(run())
