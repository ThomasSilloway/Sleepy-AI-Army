import logging
from ...graph_state import WorkflowState, MissionContext

logger = logging.getLogger(__name__)

async def git_branch_node(state: WorkflowState) -> WorkflowState:
    logger.info("Executing git_branch_node")

    # mission_context = state['mission_context']
    # logger.info(f"Git branch operations for mission ID: {mission_context.mission_id}")
    
    return {
        "mission_context": state["mission_context"],
        "current_step_name": "git_branch_node",
        "critical_error_message": state.get("critical_error_message")
    }
