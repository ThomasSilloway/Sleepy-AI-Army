## Infantry Agent: Key Design Principles & Architectural Decisions

**Version:** 1.0
**Date:** June 2, 2025

**1. Core Mandate & Vision:**

* The `Infantry Agent` is designed as a robust and reliable code execution unit within the Sleepy AI Army's "Operation: Next Level" framework.
* **"Sealed Orders" Principle:** It operates strictly on the fully contextualized `Mission` it receives. It will not prompt for human clarification during a run or fetch additional files/context beyond the mission specification. If a mission is ambiguous or lacks sufficient detail for high-confidence execution, the agent will halt and report a "blocked" or "failed" status with specific reasons.
* **Precision & Reliability:** The agent aims for surgical precision in transforming clearly defined `Missions` into verifiable, production-quality code that meticulously adheres to established project conventions and architectural integrity.

** Primary Input **

There will only be a single mission spec file per mission. It will be called `mission-spec.md`, it will already be pointed to the correct mission folder via config. Like it'll have `project_git_root` and then a relative path `mission-folder` which would be like `sleepy-ai-army/missions/chore-do-a-thing` 

**2. Primary Output: `mission-report.md`**

* For each mission, the `Infantry Agent` will produce a single, comprehensive Markdown file named `mission-report.md` within the mission's specific folder (e.g., `sleepy-ai-army/missions/mission_xyz/mission-report.md`).
* This report replaces and consolidates the previous `goal-manifest.md` and `changelog.md` concepts for the individual mission.
* **Key Sections of `mission-report.md`:**
    * **Mission Title:** Human-readable title of the mission (derived from the mission specification).
    * **Mission Description:** The original description of the mission objectives.
    * **Final Status:** Clear indication of the outcome (e.g., `SUCCESS`, `FAILURE`, `BLOCKED`).
    * **Execution Summary:** A concise overview of actions taken by the agent.
    * **Files Modified/Created:** A list of all file paths that were created or modified during the mission.
    * **Git Summary:** A bulleted list of commits made by the agent for this mission, formatted as:
        * `commit_hash_short - Commit Title/Message`
    * **Total Cost (USD):** The estimated monetary cost of the LLM interactions for this mission.
    * **Error Details / AI Questions (If Applicable):**
        * If the mission failed or was blocked, this section will contain detailed error messages or reasons.
        * While the "sealed orders" principle aims to prevent the agent from asking questions *during* execution, if a mission concludes due to needing clarification, this section would document what information is missing.
    * **Timestamp:** Date and time of the report's last update.

**3. Execution Model: Asynchronous Native**

* The `Infantry Agent` will be built with an asynchronous-native architecture.
* The main application entry point (`main.py`) will use `asyncio.run()` to start the primary async orchestrator function.
* All LangGraph nodes that involve I/O operations (e.g., calling services for LLM interactions, file access, subprocess execution) will be defined as `async def` functions.
* Service class methods performing I/O (e.g., `LlmPromptService.get_structured_output`, `AiderService.execute`, file/git operations) will be `async def` and use `await` for non-blocking execution. Subprocesses will be managed using `asyncio`'s subprocess capabilities (e.g., `asyncio.create_subprocess_exec`).

**4. `WorkflowState` Philosophy: Lean & Focused**

* The `WorkflowState` (LangGraph's state object) will be kept lean and focused.
* It will only contain data that is truly dynamic and needs to be passed between different nodes to orchestrate the workflow for the *current mission*.
* Static configuration (e.g., general paths, default model names, fixed settings) will reside in `AppConfig`.
* Mission-specific input parameters (e.g., path to the mission folder, target project path) will be passed into the agent's execution context (e.g., via CLI arguments that update `AppConfig` or initial state).
* Temporary variables used only within a single node should be local to that node's scope and not clutter the global `WorkflowState`.

**6. Node & Code Structure:**

* **LangGraph Nodes:**
    * Nodes will primarily be lean functional orchestrators (`async def functions`).
    * Complex business logic, external tool interactions (LLMs, Git, file system), and substantial data transformations will be delegated to dedicated async service classes.
* **Service Classes:** Will follow OOP principles and encapsulate specific domains of responsibility (e.g., `AiderService`, `GitService`, `LlmPromptService`, `MissionReportService`).
* **Prompts:**
    * Each LangGraph node that utilizes significant or unique LLM prompts will have its prompts defined in a dedicated `prompts.py` file, located within a subfolder specific to that node (e.g., `src/nodes/code_execution_node/prompts.py`). This is to keep individual source files small and contextually relevant for AI-assisted development. For very simple or shared prompt snippets, a more central prompt utility might be considered.
* **Configuration:**
    * Static application settings will be managed via an `AppConfig` Pydantic model, loaded from a `config.yml` file.
    * Mission-specific parameters (like the target project's root git path and the path to the specific mission folder) will be provided as command-line arguments, overriding `AppConfig` values as needed, to allow the `General` to direct the `Infantry Agent`.
* **Folder Structure:**
    * The `src/` directory will maintain `nodes/` and `services/` subdirectories.
    * Mission-related outputs (including the `mission-report.md`) will be placed within a main project output directory named `sleepy-ai-army/missions/`, with each mission having its own subfolder (e.g., `sleepy-ai-army/missions/mission_abc/`).
