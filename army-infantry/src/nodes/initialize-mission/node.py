import logging
# Adjust import as per final structure, assuming graph_state is two levels up
from ...graph_state import WorkflowState, MissionContext 

logger = logging.getLogger(__name__)

async def initialize_mission_node(state: WorkflowState) -> WorkflowState:
    logger.info("Executing initialize_mission_node")
    # For initial scaffolding, just updating current_step_name is sufficient
    # and returning the rest of the state as is.
    # The spec example showed {**state, "current_step_name": "..."}
    # which is a good way to do it.
    
    # Example of how to access mission_context if needed for future expansion:
    # mission_context = state['mission_context']
    # logger.info(f"Mission ID: {mission_context.mission_id}")

    # Example of immutable update for mission_context (not required for this initial node):
    # updated_mission_context = mission_context.copy(update={"mission_title": "Initialized Mission"})
    # return {
    #     "mission_context": updated_mission_context,
    #     "current_step_name": "initialize_mission_node",
    #     "critical_error_message": state.get("critical_error_message") # Preserve other state parts
    # }

    return {
        "mission_context": state["mission_context"], # Ensure mission_context is passed through
        "current_step_name": "initialize_mission_node",
        "critical_error_message": state.get("critical_error_message")
    }
