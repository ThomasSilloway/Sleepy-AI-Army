import logging

from ...graph_state import WorkflowState

logger = logging.getLogger(__name__)

async def mission_reporting_node(state: WorkflowState) -> WorkflowState:
    logger.info("Executing mission_reporting_node")

    # mission_context = state['mission_context']
    # logger.info(f"Mission reporting for mission ID: {mission_context.mission_id}")

    return {
        "mission_context": state["mission_context"],
        "current_step_name": "mission_reporting_node",
        "critical_error_message": state.get("critical_error_message")
    }
