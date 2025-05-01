# Tool for processing the backlog file
import logging
import os
from typing import Dict, Any, Optional

# Critical import for accessing actions like escalate
from google.adk.tools import ToolContext

# Import constants from the shared library using relative path
from ...shared_libraries import constants

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# This function MUST accept tool_context to signal escalation
def process_backlog_file(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Reads the first line from the backlog file, removes it, and returns it.

    If the file is empty or doesn't exist, it signals for escalation via the
    tool_context to terminate the parent LoopAgent. It requires ToolContext.

    Args:
        tool_context: The ADK ToolContext, automatically injected by the framework.
                      Crucial for setting actions.escalate.

    Returns:
        A dictionary containing:
        - 'status': 'ok', 'empty', or 'error'
        - 'task_description': The content of the first line (if status is 'ok')
        - 'message': A descriptive message about the outcome or error.
    """
    file_path = constants.BACKLOG_FILE_PATH
    logger.info(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Processing backlog file: {file_path}")

    # --- Context Check ---
    if tool_context is None:
         logger.error(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: ToolContext was not provided. Cannot escalate.")
         # Cannot escalate without context, return error status but loop might continue incorrectly.
         return {"status": "error", "message": "Critical Error: ToolContext is missing."}

    try:
        # --- File Check ---
        # Check if the file exists and is not empty
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            logger.info(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Backlog file is empty or does not exist at '{file_path}'. Signaling escalation.")
            # Signal to the LoopAgent to stop
            tool_context.actions.escalate = True
            return {"status": "empty", "message": "Backlog is empty or not found."}

        # --- Read and Modify File ---
        lines = []
        try:
            # Ensure the directory exists before trying to open the file
            # This check is redundant if os.path.exists passed, but good practice
            file_dir = os.path.dirname(file_path)
            if file_dir and not os.path.exists(file_dir):
                 logger.warning(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Directory '{file_dir}' for backlog file does not exist. Attempting to read anyway.")
                 # Proceed to let the open() call handle the FileNotFoundError if the dir is truly missing

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            # This case should ideally be caught by the initial os.path.exists check,
            # but handle it defensively.
            logger.info(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Backlog file not found during read at '{file_path}'. Signaling escalation.")
            tool_context.actions.escalate = True
            return {"status": "empty", "message": "Backlog file not found."}


        if not lines: # Double-check if file was empty after opening (e.g., race condition or empty file)
             logger.info(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Backlog file at '{file_path}' contained no lines after opening. Signaling escalation.")
             tool_context.actions.escalate = True
             return {"status": "empty", "message": "Backlog file is empty."}

        # Get the first line and remove leading/trailing whitespace (incl. newline)
        first_line = lines[0].strip()
        remaining_lines = lines[1:] # Get all lines except the first

        # Rewrite the file with the remaining lines
        # Ensure the directory exists before writing
        file_dir = os.path.dirname(file_path)
        if file_dir and not os.path.exists(file_dir):
            try:
                os.makedirs(file_dir)
                logger.info(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Created directory '{file_dir}' for backlog file.")
            except OSError as e:
                 logger.error(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Failed to create directory '{file_dir}': {e}. Cannot write file.")
                 tool_context.actions.escalate = True # Escalate as we cannot modify the file
                 return {"status": "error", "message": f"Failed to create directory for backlog file: {e}"}


        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(remaining_lines)
            # Ensure newline at end of file if remaining_lines is not empty
            if remaining_lines and not remaining_lines[-1].endswith('\n'):
                 f.write('\n')
            # If remaining_lines is empty, the file should be empty (no newline needed)


        logger.info(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Successfully processed task: '{first_line}'")
        # IMPORTANT: Ensure escalation is FALSE if a task was processed
        tool_context.actions.escalate = False
        return {"status": "ok", "task_description": first_line, "message": "Task processed successfully."}

    except Exception as e:
        logger.error(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Error processing backlog file {file_path}: {e}", exc_info=True)
        # Signal escalation on error to prevent potential infinite loops
        if tool_context: # Check again in case error happened before context check
             tool_context.actions.escalate = True
        return {"status": "error", "message": f"An error occurred: {str(e)}"}