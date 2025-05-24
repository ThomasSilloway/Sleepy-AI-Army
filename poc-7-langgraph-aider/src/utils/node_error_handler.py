import logging
from enum import Enum

# It's assumed WorkflowState is a TypedDict or a class where keys are known,
# but for this implementation, we'll treat it as a dict.

class NodeOperation(Enum):
    GENERAL_VALIDATION = "General Validation"
    LLM_CALL = "LLM Call"
    FILE_WRITE = "File Write"
    CHANGELOG_UPDATE = "Changelog Update"
    GIT_COMMIT = "Git Commit"
    UNEXPECTED_ERROR = "Unexpected Error" # Added as per spec suggestion for outermost try-except
    # ... other common operations can be added as needed

# Defines state keys that are often set to a default 'error' value (e.g., False, None)
# These are general defaults; operation-specific logic can override or add to these.
DEFAULT_ERROR_STATE_UPDATES = {
    # Flags that might be set to False on many types of errors
    "is_manifest_generated": False,
    "is_changelog_entry_added": False,
    # Data fields that might be cleared
    "manifest_data": None,
    # Add other common state fields that should be reset on error if applicable
}

def _apply_state_updates(state: dict, operation: NodeOperation, custom_updates: dict = None):
    """
    Applies a combination of default, operation-specific, and custom state updates.
    The order of precedence for updates on a specific key is:
    1. Custom updates (most specific)
    2. Operation-specific defaults (defined in this function)
    3. General defaults (from DEFAULT_ERROR_STATE_UPDATES)
    """
    updates_to_apply = DEFAULT_ERROR_STATE_UPDATES.copy()

    # Operation-specific default overrides or additions
    if operation == NodeOperation.LLM_CALL:
        updates_to_apply["is_manifest_generated"] = False
        updates_to_apply["manifest_data"] = None
    elif operation == NodeOperation.FILE_WRITE:
        # Example: If a file write is critical for manifest, ensure this is False.
        # This might be redundant if 'is_manifest_generated' is already in DEFAULT_ERROR_STATE_UPDATES,
        # but explicitly stated here for clarity if it's a critical side-effect of this operation failing.
        # If the file write is *for* the manifest, this is crucial.
        # If it's for something else, custom_updates should specify the impact.
        updates_to_apply["is_manifest_generated"] = False # Assuming file write could be the manifest itself
    elif operation == NodeOperation.CHANGELOG_UPDATE:
        updates_to_apply["is_changelog_entry_added"] = False
    elif operation == NodeOperation.UNEXPECTED_ERROR:
        # For truly unexpected errors, we might want to reset more state
        updates_to_apply["is_manifest_generated"] = False
        updates_to_apply["is_changelog_entry_added"] = False
        updates_to_apply["manifest_data"] = None
        # Potentially other fields like 'small_tweak_file_path': None, etc.

    # Apply custom updates, which take the highest precedence
    if custom_updates:
        updates_to_apply.update(custom_updates)

    for key, value in updates_to_apply.items():
        state[key] = value


def handle_operation_error(
    state: dict, # Actually WorkflowState (dict)
    config: dict, # The node's config (dict), for accessing logger, etc.
    operation: NodeOperation,
    exception: Exception,
    custom_error_message_override: str = None, # Override the standard "[Operation] Error: {exception}"
    additional_error_info: str = None, # Appended to the standard error message for context
    custom_state_updates: dict = None,
    set_aider_exit_code: bool = True # Default to setting generic exit code
) -> bool: # Returns True if an error was handled, signaling the node should typically return state
    """
    Handles errors for a node operation, updates state, and logs.
    Returns True if the calling node should typically return its state due to the error.
    """
    # Logger acquisition as per spec:
    # from config if available, else from state['current_step_name'], else 'NodeOperationHandler'
    logger = None
    if config and "logger" in config and config["logger"] is not None:
        logger = config["logger"]
    else:
        logger_name = state.get('current_step_name', 'NodeOperationHandler')
        logger = logging.getLogger(logger_name)

    # Determine the core message part
    core_message_for_log = ""
    if custom_error_message_override:
        core_message_for_log = custom_error_message_override
        # Append actual exception string if it's not redundant and provides detail
        exception_str = str(exception)
        if exception_str and exception_str not in custom_error_message_override:
            core_message_for_log += f" (Exception: {exception_str})"
    else:
        core_message_for_log = f"Error: {str(exception)}"

    # Prepend operation type for the full log message / state['error_message'] entry
    final_error_description_for_state_and_log = f"[{operation.value}] {core_message_for_log}"
    
    if additional_error_info:
        final_error_description_for_state_and_log += f" ({additional_error_info})"

    logger.error(final_error_description_for_state_and_log, exc_info=True)

    existing_error_message = state.get('error_message', "")
    if existing_error_message and not existing_error_message.endswith('\n'): # Use '\n' for newline in f-string or raw string
        existing_error_message += "\n"
    
    state['error_message'] = f"{existing_error_message}{final_error_description_for_state_and_log}"
    
    # Set last_event_summary (this part of the original logic was good)
    if custom_error_message_override:
        state['last_event_summary'] = custom_error_message_override
    elif additional_error_info:
        state['last_event_summary'] = f"Error during {operation.value}: {additional_error_info}."
    else:
        state['last_event_summary'] = f"Error: {operation.value} failed due to {type(exception).__name__}."

    _apply_state_updates(state, operation, custom_state_updates)
    
    # Set aider_last_exit_code if requested and not already set by a more specific error
    if set_aider_exit_code and state.get('aider_last_exit_code') is None:
        state['aider_last_exit_code'] = -1 # Generic error code

    return True # Default to signaling that the node should return
