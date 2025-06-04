ALWAYS FOLLOW THESE CONVENTIONS:
 - When adding comments - Single lines of code should get no comments
 - When adding comments - Multiple lines of code should be Concise, Minimal only - 1 line max, 80 characters max 
 - `typing.Dict` is deprecated, use `dict` instead
 - `typing.List` is deprecated, use `list` instead
 - `typing.Type` is deprecated, use `type` instead
 - Use solid object oriented coding practices
 - Do not duplicate code, prefer to use functions and classes that re-use code
 - Prefer simple, elegant code with less lines rather than duplicated, complex code that maybe has one or two differences.
   - Example BAD: 
     ```
	try:
        state = await _initialize_mission(state, config)
    except GitServiceError as e:
        _message = f"GitService error: {e.stderr or str(e)}"
        logger.error(f"Error in {state['current_step_name']}: {_message}", exc_info=True)
        mission_context.status = "ERROR"
        mission_context.mission_errors.append(StructuredError(
            node_name=state['current_step_name'], message=_message,
            details={"error_type": "GitServiceError", "stderr": e.stderr}, 
            timestamp=timestamp
        ))
        state["critical_error_message"] = _message
    except ValueError as e: # Catch config errors like missing repo_path from _initialize_mission
        _message = f"Configuration or value error: {str(e)}"
        logger.error(f"Error in {state['current_step_name']}: {_message}", exc_info=True)
        mission_context.status = "ERROR"
        mission_context.mission_errors.append(StructuredError(
            node_name=state['current_step_name'], message=_message,
            details={"error_type": "ValueError"}, 
            timestamp=timestamp
        ))
        state["critical_error_message"] = _message
    except RuntimeError as e: # Catch runtime errors from _extract_mission_data or _load_mission_spec
        _message = f"Runtime error: {str(e)}"
        logger.error(f"Error in {state['current_step_name']}: {_message}", exc_info=True)
        mission_context.status = "ERROR"
        mission_context.mission_errors.append(StructuredError(
            node_name=state['current_step_name'], message=_message,
            details={"error_type": "RuntimeError"}, 
            timestamp=timestamp
        ))
        state["critical_error_message"] = _message
    except Exception as e: # Catch-all for any other unexpected errors
        _message = f"An unexpected error occurred: {str(e)}"
        logger.error(f"Error in {state['current_step_name']}: {_message}", exc_info=True)
        mission_context.status = "ERROR"
        mission_context.mission_errors.append(StructuredError(
            node_name=state['current_step_name'], message=_message,
            details={"error_type": type(e).__name__}, 
            timestamp=timestamp
        ))
        state["critical_error_message"] = _message
		``` 

   - Example GOOD:
   ```
    try:
        state = await _initialize_mission(state, config)
    except Exception as e:
        logger.error(f"Error in initialize_mission_node: {e}", exc_info=True)
        state["critical_error_message"] = f"Error in initialize_mission_node: {e}"
        state['mission_context'].status = "ERROR"
        return state
	```

 File Structure:
  - Always put paths and other hardcoded strings into `config.py` and update `config.yml` appropriately
  - Always put prompts in the correct `prompt.py` instead of inlining them in the code



