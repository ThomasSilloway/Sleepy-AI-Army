import logging
import os
from typing import Any

from ...app_config import AppConfig
from ...graph_state import MissionContext, WorkflowState
from ...services.git_service import GitService
from ...services.llm_prompt_service import LlmPromptService
from .models import MissionData
from .prompts import get_system_prompt, get_user_prompt

logger = logging.getLogger(__name__)

async def initialize_mission_node(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    state['current_step_name'] = initialize_mission_node.__name__
    logger.overview(f"Executing {state['current_step_name']}")

    # mission_context is guaranteed to be in state by the graph runner
    mission_context: MissionContext = state['mission_context']

    try:
        state = await _initialize_mission(state, config)
    except Exception as e:
        error_message = f"Error in {state['current_step_name']}: {str(e)}"
        logger.error(error_message, exc_info=True)

        mission_context.status = "ERROR"

        state["critical_error_message"] = error_message # Use the more concise error_message

    return state

async def _initialize_mission(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:

    configurable = config["configurable"]
    app_config: AppConfig = configurable["app_config"]
    llm_service: LlmPromptService = configurable["llm_prompt_service"]
    git_service: GitService = configurable.get("git_service")

    mission_spec_content: str = _load_mission_spec_content_from_file(app_config)

    # Get original branch name
    original_branch_name = await git_service.get_current_branch()
    logger.info(f"Original Git branch: {original_branch_name}")

    # Perform LLM call to get MissionData (title and git_branch_base_name)
    mission_data = await _extract_mission_data(llm_service, app_config, mission_spec_content)

    # Verify files and prepare for Aider
    # TODO: Extract files to read separately and add to mission_context and then process with `--read` command for Aider so it can't edit them
    files_to_edit = await _verify_and_prepare_aider_files(app_config, mission_data)

    # Update mission context
    mission_context = state['mission_context']
    mission_context.mission_spec_content = mission_spec_content
    mission_context.mission_title = mission_data.mission_title
    mission_context.original_branch_name = original_branch_name
    mission_context.generated_branch_name = mission_data.git_branch_name
    mission_context.aider_editable_files = files_to_edit
    mission_context.status = "IN_PROGRESS"

    debug_files_to_edit: list[str] = [" "]
    debug_files_to_edit.extend(mission_context.aider_editable_files) if mission_context.aider_editable_files else ["None identified"]

    # TODO: Change editable files to a file tree visual
    logger.overview(f"""
        Mission initialized:
            - Title: '{mission_data.mission_title}'
            - Branch to be created: '{mission_context.generated_branch_name}'
            - Original branch: '{original_branch_name}'
            - Editable files: {"\n                   -".join(debug_files_to_edit)}
            - Mission spec: '{mission_spec_content}'
    """)

    return state

def _load_mission_spec_content_from_file(app_config: AppConfig) -> str:
    mission_spec_path = app_config.mission_description_path
    logger.info(f"Loading mission spec from: {mission_spec_path}")
    try:
        with open(mission_spec_path, encoding="utf-8") as f:
            mission_spec_content = f.read()
    except Exception as e:
        logger.error(f"Error reading mission spec file {mission_spec_path}: {e}", exc_info=True)
        raise RuntimeError(f"Error reading mission spec file {mission_spec_path}: {e}")
    return mission_spec_content

async def _extract_mission_data(llm_service: LlmPromptService, app_config: AppConfig, mission_spec_content: str) -> MissionData:
    messages = [
        {"role": "system", "content": get_system_prompt(app_config.valid_branch_types)},
        {"role": "user", "content": get_user_prompt(mission_spec_content)}
    ]
    try:
        # Using the updated MissionData model that includes git_branch_base_name
        extracted_data: MissionData | None = await llm_service.get_structured_output(
            messages=messages,
            output_pydantic_model_type=MissionData,
            llm_model_name=app_config.mission_data_extraction_model
        )
        # TODO: Now that this is using a paid model, need to get the cost and add it to the mission context
        if extracted_data and extracted_data.mission_title and extracted_data.git_branch_name:
            extracted_data.sanitize()
            return extracted_data
        else:
            logger.error("Extracted data is None or mission_title/git_branch_base_name is missing.")
            raise RuntimeError("Extracted data is None or mission_title/git_branch_base_name is missing.")
    except Exception as e:
        logger.error(f"Failed to extract mission data from mission spec: {e}", exc_info=True)
        raise RuntimeError(f"Failed to extract mission data from mission spec: {e}")


async def _verify_and_prepare_aider_files(app_config: AppConfig, mission_data: MissionData) -> list[str]:
    """
    Verifies file existence for 'files_to_edit' and creates 'files_to_create' (or confirms existence).
    Raises RuntimeError if validation fails for files_to_edit or if creation fails for new files_to_create.
    """
    project_git_root = app_config.root_git_path
    verified_files_to_edit = []
    verified_files_to_read = []
    prepared_files_to_create = []

    # Process mission_data.files_to_edit
    for file_path in mission_data.files_to_edit:
        full_path = os.path.join(project_git_root, file_path)
        if not os.path.exists(full_path):
            logger.error(f"File specified for editing does not exist: {file_path} (full path: {full_path})")
            raise RuntimeError(f"File specified for editing does not exist: {file_path} (full path: {full_path})")
        verified_files_to_edit.append(file_path)

    # Process mission_data.files_to_read
    for file_path in mission_data.files_to_read:
        full_path = os.path.join(project_git_root, file_path)
        if not os.path.exists(full_path):
            logger.error(f"File specified for reading does not exist: {file_path}")
            raise RuntimeError(f"File specified for reading does not exist: {file_path}")
        verified_files_to_read.append(file_path)

    # Process mission_data.files_to_create
    for file_path in mission_data.files_to_create:
        full_path = os.path.join(project_git_root, file_path)
        if os.path.exists(full_path):
            logger.debug(f"File specified for creation '{file_path}' already exists, proceeding with existing file.")
        else:
            logger.info(f"Creating empty file as placeholder: {file_path}")
            parent_dir = os.path.dirname(full_path)
            if parent_dir: 
                os.makedirs(parent_dir, exist_ok=True)
            try:
                with open(full_path, "w") as f:
                    pass 
            except OSError as e_create: # Catch specific errors
                logger.error(f"IOError/OSError creating file {file_path}: {e_create}", exc_info=True)
                raise RuntimeError(
                    f"Failed to create placeholder file {file_path} due to an IO/OS error: {e_create}"
                )
        prepared_files_to_create.append(file_path) # Add to list if it exists or was successfully created

    return verified_files_to_edit + prepared_files_to_create + verified_files_to_read
