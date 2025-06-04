## General Instructions:
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

  - File Structure:
    - Always put paths and other hardcoded strings into `config.py` and update `config.yml` appropriately
    - Always put prompts in the correct `prompt.py` instead of inlining them in the code

  - If unsure about code to write, implement to the best of your ability making assumptions where necessary. There is no need to add comments with different implementation options, I am going to delete them anyways.

## Task Instructions

You are an expert software architect. You have a couple of jobs:

1. Explain how the current code works related to the problem outlined below.
2. Brainstorm 2-3 solutions to the problem below. After that, brainstorm 2 radically different approaches.
3. Write this brainstorming to a temporary file that's appropriately named in ai-docs/planning/<insert-next-number>_<insert-appropriate-folder-name>/brainstorming.md   ex folder name: `01_task-name` - Make sure to look at the list of folders we already have to figure out the next number to use for this folder name.
  IMPORTANT - Do not brainstorm any tests, tests are not needed for this project

When those are completed, assume the role of a critical CTO for the company and critique the brainstorming options. You have a couple different jobs:

1. List out the pros and cons and give each one a grade from A-F (A is excellent, F is fail just like in school).
2. Make a recommendation of which approach is best.
3. Generate a final solution that uses that final version, with changes to mitigate the pros and turn the plan from whatever grade it was into an A+ grade. If it makes sense, integrate elements from other solutions that were proposed that seem valuable. Write the entire critique to ai-docs/planning/<insert-appropriate-folder-name>/critique.md
4. Generate a spec for an ai coding agent containing the follow sections - Problem, Solution, High Level Implementation Plan. Use Sparse Priming Representation for this spec. Write this spec to a temporary file that's appropriately named ai-docs/planning/<insert-appropriate-folder-name>/spec.md
  IMPORTANT - Do not include testing in your critique, tests are not needed for this project

When the spec is completed, assume the role of a software engineer that has a single job:
1. Implement the changes described in the new spec file

When the spec is implemented, assume the role of the CTO again and do the following:
1. Follow the same CTO process to critique the code.
2. Add your critique to a file called `ai-docs/planning/<insert-appropriate-folder-name>/critique-code.md`

When the code critique is completed, assume the role of a software engineer again that has a single job:
1. Implement the changes suggested by the CTO.

Here's the problem we are trying to solve:

```
Working Directory: `army-infantry`

Status:

- Added the file scaffolding for the army-infantry folder. 
- Implemented - Graph builder and graph state
- Implemented - `army-infantry\src\nodes\initialize_mission\node.py`

Task to Implement:

1. Update `army-infantry\src\nodes\initialize_mission\node.py` to also extract a branch name. The prompt, model, node, graph_state and possibly more code will need to be updated for this.
2. Implement the `git_branch` and `git_checkout_original_branch` nodes. Make sure to utilize the correct set of files with node.py, prompts.py, config.py, config.yml, etc. Make sure to use the branch name extracted in the `initialize_mission` node that should be passed via the graph_state.

Here's guidance on how to construct branch names:

Use the format `<type>/<description-with-dashes>`. Use these for <type>: fix, feature, polish. Ensure the branch name - Starts with the appropriate prefix. - Is in the imperative mood (e.g., \"add-feature\" not \"added-feature\" or \"adding-feature\"). - Does not exceed 50 characters.


Refer to the following planning files for more context:
- `ai-docs\planning\01_infantry-full\01_vision-statement.md`
- `ai-docs\planning\01_infantry-full\03_tech-design-considerations.md`
- `ai-docs\planning\01_infantry-full\04_feature-list.md`
```