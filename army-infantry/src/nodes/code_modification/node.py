import logging
from typing import Any

from src.app_config import AppConfig

# MissionContext and StructuredError are now directly imported above
from src.models.aider_summary import AiderRunSummary
from src.services.aider_service import AiderExecutionResult, AiderService

# Corrected import path for MissionContext and StructuredError
from ...graph_state import MissionContext, WorkflowState
from .prompts import get_aider_prompt_template

logger = logging.getLogger(__name__)


async def code_modification_node(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    """
    Modifies code based on the mission context.
    """
    state['current_step_name'] = code_modification_node.__name__
    logger.overview(f"Executing {state['current_step_name']}")

    try:
        state = await _code_modification(state, config)
    except Exception as e:
        logger.error(f"Error in {state['current_step_name']}: {e}", exc_info=True)
        state["critical_error_message"] = f"Error in {state['current_step_name']}: {e}"
        state['mission_context'].status = "ERROR"
        return state

    return state

async def _code_modification(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    """
    Private function to handle the core logic of code modification.
    """
    mission_context: MissionContext = state['mission_context']
    app_config: AppConfig = config["configurable"]["app_config"]
    aider_service: AiderService = config["configurable"]["aider_service"]

    aider_result: AiderExecutionResult = await _call_aider_service(app_config, aider_service, mission_context)

    aider_summary: AiderRunSummary = await _get_aider_summary(aider_service, aider_result)

    _update_mission_context_from_aider_summary(mission_context, aider_summary, state)

    return state

async def _call_aider_service(app_config: AppConfig, aider_service: AiderService, mission_context: MissionContext) -> AiderExecutionResult:

    # Get prompt template
    mission_spec_filename = app_config.mission_description_filename
    aider_prompt = get_aider_prompt_template(mission_spec_filename)

    command_args = [
            "-m", aider_prompt,
            "--model", app_config.aider_code_model,
            "--auto-commits",
            "--config", app_config.aider_config_file_path
        ]

    files_read_only = [
        app_config.mission_description_path,
        app_config.conventions_file_path
    ]

    files_editable = mission_context.aider_editable_files
    logger.info(f"Aider will attempt to edit the following files: {files_editable}")

    logger.info("Calling AiderService to execute modification mission.")
    try:
        aider_result: AiderExecutionResult = await aider_service.execute(
            command_args=command_args,
            files_editable=files_editable,
            files_read_only=files_read_only
        )
        return aider_result
    except Exception as e:
        raise RuntimeError(f"Error executing aider service: {e}")

async def _get_aider_summary(aider_service: AiderService, aider_result: AiderExecutionResult) -> AiderRunSummary:

    try:
        aider_summary = await aider_service.get_summary(aider_result)
    except Exception as e:
        raise RuntimeError(f"Error getting aider summary: {e}")

    if aider_summary is None:
        raise RuntimeError("No summary was produced by the Aider service.")

    return aider_summary

def _update_mission_context_from_aider_summary(mission_context: MissionContext, aider_summary: AiderRunSummary, state: WorkflowState):
    logger.debug(f"Aider Summary: \n{aider_summary.model_dump_json(indent=2)}")

    # Update execution summary
    if aider_summary.changes_made:
        mission_context.execution_summary = "\n".join(aider_summary.changes_made)
    else:
        mission_context.execution_summary = aider_summary.raw_output_summary

    # Update files modified/created
    mission_context.files_created = aider_summary.files_created
    mission_context.files_modified = aider_summary.files_modified

    mission_context.git_summary = aider_summary.commits
    mission_context.total_cost_usd += aider_summary.total_cost

    # Update mission status and errors if any
    if aider_summary.errors_reported:

        for error in aider_summary.errors_reported:
            mission_context.mission_errors.append(error)

        raise RuntimeError(f"Aider reported {len(aider_summary.errors_reported)} errors during its execution.")

    # If no commits were made, then the mission failed
    elif not aider_summary.commits:

        mission_context.files_created = []
        mission_context.files_modified = []
        raise RuntimeError("Aider did not make any commits during its execution.")

    # If we made it this far, then the mission was successful
    mission_context.status = "SUCCESS"
