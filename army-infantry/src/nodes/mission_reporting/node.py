import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ...app_config import AppConfig
from ...graph_state import MissionContext, WorkflowState
from ...services.write_file_from_template_service import WriteFileFromTemplateService

logger = logging.getLogger(__name__)

async def mission_reporting_node(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    """
    Generates and potentially sends a mission report.
    """
    state['current_step_name'] = mission_reporting_node.__name__
    logger.overview(f"Executing {state['current_step_name']}")

    try:
        state = await _mission_reporting(state, config)
    except Exception as e:
        error_message = f"Error in {state['current_step_name']}: {str(e)}"
        logger.error(error_message, exc_info=True) # Log full traceback

        mission_context = state.get('mission_context')
        mission_context.status = "ERROR"
        state["critical_error_message"] = error_message
        return state 

    return state

async def _mission_reporting(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    """
    Private async function to handle the core logic of mission reporting.
    """
    logger.info(f"Executing {state['current_step_name']}._mission_reporting (private helper)")

    configurable = config["configurable"]
    app_config: AppConfig = configurable['app_config']
    write_file_service: WriteFileFromTemplateService = configurable['write_file_from_template_service']
    mission_context: MissionContext = state['mission_context']

    critical_error_from_state = state.get("critical_error_message")
    mission_errors_list = [critical_error_from_state].extend(mission_context.mission_errors)

    # Create variable for timestamp in the format year-month-day hour-minute-second
    report_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    template_data = {
        "mission_title": mission_context.mission_title,
        "mission_description": mission_context.mission_spec_content,
        "status": mission_context.status,
        "report_timestamp": report_timestamp,
        "execution_summary": mission_context.execution_summary,
        "files_modified": mission_context.files_modified,
        "files_created": mission_context.files_created,
        "generated_branch_name": mission_context.generated_branch_name,
        "git_summary": mission_context.git_summary,
        "total_cost_usd": mission_context.total_cost_usd,
        "mission_errors": mission_errors_list,
    }

    template_abs_path: str = app_config.mission_report_template_abs_path
    output_abs_path: str = app_config.mission_report_path

    logger.info(f"Attempting to render mission report using template: {template_abs_path}")
    logger.info(f"Report will be written to: {output_abs_path}")

    success = write_file_service.render_and_write_file(
        template_abs_path_str=template_abs_path,
        context=template_data,
        output_abs_path_str=output_abs_path
    )

    if not success:
        raise RuntimeError("Failed to render and write mission report. Service returned False.")

    return state
