import logging
from typing import Any

from ...app_config import AppConfig
from ...graph_state import WorkflowState
from ...services.llm_prompt_service import LlmPromptService
from .models import MissionData
from .prompts import get_system_prompt, get_user_prompt

logger = logging.getLogger(__name__)

async def initialize_mission_node(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:

    # Initialize current step name with current function name
    state['current_step_name'] = initialize_mission_node.__name__

    logger.info(f"Executing {state['current_step_name']}")

    try:
        state = await _initialize_mission(state, config)
    except Exception as e:
        logger.error(f"Error in initialize_mission_node: {e}", exc_info=True)
        state["critical_error_message"] = f"Error in initialize_mission_node: {e}"
        state['mission_context'].status = "ERROR"
        return state

    return state

async def _initialize_mission(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:

    # Gather services and config
    configurable = config["configurable"]
    app_config: AppConfig = configurable["app_config"]
    llm_service: LlmPromptService = configurable["llm_prompt_service"]

    # Load mission spec content
    mission_spec_content: str = _load_mission_spec_content_from_file(app_config)

    # Perform LLM call
    mission_title: str = await _extract_mission_title(llm_service, app_config, mission_spec_content)

    # Update mission context
    mission_context = state.get('mission_context')
    mission_context.mission_spec_content = mission_spec_content
    mission_context.mission_title = mission_title
    mission_context.status = "IN_PROGRESS"

    return state

def _load_mission_spec_content_from_file(app_config: AppConfig) -> str:
    mission_spec_path = app_config.mission_description_path
    logger.info(f"Loading mission spec from: {mission_spec_path}")
    try:
        with open(mission_spec_path, "r", encoding="utf-8") as f:
            mission_spec_content = f.read()
    except Exception as e:
        raise RuntimeError(f"Error reading mission spec file {mission_spec_path}: {e}")
    return mission_spec_content

async def _extract_mission_title(llm_service: LlmPromptService, app_config: AppConfig, mission_spec_content: str) -> str:
    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": get_user_prompt(mission_spec_content)}
    ]
    try:
        extracted_data = await llm_service.get_structured_output(
            messages=messages,
            output_pydantic_model_type=MissionData,
            llm_model_name=app_config.mission_title_extraction_model
        )
        if extracted_data and extracted_data.mission_title:
            logger.info(f"Successfully extracted mission title: {extracted_data.mission_title}")
            return extracted_data.mission_title
        else:
            raise RuntimeError("Extracted data is None or does not contain mission_title.")
    except Exception as e:
        raise RuntimeError(f"Failed to extract mission title from mission spec: {e}")
