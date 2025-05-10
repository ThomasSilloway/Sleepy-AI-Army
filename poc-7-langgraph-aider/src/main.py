"""Main application entry point for the PoC7 Orchestrator."""
import logging
# Removed OmegaConf and ValidationError as they are now handled in AppConfig
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

def main():
    logger.info("PoC7 LangGraph Orchestrator Starting...")

    try:
        # Load configuration using the AppConfig class method
        app_config = AppConfig.load_from_yaml()
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

    # NOTE: All TODOs below here should be in separate functions

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
