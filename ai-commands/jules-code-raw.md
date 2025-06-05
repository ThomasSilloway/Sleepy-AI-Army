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

 - File Structure:
    - Always put paths and other hardcoded strings into `config.py` and update `config.yml` appropriately
    - Always put prompts in the correct `prompt.py` instead of inlining them in the code

  - If unsure about code to write, implement to the best of your ability making assumptions where necessary. There is no need to add comments with different implementation options, I am going to delete them anyways.

## Code Examples
### Example BAD
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

### Example GOOD
```
    try:
        state = await _initialize_mission(state, config)
    except Exception as e:
        logger.error(f"Error in initialize_mission_node: {e}", exc_info=True)
        state["critical_error_message"] = f"Error in initialize_mission_node: {e}"
        state['mission_context'].status = "ERROR"
        return state
```

### Example BAD #2
```
# army-infantry/src/nodes/git_branch/node.py
import logging
from typing import Any
import datetime # For timestamping errors (used in preliminary checks)

from ...app_config import AppConfig
from ...graph_state import WorkflowState, MissionContext, StructuredError # Used in preliminary checks
from ...services.git_service import GitService, GitServiceError # Used in core logic

logger = logging.getLogger(__name__)

async def git_branch_node(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    """
    Creates and checks out a new Git branch based on the generated_branch_name
    stored in the mission_context.
    """
    state['current_step_name'] = git_branch_node.__name__
    node_function_name = state['current_step_name'] # For error messages
    logger.info(f"Executing {node_function_name}")
    
    mission_context: MissionContext = state['mission_context']
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat() # For preliminary checks

    # Preliminary checks - these can remain specific as they are preconditions
    # and StructuredError is already imported and used for them.
    configurable = config["configurable"]
    app_config: AppConfig = configurable["app_config"]
    
    if not hasattr(app_config, 'repo_path') or not app_config.repo_path:
        _message = f"Repository path 'repo_path' not configured in AppConfig for {node_function_name}."
        logger.error(_message)
        mission_context.status = "ERROR"
        mission_context.mission_errors.append(StructuredError(
            node_name=node_function_name, message=_message, details=None, timestamp=timestamp
        ))
        state["critical_error_message"] = _message
        return state
    
    # GitService can be instantiated here or passed if already available in config
    git_service: GitService = configurable.get("git_service")
    if not git_service:
        logger.info(f"GitService not found in configurable for {node_function_name}, creating new instance.")
        git_service = GitService(repo_path=app_config.repo_path)
    
    generated_branch_name = mission_context.generated_branch_name

    if not generated_branch_name:
        _message = f"Generated branch name is not set in mission_context for {node_function_name}."
        logger.error(_message)
        mission_context.status = "ERROR"
        mission_context.mission_errors.append(StructuredError(
            node_name=node_function_name, message=_message, details=None, timestamp=timestamp
        ))
        state["critical_error_message"] = _message
        return state

    # Core logic for Git operations with simplified top-level error handling
    try:
        logger.info(f"Attempting to create and checkout branch: {generated_branch_name}")
        
        try:
            # Attempt to create and checkout the new branch using 'git checkout -b'
            await git_service.checkout_branch(generated_branch_name, create_new=True)
            logger.info(f"Successfully created and checked out new branch: {generated_branch_name}")
        except GitServiceError as e_create:
            # Idempotency check: if 'checkout -b' failed because branch already exists
            already_exists_indicators = ["a branch named", "already exists"] # Case-insensitive check
            error_text_lower = (e_create.stderr or str(e_create)).lower()
            is_already_exists_error = any(indicator in error_text_lower for indicator in already_exists_indicators)

            if is_already_exists_error:
                logger.warning(
                    f"Branch '{generated_branch_name}' already exists (create_new=True failed). Attempting to checkout existing branch."
                )
                # Attempt to checkout the existing branch without create_new flag
                await git_service.checkout_branch(generated_branch_name, create_new=False)
                current_branch_checkout = await git_service.get_current_branch() # Verify current branch
                if current_branch_checkout == generated_branch_name:
                    logger.info(f"Successfully checked out existing branch: {generated_branch_name}")
                else:
                    # This is an unexpected state if checkout was supposed to succeed
                    raise GitServiceError(
                        f"Verification failed: Expected to be on branch '{generated_branch_name}' after checkout, but on '{current_branch_checkout}'.",
                        stderr="Post-checkout branch mismatch" 
                    ) # This will be caught by the outer generic Exception handler
            else:
                # If it's a GitServiceError but not "already exists", re-raise to be caught by outer handler
                raise
        
        # If all successful, mission_context.status remains as is (e.g., IN_PROGRESS)

    except Exception as e: # Single generic exception handler for the core Git logic block
        error_message = f"Error in {node_function_name}: {str(e)}"
        logger.error(error_message, exc_info=True)
        
        mission_context.status = "ERROR"
        # As per simplified pattern, do not add StructuredError to mission_context.mission_errors here for this main block.
        
        state["critical_error_message"] = error_message
        
    return state

```

### Example Good #2
```
import logging
from typing import Any

from ...graph_state import MissionContext, WorkflowState
from ...services.git_service import GitService

logger = logging.getLogger(__name__)

async def git_branch_node(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    state['current_step_name'] = git_branch_node.__name__
    logger.info(f"Executing {state['current_step_name']}")

    mission_context: MissionContext = state['mission_context']

    try:
        state = await _git_branch(state, config)
    except Exception as e:
        error_message = f"Error in {state['current_step_name']}: {str(e)}"
        logger.error(error_message, exc_info=True)

        mission_context.status = "ERROR"
        state["critical_error_message"] = error_message

    return state

async def _git_branch(state: WorkflowState, config: dict[str, Any]) -> WorkflowState:
    """
    Creates and checks out a new Git branch based on the generated_branch_name
    stored in the mission_context.
    """
    mission_context: MissionContext = state['mission_context']

    configurable = config["configurable"]
    git_service: GitService = configurable.get("git_service")

    generated_branch_name = mission_context.generated_branch_name

    # Core logic for Git operations with simplified top-level error handling
    try:
        logger.info(f"Attempting to create and checkout branch: {generated_branch_name}")

        # Attempt to create and checkout the new branch using 'git checkout -b'
        await git_service.checkout_branch(generated_branch_name, create_new=True)
        logger.overview(f"Checked out branch: {generated_branch_name}")
    except Exception as e:
        raise RuntimeError(f"Failed to create and checkout branch '{generated_branch_name}': {e}")

    return state

```

## Task instructions

Refer to the following planning files for more context:
- `ai-docs\planning\01_infantry-full\01_vision-statement.md`
- `ai-docs\planning\01_infantry-full\03_tech-design-considerations.md`
- `ai-docs\planning\01_infantry-full\04_feature-list.md`

Update `army-general` for asyncio `git-service.py` Usage:

- **Mission ID:** `general_update_git_service_usage_01`

## Objective

Modify `army-general`'s codebase, primarily within `army-general/src/main.py` and any other files that directly invoke methods from `army-general/src/services/git_service.py`, to correctly use the `async` nature of the `git_service.py`. This involves ensuring that all calls to async methods in `git_service.py` are properly `await`ed.

## Scope

- Identify all call sites of `git_service.py` methods within `army-general`.
- Update these call sites to use `await` where the called method is `async`.
- Ensure that the calling methods themselves are `async` if they weren't already, and propagate `async` up the call stack as necessary.
- The `git-service.py` itself (`army-general/src/services/git_service.py`) is already `async` and does not need to be modified for this mission.

## Key Files to Modify (anticipated)

- `army-general/src/main.py`
- Potentially other service or utility files within `army-general/src/` if they use `git_service.py`.

## Acceptance Criteria

- All calls to `git_service.py` methods that are asynchronous are `await`ed.
- `army-general` remains fully functional with these changes (existing tests should pass, or be updated if their structure is impacted by async changes).
- No linting errors related to `async/await` usage are present in the modified files.

## Commander's Notes

This mission is a prerequisite for other `army-general` refactoring tasks that depend on correct `async` operation of git commands, such as branch checking and cleanup operations. Focus on making the existing callsites compliant with `asyncio`.

