# Brainstormed Architecture Options: PoC7 (LangGraph Orchestration - Initial Phase)

The overall technical feasibility of the project as described in the PRD is perceived to be **high, especially for a Proof of Concept.** The scope is well-defined, leveraging specific tools (LangGraph, `aider`) for a limited set of sequential tasks. The main complexities will likely lie in the precise interaction with `aider` and robust error handling/logging within the LangGraph framework.

Below are two distinct high-level architectural approaches for implementing the PoC7 requirements.

---

## Approach 1: Direct Sequential Workflow

**a. Conceptual Overview:**
This approach uses LangGraph to define a straightforward, linear sequence of tasks, directly mapping to the primary functional requirements. It emphasizes simplicity and rapid implementation for the PoC. Each major step in the PRD (input validation, manifest generation, changelog generation) becomes a distinct node in the LangGraph. Error handling would be managed by conditional edges to a common error-reporting node. This aligns with a basic **Pipes and Filters** architectural style, where LangGraph nodes act as filters processing the state.

**b. Key Conceptual Components & Interactions:**
* **`State` Object (TypedDict):**
    * `config_path`: Path to configuration file.
    * `goal_folder_path`: Path to the target folder.
    * `task_description_path`: Path to `task-description.md`.
    * `manifest_template_path`: Path to manifest template/sample.
    * `changelog_template_path`: Path to changelog template/sample.
    * `manifest_path`: Path to the generated `goal-manifest.md`.
    * `changelog_path`: Path to the generated `changelog.md`.
    * `last_error`: Stores error message if any.
    * `high_level_log_path`: Path to the high-level log file.
    * `detailed_log_path`: Path to the detailed log file.
* **LangGraph Nodes:**
    1.  `setup_environment_node`:
        * Reads config for `goal_folder_path`.
        * Initializes paths for log files.
        * Sets up basic logging (to console, high-level log, detailed log).
        * Validates presence of `goal_folder_path`.
    2.  `validate_inputs_node`:
        * Checks for `task-description.md` in the `goal_folder_path`.
        * Checks for sample/template files if their paths are provided or inferred.
        * Updates state with paths.
    3.  `generate_manifest_node`:
        * Constructs `aider` command with `task-description.md` and manifest template.
        * Executes `aider` as a subprocess.
        * Captures `aider` stdout/stderr for console and detailed log.
        * Checks `aider` exit code.
        * Verifies `goal-manifest.md` creation.
    4.  `generate_changelog_node`:
        * Constructs `aider` command, possibly using information from manifest creation (e.g., timestamp, manifest path) from the state, and changelog template.
        * Executes `aider` as a subprocess.
        * Captures `aider` stdout/stderr for console and detailed log.
        * Checks `aider` exit code.
        * Verifies `changelog.md` creation/update.
    5.  `error_handler_node`:
        * Logs the error from `last_error` to console and logs.
        * Terminates the graph (END).
    6.  `success_node`:
        * Logs overall success.
        * Terminates the graph (END).
* **Interactions:**
    * Nodes update the shared `State` object.
    * Control flow: `setup_environment_node` -> `validate_inputs_node` -> `generate_manifest_node` -> `generate_changelog_node` -> `success_node`.
    * Conditional edges from `validate_inputs_node`, `generate_manifest_node`, `generate_changelog_node` to `error_handler_node` if a failure occurs.
    * Logging utilities are called from each node to write to console, high-level, and detailed logs.

**c. Core Interface & Data Ideas:**
* **Interfaces:**
    * Process initiated via Python script (`uv run poc7_script.py`).
    * `aider` invoked via `subprocess` calls (Command-Line Interface).
    * File system for reading inputs (`task-description.md`, templates, config) and writing outputs (`goal-manifest.md`, `changelog.md`, log files).
* **Data Handling:**
    * State managed by LangGraph `State` (Python TypedDict).
    * Input files: Markdown.
    * Output files: Markdown.
    * Log files: Plain text or structured text (e.g., JSON lines) for easier parsing if desired later.
    * `aider` communication: Primarily via file inputs and command-line arguments for prompts/context.

**d. Relevant Technology Categories:**
* **Orchestration:** LangGraph.
* **Compute/Execution:** Python script run with `uv`.
* **External Tooling:** `aider` (CLI).
* **Data Storage (for this PoC):** File system.
* **Logging:** Standard Python `logging` module configured for console, high-level file, and detailed file output.

**e. Initial Risk Assessment:**
1.  **`aider`Brittleness:** `aider` might not consistently produce the desired output format or handle diverse `task-description.md` inputs robustly given "high-level directions." Requires careful prompt engineering for `aider` calls.
2.  **Error Propagation:** Ensuring errors from `aider` (e.g., non-zero exit codes, specific error messages in stdout/stderr) are correctly captured and lead to the `error_handler_node` requires diligent subprocess management.
3.  **State Complexity:** While simple for this PoC, if many more files or details were added to the state, managing it as a single dictionary could become cumbersome without clear schemas.

**f. Pros & Cons Analysis:**
* **Pros:**
    * **Simplicity & Speed (aligns with PoC Goal):** Quickest to implement, straightforward logic flow.
    * **Clear Mapping to FRs:** Each functional requirement can be easily mapped to a node.
    * **Good for User Learning (Objective 4):** Provides a basic understanding of LangGraph sequencing.
    * **Direct Observability (NFR-PoC7-003):** Simple to stream `aider` output directly and log node transitions.
* **Cons:**
    * **Limited Modularity (Potential NFR-PoC7-004 Gap):** `aider` invocation logic is embedded within larger task nodes. Reusing `aider` interaction logic for different purposes might involve code duplication.
    * **Less Granular Error Handling:** Errors within a large node (e.g., within `generate_manifest_node`) might be harder to pinpoint than with smaller, more focused nodes.
    * **Scalability for Complex Workflows:** This linear approach might become unwieldy if more conditional logic or parallel tasks were introduced in future "Sleepy Dev Team" iterations.

---

## Approach 2: Modular Service-Node Orchestration

**a. Conceptual Overview:**
This approach emphasizes modularity (NFR-PoC7-004) by breaking down the workflow into more granular LangGraph nodes. Key operations, especially interactions with `aider` and file system checks, are encapsulated in their own nodes. This can be seen as applying a **Service-Oriented** thinking within the LangGraph structure, where specific nodes offer "services" like "invoke `aider`" or "validate file." `aider` interactions could be wrapped using an **Adapter Pattern** to provide a consistent interface to the rest of the graph. LangGraph still orchestrates the overall flow, which can involve more complex conditional logic based on the outcomes of these granular nodes.

**b. Key Conceptual Components & Interactions:**
* **`State` Object (TypedDict):** Similar to Approach 1, but might include more fine-grained status flags.
    * `config_data`: Parsed configuration.
    * `goal_folder_path`, `task_description_path`, etc.
    * `manifest_generation_prompt`: The specific prompt for `aider` for manifest.
    * `changelog_generation_prompt`: The specific prompt for `aider` for changelog.
    * `aider_last_stdout`, `aider_last_stderr`, `aider_last_exit_code`.
    * `is_manifest_created`, `is_changelog_created`.
    * `last_error`, `high_level_log_path`, `detailed_log_path`.
* **Logging Utility:** A shared Python module/class providing methods like `log_high_level(message)`, `log_detailed(message, data_dump)`.
* **LangGraph Nodes:**
    1.  `initialize_workflow_node`:
        * Reads and validates configuration file (e.g., for `goal_folder_path`).
        * Sets up logger instances (high-level, detailed, console).
        * Initializes paths in state.
    2.  `check_input_files_node`:
        * Verifies `task-description.md` exists.
        * Verifies template files exist.
        * (Conditional) -> `error_handler_node` if missing.
    3.  `prepare_manifest_generation_node`:
        * Constructs the precise prompt/command for `aider` to generate `goal-manifest.md` using `task-description.md` and manifest template. Stores this in the state.
    4.  `invoke_aider_node`: (Potentially a reusable "service" node)
        * Input: `prompt_to_execute`, `target_output_file_path_in_state_to_check`, `context_for_logging`.
        * Executes the `aider` command provided in the state (e.g., `manifest_generation_prompt`).
        * Captures `aider` stdout/stderr, exit code, and stores them in state.
        * Streams `aider` output to console and detailed log.
        * Logs high-level entry/exit.
    5.  `verify_file_creation_node`: (Potentially reusable)
        * Input: `file_path_in_state_to_check`, `artifact_name_for_logging`.
        * Checks if the specified output file (e.g., `goal-manifest.md`) was created.
        * (Conditional) -> `error_handler_node` if not created or `aider_last_exit_code` was non-zero.
        * Updates state flag (e.g., `is_manifest_created = True`).
    6.  `prepare_changelog_generation_node`:
        * Constructs the prompt/command for `aider` for `changelog.md`, using confirmation of manifest creation (from state) and changelog template.
    7.  (`invoke_aider_node` again, with different prompt from state)
    8.  (`verify_file_creation_node` again, for changelog)
    9.  `error_handler_node`:
        * Logs detailed error from `last_error` / `aider_last_stderr`.
        * Terminates graph.
    10. `finalize_workflow_node`:
        * Logs overall success summary.
        * Terminates graph.
* **Interactions:**
    * Flow: `initialize` -> `check_input_files` -> `prepare_manifest` -> `invoke_aider` -> `verify_file_creation` (for manifest) -> `prepare_changelog` -> `invoke_aider` -> `verify_file_creation` (for changelog) -> `finalize_workflow`.
    * Multiple nodes can conditionally branch to `error_handler_node`.
    * The `invoke_aider_node` and `verify_file_creation_node` are designed to be more generic and reusable by being parameterized through the state.

**c. Core Interface & Data Ideas:**
* **Interfaces:** Same as Approach 1 (Python script, `subprocess` for `aider`, File system).
* **Data Handling:** Same as Approach 1. The structure of the `State` object will be critical for passing parameters to the more granular nodes.

**d. Relevant Technology Categories:**
* Same as Approach 1 (LangGraph, Python/`uv`, `aider` CLI, File system, Python `logging`).

**e. Initial Risk Assessment:**
1.  **Over-Granularity for PoC:** Defining many small nodes might be more setup effort than necessary for the PoC's simple two-step generation, potentially obscuring the main workflow.
2.  **`aider` Brittleness:** Same as Approach 1. This risk remains regardless of LangGraph structure, though better error isolation per step might help diagnose issues.
3.  **State Management Complexity:** While promoting modularity, passing all necessary parameters and context through the state to generic nodes like `invoke_aider_node` needs careful design of the state object.

**f. Pros & Cons Analysis:**
* **Pros:**
    * **Enhanced Modularity (NFR-PoC7-004):** `aider` interactions and file validations are encapsulated, making them potentially reusable for future, more complex workflows (aligns with Vision Statement for "Sleepy Dev Team").
    * **Improved Testability:** Smaller, focused nodes can be easier to test in isolation (though LangGraph's execution model is holistic).
    * **Granular Error Handling & Logging (FR-PoC7-004, NFR-PoC7-003):** Easier to pinpoint exactly where a failure occurred (e.g., `aider` call for manifest vs. `aider` call for changelog). Logs can be more targeted per micro-step.
    * **Better Adherence to Design Goals (NFR-PoC7-004):** "distinct, logically separated components/nodes" and "modular way" for `aider` usage is better achieved.
* **Cons:**
    * **Increased Initial Complexity:** More nodes and edges to define in LangGraph, potentially making the graph harder to visualize initially for a simple sequence.
    * **Potential for Boilerplate:** Passing context to generic nodes might require more state management boilerplate code.
    * **Slightly Steeper Learning Curve (Objective 4):** The indirection through generic nodes might be slightly more complex to grasp initially than a direct 1:1 mapping of FRs to nodes.

