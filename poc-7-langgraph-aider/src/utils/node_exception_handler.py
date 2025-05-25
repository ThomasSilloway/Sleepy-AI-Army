import logging
from functools import wraps
from .custom_exceptions import NodeOperationError, NodeOperation 

# Declarative configuration for error handling
# Based on the A+ solution sketch from critique_v2.txt
NODE_ERROR_CONFIG = {
    NodeOperation.LLM_CALL: {
        "summary_template": "LLM operation failed: {specific_message}",
        "state_updates": {"is_manifest_generated": False, "manifest_data": None}
    },
    NodeOperation.FILE_WRITE: {
        "summary_template": "File writing failed: {specific_message}",
        "state_updates": {"is_manifest_generated": False} 
    },
    NodeOperation.VALIDATION: {
        "summary_template": "Validation failed: {specific_message}",
        # Example: Validation failure might imply manifest cannot be generated
        "state_updates": {"is_manifest_generated": False, "manifest_data": None} 
    },
    NodeOperation.CONFIGURATION: {
        "summary_template": "Node configuration error: {specific_message}",
        "state_updates": {"is_manifest_generated": False, "manifest_data": None}
    },
    NodeOperation.CHANGELOG_UPDATE: {
        "summary_template": "Changelog update failed: {specific_message}",
        "state_updates": {"is_changelog_entry_added": False}
    },
    NodeOperation.GIT_COMMIT: {
        "summary_template": "Git commit failed: {specific_message}",
        "state_updates": {}, # No specific state flags directly, but summary/error_message will be set
        "set_aider_exit_code": False # Git commit failure alone might not halt the entire workflow
    },
    NodeOperation.UNEXPECTED: { 
        "summary_template": "An unexpected error occurred: {specific_message}",
        "state_updates": { # General reset for unexpected errors
            "is_manifest_generated": False, "manifest_data": None, 
            "is_changelog_entry_added": False 
            # Consider other critical flags that should be reset
        }
    }
}

def _get_logger(state: dict, node_config_arg: dict, default_name: str = 'NodeExceptionHandler'):
    """
    Retrieves a logger instance. 
    Prefers logger from node_config_arg if available, else uses current_step_name from state,
    or falls back to a default name.
    """
    # 'node_config_arg' is the 'config' dict passed to the node function.
    if node_config_arg and "logger" in node_config_arg and node_config_arg["logger"] is not None:
        return node_config_arg["logger"]
    
    logger_name = default_name # Fallback logger name
    if state and 'current_step_name' in state and state['current_step_name']:
        logger_name = state['current_step_name']
        
    return logging.getLogger(logger_name)

def _process_error_and_update_state(state: dict, node_config_arg: dict, exception: Exception):
    """
    Processes the caught exception, updates the WorkflowState based on declarative configuration,
    and logs the error.
    """
    logger = _get_logger(state, node_config_arg, '_process_error_and_update_state') 
    
    operation_type = NodeOperation.UNEXPECTED # Default for generic exceptions
    error_config_details = NODE_ERROR_CONFIG[NodeOperation.UNEXPECTED] 
    specific_message = str(exception)
    exception_for_trace = exception # The actual exception to log with its trace

    if isinstance(exception, NodeOperationError):
        operation_type = exception.operation_type
        # Get specific config for this error type, or fall back to UNEXPECTED's config
        error_config_details = NODE_ERROR_CONFIG.get(operation_type, NODE_ERROR_CONFIG[NodeOperation.UNEXPECTED])
        if exception.original_exception: # If our custom error wrapped an original one
            exception_for_trace = exception.original_exception
    
    # Format the log message and the message to be stored in state['error_message']
    error_log_message = f"[{operation_type.value}] {specific_message}"
    
    # Format the summary message for state['last_event_summary']
    summary_for_state = error_config_details.get(
        "summary_template", 
        "Operation failed: {specific_message}" # Default template
    ).format(specific_message=specific_message)

    logger.error(error_log_message, exc_info=exception_for_trace) 

    # Append to existing error messages in state, if any
    existing_error_message = state.get('error_message', "")
    if existing_error_message and not existing_error_message.endswith('\n'):
        existing_error_message += "\n"
    state['error_message'] = f"{existing_error_message}{error_log_message}"
    
    state['last_event_summary'] = summary_for_state

    # Apply specific state updates from the configuration
    if "state_updates" in error_config_details:
        for key, value in error_config_details["state_updates"].items():
            state[key] = value
            
    # Set aider_last_exit_code, allowing override from config
    apply_exit_code = error_config_details.get("set_aider_exit_code", True)
    if apply_exit_code and state.get('aider_last_exit_code') is None:
        state['aider_last_exit_code'] = -1 # Default error code

def handle_node_exceptions(node_function_to_wrap):
    """
    Decorator to wrap node functions for standardized exception handling and state updates.
    """
    @wraps(node_function_to_wrap)
    def wrapper(state: dict, config: dict, *args, **kwargs): 
        # 'state' and 'config' are assumed to be the first two arguments of the node function
        try:
            return node_function_to_wrap(state, config, *args, **kwargs)
        except NodeOperationError as noe: # Catch our defined custom errors
            _process_error_and_update_state(state, config, noe) 
            return state # Return state, as error has been processed
        except Exception as e: # Catch any other unexpected error
            # Wrap generic exceptions in NodeOperationError for consistent processing
            unexpected_error = NodeOperationError(str(e), NodeOperation.UNEXPECTED, original_exception=e)
            _process_error_and_update_state(state, config, unexpected_error)
            return state # Return state
    return wrapper
