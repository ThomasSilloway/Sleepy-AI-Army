# Features: Implement Manifest Generation Node Logic

## Objectives

- Refactor `generate_manifest_node` to use `LlmPromptService` for extracting structured data (e.g., goal title, target file path, manifest-specific task description) from the `task-description.md` content.
- Refactor `generate_manifest_node` to use `WriteFileFromTemplateService` to render the `goal-manifest.md` file using a Jinja2 template and the data obtained from the LLM and workflow state.
- Ensure `generate_manifest_node` invokes the existing `ChangelogService` to record the manifest creation event after a successful manifest generation.
- Update `WorkflowState` with the status of manifest generation, changelog entry addition, and any relevant summaries or error messages.
- Use Pydantic model, `ManifestConfigLLM` defined in `poc-7-langgraph-aider\src\pydantic_models\core_schemas.py`, to structure the data expected from the LLM.
- Ensure the `LlmPromptService` is correctly instantiated and made available to the `generate_manifest_node` via `runnable_config` in `main.py`.

## Context
```
/add poc-7-langgraph-aider\src\nodes\manifest_generation.py
/add poc-7-langgraph-aider\src\main.py

/read-only ai-docs/CONVENTIONS.md
/read-only poc-7-langgraph-aider\templates\goal-manifest.j2
/read-only poc-7-langgraph-aider\src\pydantic_models\core_schemas.py
/read-only poc-7-langgraph-aider\ai-docs\planning\03_manifest-generation-pydantic-ai\03_prd.md
/read-only poc-7-langgraph-aider\ai-docs\planning\03_manifest-generation-pydantic-ai\05_1_tech_architecture_overview.md
/read-only poc-7-langgraph-aider\ai-docs\planning\03_manifest-generation-pydantic-ai\05_2-tech_architecture-flow.md
/read-only poc-7-langgraph-aider\src\config.py
/read-only poc-7-langgraph-aider\src\state.py
/read-only poc-7-langgraph-aider\src\services\llm_prompt_service.py
/read-only poc-7-langgraph-aider\src\services\write_file_from_template_service.py
/read-only poc-7-langgraph-aider\src\services\changelog_service.py
/read-only poc-7-langgraph-aider\src\nodes\__init__.py
/read-only poc-7-langgraph-aider\tests\test_write_file_from_template_service.py
/read-only poc-7-langgraph-aider\tests\test_llm_prompt_service.py
```

## Low-Level Tasks
> Ordered from start to finish. Implement the described functionality, using standard Python features, error handling, and logging as appropriate.

### Task 2: Integrate LLM Interaction in Manifest Generation Node
```
- UPDATE `poc-7-langgraph-aider\src\nodes\manifest_generation.py`:
    - Modify the node to retrieve `LlmPromptService` and `AppConfig` from the `runnable_config` passed to the node.
    - Use the `task_description_content` from `WorkflowState` to construct the necessary prompts (e.g., system and user messages) for the `LlmPromptService`. Refer to `tests/test_llm_prompt_service.py` for guidance on constructing prompts.
    - Invoke `llm_prompt_service.get_structured_output()` asynchronously, passing the prepared messages, the `ManifestConfigLLM` model type as the desired output structure, and the Gemini model name specified in `AppConfig` (e.g., `gemini_weak_model_name`). Refer to `tests/test_llm_prompt_service.py` for guidance on invoking `get_structured_output`.
    - Store the returned `ManifestConfigLLM` object or handle potential errors (e.g., LLM call failure, parsing issues) by updating `WorkflowState` with an appropriate error message and summary.
```

### Task 3: Integrate Template-Based File Writing in Manifest Generation Node
```
- UPDATE `poc-7-langgraph-aider\src\nodes\manifest_generation.py`:
    - Retrieve the `WriteFileFromTemplateService` from the `runnable_config`.
    - If the LLM interaction was successful and a `ManifestConfigLLM` object is available:
        - Prepare a context dictionary for the Jinja2 template. This dictionary should include:
            - `goal_title`: from `ManifestConfigLLM.goal_title`.
            - `task_description_for_manifest`: from `ManifestConfigLLM.task_description_for_manifest`.
            - `last_updated_timestamp`: current system timestamp, formatted appropriately (e.g., ISO format).
            - `overall_status`: "New" (as per PRD section 7.2).
            - `current_focus`: full content of `task-description.md` from `WorkflowState.task_description_content`.
            - `artifacts_section_content`: formatted string based on `ManifestConfigLLM.small_tweak_file_path` (e.g., `* [in-progress] path/to/file.ext`). Note: The Pydantic model field is `small_tweak_file_path`, ensure this is used.
            - `ai_questions_list`: an empty list (as per PRD section 7.2).
            - `default_ai_questions_placeholder`: "[Empty by default]" or similar.
            - `human_responses_content`: "NONE" (as per PRD section 7.2).
        - Retrieve `manifest_template_path` and `manifest_output_path` from `WorkflowState`.
        - Call `write_file_from_template_service.render_and_write_file()` with the template path, context, and output path. Refer to `tests/test_write_file_from_template_service.py` for guidance on preparing the context and invoking `render_and_write_file`.
    - Update `WorkflowState.is_manifest_generated` to `True` upon successful file writing, or set an error message if it fails. Update `last_event_summary` accordingly.
```

### Task 4: Integrate Changelog Service Invocation in Manifest Generation Node
```
- UPDATE `poc-7-langgraph-aider\src\nodes\manifest_generation.py`:
    - Retrieve the `ChangelogService` from the `runnable_config`.
    - If `goal-manifest.md` was generated successfully (`WorkflowState.is_manifest_generated` is `True`):
        - Construct a summary message for the changelog, e.g., "Goal Manifest Created: [Goal Title from ManifestConfigLLM]".
        - Call `changelog_service.record_event_in_changelog()`, passing the current `WorkflowState` and the summary message.
    - Update `WorkflowState.is_changelog_entry_added` to `True` if the changelog service reports success, or set an error message if it fails. Update `last_event_summary` accordingly.
```

### Task 5: Ensure Services are Configured in Main Application
```
- UPDATE `poc-7-langgraph-aider\src\main.py`:
    - Import `LlmPromptService` from `src.services`.
    - Instantiate `LlmPromptService` along with other services, passing the `app_config` to its constructor.
    - Add the `LlmPromptService` instance to the `runnable_config` dictionary under the key `"llm_prompt_service"` so it is accessible within the `generate_manifest_node`.
```
