import logging
from typing import Any

from ..graph_state import WorkflowState

logger = logging.getLogger(__name__)

async def error_handling_node(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    """
    Handles errors that occur during the workflow execution.
    """
    state['current_step_name'] = error_handling_node.__name__
    logger.info(f"Executing {state['current_step_name']}")

    try:
        state = await _error_handling(state, config)
    except Exception as e:
        # Log critical error if error handling itself fails
        logger.critical(f"CRITICAL ERROR IN {state['current_step_name']}: {e}", exc_info=True)
        # Preserve original error message if possible, otherwise update
        original_error = state.get("critical_error_message", "Unknown error before error_handling_node.")
        state["critical_error_message"] = f"Error in {state['current_step_name']}: {e}. Original error: {original_error}"
        if 'mission_context' in state and hasattr(state['mission_context'], 'status'):
            state['mission_context'].status = "ERROR" # Ensure status reflects an error state
        else:
            logger.warning("Mission context or status attribute not found in state during error handling.")
        return state

    return state

async def _error_handling(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    """
    Private function to handle the core logic of error processing.
    """
    logger.info(f"Executing {state['current_step_name']}._error_handling")

    error_message = state.get("critical_error_message")
    logger.error(f"Critical error being processed by error_handling_node: {error_message}")

    # TODO: Implement more sophisticated error handling logic here
    # For example, send notifications, attempt recovery, or provide detailed error reports.

    # Ensure the mission status is set to ERROR
    if 'mission_context' in state and hasattr(state['mission_context'], 'status'):
        state['mission_context'].status = "ERROR"
    else:
        logger.warning("Mission context or status attribute not found in state within _error_handling.")

    return state
