"""Contains logic for the initialize_workflow node."""
import logging
from pathlib import Path

from src.config import AppConfig
from src.state import WorkflowState  # Assuming WorkflowState is a TypedDict

logger = logging.getLogger(__name__)

def initialize_workflow_node(state: WorkflowState, config) -> WorkflowState:
    """
    Initializes the workflow: sets up logging, validates paths from AppConfig,
    resolves and stores critical paths in WorkflowState, and ensures the
    log directory exists.
    """
    state['current_step_name'] = "initialize_workflow_node"

    config = config["configurable"]
    app_config: AppConfig = config["app_config"]

    logger.info("[Initializer] Initializer Node")

    # Validate goal_root_path and workspace_root_path
    goal_root_path = Path(app_config.goal_root_path).resolve()
    workspace_root_path = Path(app_config.workspace_root_path).resolve()

    if not goal_root_path.is_dir():
        error_msg = f"[Initializer] Goal root path does not exist or is not a directory: {goal_root_path}"
        logger.error(error_msg)
        state['error_message'] = error_msg
        state['last_event_summary'] = f"Error: {error_msg}"
        return state

    if not workspace_root_path.is_dir():
        error_msg = f"[Initializer] Workspace root path does not exist or is not a directory: {workspace_root_path}"
        logger.error(error_msg)
        state['error_message'] = error_msg
        state['last_event_summary'] = f"Error: {error_msg}"
        return state

    state['goal_folder_path'] = str(goal_root_path)
    state['workspace_folder_path'] = str(workspace_root_path)
    # logger.info(f"Validated goal_folder_path: {state['goal_folder_path']}")
    # logger.info(f"Validated workspace_folder_path: {state['workspace_folder_path']}")

    # Resolve and store critical absolute paths in WorkflowState
    try:
        state['manifest_template_path'] = str(workspace_root_path / app_config.manifest_template_filename)

        state['task_description_path'] = str(goal_root_path / app_config.task_description_filename)
        state['manifest_output_path'] = str(goal_root_path / app_config.manifest_output_filename)
        state['changelog_output_path'] = str(goal_root_path / app_config.changelog_output_filename)



        # logger.info(f" - Task description path: {state['task_description_path']}")
        # logger.info(f"Manifest template path: {state['manifest_template_path']}")
        # logger.info(f"Manifest output path: {state['manifest_output_path']}")
        # logger.info(f"Changelog output path: {state['changelog_output_path']}")

    except Exception as e:
        error_msg = f"[Initializer] Error resolving paths or creating log directory: {e}"
        logger.error(error_msg)
        state['error_message'] = error_msg
        state['last_event_summary'] = f"Error: {error_msg}"
        return state

    state['last_event_summary'] = "Initialization complete; paths resolved."
    # logger.info("Workflow initialization successful.")

    # Clear error message if initialization was successful
    state['error_message'] = None 
    return state
