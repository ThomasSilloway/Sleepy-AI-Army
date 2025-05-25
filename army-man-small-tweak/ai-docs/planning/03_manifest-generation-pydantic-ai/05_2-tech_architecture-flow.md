## 2. Component Breakdown (Revised)

The system consists of existing components and will be augmented by new services and models. The core changes will occur within the `generate_manifest_node` and involve the introduction of two new service classes.

### 2.1 Existing Core Components (from `src` directory)

* **LangGraph Orchestrator (`src/graph_builder.py`, `src/main.py`):**
    * **Description:** The existing LangGraph `StateGraph` that defines the workflow, including nodes like `initialize_workflow`, `validate_inputs`, `generate_manifest_node`, `execute_small_tweak`, `error_path`, and `success_path`.
    * **Responsibilities:** Manages `WorkflowState`, orchestrates node execution, and handles data flow and conditional logic.
    * **Note:** This project primarily impacts the `generate_manifest_node`.

* **Workflow State (`src/state.py` - `WorkflowState` TypedDict):**
    * **Description:** The TypedDict defining the structure of the data that flows through the LangGraph.
    * **Responsibilities:** Holds all dynamic data for the workflow, such as file paths, content, status flags, and error messages.
    * **Note:** Will be utilized by the new services operating within `generate_manifest_node`.

* **Application Configuration (`src/config.py` - `AppConfig` Pydantic Model):**
    * **Description:** Pydantic model for loading and providing access to application configurations from `config.yml`.
    * **Responsibilities:** Supplies settings like file paths (e.g., `goal_root_path`, `workspace_root_path`, `manifest_template_filename`, `task_description_filename`), model names (e.g., `changelog_aider_model`, and will need one for the Gemini model), and log settings. The Gemini API key itself is expected to be loaded from an environment variable in `main.py`.
    * **Note:** A new field for the Gemini model name (e.g., `gemini_text_model_name`) will be required in `AppConfig`.

* **Services (`src/services/`):**
    * **`AiderService` (`aider_service.py`):** Existing service to interact with the `aider` CLI tool.
    * **`ChangelogService` (`changelog_service.py`):** Existing service that uses `AiderService` to create/update `changelog.md`. This service will be invoked by the modified `generate_manifest_node` after successful manifest generation.
    * **`GitService` (`git_service.py`):** Existing service for Git operations. (Less directly involved in *this specific feature* but part of the overall system).

* **LangGraph Nodes (`src/nodes/`):**
    * **`initialize_workflow_node` (`initialization.py`):** Sets up initial paths in `WorkflowState`.
    * **`validate_inputs_node` (`validation.py`):** Validates existence of input files and reads `task_description.md` content.
    * **`generate_manifest_node` (`manifest_generation.py`):** **Component Under Modification.** Currently a skeleton/placeholder. This node will be refactored to use the new `LlmPromptService` and `WriteFileFromTemplateService` for manifest creation, and then call the existing `ChangelogService`.
    * Other nodes (`execute_small_tweak_node`, `finalization_nodes.py`): Largely unaffected by this specific feature.

* **Logging (`src/utils/logging_setup.py`):**
    * **Description:** Existing module for configuring console and file logging.
    * **Responsibilities:** Provides standardized logging across the application.

### 2.2 New Components to be Developed

* **`LlmPromptService` (New Service):**
    * **Description:** A new service class responsible for abstracting interactions with the Google Gemini LLM using the `pydantic-ai` library.
    * **Location:** Proposed: `src/services/llm_prompt_service.py`.
    * **Responsibilities:**
        * Initialize with `AppConfig` (to access the Gemini model name, e.g., `gemini_text_model_name`). The Gemini API key is expected to be available as an environment variable (e.g., `GEMINI_API_KEY`) loaded by `src/main.py`.
        * Accept input text (content of `task-description.md`) and system prompts.
        * Construct and send requests to the Gemini LLM via `pydantic-ai`'s `model_request`.
        * Ensure the LLM's output is parsed into a structured Pydantic model (`ManifestConfigLLM`). For this iteration, it will focus on extracting explicitly defined fields and will not generate clarifying questions if the input is ambiguous.
        * Handle LLM API communication errors and retries (if configured).
    * **Key Interactions:** Instantiated in `src/main.py` and passed to `generate_manifest_node` via `runnable_config`. Called by `generate_manifest_node` with task description content. Returns a `ManifestConfigLLM` instance or error.

* **`WriteFileFromTemplateService` (New Service):**
    * **Description:** A new service class responsible for rendering files using Jinja2 templates and writing them to disk.
    * **Location:** Proposed: `src/services/write_file_from_template_service.py`.
    * **Responsibilities:**
        * Load a specified Jinja2 template file (path provided, e.g., from `AppConfig.manifest_template_filename` resolved against `workspace_folder_path`).
        * Accept a context dictionary containing data for rendering.
        * Render the template using the provided context.
        * Write the rendered content to a specified output file path.
        * Handle file I/O operations and related errors.
    * **Key Interactions:** Instantiated in `src/main.py` and passed to `generate_manifest_node` via `runnable_config`. Called by `generate_manifest_node` with template path, context data (derived from `ManifestConfigLLM` output, `task_description_content`, timestamps, etc.), and the output path for `goal-manifest.md`.

### 2.3 Data Models (New and Existing Pydantic Models)

* **`AppConfig` (Existing - `src/config.py`):**
    * As described above. Will require a new field for `gemini_text_model_name` (or similar).
* **`WorkflowState` (Existing - `src/state.py`):**
    * As described above. Will hold inputs for and outputs from the new services within the scope of `generate_manifest_node`.
* **`ManifestConfigLLM` (New Pydantic Model):**
    * **Description:** Defines the structured data to be extracted/inferred by the `LlmPromptService` from `task-description.md`.
    * **Location:** Proposed: `src/models/manifest_models.py` (new file/directory).
    * **Example Fields:** `goal_title: str`, `task_description_for_manifest: str`, `target_file_path_relative_to_git_root: str`.
    * **Responsibilities:** Ensures type safety and validated structure for data passed from the LLM to the templating service.
    * **Note:** The "AI Questions for User" field in the output `goal-manifest.md` will be defaulted to an empty/null value for this iteration (as per PRD Section 7.2: "AI Questions for User: Empty by default"; "Human Responses: NONE"). The LLM will not be prompted to generate these questions.

### 2.4 Integration within `generate_manifest_node.py`

The existing `src/nodes/manifest_generation.py` will be refactored to:
1.  Receive instances of `LlmPromptService`, `WriteFileFromTemplateService`, and the existing `ChangelogService` (along with `AppConfig`) from the `runnable_config` passed by `src/main.py`.
2.  Retrieve `task_description_content`, `manifest_template_path` (from `AppConfig` via `WorkflowState` or direct `AppConfig` access if passed differently), and `manifest_output_path` from the `WorkflowState`.
3.  Call `llm_prompt_service.get_structured_output(...)` (async if needed, managed by the node) with the `task_description_content` to obtain the populated `ManifestConfigLLM` object.
4.  If the LLM call is successful, prepare a Jinja2 context dictionary using data from `ManifestConfigLLM`, `task_description_content`, current timestamp, and initial values as defined in PRD section 7.2 (e.g., "Overall Status: New", "AI Questions for User: Empty", "Human Responses: NONE").
5.  Call `write_file_from_template_service.render_and_write_file(...)` with the template path, context, and output path.
6.  If manifest generation is successful, call `changelog_service.record_event_in_changelog(...)` with appropriate details (e.g., derived from `ManifestConfigLLM.goal_title` and timestamp) to log the manifest creation.
7.  Update `WorkflowState` with status (`is_manifest_generated`, `is_changelog_entry_added`) and `last_event_summary` or `error_message`.


## 10. Service class interfaces

```
from typing import List, Dict, Optional, Type, Any
from pydantic import BaseModel

class AppConfig(BaseModel):
    gemini_text_model_name: str

PydanticModelType = Type[BaseModel]

class LlmPromptService:
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config
        pass

    async def get_structured_output(
        self,
        messages: List[Dict[str, str]],
        output_model_type: PydanticModelType,
        llm_model_name: Optional[str] = None,
        model_parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[PydanticModelType]:
        return None

class WriteFileFromTemplateService:
    def __init__(self):
        pass

    def render_and_write_file(
        self,
        template_abs_path_str: str,
        context: Dict[str, Any],
        output_abs_path_str: str
    ) -> bool:
        return False
```