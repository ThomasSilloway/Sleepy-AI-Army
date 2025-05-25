# Features: Implement LLM Services for Manifest Data Extraction

> Given the Objective, implement every detail of every task, using the referenced architectural documents as the primary guide for implementation specifics.

## Objectives
- Define the `ManifestConfigLLM` Pydantic model to structure data extracted by the LLM for goal manifest generation.
- Implement the `LlmPromptService` to interact with Google Gemini (via `pydantic-ai`) for populating the `ManifestConfigLLM`.
- Ensure `LlmPromptService` can accept prompts, utilize a configured Gemini model, and return structured, validated Pydantic model instances.
- Update the application configuration (`AppConfig`) to support the new `LlmPromptService` requirements, such as specifying the Gemini model name.

## Context
```
/add poc-7-langgraph-aider\src\pydantic_models\__init__.py
/add poc-7-langgraph-aider\src\pydantic_models\core_schemas.py
/add poc-7-langgraph-aider\src\services\llm_prompt_service.py
/add poc-7-langgraph-aider\src\services\__init__.py
/add poc-7-langgraph-aider\src\config.py

/read-only poc-7-langgraph-aider\ai-docs\planning\03_manifest-generation-pydantic-ai\05_1_tech_architecture_overview.md
/read-only poc-7-langgraph-aider\ai-docs\planning\03_manifest-generation-pydantic-ai\05_2-tech_architecture-flow.md
/read-only poc-7-langgraph-aider\ai-docs\planning\03_manifest-generation-pydantic-ai\05_3-tech_architecture-file-structure.md
/read-only poc-7-langgraph-aider\ai-docs\planning\03_manifest-generation-pydantic-ai\03_prd.md
/read-only poc-7-langgraph-aider\ai-docs\pydantic-ai-sample.py
/read-only poc-7-langgraph-aider\ai-docs\pydantic-ai-best-practices.md
/read-only poc-7-langgraph-aider\src\config.py
/read-only poc-7-langgraph-aider\src\services\__init__.py
/read-only poc-7-langgraph-aider\config.yml
/read-only ai-docs\CONVENTIONS.md
```

## Low-Level Tasks
> Ordered from start to finish. Implement the described functionality, using standard Python features, error handling, and logging as appropriate.

### Task 1: Establish Data Structures for LLM-driven Manifest Configuration
```
- UPDATE `poc-7-langgraph-aider\src\pydantic_models\core_schemas.py`:
    - Define a Pydantic model (`ManifestConfigLLM`) to represent the structured information (e.g., goal title, target file path, task description for manifest) that the LLM will extract or infer. Refer to `05_2-tech_architecture-flow.md` for field details.
- UPDATE `poc-7-langgraph-aider\src\pydantic_models\__init__.py`:
    - Ensure the new `ManifestConfigLLM` Pydantic model (and any associated sub-models) are correctly exposed for import from the `src.pydantic_models` package.
```

### Task 2: Develop a Service for LLM-based Structured Data Extraction
```
- UPDATE `poc-7-langgraph-aider\src\services\llm_prompt_service.py`:
    - Create the `LlmPromptService` class, responsible for orchestrating calls to the Gemini LLM using `pydantic-ai`.
    - Implement the `__init__` method to accept an `AppConfig` instance for configuration (e.g., Gemini model name).
    - Implement the `get_structured_output` asynchronous method. This method should take messages (prompts), an output Pydantic model type, an optional LLM model name, and optional model parameters. It should return an instance of the provided Pydantic model populated by the LLM, or handle errors appropriately. Refer to the interface defined in `05_2-tech_architecture-flow.md`.
- UPDATE `poc-7-langgraph-aider\src\services\__init__.py`:
    - Add `LlmPromptService` to the `__all__` list to make it accessible for instantiation and use within the application (e.g., in `main.py` and passed via `runnable_config`).
```

### Task 3: Configure Application for LLM Model Selection
```
- UPDATE `poc-7-langgraph-aider\src\config.py`:
    - Modify the `AppConfig` Pydantic model to include a new configuration field (e.g., `gemini_text_model_name`) for specifying the Gemini model to be used by the `LlmPromptService`. This aligns with the requirements outlined in `05_2-tech_architecture-flow.md`.
```
