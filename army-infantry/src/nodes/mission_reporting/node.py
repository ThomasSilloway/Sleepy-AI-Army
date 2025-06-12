import logging
from datetime import datetime, timezone
from typing import Any

from ...app_config import AppConfig
from ...graph_state import MissionContext, WorkflowState
from ...services.git_service import GitService, GitServiceError
from ...services.llm_prompt_service import LlmPromptService
from ...services.write_file_from_template_service import WriteFileFromTemplateService
from . import models, prompts

logger = logging.getLogger(__name__)


async def _generate_execution_summary(
    commit_hashes: list[str],
    git_service: GitService,
    llm_service: LlmPromptService,
    app_config: AppConfig
) -> tuple[list[str], float]:
    """
    Generates an execution summary from git commits using an LLM.
    """
    if not commit_hashes:
        logger.info("No commit hashes provided, returning default summary.")
        return (["No commits submitted by aider"], 0.0)

    all_diffs = []
    logger.info(f"Fetching diffs for {len(commit_hashes)} commits.")
    for commit_hash in commit_hashes:
        try:
            diff = await git_service.get_diff_for_commit(commit_hash)
            all_diffs.append(diff)
        except GitServiceError as e:
            logger.warning(f"Could not get diff for commit {commit_hash}: {e}")
    
    if not all_diffs:
        logger.error("Could not retrieve diffs for any of the provided commits.")
        return (["Could not retrieve diffs for any commits."], 0.0)

    concatenated_diffs = "\n\n---\n\n".join(all_diffs)
    
    system_prompt = prompts.get_system_prompt()
    user_prompt = prompts.get_user_prompt(concatenated_diffs)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # Assuming a model for reporting is defined in AppConfig, with a fallback.
    reporting_model = getattr(app_config, 'reporting_model', 'gemini-1.5-flash-latest')
    logger.info(f"Requesting execution summary from LLM using model: {reporting_model}")

    parsed_response, cost = await llm_service.get_structured_output(
        messages=messages,
        output_pydantic_model_type=models.ExecutionSummary,
        llm_model_name=reporting_model
    )

    cost = cost or 0.0

    if not parsed_response or not parsed_response.summary:
        logger.warning("LLM failed to generate a valid execution summary.")
        return (["Unable to generate Execution Summary, see Aider summary below"], cost)

    logger.info("Successfully generated execution summary from LLM.")
    return (parsed_response.summary, cost)


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
        if mission_context:
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

    # Parse commit hashes from git_summary ("hash - message")
    commit_hashes = [summary.split(' ')[0] for summary in mission_context.git_summary if summary]

    # Instantiate services required for summary generation
    # Assuming repo_path is available in app_config, with a fallback.
    repo_path = getattr(app_config, 'repo_path', '.') 
    git_service = GitService(repo_path=repo_path)
    llm_service = LlmPromptService(app_config=app_config)

    # Call helper to generate the execution summary
    execution_summary_list, cost = await _generate_execution_summary(
        commit_hashes=commit_hashes,
        git_service=git_service,
        llm_service=llm_service,
        app_config=app_config
    )

    # Update total cost in mission context
    if cost:
        mission_context.total_cost_usd += cost

    critical_error_from_state = state.get("critical_error_message")
    mission_errors_list = []
    if critical_error_from_state:
        mission_errors_list.append(critical_error_from_state)
    if mission_context.mission_errors:
        mission_errors_list.extend(mission_context.mission_errors)

    # Create variable for timestamp in the format year-month-day hour-minute-second
    report_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    template_data = {
        "mission_title": mission_context.mission_title,
        "mission_description": mission_context.mission_spec_content,
        "status": mission_context.status,
        "report_timestamp": report_timestamp,
        "execution_summary": execution_summary_list,
        "aider_changes_made": mission_context.aider_changes_made,
        "aider_questions_asked": mission_context.aider_questions_asked,
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
