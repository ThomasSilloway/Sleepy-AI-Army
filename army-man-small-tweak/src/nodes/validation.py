import logging
from pathlib import Path

from src.config import AppConfig
from src.state import WorkflowState

logger = logging.getLogger(__name__)

def validate_inputs_node(state: WorkflowState, config) -> WorkflowState:
    """
    Validates the existence of necessary input files and reads the
    task description content into the WorkflowState.
    """
    state['current_step_name'] = "validate_inputs_node"

    logger.info(f"[Input Validation] Starting input validation.")

    # File paths to check
    paths_to_check = {
        "Task Description": state.get('task_description_path'),
        "Manifest Template": state.get('manifest_template_path'),
    }

    for file_description, file_path_str in paths_to_check.items():
        if not file_path_str:
            error_msg = f"[Input Validation] {file_description} path is not set in WorkflowState."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = f"Validation Error: {error_msg}"
            return state

        file_path = Path(file_path_str)
        if not file_path.is_file():
            error_msg = f"[Input Validation] {file_description} file not found at: {file_path}"
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = f"Validation Error: {error_msg}"
            return state
        logger.debug(f"[Input Validation] Found {file_description} file: {file_path}")

    # All required files exist, now read task_description_content
    try:
        task_desc_path_str = state.get('task_description_path')
        # This path was already validated above, so it should exist.
        task_description_content = Path(task_desc_path_str).read_text()
        state['task_description_content'] = task_description_content
        logger.debug(f"[Input Validation] Successfully read task description content.")
    except IOError as e:
        error_msg = f"[Input Validation] Error reading task description file {state.get('task_description_path')}: {e}"
        logger.error(error_msg)
        state['error_message'] = error_msg
        state['last_event_summary'] = f"Validation Error: {error_msg}"
        return state
    except Exception as e: # Catch any other unexpected errors during file read
        error_msg = f"[Input Validation] Unexpected error reading task description file {state.get('task_description_path')}: {e}"
        logger.error(error_msg)
        state['error_message'] = error_msg
        state['last_event_summary'] = f"Validation Error: {error_msg}"
        return state

    # If all checks passed
    success_summary = "Input files validated successfully."
    state['last_event_summary'] = success_summary
    logger.info(f"[Input Validation] {success_summary}")
    state['error_message'] = None  # Ensure error_message is None on success
    return state
