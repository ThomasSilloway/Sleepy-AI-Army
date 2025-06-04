import logging
from typing import Any

from ...graph_state import MissionContext, WorkflowState
from ...services.git_service import GitService

logger = logging.getLogger(__name__)

async def git_branch_node(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    state['current_step_name'] = git_branch_node.__name__
    logger.info(f"Executing {state['current_step_name']}")

    mission_context: MissionContext = state['mission_context']

    try:
        state = await _git_branch(state, config)
    except Exception as e:
        error_message = f"Error in {state['current_step_name']}: {str(e)}"
        logger.error(error_message, exc_info=True)

        mission_context.status = "ERROR"
        state["critical_error_message"] = error_message

    return state

async def _git_branch(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    """
    Creates and checks out a new Git branch based on the generated_branch_name
    stored in the mission_context.
    """
    mission_context: MissionContext = state['mission_context']

    configurable = config["configurable"]
    git_service: GitService = configurable.get("git_service")

    generated_branch_name = mission_context.generated_branch_name

    # Core logic for Git operations with simplified top-level error handling
    try:
        logger.info(f"Attempting to create and checkout branch: {generated_branch_name}")

        # Attempt to create and checkout the new branch using 'git checkout -b'
        await git_service.checkout_branch(generated_branch_name, create_new=True)
        logger.overview(f"Checked out branch: {generated_branch_name}")
    except Exception as e:
        raise RuntimeError(f"Failed to create and checkout branch '{generated_branch_name}': {e}")

    return state
