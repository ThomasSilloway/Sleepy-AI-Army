import logging
from typing import Any

from ...graph_state import WorkflowState

logger = logging.getLogger(__name__)

async def mission_reporting_node(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    """
    Generates and potentially sends a mission report.
    """
    state['current_step_name'] = mission_reporting_node.__name__
    logger.info(f"Executing {state['current_step_name']}")

    try:
        state = await _mission_reporting(state, config)
    except Exception as e:
        logger.error(f"Error in {state['current_step_name']}: {e}", exc_info=True)
        # Even in reporting, an error should be captured.
        # Depending on policy, this might not set mission_context.status to "ERROR"
        # if the core mission was a success, but the reporting failed.
        # For now, we'll follow the pattern.
        state["critical_error_message"] = f"Error in {state['current_step_name']}: {e}"
        if 'mission_context' in state and hasattr(state['mission_context'], 'status'):
            # If the mission was already completed, we might not want to overwrite the status.
            # However, if reporting is critical, this might be appropriate.
            # For now, setting to error to indicate a problem in this node.
            current_status = state['mission_context'].status
            if current_status not in ["COMPLETED", "SUCCESS"]: # Example: don't overwrite a success
                 state['mission_context'].status = "ERROR"
            logger.info(f"Mission status was {current_status}, critical error in reporting. Status is now {state['mission_context'].status}")
        else:
            logger.warning("Mission context or status attribute not found in state.")
        return state

    return state

async def _mission_reporting(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    """
    Private function to handle the core logic of mission reporting.
    """
    logger.info(f"Executing {state['current_step_name']}._mission_reporting")

    # TODO: Implement the actual mission reporting logic here
    # This could involve:
    # - Compiling results from mission_context
    # - Generating a formatted report (e.g., text, JSON, PDF)
    # - Sending the report (e.g., email, API call, saving to file)

    # Example: Log final mission status for reporting
    mission_status = "UNKNOWN"
    if 'mission_context' in state and hasattr(state['mission_context'], 'status'):
        mission_status = state['mission_context'].status

    logger.info(f"Final mission status for reporting: {mission_status}")
    if state.get("critical_error_message"):
        logger.info(f"Mission ended with error: {state.get('critical_error_message')}")

    # Typically, this node would not change mission_context.status further,
    # but rather report on the existing status.

    return state
