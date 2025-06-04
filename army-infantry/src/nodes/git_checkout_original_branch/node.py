import logging
from typing import Any

from ...graph_state import MissionContext, WorkflowState
from ...services.git_service import GitService

logger = logging.getLogger(__name__)

async def git_checkout_original_branch_node(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    state['current_step_name'] = git_checkout_original_branch_node.__name__
    logger.info(f"Executing {state['current_step_name']}")

    # mission_context is guaranteed to be in state by the graph runner
    mission_context: MissionContext = state['mission_context']

    try:
        state = await _git_checkout_original_branch(state, config)
    except Exception as e:
        error_message = f"Error in {state['current_step_name']}: {str(e)}"
        logger.error(error_message, exc_info=True)

        mission_context.status = "ERROR"

        state["critical_error_message"] = error_message # Use the more concise error_message

    return state

async def _git_checkout_original_branch(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    """
    Checks out the original Git branch that was active before a new mission branch was created.
    """
    mission_context: MissionContext = state['mission_context']

    configurable = config["configurable"]
    git_service: GitService = configurable.get("git_service")

    original_branch_name = mission_context.original_branch_name

    # Core logic for Git operations with simplified top-level error handling
    try:
        logger.info(f"Attempting to checkout original branch: {original_branch_name}")

        current_branch_before_checkout = await git_service.get_current_branch()
        if current_branch_before_checkout == original_branch_name:
            logger.overview(f"Already on the original branch '{original_branch_name}'. No checkout needed.")
        else:
            await git_service.checkout_branch(original_branch_name, create_new=False)
            logger.overview(f"Checked out original branch: {original_branch_name}")

    except Exception as e:
        raise RuntimeError(f"Failed to checkout original branch '{original_branch_name}': {e}")

    return state
