"""Contains logic for workflow finalization nodes (success, error)."""
import logging
from src.state import WorkflowState

logger = logging.getLogger(__name__)

def success_path_node(state: WorkflowState) -> WorkflowState:
    """Node for the success path after a significant workflow stage."""
    logger.info("Executing success_path_node.")
    # This node currently signifies successful completion of a phase.
    state['current_step_name'] = "success_path_node"
    state['last_event_summary'] = "Workflow completed successfully."
    return state

def error_path_node(state: WorkflowState) -> WorkflowState:
    """Node for the error handling path."""
    error_msg = state.get('error_message', "Unknown error")
    current_step = state.get('current_step_name', "Unknown step") # Step where error was detected
    logger.error(f"Executing error_path_node. Error detected in step '{current_step}': {error_msg}")
    state['current_step_name'] = "error_path_node" # Update current step to this node
    state['last_event_summary'] = f"Error path taken due to: {error_msg} in step {current_step}."
    # Potentially add more error handling logic here, e.g., notifications, cleanup
    return state
