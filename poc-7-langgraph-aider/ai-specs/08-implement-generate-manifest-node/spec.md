# Features: Implement `generate_manifest_node` for Goal Manifest Creation

> Given the Objective, implement every detail of every task, using the referenced architectural documents as the primary guide for implementation specifics.

## Objectives

- Implement the `generate_manifest_node` LangGraph node as defined in the technical architecture.
- This node will orchestrate `AiderService` to generate a goal manifest file based on the task description and relevant templates.
- The node will update `WorkflowState` with the outcome of the manifest generation, including status flags, file paths, and error messages if any.
- Upon successful manifest generation, the node will invoke `ChangelogService` to record the event.
- The node will correctly handle and report errors encountered during the manifest generation process, allowing the graph to route to an error handler.

## Context
```
/add poc-7-langgraph-aider\src\nodes\manifest_generation.py
/add poc-7-langgraph-aider\src\graph_builder.py
/read-only poc-7-langgraph-aider\src\state.py

/read-only poc-7-langgraph-aider\src\config.py
/read-only poc-7-langgraph-aider\src\services\aider_service.py
/read-only poc-7-langgraph-aider\src\services\changelog_service.py
/read-only poc-7-langgraph-aider\src\main.py
/read-only poc-7-langgraph-aider\src\nodes\initialization.py
/read-only poc-7-langgraph-aider\ai-docs\planning\01_manifest-and-changelist\05_1_tech_architecture_overview.md
/read-only poc-7-langgraph-aider\ai-docs\planning\01_manifest-and-changelist\05_2-tech_architecture-flow.md
/read-only poc-7-langgraph-aider\ai-docs\planning\01_manifest-and-changelist\05_3-tech_architecture-file-structure.md
/read-only poc-7-langgraph-aider\ai-docs\aider-cli-usage.md
/read-only poc-7-langgraph-aider\ai-docs\langgraph-best-practices.md
/read-only ai-docs\CONVENTIONS.md
```

## Low-Level Tasks
> Ordered from start to finish. Implement the described functionality, using standard Python features, error handling, and logging as appropriate.

### Task 1: Define Core `generate_manifest_node` Logic
```
- UPDATE `poc-7-langgraph-aider\src\nodes\manifest_generation.py`:
    - Update Python function `generate_manifest_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState`.
    - Retrieve `app_config`, `aider_service` from the `config` argument. using `nodes\initialization.py` as an example
    - Set `state['current_step_name']` to an appropriate value (e.g., "generate_manifest_node").
    - Construct the detailed `aider` prompt for manifest generation. This prompt should utilize:
        - `state['task_description_content']`.
        - The manifest template path (derived from `app_config.manifest_template_filename` and `state['workspace_folder_path']`).
        - The manifest output path (`state['manifest_output_path']`).
    - Prepare the arguments for `AiderService.execute()`, including the prompt and the target manifest file to be added/edited. Use the `changelog_service.py` as an example for how to specify read-only files
    - Invoke `aider_service.execute()` with the prepared arguments.
    - Store the exit code from `aider_service.execute()` in `state['aider_last_exit_code']`.
```

### Task 2: Handle Successful Manifest Generation in `generate_manifest_node`
```
- UPDATE `poc-7-langgraph-aider\src\nodes\manifest_generation.py`:
    - Within `generate_manifest_node`, after invoking `AiderService.execute()`:
    - Check if the `aider` command was successful (e.g., exit code 0) and if the manifest file (specified by `state['manifest_output_path']`) exists.
    - If successful:
        - Set `state['is_manifest_generated'] = True`.
        - Set `state['last_event_summary']` to a message indicating successful manifest generation (e.g., f"Goal Manifest generated: {state['generated_manifest_filepath']}").
        - Retrieve `changelog_service` from the `config` argument.
        - Invoke `changelog_service.record_event_in_changelog(current_workflow_state=state, preceding_event_summary=state['last_event_summary'])`.
        - Update `state['is_changelog_entry_added']` based on the boolean return value of `record_event_in_changelog()`.
        - Log the successful manifest generation and the outcome of the changelog update attempt (e.g., whether the changelog entry was added).
```

### Task 3: Handle Manifest Generation Failure in `generate_manifest_node`
```
- UPDATE `poc-7-langgraph-aider\src\nodes\manifest_generation.py`:
    - Within `generate_manifest_node`, if the `aider` command for manifest generation fails (e.g., non-zero exit code or manifest file does not exist):
        - Set `state['is_manifest_generated'] = False`.
        - Set `state['error_message']` to a descriptive message detailing the manifest generation failure.
        - Set `state['last_event_summary']` to reflect the manifest generation failure (e.g., "Failed to generate Goal Manifest.").
        - Log the failure.
        - Ensure the node returns the updated state, which will be used by conditional edges in the graph to route to an error handler.
```

### Task 4: Integrate `generate_manifest_node` into the Graph
```
- UPDATE `poc-7-langgraph-aider\src\graph_builder.py`:
    - Import `generate_manifest_node` from `src.nodes.manifest_generation`.
    - Add `generate_manifest_node` to the `StateGraph` instance using `graph_builder.add_node("generate_manifest_node", generate_manifest_node)`.
    - Update the graph's edges:
        - Add an edge from the `validate_inputs_node` to `generate_manifest_node` for the success path of input validation.
        - Add conditional edges from `generate_manifest_node`:
            - If `state.get('error_message')` has a value after `generate_manifest_node` execution, transition to the `error_handler_node`.
            - Otherwise (on success), transition to the `success_node` (or the next appropriate node in the workflow, which for this PoC is likely the success node).
```
