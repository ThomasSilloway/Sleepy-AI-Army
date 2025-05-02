from typing import Dict, Any
import os
import re
import logging
from ..shared_libraries import constants

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_next_task_number(base_path: str, prefix: str) -> Dict[str, Any]:
    """
    Determines the next sequential task number for a given prefix within a base directory.

    Scans the base_path for directories matching the pattern 'Prefix_NNN_'
    (where NNN is a number) and returns the next available integer sequence number.

    Args:
        base_path: The absolute path to the directory containing task folders (e.g., /path/to/ai-tasks).
        prefix: The task prefix to search for (e.g., "Feature_").

    Returns:
        A dictionary containing:
            'status': 'success' or 'error'.
            'next_number': The next integer sequence number (e.g., 1, 2, 3, ...), or None if an error occurred.
            'message': A confirmation message or error details.
    """
    logging.info(f"Getting next task number for prefix '{prefix}' in base path: {base_path}")
    if not os.path.isdir(base_path):
        logging.error(f"Base path does not exist or is not a directory: {base_path}")
        # As per PRD Edge Case: /ai-tasks/ directory doesn't exist. Mitigation: tool should handle this.
        # Let's assume we should start from 1 if the directory doesn't exist yet.
        logging.warning(f"Base path '{base_path}' not found. Assuming first task, returning 1.")
        return {"status": "success", "next_number": 1, "message": f"Base path not found, starting sequence at 1 for prefix '{prefix}'."}

    max_num = 0
    # Regex to match 'Prefix_NNN_' format and capture NNN
    # Ensure prefix is escaped in case it contains regex special characters
    pattern = re.compile(f"^{re.escape(prefix)}(\\d+)_.*")

    try:
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path):
                match = pattern.match(item)
                if match:
                    num_str = match.group(1)
                    try:
                        num = int(num_str)
                        if num > max_num:
                            max_num = num
                        logging.debug(f"Found matching task folder: {item} with number {num}")
                    except ValueError:
                        logging.warning(f"Could not parse number from folder name: {item}")
                        continue # Skip folders with non-integer numbers after prefix

        next_num = max_num + 1
        logging.info(f"Determined next task number for prefix '{prefix}': {next_num}")
        return {"status": "success", "next_number": next_num, "message": f"Next sequence number for prefix '{prefix}' is {next_num}."}

    except OSError as e:
        logging.error(f"Error listing directory {base_path}: {e}", exc_info=True)
        return {"status": "error", "next_number": None, "message": f"Error accessing base path: {e}"}
    except Exception as e:
        logging.error(f"Unexpected error getting next task number: {e}", exc_info=True)
        return {"status": "error", "next_number": None, "message": f"Unexpected error: {e}"}
