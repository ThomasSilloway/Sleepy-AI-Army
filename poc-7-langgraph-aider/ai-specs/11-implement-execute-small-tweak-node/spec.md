# Features: Implement execute_small_tweak_node for Automated File Modification

> Given the Objective, implement every detail of every task, using the referenced architectural documents as the primary guide for implementation specifics.

## Objectives

- Implement the `execute_small_tweak_node` as a new LangGraph node responsible for automated file modifications.
- The node should orchestrate `AiderService` to apply a "Small Tweak" to project files, based on instructions from a `task_description_filepath` specified in the `WorkflowState`. `AiderService` should be configured so `aider` automatically commits successful changes.
- Upon successful execution of the tweak by `AiderService`, the node must invoke `GitService` to retrieve the commit hash, summary, and file change statistics for the applied tweak.
- The node must update `WorkflowState` with the status of the tweak execution (`is_code_change_committed`), the retrieved Git information (`last_change_commit_hash`, `last_change_commit_summary`, `tweak_file_change_stats`), and an appropriate `last_event_summary`.
- After a successful tweak, the node should invoke `ChangelogService` to record the event, including relevant details from the `WorkflowState`.
- The node must handle potential errors from `AiderService` or other services, update `WorkflowState` with error information, and ensure the graph can route to an error handling path.
- Integrate the `execute_small_tweak_node` into the existing LangGraph workflow, connecting it logically after manifest generation and before final success or error paths.

## Context
```
/add poc-7-langgraph-aider\src\nodes\small_tweak_execution.py
/add poc-7-langgraph-aider\src\state.py
/add poc-7-langgraph-aider\src\graph_builder.py
/add poc-7-langgraph-aider\src\nodes\__init__.py

/read-only poc-7-langgraph-aider\ai-docs\planning\02_small-tweak-code-change\05_2-tech_architecture-flow.md
/read-only poc-7-langgraph-aider\src\nodes\manifest_generation.py
/read-only poc-7-langgraph-aider\src\services\aider_service.py
/read-only poc-7-langgraph-aider\src\services\git_service.py
/read-only poc-7-langgraph-aider\src\services\changelog_service.py
/read-only poc-7-langgraph-aider\src\config.py
/read-only poc-7-langgraph-aider\ai-docs\aider-cli-usage.md
/read-only poc-7-langgraph-aider\ai-docs\langgraph-best-practices.md
/read-only ai-docs\CONVENTIONS.md
/read-only poc-7-langgraph-aider\ai-specs\11-implement-execute-small-tweak-node\spec.md
```

## Low-Level Tasks
> Ordered from start to finish. Implement the described functionality, using standard Python features, error handling, and logging as appropriate.

### Task 1: Update `WorkflowState` with Tweak-Related Fields
```
- UPDATE `poc-7-langgraph-aider\src\state.py`:
    - Add new fields to the `WorkflowState` TypedDict to store information related to the "Small Tweak" execution:
        - `is_code_change_committed`: `bool` (to indicate if the tweak was successfully applied)
        - `last_change_commit_hash`: `Optional[str]` (to store the Git commit hash of the tweak)
        - `last_change_commit_summary`: `Optional[str]` (to store the Git commit summary/message)
```

### Task 2: Implement the `execute_small_tweak_node`
```
- CREATE `poc-7-langgraph-aider\src\nodes\small_tweak_execution.py`:
    - Define a new node function `execute_small_tweak_node(state: WorkflowState, config) -> WorkflowState`.
    - The node should retrieve `app_config`, `aider_service`, `git_service`, and `changelog_service` from the `config`'s `configurable` attribute.
    - Retrieve the `task_description_path` from the input `WorkflowState`.
    - Construct the appropriate prompt and command arguments for `AiderService` to execute the "Small Tweak". This involves instructing `aider` to apply changes based on the content of `task_description_path` and to automatically commit successful changes.
    - Invoke `aider_service.execute()` with the constructed command and the `task_description_path` (and any other files `aider` needs to edit or read).
    - Based on the `aider_service.execute()` exit code:
        - If successful (exit code 0):
            - Invoke `git_service.get_last_commit_hash()`, `git_service.get_last_commit_summary()`, and `git_service.get_last_commit_file_stats()` to retrieve details of the commit made by `aider`.
            - Update `WorkflowState`: set `is_code_change_committed` to `True`, populate `last_change_commit_hash`, `last_change_commit_summary` with the retrieved Git information. The last file stats should be appended to `last_change_commit_summary`
            - Prepare a descriptive `last_event_summary` for the successful tweak (e.g., "Small Tweak applied. Commit: <hash> - <summary>").
            - Invoke `changelog_service.record_event_in_changelog()` using the updated state and the event summary. Update `is_changelog_entry_added` in the state.
            - Ensure `error_message` in `WorkflowState` is `None`.
        - If failed (non-zero exit code):
            - Update `WorkflowState`: set `is_code_change_committed` to `False`.
            - Populate `error_message` with details about the `AiderService` failure and the exit code.
            - Set `last_event_summary` to indicate the failure (e.g., "Failed to apply Small Tweak. Aider exit code: <exit_code>").
    - Implement comprehensive error handling for interactions with all services (`AiderService`, `GitService`, `ChangelogService`) and for unexpected issues.
    - Update `current_step_name` in the state to "execute_small_tweak_node".
    - Return the updated `WorkflowState`.
```

### Task 3: Export the New Node
```
- UPDATE `poc-7-langgraph-aider\src\nodes\__init__.py`:
    - Import the `execute_small_tweak_node` function from `src.nodes.small_tweak_execution`.
    - Add `execute_small_tweak_node` to the `__all__` list to make it available for graph construction.
```

### Task 4: Integrate `execute_small_tweak_node` into the Graph
```
- UPDATE `poc-7-langgraph-aider\src\graph_builder.py`:
    - Import the `execute_small_tweak_node` from `src.nodes`.
    - Add `execute_small_tweak_node` as a new node to the `StateGraph`.
    - Modify the graph's conditional routing logic:
        - Adjust the routing from `generate_manifest_node` (or the node that precedes the tweak execution step). On successful completion of the preceding node, route to `execute_small_tweak_node`.
        - Define a new conditional routing function for edges from `execute_small_tweak_node`:
            - If `WorkflowState.error_message` is populated after `execute_small_tweak_node` execution, route to the `error_path` node.
            - Otherwise (if no error), route to the `success_path` node (or to a subsequent node like `update_goal_manifest_node` if it were defined as the next step in a larger workflow). For this spec, assume routing to `success_path` on success.
```
