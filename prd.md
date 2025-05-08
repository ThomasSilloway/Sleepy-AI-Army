# Product Requirements Document: Sleepy Dev Team (MVP)

**Version:** 1.0
**Date:** 2025-05-01

## 1. Introduction / Vision

This document outlines the requirements for the Minimum Viable Product (MVP) of "Sleepy Dev Team," an AI-assisted development orchestrator. The vision is to create a system that leverages AI (specifically Google Gemini models and tools like `aider`) to make incremental progress on software development tasks outlined in a backlog, primarily during times when the user is away from the computer (e.g., overnight, during breaks). Instead of attempting end-to-end task completion, the system focuses on advancing multiple tasks by one logical step per run cycle, allowing the user to review progress and guide the overall direction. This project refactors concepts and potentially code from the earlier Godot-AI-Developer project into a more generic, scalable tool.

## 2. Goals & Objectives

* **Goal:** Automate the incremental advancement of development tasks defined in a simple backlog file.
* **Goal:** Leverage AI to perform various development sub-tasks (Q&A generation, documentation, planning, coding via `aider`, analysis) autonomously based on task state.
* **Goal:** Provide a mechanism for user review and control over the automated process via a proposal system.
* **Objective:** Implement systems capable of performing MVP tasks: Q&A, Brainstorming, PRD writing, Planning, Root Cause Analysis, Fix Planning, Polish Planning, Code Execution (via `aider`), Formatting, and Learnings Documentation.
* **Objective:** Integrate with `aider` for code generation/modification tasks, using `gemini-2.5` as the backend LLM.
* **Objective:** Implement a Discord bot interface for manual triggering.
* **Objective:** Ensure the system runs reliably in a local Docker environment.
* **Objective:** Handle Gemini API rate limits via key cycling.
* **Objective:** Refactor the Discord bot communication from the Godot-AI-Developer project for more direct command/response interaction.

## 3. Target Audience / User Personas

* **Primary User:** Individual developers (initially the project author) looking to leverage AFK time for automated assistance on their coding projects.

## 4. Functional Requirements (Features / User Stories - MVP)

### Core Workflow & Orchestration

* **FR-001: Root Agent (`LoopAgent`) Operation**
    * **User Story:** As a developer, I want the system to process tasks from my backlog iteratively when triggered, so that progress is made sequentially.
    * **Acceptance Criteria:**
        * A top-level `LoopAgent` manages the main run cycle.
        * The loop executes two sub-agents sequentially: `BacklogReaderAgent`, `SingleTaskOrchestrator`.
        * The loop terminates when `BacklogReaderAgent` escalates (signals backlog is empty) or a configured `max_iterations` limit is reached.
        * The agent system can be initiated via a function call triggered by the Discord bot or a scheduled mechanism (scheduling mechanism outside MVP scope, but architecture supports it).

* **FR-002: Backlog Reader Agent (`BacklogReaderAgent`)**
    * **User Story:** As a developer, I want the system to read my simple Markdown backlog file one task at a time during each cycle, so tasks are processed in the order I define.
    * **Acceptance Criteria:**
        * Reads the `/ai-tasks/backlog.md` file (simple bullet points, one task per line).
        * If `backlog.md` is empty: Sets `actions.escalate = True` in its context to terminate the parent `LoopAgent`. Clears `state['current_task_description']`.
        * If `backlog.md` is not empty:
            * Takes the content of the first line.
            * Stores this content in session state (`state['current_task_description']`).
            * Rewrites `backlog.md` without the first line (physical removal).
            * Ensures `actions.escalate` is False.
        * Requires File System tools (Read, Write).

* **FR-003: Single Task Orchestrator (`SingleTaskOrchestrator`)**
    * **User Story:** As a developer, I want the system to manage the processing for a single task, determining its state and delegating to the correct specialist agent to advance it.
    * **Acceptance Criteria:**
        * Receives task description via `state['current_task_description']`. Proceeds only if valid.
        * Determines if the task refers to a new item or an existing task folder (e.g., checks for `/ai-tasks/NN_slug/` existence).
        * If new: Delegates to `TaskSetupAgent`.
        * Determines the correct task folder path.
        * Delegates to `TaskPlannerAgent` to infer the next step required for the task.
        * Receives the inferred step (e.g., `Needs_PRD`, `Needs_Code`) via state.
        * Routes/Delegates execution to the specific `ExecutionAgent` corresponding to the inferred step.
        * Delegates to `ReportingAgent` after the execution agent completes.
        * Requires tools/logic for state management and folder checking.

* **FR-004: Task Setup Agent (`TaskSetupAgent`)**
    * **User Story:** As a developer, when a new task is pulled from the backlog, I want the system to create a dedicated folder and initial files for it.
    * **Acceptance Criteria:**
        * Creates a unique task folder (e.g., `/ai-tasks/01_task_slug/`). Logic includes determining the next sequential number (NN).
        * Creates an initial `changelog.md` file within the folder.
        * Moves/writes the task description into a file within the folder (e.g., `task_description.md`).
        * Handles specific naming conventions if the task description indicates a bug or polish item (e.g., `Bug_NN_slug`, `Polish_NN_slug`).
        * Requires File System tools (Create Directory, Write File, potentially Read Directory for sequencing).

* **FR-005: Task Planner Agent (`TaskPlannerAgent`)**
    * **User Story:** As a developer, I want the system to analyze the current state of a task and decide the most logical next step to advance it.
    * **Acceptance Criteria:**
        * Receives the task folder path.
        * Reads relevant files within the folder (`task_description.md`, `changelog.md`, potentially others).
        * Uses the primary LLM (`gemini-2.5`) to determine the next step from the defined MVP list.
        * Stores the inferred step name (e.g., `Create_PRD`) in session state for the orchestrator.
        * **MVP Step List:** `Ask_Clarifying_Questions`, `Create_Brainstorm_Doc`, `Create_PRD`, `Create_Tech_Architecture`, `Needs_Root_Cause_Analysis`, `Needs_Architecture_Analysis`, `Needs_Fix_Plan`, `Needs_Polish_Plan`, `Implement_Code`, `Needs_Formatting`, `Needs_Learnings_Doc`, `Task_Complete`.
        * Requires File System tools (Read File, List Directory).

* **FR-006: Reporting Agent (`ReportingAgent`)**
    * **User Story:** As a developer, after a step is completed for a task, I want the system to log the completion and propose potential next steps for my review.
    * **Acceptance Criteria:**
        * Receives context about the completed step (e.g., via state).
        * Appends an entry detailing the completed step to the task's `changelog.md` file.
        * Uses the primary LLM (`gemini-2.5`) to analyze the current task state and propose one or more logical next steps.
        * Appends these proposals (clearly linked to the originating task ID/folder) to the central `/ai-tasks/proposed_tasks.md` file.
        * Requires File System tools (Read File, Append File).

### MVP Execution Agents

* **FR-007: Q&A Agent (`QnAAgent`)**
    * **User Story:** As a developer, I want the system to generate clarifying questions when a task lacks sufficient detail.
    * **Acceptance Criteria:** Reads task context, generates questions using `gemini-2.5`, saves questions to `questions_for_user.md` in the task folder. Requires File R/W tools.

* **FR-008: Brainstorming Agent (`BrainstormingAgent`)**
    * **User Story:** As a developer, I want the system to brainstorm different implementation approaches for a feature.
    * **Acceptance Criteria:** Reads task context, generates multiple implementation ideas using `gemini-2.5`, saves them (with pros/cons) to `architecture_brainstorm.md`. Requires File R/W tools.

* **FR-009: PRD Agent (`PRDAgent`)**
    * **User Story:** As a developer, I want the system to generate a Product Requirements Document based on the task description and any prior Q&A/planning.
    * **Acceptance Criteria:** Reads task context, generates `prd.md` using `gemini-2.5`. Requires File R/W tools.

* **FR-010: Planning Agent (`PlanningAgent`)**
    * **User Story:** As a developer, I want the system to generate a technical architecture/plan based on the PRD.
    * **Acceptance Criteria:** Reads task context (PRD, brainstorm), generates `tech_architecture.md` using `gemini-2.5`. Requires File R/W tools.

* **FR-011: Root Cause Analysis Agent (`RootCauseAnalysisAgent`)**
    * **User Story:** As a developer working on a bug task, I want the system to investigate the likely root cause and document its findings.
    * **Acceptance Criteria:** Reads bug description/context, potentially uses tools to analyze code files, determines likely cause(s) using `gemini-2.5`, writes findings to `root_cause_analysis.md`. Requires File R/W tools, potentially Code Search/Analysis tool.

* **FR-012: Architecture Analyzer Agent (`ArchitectureAnalyzerAgent`)**
    * **User Story:** As a developer, I want the system to analyze the code architecture related to a task (feature or bug) and suggest improvements or solutions.
    * **Acceptance Criteria:** Reads task context (description, PRD, root cause), potentially analyzes code files, identifies architectural points/issues, proposes solutions using `gemini-2.5`, writes to `architecture_analysis.md`. Requires File R/W tools, potentially Code Search/Analysis tool.

* **FR-013: Fix Planning Agent (`FixPlanningAgent`)**
    * **User Story:** As a developer working on a bug task, after analysis, I want the system to generate a plan for fixing the bug.
    * **Acceptance Criteria:** Reads task context (bug description, root cause, architecture analysis), generates `bug_fix_plan.md` using `gemini-2.5`. Requires File R/W tools.

* **FR-014: Polish Planning Agent (`PolishPlanningAgent`)**
    * **User Story:** As a developer working on a polish task, I want the system to generate potential implementation options for the polish item.
    * **Acceptance Criteria:** Reads polish description, generates multiple implementation options/approaches in `polish_plan.md` using `gemini-2.5`. Requires File R/W tools.

* **FR-015: Code Execution Agent (`CodeExecutionAgent`)**
    * **User Story:** As a developer, I want the system to use `aider` to implement code for features, bug fixes, polish tasks, or add logging based on provided plans/instructions.
    * **Acceptance Criteria:**
        * Receives coding instructions and context (relevant files/specs) from the `SingleTaskOrchestrator`.
        * Constructs and executes the appropriate `aider` command via subprocess.
        * Configures `aider` to use `gemini-2.5` as its backend LLM.
        * Captures `aider`'s output/results/diffs.
        * Reports status back to the orchestrator.
        * Requires Subprocess tool, File R tool.

* **FR-016: Formatting Agent (`FormattingAgent`)**
    * **User Story:** As a developer, after code is generated, I want the system to automatically format the modified files.
    * **Acceptance Criteria:**
        * Identifies code files modified in the current step (e.g., based on `aider` output or file timestamps).
        * Runs configured code formatters (e.g., `black`, `prettier`) on those files via subprocess.
        * Reports status.
        * Requires Subprocess tool, File System tools.

* **FR-017: Learnings Agent (`LearningsAgent`)**
    * **User Story:** As a developer, after a bug fix task is completed, I want the system to document the learnings from the process.
    * **Acceptance Criteria:** Reads task context (`changelog`, `fix plan`, potentially code diffs), generates `bug_fix_learnings.md` using `gemini-2.5`. Requires File R/W tools.

### Supporting Functionality

* **FR-018: Discord Bot Interface (Manual Trigger)**
    * **User Story:** As a developer, I want to be able to manually start a processing run of the Sleepy Dev Team via a simple Discord command.
    * **Acceptance Criteria:**
        * A Discord bot runs locally as part of the Docker setup.
        * The bot responds to a `/start-sleepy-dev` command.
        * This command triggers the `SleepyDev_RootAgent` to start a run cycle.
        * The bot provides basic feedback (e.g., "Run started," "Run completed/stopped").

* **FR-019: Discord Bot Refactoring (Technical)**
    * **User Story:** As a developer, I want the Discord bot's communication with the ADK backend to use a direct command/response pattern for better clarity and maintainability.
    * **Acceptance Criteria:** The communication between the Discord bot frontend and the `ADK` agent backend (potentially via WebSocket) is refactored away from the previous "event function capturing" method towards a more explicit invocation model (e.g., using a singleton connection manager).

* **FR-020: API Key Cycling**
    * **User Story:** As a developer using free-tier API keys, I want the system to automatically switch to another key when a rate limit is encountered, so processing can continue.
    * **Acceptance Criteria:**
        * The system can be configured with a list of Google AI Studio API keys.
        * When an API call to Gemini fails due to rate limiting, the system attempts the call with the next key in the list.
        * Logic exists to handle exhaustion of all keys (e.g., pause and report error).

## 5. Non-Functional Requirements

* **Usability:**
    * Discord command interaction should be simple and provide clear feedback.
    * File-based backlog (`backlog.md`) and proposals (`proposed_tasks.md`) should be human-readable.
    * Task folders (`/ai-tasks/NN_slug/`) provide clear organization.
* **Reliability:**
    * Agent system should handle file I/O errors gracefully.
    * `BacklogReaderAgent` must reliably remove only the processed line.
    * `aider` integration should handle potential subprocess errors.
    * Loop termination logic must prevent infinite runs.
    * API key cycling logic should function correctly.
* **Maintainability:**
    * Codebase (Python/`ADK`) should be modular, following the defined multi-agent structure.
    * Adherence to Python best practices (PEP 8), clear comments.
    * Configuration (API keys, potentially formatter paths) should be externalized (e.g., `.env` file).
* **Performance:**
    * Individual agent steps should complete within a reasonable time.
    * A full run cycle processing one task should ideally complete within minutes, not hours (depends heavily on LLM response times and `aider` execution). Performance is secondary to functionality for MVP.
* **Security:**
    * API keys must be stored securely (e.g., `.env` file, not checked into Git).
    * `subprocess` calls (to `aider`, formatters) should be constructed carefully to avoid injection vulnerabilities (though input is generally internally generated).
* **Extensibility:** The multi-agent architecture should make it relatively easy to add new `ExecutionAgent`s post-MVP.

## 6. Design Considerations / Implementation Details

* **Framework:** Google Agent Development Kit (`ADK`).
* **Architecture:** Multi-agent system as defined (v4.1 with `TaskPlannerAgent`, merged `RootCauseAnalysisAgent`). Use `LoopAgent`, `SequentialAgent`, `LlmAgent` appropriately.
* **LLM:** `gemini-2.5` via Google AI Studio API Keys.
* **Coding Tool:** `aider` integrated via subprocess by `CodeExecutionAgent`.
* **State Management:** Primarily via `ADK` Session State and file system artifacts (`changelog.md`, generated docs within task folders, `backlog.md` modification).
* **Backlog Format:** Markdown file (`/ai-tasks/backlog.md`) with bullet points.
* **Proposal Format:** Markdown file (`/ai-tasks/proposed_tasks.md`).
* **Task Folders:** Located under `/ai-tasks/`, named `NN_slug`.
* **Discord Bot:** Python (`discord.py`), needs refactoring for communication with `ADK` backend (WebSocket suggested).

## 7. Technical Constraints & Integrations

* **Environment:** Runs locally within Docker containers orchestrated by Docker Compose. Managed via start/stop scripts.
* **Dependencies:**
    * Python 3.9+
    * `google-adk` library
    * `aider-chat` library/CLI tool
    * `discord.py` library
    * Google Cloud SDK (for auth if needed, though AI Studio keys preferred)
    * Code formatters (e.g., `black`, `prettier`) accessible in the environment.
    * `Git` (for project structure and recovery).
* **LLM Access:** Requires valid Google AI Studio API keys with access to `gemini-2.5`.

## 8. Data Requirements

* **Input Data:**
    * `/ai-tasks/backlog.md`: User-maintained list of tasks.
    * Project source code files (accessed by `aider` and analysis agents).
    * `/ai-docs/best_practices.md` (referenced in prompts).
* **Intermediate Data:**
    * `ADK` Session State (tracking loop index, current task, intermediate results).
    * Task Folders (`/ai-tasks/NN_slug/`) containing:
        * `task_description.md`
        * `changelog.md`
        * Generated documents (`prd.md`, `tech_architecture.md`, `root_cause_analysis.md`, etc.)
        * Code files modified/generated by `aider`.
* **Output Data:**
    * Modified source code files.
    * Updated task folders with new documents and updated changelogs.
    * Updated `/ai-tasks/proposed_tasks.md` file.
    * Modified `/ai-tasks/backlog.md` (lines removed).
    * Discord bot messages (status updates).

## 9. Potential Risks & Edge Cases

* **Risk:** LLM (`gemini-2.5`) may struggle with complex reasoning for `TaskPlannerAgent` or `RootCauseAnalysisAgent`. (Mitigation: Prompt engineering, potentially using more capable models post-MVP).
* **Risk:** `aider` fails to apply code changes correctly or gets stuck. (Mitigation: Robust error handling in `CodeExecutionAgent`, timeout limits, capturing `aider` logs).
* **Risk:** `BacklogReaderAgent` corrupts `backlog.md` during rewrite. (Mitigation: Careful file I/O implementation, reliance on Git for recovery).
* **Risk:** API rate limits heavily restrict throughput even with key cycling. (Mitigation: User needs sufficient keys, potential for delays).
* **Risk:** Discord bot communication refactoring proves difficult. (Mitigation: Treat as a core technical task, potentially simplify initial bot interaction).
* **Edge Case:** Task description in backlog is ambiguous, leading to incorrect folder creation or planning. (Mitigation: User needs to provide reasonably clear descriptions).
* **Edge Case:** `aider` or formatters not found in PATH within Docker container. (Mitigation: Correct Dockerfile setup).
* **Edge Case:** Loop terminates unexpectedly (e.g., `max_iterations` too low, uncaught error). (Mitigation: Clear logging, robust error handling per agent).

## 10. Release Criteria / Success Metrics

* **Release Criteria:**
    * Core multi-agent application runs within Docker Compose environment.
    * Discord bot connects and `/start-sleepy-dev` command triggers a run.
    * `BacklogReaderAgent` correctly reads and removes lines from `backlog.md` and signals termination via escalation.
    * `SingleTaskOrchestrator` correctly routes tasks based on `TaskPlannerAgent` output.
    * All defined MVP Execution Agents can be successfully invoked and produce expected output files/actions (Q&A, PRD, Plan, Code via `aider`, Formatting, Analysis docs, Learnings doc).
    * `ReportingAgent` correctly updates `changelog.md` and `proposed_tasks.md`.
    * API key cycling mechanism functions when tested (e.g., by simulating rate limit errors).
    * Basic error handling is in place for common issues (file not found, tool errors).
    * Discord bot communication refactoring is complete.
* **Success Metrics (Qualitative MVP):**
    * System successfully processes multiple tasks from the backlog over several runs without critical failures.
    * Generated artifacts (docs, code changes) are generally coherent and relevant to the input task.
    * The proposal mechanism allows the user to effectively review and guide the next steps.
    * Developer observes tangible progress on backlog items after automated runs.

## 11. Future Considerations / Roadmap (Post-MVP)

* Implement parallel task processing (`ParallelAgent`).
* Add more specialized execution agents (Verification, Review Request, User Action Request, advanced Bug/Polish flows, central doc updates).
* Integrate external project management tools for backlog input/output.
* Enhance `TaskPlannerAgent` reasoning (e.g., considering task dependencies).
* Implement more sophisticated error handling and recovery within agent flows.
* Explore using more advanced/capable LLMs if `gemini-2.5` proves insufficient for some tasks.
* Add automated testing and evaluation using `ADK`'s evaluation tools.
* Consider using `aider` for modifying documents (not just code) for efficiency.
* Implement "Boomerang Mode" subtask creation.
