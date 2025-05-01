# Product Requirements Document: Sleepy Dev Team - Core Loop PoC

**Version:** PoC-1.0
**Date:** 2025-05-01

## 1. Introduction / Vision

This document outlines the requirements for a specific Proof-of-Concept (PoC) task derived from the larger "Sleepy Dev Team" project vision. The purpose of this PoC is to implement and validate the fundamental agent looping and backlog consumption mechanism using the Google Agent Development Kit (ADK). It focuses solely on demonstrating a `LoopAgent` successfully invoking a `BacklogReaderAgent` which reads, reports, and removes tasks from a designated backlog file using ADK tools. This PoC serves as a foundational step before implementing the more complex orchestration and execution agents defined in the full project PRD.

## 2. Goals & Objectives

* **Goal:** Demonstrate a functional agent loop using ADK's `LoopAgent`.
* **Goal:** Prove the ability of an ADK agent (`BacklogReaderAgent`) to interact with the local file system via ADK tools to read and modify a simple backlog file.
* **Goal:** Validate the core termination logic for the loop based on backlog state.
* **Objective:** Implement a `LoopAgent` that iteratively calls a `BacklogReaderAgent`.
* **Objective:** Implement a `BacklogReaderAgent` that reads the first task from `/ai-tasks/backlog.md`, reports it, and removes it from the file using ADK `FunctionTool`(s).
* **Objective:** Implement loop termination triggered by the `BacklogReaderAgent` signaling (via `actions.escalate`) when the backlog file is empty.
* **Objective:** Structure the PoC as a basic ADK application runnable via the `adk web` command in a local Python virtual environment (`venv`).

## 3. Target Audience / User Personas

* **Primary User:** The developer (project author) validating the basic ADK agent interaction, file I/O tooling, and control flow patterns before proceeding with the full project.

## 4. Functional Requirements (Features - PoC Scope)

### Core Workflow & Orchestration (PoC Subset)

* **PoC-FR-001: Root Agent (`LoopAgent`) Operation**
    * **Description:** A top-level `LoopAgent` manages the main run cycle for the PoC.
    * **Acceptance Criteria:**
        * The `LoopAgent` is the root agent of the ADK application.
        * It contains the `BacklogReaderAgent` as its sub-agent.
        * In each iteration, it invokes the `BacklogReaderAgent`.
        * The loop continues until the `BacklogReaderAgent` escalates or a potential (optional) `max_iterations` limit is reached (escalation is the primary mechanism).
        * The agent system is initiated via the standard `adk web` flow.

* **PoC-FR-002: Backlog Reader Agent (`BacklogReaderAgent`) Operation**
    * **Description:** This agent is responsible for reading the next task from the backlog file, reporting it, modifying the file, and signaling when the backlog is empty.
    * **Acceptance Criteria:**
        * The agent uses one or more ADK `FunctionTool`(s) to interact with the file system.
        * The tool(s) target the `/ai-tasks/backlog.md` file. The expected format is Markdown bullet points (e.g., `* Task description`).
        * **File Interaction Logic (ideally within a single tool call for efficiency):**
            * Attempt to read the `backlog.md` file.
            * **If the file is empty or does not exist:** The tool informs the agent, and the agent sets `actions.escalate = True` in its `ToolContext`. The agent should provide a status message response (e.g., "Backlog is empty. Signaling termination.") but no task description.
            * **If the file is not empty:**
                * Read the content of the *first* line.
                * Rewrite the `backlog.md` file *without* the first line (physically removing it).
                * Return the content of the removed line to the agent.
        * If a task was successfully read and removed:
            * The agent's primary text response should be formatted as: `Next backlog item: [Task Description]` (where `[Task Description]` is the content of the removed line).
            * The agent ensures `actions.escalate` is `False`.
        * Requires necessary file system permissions to read and write `/ai-tasks/backlog.md`.

## 5. Non-Functional Requirements (PoC Scope)

* **Environment:** Must run locally within a standard Python virtual environment (`venv`). Docker is explicitly excluded for this PoC.
* **Usability:** Console output during `adk web` execution should be clear, showing status messages (loop start/iteration, reading backlog, task reported, termination signal) for traceability.
* **Reliability:**
    * Should handle an empty or non-existent `backlog.md` file gracefully by triggering the termination flow.
    * File modification logic must reliably remove only the first line without corrupting the rest of the file.
* **Maintainability:** Code should be clear and understandable as a prototype example of basic ADK usage.
* **Performance:** Not a primary concern, but execution should complete in a reasonable time for a small number of backlog items.

## 6. Design Considerations / Implementation Details (High-Level)

* **Framework:** Google Agent Development Kit (ADK).
* **Key Agents:** A root `LoopAgent`, containing a single `BacklogReaderAgent` (likely an `LlmAgent` or a custom `BaseAgent` implementation).
* **Tools:** Requires one or more ADK `FunctionTool`(s) wrapping Python function(s) to perform the read/modify/check-empty logic for the `/ai-tasks/backlog.md` file. These tool functions will need `ToolContext` access to set `actions.escalate`.
* **Execution:** Application started and interacted with via `adk web`. Observe results via console logs.
* **Control Flow:** `LoopAgent` manages iterations. `BacklogReaderAgent` uses tool results and `actions.escalate` to signal termination status back to the `LoopAgent`.

## 7. Technical Constraints

* Requires Python 3.9+ (or as required by the `google-adk` library version used).
* Requires the `google-adk` library to be installed in the `venv`.
* Requires standard file system read/write access for the user running the `adk web` process to the path `/ai-tasks/backlog.md`.
* Excludes Docker and any other agents or complex dependencies from the full "Sleepy Dev Team" PRD.

## 8. Data Requirements

* **Input Data:**
    * `/ai-tasks/backlog.md`: A text file containing tasks as Markdown bullet points, one per line. Must be created manually for testing.
* **Output Data:**
    * Console output/logs generated by `adk web`, including status messages and reported task descriptions.
    * The `/ai-tasks/backlog.md` file will be modified (lines removed) during execution.

## 9. Potential Risks & Edge Cases (PoC Specific)

* **Risk:** File I/O errors due to incorrect path, missing file, or insufficient permissions. (Mitigation: Clear error reporting from the file I/O tool).
* **Risk:** Logic error in the file modification tool corrupts `backlog.md`. (Mitigation: Careful implementation and testing; keep backups of the test file).
* **Risk:** Incorrect use of ADK `ToolContext` or `actions.escalate`, preventing proper loop termination. (Mitigation: Adhere to ADK documentation/examples for tool implementation and escalation).
* **Edge Case:** `backlog.md` contains empty lines or non-bullet point lines. (Mitigation: PoC assumes clean input format; robust handling is out of scope for PoC).

## 10. Release Criteria / Success Metrics (PoC Specific)

* **Release Criteria:**
    * The ADK application can be successfully launched using `adk web`.
    * The `LoopAgent` initiates and iterates.
    * The `BacklogReaderAgent`, via its tool(s), successfully reads the first line of a non-empty `/ai-tasks/backlog.md`.
    * The first line is correctly removed from `/ai-tasks/backlog.md`.
    * The agent outputs the message "Next backlog item: [Task Description]" to the console/log.
    * The loop continues processing subsequent lines correctly on further iterations.
    * When `/ai-tasks/backlog.md` becomes empty, the `BacklogReaderAgent` correctly detects this and sets `actions.escalate = True`.
    * The `LoopAgent` correctly terminates upon receiving the escalation signal.
    * Status messages ("Starting loop iteration...", "Reading backlog...", "Signaling empty backlog.", "Finished loop.") are observed in the output.
* **Success Metrics (Qualitative):**
    * The PoC runs end-to-end without Python errors for a sample `backlog.md` file.
    * The observed behavior (file modification, console output, termination) matches the requirements defined in this document.
    * Provides confidence in the basic ADK mechanisms for looping, file I/O via tools, and control flow escalation.