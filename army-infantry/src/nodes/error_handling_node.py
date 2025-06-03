import logging
from ..graph_state import WorkflowState

logger = logging.getLogger(__name__)

async def error_handling_node(state: WorkflowState) -> WorkflowState:
    error_message = state.get("critical_error_message")
    logger.error(f"Critical error encountered in workflow: {error_message}")
    
    # Potentially update mission_context to reflect failure status
    # mission_context = state['mission_context']
    # updated_mission_context = mission_context.copy(
    #     update={
    #         "final_status": "FAILURE",
    #         "execution_summary": (mission_context.execution_summary or "") + f"\nCritical error: {error_message}"
    #     }
    # )
    # return {
    #     "mission_context": updated_mission_context,
    #     "current_step_name": "error_handling_node",
    #     "critical_error_message": error_message 
    # }
    # For now, just log and pass through state
    return {
        "mission_context": state["mission_context"],
        "current_step_name": "error_handling_node", # Update step name
        "critical_error_message": error_message 
    }
