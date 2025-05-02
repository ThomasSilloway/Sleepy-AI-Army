# Product Requirements Document: Sleepy Dev Team - PoC 3 (Context & Q&A Agents)

**Version:** PoC-3.0
**Date:** 2025-05-02
**Based on Final Assumptions:** Revision 12

## 1. Introduction

This document outlines the requirements for the third Proof-of-Concept (PoC 3) for the "Sleepy Dev Team" project. This PoC focuses on implementing the initial context gathering and the iterative Q&A process required when a development task lacks sufficient detail for subsequent steps like PRD generation or technical planning. It involves the coordination of multiple agents (`TaskPlannerAgent`, `ContextResearchAgent`, `QnAAgent`, `ChangelogAgent`) interacting via file system artifacts and status files within a defined task folder structure, using the Google Agent Development Kit (ADK).

This PoC directly addresses aspects of FR-005 (`TaskPlannerAgent`'s routing logic) and FR-007 (`QnAAgent`) from the main project PRD, introducing a `ContextResearchAgent` and leveraging a `ChangelogAgent` (related to FR-006 reporting).

## 2. Goals & Objectives

* **Goal:** Demonstrate an agent system that can identify the need for context or clarification for a given development task.
* **Goal:** Implement an agent (`ContextResearchAgent`) to perform initial context gathering by analyzing existing documents (`task_description.md`, `tech_architecture.md`) and file structure, creating a baseline context file (`task_context.md`).
* **Goal:** Implement an agent (`QnAAgent`) that iteratively generates assumptions and clarifying questions based on the task context, stores them for asynchronous user review, processes user feedback, and determines readiness for the next phase.
* **Goal:** Establish a clear workflow using a status file (`task_status.md`) to manage the state transitions between context gathering, user review (context), Q&A generation, user review (feedback), and readiness determination, involving explicit user action to advance certain states.
* **Goal:** Implement a reusable agent (`ChangelogAgent`) invoked as a tool to append activity records to a task-specific changelog.
* **Goal:** Validate the use of different LLM models (Flash vs. Gemini 2.5) based on agent task complexity.
* **Objective:** Implement the `TaskPlannerAgent` logic to read the task status and delegate control appropriately based on the defined states.
* **Objective:** Implement the `ContextResearchAgent` with required tools (`ReadFile`, `ListDirectory`, `WriteFile`, `AgentTool`) and LLM interaction (Flash model) for context extraction.
* **Objective:** Implement the `QnAAgent` with required tools (`ReadFile`, `WriteFile`, `AgentTool`), LLM interaction (Gemini 2.5 model) for reasoning/generation/processing, and logic for handling user feedback via structured comment tags.
* **Objective:** Implement the `ChangelogAgent` as an `AgentTool` with its `AppendFile` tool (Flash model).
* **Objective:** Define and implement the specified file formats (`task_context.md`, `questions-and-answers.md`, `task_status.md`, `changelog.md`).

## 3. Target Audience / User Personas

* **Primary User:** The developer (project author) validating the context gathering and requirements elicitation phases of the automated development workflow.

## 4. Functional Requirements

### FR-PoC3-001: Task Planner Agent - Status Check & Routing
* **Description:** Acts as the entry point for processing a specific task folder. Determines the current state of the task using `task_status.md` and delegates control to the appropriate next agent or reports status to the user.
* **ADK Agent:** `TaskPlannerAgent` (Likely `LlmAgent` using Flash model, name TBD).
* **Tools:** `ReadFile`.
* **Input:** Task folder path.
* **Processing Logic:**
    1.  Attempt to read `task_status.md` within the task folder.
    2.  **If Read Fails (File Not Found):** Transfer control to `ContextResearchAgent`.
    3.  **If Read Succeeds:** Parse the first line for status string.
        * If status is `AWAITING_CONTEXT_REVIEW`: Respond "Initial context generated in `task_context.md`. Please review/update and then change `task_status.md` to `AWAITING_QUESTIONS`." Stop processing for this task cycle.
        * If status is `AWAITING_QUESTIONS`: Transfer control to `QnAAgent`.
        * If status is `AWAITING_USER_FEEDBACK`: Transfer control to `QnAAgent`.
        * If status is `READY_FOR_PRD`: Respond "Q&A ready for user review and next step assignment." Stop processing for this task cycle.
        * If status is unexpected/empty: Respond with error message and stop.
* **Output:** Delegation to another agent or a status message to the user.

### FR-PoC3-002: Context Research Agent - Initial Context Generation
* **Description:** Generates the initial `task_context.md` file if it doesn't exist.
* **ADK Agent:** `ContextResearchAgent` (Likely `LlmAgent` using Flash model, name TBD).
* **Tools:** `ReadFile`, `ListDirectory`, `WriteFile`, `AgentTool` (for `ChangelogAgent`).
* **Input:** Task folder path, Task Description (implicitly read).
* **Processing Logic:**
    1.  Triggered by `TaskPlannerAgent` if `task_status.md` is missing.
    2.  Read content of `task_description.md`.
    3.  Attempt to read content of `tech_architecture.md`.
    4.  If `tech_architecture.md` exists, use LLM (Flash) prompted to extract relevant sections/points based on the task description.
    5.  Use `ListDirectory` to get file/folder listing (limit 100).
    6.  Use `WriteFile` to create `task_context.md` containing: Task Description, Extracted Architecture Context (if any), File List.
    7.  Use `WriteFile` to create `task_status.md` with content:
        ```
        AWAITING_CONTEXT_REVIEW
        # Note: After reviewing context, update this status to AWAITING_QUESTIONS
        ```
    8.  Formulate changelog entry text (e.g., "Generated initial context, awaiting review.").
    9.  Call `ChangelogAgent` tool with `changelog_entry_text`.
* **Output:** Creation/update of `task_context.md`, `task_status.md`, and call to `ChangelogAgent`.

### FR-PoC3-003: Q&A Agent - Iterative Clarification
* **Description:** Generates assumptions and questions based on context, processes user feedback, and determines readiness for next steps.
* **ADK Agent:** `QnAAgent` (Likely `LlmAgent` using Gemini 2.5 model, name TBD).
* **Tools:** `ReadFile`, `WriteFile`, `AgentTool` (for `ChangelogAgent`).
* **Input:** Task folder path, `task_context.md`, `questions-and-answers.md` (if exists).
* **Processing Logic:**
    1.  Triggered by `TaskPlannerAgent` if status is `AWAITING_QUESTIONS` or `AWAITING_USER_FEEDBACK`.
    2.  Read `task_context.md`.
    3.  Read `questions-and-answers.md` (if exists).
    4.  Parse feedback sections (between `` tags).
    5.  **Check for Feedback:**
        * If status was `AWAITING_USER_FEEDBACK` and no actual feedback text was found (all sections contain only placeholder):
            * Respond "Checked Q&A file; no new user feedback provided yet."
            * Ensure `task_status.md` is `AWAITING_USER_FEEDBACK` (with its note).
            * Do **not** call `ChangelogAgent`.
            * End turn.
        * **Otherwise (initial run or feedback found):**
            * Use LLM (Gemini 2.5) to process existing context and any new feedback.
            * Generate/update assumptions.
            * Generate/update clarifying questions.
            * Use LLM to determine readiness status (`AWAITING_USER_FEEDBACK` or `READY_FOR_PRD`).
            * Use `WriteFile` to overwrite `questions-and-answers.md` with updated assumptions, questions, and feedback placeholders (`USER FEEDBACK REQUIRED` between tags).
            * Use `WriteFile` to update `task_status.md` with the determined status and corresponding instructional note (e.g., `AWAITING_USER_FEEDBACK\n# Note: After providing feedback...` or `READY_FOR_PRD\n# Note: Q&A complete...`).
            * Formulate appropriate changelog entry text (e.g., "Generated initial questions.", "Processed feedback, updated Q&A.").
            * Call `ChangelogAgent` tool with `changelog_entry_text`.
            * End turn.
* **Output:** Update of `questions-and-answers.md`, `task_status.md`, call to `ChangelogAgent` (if work done), or a status message if no feedback found.

### FR-PoC3-004: Changelog Agent - Append Entry
* **Description:** Appends a provided text entry to the task's `changelog.md`.
* **ADK Agent:** `ChangelogAgent` (Implemented as `AgentTool`, likely `LlmAgent` using Flash model, name TBD).
* **Tools:** `AppendFile`.
* **Input:** `changelog_entry_text` (string argument passed via tool call). Task folder path (implicit from context or passed).
* **Processing Logic:**
    1.  Receive `changelog_entry_text` argument.
    2.  Construct full path to `changelog.md` within the task folder.
    3.  Use `AppendFile` tool to add the `changelog_entry_text` (prefixed with a timestamp or markdown bullet) to the file. Ensure a newline is added appropriately.
* **Output:** Updated `changelog.md` file. Return status (e.g., `{'status': 'success'}`) to the calling agent.

## 5. Non-Functional Requirements

* **Environment:** Runs locally within a standard Python virtual environment (`.venv`). Execution via `adk web` or direct Python script.
* **Usability:** User interacts via editing files (`task_status.md`, `questions-and-answers.md`). Agent responses provide clear status or indicate next steps required from the user. Instructional comments in `task_status.md` guide the user.
* **Reliability:** Agents handle file I/O errors gracefully (e.g., file not found from `ReadFile`). Status transitions are clear and managed correctly via `task_status.md`. `AppendFile` tool reliably appends without overwriting.
* **Maintainability:** Code organized into separate agents. Tools (`ReadFile`, `WriteFile`, `AppendFile`, `ListDirectory`) likely implemented as reusable functions wrapped by `FunctionTool`. Use of constants for file names, statuses.
* **Performance:** Individual agent steps complete in reasonable time (primarily dependent on LLM response times). Context gathering limits (file count) prevent excessive I/O.
* **Extensibility:** The status-driven flow and modular agents should allow for adding new states or agents (like `PRDAgent`) later.

## 6. Design Considerations / Implementation Details

* **Framework:** Google Agent Development Kit (`google-adk`).
* **Agents:** `TaskPlannerAgent` (Flash), `ContextResearchAgent` (Flash), `QnAAgent` (Gemini 2.5), `ChangelogAgent` (Flash, used as `AgentTool`). Primarily `LlmAgent` type.
* **State Management:** Primarily via file system (`task_status.md`, `task_context.md`, `questions-and-answers.md`). Minimal reliance on ADK Session State, except potentially temporary flags or passing the changelog entry text *before* the `AgentTool` call if absolutely necessary (though argument passing is preferred).
* **File Formats:** Defined in assumptions (Markdown, simple status strings, specific HTML comment tags for feedback).
* **Tool Implementation:** Standard Python functions wrapped using `google.adk.tools.FunctionTool`. `ChangelogAgent` wrapped using `google.adk.tools.agent_tool.AgentTool`.

## 7. Technical Constraints & Integrations

* Requires Python 3.9+ (or as required by `google-adk`).
* Requires `google-adk` library.
* Requires file system read/write/append permissions.
* Requires LLM access (Gemini 2.5 and Flash via API Key).

## 8. Data Requirements

* **Input:** Task Description (initially), User Feedback (via editing `questions-and-answers.md`), User status updates (via editing `task_status.md`).
* **Intermediate/Output:** `task_status.md`, `task_context.md`, `questions-and-answers.md`, `changelog.md`. Agent responses in `adk web` console.

## 9. Success Metrics (PoC 3 Specific)

* `TaskPlannerAgent` correctly routes to `ContextResearchAgent` or `QnAAgent` based on `task_status.md`.
* `TaskPlannerAgent` correctly identifies the `READY_FOR_PRD` status and reports appropriately.
* `ContextResearchAgent` successfully creates `task_context.md` and sets status to `AWAITING_CONTEXT_REVIEW`.
* `QnAAgent` successfully generates initial questions/assumptions and sets status to `AWAITING_USER_FEEDBACK`.
* `QnAAgent` correctly parses feedback provided between designated comment tags.
* `QnAAgent` correctly handles the "no feedback provided" scenario.
* `QnAAgent` successfully updates `questions-and-answers.md` and `task_status.md` after processing feedback.
* `QnAAgent` correctly identifies the `READY_FOR_PRD` state based on its internal logic.
* `ChangelogAgent` (as `AgentTool`) successfully appends entries provided by other agents to `changelog.md`.
* The overall workflow progresses through the defined states based on agent actions and simulated user updates to `task_status.md`.