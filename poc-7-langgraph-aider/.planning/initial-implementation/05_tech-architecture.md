# Technical Architecture: PoC7 - LangGraph Orchestration for Initial Document Generation

**Version:** 1.1
**Date:** 2025-05-09 (Revised)
**Project Name:** PoC7 - LangGraph Orchestration for Initial Document Generation

## 1. Overview

This document details the technical architecture for Proof-of-Concept (PoC) 7. The project's primary goal is to validate LangGraph's effectiveness in orchestrating a stateful, multi-step workflow. This PoC specifically focuses on LangGraph orchestrating the `aider` tool for the initial generation of a `goal-manifest.md` and the recording of this event in a `changelog.md`. This serves as a foundational step for the broader "Sleepy Dev Team" project. This architecture prioritizes demonstrating core orchestration mechanics and `aider` integration over exhaustive, deep error recovery, user interface considerations, or advanced file content validation for this PoC phase.

The chosen architecture is a **Direct Sequential Workflow** leveraging LangGraph. Key aspects of this architecture include:
* Service-oriented interactions for external tools: A dedicated `AiderService` encapsulates `aider` CLI interactions for document generation, and a `ChangelogService` (also utilizing `aider` for this PoC) handles structured updates to the `changelog.md`.
* A formalized `AppConfig` Pydantic model for static configurations.
* Dependency injection of services and configurations into LangGraph nodes via `RunnableConfig`.
* A dual-logging mechanism (`overview.log` and `detailed.log`) with specified timestamp formats.
* Adherence to a modular Python file structure.

The main objectives are to demonstrate `aider` orchestration for document creation and changelog updates, ensure clear observability, and provide insights into LangGraph's capabilities for sequencing, state management, and basic error handling, all within a `uv`-managed Python environment.

## 2. Component Breakdown

The system comprises the following major components, interacting to achieve the PoC's objectives:

### 2.1. `LangGraph Orchestrator`
* **Description:** The central component, implemented as a LangGraph `StateGraph`, responsible for managing and executing the defined sequence of operations.
* **Responsibilities:**
    * Define and execute workflow steps (initialization, input validation, document generation, changelog recording, finalization/error handling) as a sequence of connected nodes.
    * Manage the flow of control and data (via `WorkflowState`) between different stages.
    * Make decisions based on the outcome of previous steps.
* **Key Interactions:**
    * Manipulates and transitions the `WorkflowState`.
    * Invokes `AiderService` for manifest generation and `ChangelogService` for changelog updates.
    * Utilizes the `Logging System` for recording progress and issues.
    * Accesses configuration from `AppConfig` (via `RunnableConfig`).
    * Initialized and run by the `Main Execution Script`.

### 2.2. `AppConfig` (Configuration Model)
* **Description:** A Pydantic `BaseModel` holding all static configurations, ensuring type safety and structured access. The term `goal_root_path` in this model refers to the top-level directory for a specific goal's inputs and outputs.
* **Responsibilities:**
    * Store paths (`workspace_root_path`, `goal_root_path`), filenames for templates, inputs, outputs, and logs.
* **Key Interactions:**
    * Loaded from `config.yml` by the `Main Execution Script`.
    * Injected via `RunnableConfig` into the `LangGraph Orchestrator` and services.

### 2.3. `AiderService` (Tool Interaction Service)
* **Description:** A dedicated Python class abstracting CLI interactions with the `aider` tool, primarily for generating files like `goal-manifest.md`.
* **Responsibilities:**
    * Construct `aider` commands for file generation/modification.
    * Execute `aider` as a subprocess.
    * Handle real-time streaming of `aider`'s `stdout`/`stderr` to console and logs.
    * Capture `aider`'s exit status.
* **Key Interactions:**
    * Instantiated by the `Main Execution Script`.
    * Injected via `RunnableConfig` and invoked by `LangGraph Orchestrator` nodes (e.g., `generate_manifest_node`).
    * Uses the `Logging System`.

### 2.4. `ChangelogService` (Changelog Management Service)
* **Description:** A dedicated Python class responsible for managing entries in the `changelog.md` file. For this PoC, it will internally use `aider` to append structured entries, ensuring consistency with other document generation methods.
* **Responsibilities:**
    * Provide a method to add new entries, e.g., `add_entry(event_title: str, event_details: List[str], timestamp: datetime.datetime)`.
    * Format the entry data according to the structure defined in `format-changelog.md` (title, timestamp, bullet points).
    * Construct and execute the appropriate `aider` command to append the formatted entry to `changelog.md`.
    * Ensure changelog entries are appended robustly, minimizing risk of corrupting existing content (within `aider`'s capabilities).
    * Handle `aider`'s output and exit status for the changelog operation.
* **Key Interactions:**
    * Instantiated by the `Main Execution Script`.
    * Injected via `RunnableConfig` and invoked by `LangGraph Orchestrator` nodes (e.g., by `generate_manifest_node` after successful manifest creation).
    * Uses the `Logging System`.
    * Interacts with `changelog.md` located at the path derived from `AppConfig.goal_root_path` and `AppConfig.changelog_output_filename`.

### 2.5. `WorkflowState` (LangGraph State Object)
* **Description:** A `typing.TypedDict` defining the dynamic data structure passed between nodes within the `LangGraph Orchestrator`. Path fields store absolute, resolved paths. The `goal_folder_path` field herein is populated from `AppConfig.goal_root_path`.
* **Responsibilities:**
    * Hold all dynamic data for workflow execution (resolved paths, file content, tool outputs, status flags, error messages).
* **Key Interactions:**
    * Read from and updated by `LangGraph Orchestrator` nodes.

### 2.6. `Logging System`
* **Description:** A utility system for generating application logs. Its setup logic (e.g., using `logging.config.dictConfig` or helper functions) resides in a dedicated utility module (e.g., `src.poc7_orchestrator.utils.logging_setup.py`) and is invoked by the `initialize_workflow_node`.
* **Responsibilities:**
    * Provide timestamped (`[HH:MM:SS.mmm]` format) logging to console, `overview.log`, and `detailed.log`.
* **Key Interactions:**
    * Configured and initialized by `initialize_workflow_node` using `AppConfig`.
    * Used by all major components (`LangGraph Orchestrator` nodes, `AiderService`, `ChangelogService`).

### 2.7. `Main Execution Script` (`poc7_orchestrator.main.py`)
* **Description:** The primary Python script serving as the PoC's entry point.
* **Responsibilities:**
    * Load `AppConfig`.
    * Instantiate `AiderService` and `ChangelogService`.
    * Define and compile the `LangGraph Orchestrator`.
    * Prepare initial `WorkflowState` and `RunnableConfig`.
    * Invoke graph execution and handle overall setup/teardown.
* **Key Interactions:**
    * Entry point for `uv run`. Orchestrates component setup and LangGraph execution.

## 3. Technology Stack

The following technologies are chosen for the development and execution of this PoC:

* **Primary Language:**
    * **Python:** Version 3.9 or higher (as indicated in `uv-project-setup.md` and aligning with LangGraph best practices).
* **Orchestration Framework:**
    * **LangGraph:** The core Python library for building the stateful, multi-step workflow.
* **Core Python Libraries:**
    * **Pydantic:** Utilized for defining the `AppConfig` data model.
    * **Python `subprocess` module:** Employed by `AiderService` and `ChangelogService` to interact with `aider`.
    * **Python `logging` module:** Standard library module for the `Logging System`.
    * **Python `typing` module:** Used for type hints, including `TypedDict` for `WorkflowState`.
    * **Python `datetime` module:** Used for generating timestamps for changelog entries.
* **External Tools & Services (CLI-based):**
    * **`aider`:** AI-powered tool used as a service by `AiderService` and `ChangelogService`.
    * **`uv`:** Python packaging tool for environment management and script execution.
* **Development & Version Control:**
    * **Git:** For source code version control.

## 4. Data Models / Structures

This section defines important data formats and schemas.

### 4.1. `AppConfig` (Static Configuration Schema)

* **Description:** A Pydantic `BaseModel` for static configurations.
* **Source:** Populated from `config.yml` at project root.
* **Key Fields (Illustrative Schema):**
    * `workspace_root_path: str` (Absolute path to workspace with shared assets like templates)
    * `goal_root_path: str` (Absolute path to the directory for the current goal's specific files)
    * `task_description_filename: str` (e.g., "task-description.md"; relative to `goal_root_path`)
    * `manifest_template_filename: str` (e.g., "templates/goal-manifest-template.md"; relative to `workspace_root_path`)
    * `manifest_output_filename: str` (e.g., "goal-manifest.md"; relative to `goal_root_path`)
    * `changelog_template_filename: str` (e.g., "templates/changelog-template.md"; relative to `workspace_root_path`)
    * `changelog_output_filename: str` (e.g., "changelog.md"; relative to `goal_root_path`)
    * `log_subdirectory_name: str` (Fixed as "logs"; relative to `goal_root_path`)
    * `overview_log_filename: str` (Fixed as "overview.log")
    * `detailed_log_filename: str` (Fixed as "detailed.log")

### 4.2. `WorkflowState` (Dynamic Workflow State Schema)

* **Description:** A `typing.TypedDict` for the dynamic state. All path fields are absolute and resolved.
* **Key Fields (Illustrative Schema):**
    * `current_step_name: Optional[str]`
    * `goal_folder_path: str` (Absolute path, corresponds to `AppConfig.goal_root_path`)
    * `workspace_folder_path: str` (Absolute path, corresponds to `AppConfig.workspace_root_path`)
    * `task_description_path: str`
    * `task_description_content: Optional[str]`
    * `manifest_template_path: str`
    * `changelog_template_path: str`
    * `manifest_output_path: str`
    * `changelog_output_path: str`
    * `generated_manifest_filepath: Optional[str]`
    * `aider_last_exit_code: Optional[int]`
    * `error_message: Optional[str]`
    * `is_manifest_generated: bool` (Default: False)
    * `is_changelog_entry_added: bool` (Default: False)

### 4.3. Input File Formats

* **Configuration File (`config.yml`):** YAML format, adhering to `AppConfig` schema.
* **Task Description File:** Markdown (`.md`), free-form. Located in `goal_root_path`.
* **Template Files:** Markdown (`.md`), structural skeletons. Located in `workspace_root_path`.

### 4.4. Output File Formats

* **Goal Manifest File:** Markdown (`.md`), `aider`-generated, guided by `format-goal-manifest.md`. Located in `goal_root_path`.
* **Changelog File:** Markdown (`.md`), `aider`-updated by `ChangelogService`. Entries follow `format-changelog.md` (Title, Timestamp `[YYYY-MM-DD HH:MM AM/PM TZ]`, Bullets). Located in `goal_root_path`.
* **Log Files (`overview.log`, `detailed.log`):** Plain Text (`.log`). Entries prefixed with `[HH:MM:SS.mmm]` timestamp. Located in `goal_root_path/logs/`.

### 4.5. Data Types for Service Interactions

* **`AiderService`:** Inputs: Prompts (`str`), file paths (`List[str]`), working directory (`str`). Outputs: Exit status (`int`).
* **`ChangelogService` (`add_entry` method - illustrative):** Inputs: `event_title: str`, `event_details: List[str]`, `timestamp: datetime.datetime`. Outputs: Success (`bool`).

## 5. NFR Fulfillment

* **NFR-PoC7-001: Idempotency:** Achieved by nodes checking pre-conditions or services instructed for specific initial state creation/overwrite if run on a virgin state. First changelog entry is singular.
* **NFR-PoC7-002: Correctness:** Via typed `AppConfig`/`WorkflowState`; precise service command construction; templates as structural contracts; quality prompt engineering for `aider` (clear instructions, effective context use); direct output file verification.
* **NFR-PoC7-003: Traceability & Observability:** Via console streaming; dual timestamped (`[HH:MM:SS.mmm]`) logs (`overview.log` for flow, `detailed.log` for granular ops including `aider` I/O); contextual logging with `current_step_name`.
* **NFR-PoC7-004: Modularity:** `AiderService` and `ChangelogService` encapsulate tool interactions. `AppConfig` centralizes configuration. LangGraph nodes have distinct responsibilities. `ChangelogService` enhances modularity for changelog ops.

## 6. Key Interaction Flows

**Flow 1: Successful Document Generation & Changelog Update**

1.  **Initiation (`Main Execution Script`):** User runs script. `AppConfig` loaded. `AiderService`, `ChangelogService` instantiated. `LangGraph Orchestrator` defined & compiled. Minimal initial `WorkflowState` and `RunnableConfig` prepared. Graph invoked.
2.  **Workflow Initialization (`initialize_workflow_node`):** Receives state & `RunnableConfig`. Sets up `Logging System` (via `utils.logging_setup`). Logs start. Sets `current_step_name`. Validates `AppConfig.goal_root_path` and `AppConfig.workspace_root_path`. Resolves and stores absolute paths in `WorkflowState`. Logs success.
3.  **Input Validation (`validate_inputs_node`):** Sets `current_step_name`. Verifies `task_description.md` and templates. Reads task content. Logs success or signals error.
4.  **Goal Manifest Generation (`generate_manifest_node`):** Sets `current_step_name`.
    * Constructs `aider` prompt for manifest (using task content, manifest template, output path). Invokes `AiderService.execute(...)`.
    * Updates `WorkflowState` with `aider_last_exit_code`.
    * If successful: Sets `is_manifest_generated`, `generated_manifest_filepath`. Prepares changelog details (`event_title`, `event_details` using `generated_manifest_filepath`, `timestamp = datetime.datetime.now()`). Invokes `ChangelogService.add_entry(...)`. If changelog fails, logs WARNING in `overview.log` but continues. Sets `is_changelog_entry_added`. Logs outcome.
    * If manifest fails, signals error.
5.  **Successful Completion (`success_node`):** Sets `current_step_name`. Logs PoC success. Transitions to LangGraph `END`.

**Flow 2: Error Handling**

1.  **Error Detection & Signaling:** Operational node encounters issue. In accordance with LangGraph's state update mechanism, node returns updated `WorkflowState` with `error_message` and `current_step_name`.
2.  **Transition to Error Handler:** Conditional edge routes to `error_handler_node`.
3.  **Error Processing (`error_handler_node`):** Sets `current_step_name`. Logs critical failure (with `error_message` and original step) to all outputs. Transitions to LangGraph `END`. Main script may exit non-zero.

## 7. Error Handling Strategy

* **General Approach:** Graceful reporting, clear messages via `WorkflowState.error_message`, centralized `error_handler_node` leading to `END`.
* **Error Categories & Handling Specifics:**
    * **Configuration/Input File Errors:** Early termination or transition to `error_handler_node`.
    * **`AiderService`/`ChangelogService` Errors:** (Subprocess fail, `aider` non-zero exit, no output). Service methods report to calling node. Node updates state for `error_handler_node`. For PoC7, a `ChangelogService` failure after successful manifest generation is logged as a WARNING and does not halt the primary success indication.
    * **File System Errors:** Caught by node/service, populates `error_message`.
    * **Unexpected Python Exceptions:** Nodes aim to catch exceptions and populate `error_message`. A global try-except around `app.stream()` in `main.py` is the final fallback for logging before termination.

## 8. Proposed Folder and File Structure

```
poc7_langgraph_orchestrator/
├── .venv/
├── goal_examples/
│   └── poc7_initial_setup_goal/
│       ├── task-description.md
│       ├── logs/
│       │   ├── overview.log
│       │   └── detailed.log
│       ├── goal-manifest.md
│       └── changelog.md
├── src/
│   └── poc7_orchestrator/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── state.py
│       ├── constants.py         # e.g., LOG_SUBDIR_NAME = "logs"
│       ├── nodes/
│       │   ├── __init__.py
│       │   ├── initialization.py
│       │   ├── validation.py
│       │   ├── manifest_generation.py # Includes logic to call ChangelogService
│       │   └── control.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── aider_service.py
│       │   └── changelog_service.py
│       └── utils/
│           ├── __init__.py
│           └── logging_setup.py
├── workspace_examples/
│   └── templates/
│       ├── goal-manifest-template.md
│       └── changelog-template.md
├── tests/
│   └── ...
├── pyproject.toml
├── uv.lock
├── config.yml                   # Located at project root
└── README.md
```

## 9. Risks & Dependencies

* **Risks:**
    1.  **`aider` Reliability for Structured Appends (`ChangelogService`):** `aider` may struggle with consistently appending to `changelog.md` without errors. Mitigation: Robust append-focused prompts, simple/append-friendly changelog entry format. For future, direct file I/O for `ChangelogService` might be more reliable if `aider` proves unsuitable for this specific task, though this deviates from the PoC's '`aider` for all docs' constraint.
    2.  **Prompt Engineering Complexity:** Crafting effective prompts for both services is iterative.
    3.  **Environmental Inconsistencies:** `uv.lock` and clear setup docs mitigate.
    4.  **State Management Complexity (Future):** `WorkflowState` could grow. PoC scope is manageable.
    5.  **Scope Creep:** Adhere to PRD.
    6.  **`aider` CLI Changes:** Encapsulation in services helps, but services may need updates.
    7.  **Changelog Atomicity:** For PoC, if manifest succeeds but changelog fails, it's logged as a warning; true atomicity (rollback) is out of scope.
* **Dependencies:**
    1.  Python >=3.9 (`uv` managed).
    2.  Libraries: LangGraph, Pydantic (per `pyproject.toml`).
    3.  `aider` CLI: Installed, in PATH, functional (tested version assumed).
    4.  Input Files: Correctly formatted and accessible `config.yml`, `task-description.md`, templates.
    5.  File System Access: Read/write permissions for relevant paths.
    6.  Compatible OS for Python, `uv`, `aider`.