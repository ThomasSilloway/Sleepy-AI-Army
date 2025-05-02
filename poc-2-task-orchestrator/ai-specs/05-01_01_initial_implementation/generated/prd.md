# Product Requirements Document: Sleepy Dev Team - Task Intake & Setup PoC (PoC2)

**Version:** PoC-2.2 (Final Tool Spec & NNN Padding)
**Date:** 2025-05-01

## 1. Introduction / Vision

This document outlines the requirements for the second Proof-of-Concept (PoC2) task for the "Sleepy Dev Team" project. Following the successful validation of the core loop and backlog reading (PoC1), this PoC focuses on the next logical steps: **task intake and initial setup**. It implements the `SingleTaskOrchestrator` (STO) agent to handle incoming task requests (using LLM reasoning to interpret input format) and the `TaskSetupAgent` (TSA) agent to create the necessary file system structure for *new* tasks using the Google Agent Development Kit (ADK) and a set of **generalized, shared tools**. This version specifies three-digit zero-padded numbering (NNN) for task folders.

## 2. Goals & Objectives

* **Goal:** Demonstrate an agent (`SingleTaskOrchestrator`) receiving input and routing appropriately based on whether the input represents a new task or refers to an existing one, using LLM reasoning to interpret the input format.
* **Goal:** Demonstrate an agent (`TaskSetupAgent`) creating a standardized task folder structure (using NNN numbering) based on a new task description, orchestrating calls to generalized tools.
* **Goal:** Validate the logic for inferring task type prefixes (e.g., `Bug_`, `Feature_`) using an LLM within the TSA agent.
* **Goal:** Validate the logic for determining the correct sequential number (NNN format) for new tasks based on their prefix by using dedicated directory scanning and parsing tools.
* **Goal:** Validate the logic for generating a concise slug from a task description using LLM reasoning within the TSA agent.
* **Objective:** Implement the `SingleTaskOrchestrator` agent (acting as root for this PoC, likely `LlmAgent`) to receive user input from `adk web`.
* **Objective:** Implement STO's LLM prompt/logic to analyze the input string, determine if it refers to an existing task based on format (e.g., contains `/ai-tasks/` or matches `Prefix_NNN_slug` pattern), extract the path/name if applicable, and respond accordingly.
* **Objective:** Implement STO logic to delegate new task descriptions to the `TaskSetupAgent`.
* **Objective:** Implement the `TaskSetupAgent` (as a sub-agent to STO, likely `LlmAgent`).
* **Objective:** Implement TSA's LLM prompt/logic to infer prefixes (`Bug_`, `Polish_`, `Feature_`, `Refactor_`, fallback `Task_`) AND generate a <= 5-word, hyphenated slug from the task description.
* **Objective:** Implement TSA logic to call the `get_next_task_number` tool to determine the sequence number.
* **Objective:** Implement TSA logic to format the sequence number with three-digit zero-padding (NNN).
* **Objective:** Implement TSA logic to call `create_directory` and `write_file` tools to create the folder structure and initial files.
* **Objective:** Run the application using `adk web` in a local Python `.venv`.

## 3. Target Audience / User Personas

* **Primary User:** The developer (project author) validating the task intake, routing, and setup stages of the agent workflow using a modular, tool-based approach with LLM reasoning for input interpretation and generation tasks.

## 4. Functional Requirements (Features - PoC2 Scope)

* **PoC2-FR-001: Single Task Orchestrator (STO) Operation**
    * **Function:** Acts as the root agent for this PoC. Receives user chat input via `adk web`. Uses LLM reasoning (guided by its instruction prompt) to analyze the input string, determine if it represents a new task description or refers to an existing task folder (based on patterns like path inclusion or `Prefix_NNN_slug` format), and routes processing accordingly.
    * **ADK Type Suggestion:** `google.adk.agents.LlmAgent` (or `Agent`) is required to perform the input format analysis using LLM reasoning.
    * **Required Generalized Tools:** None. Relies on internal LLM reasoning.
    * **Acceptance Criteria:**
        * Configured as the root agent for the `adk web` application.
        * Successfully receives the user's chat input string.
        * Correctly uses its LLM reasoning (prompt-driven) to identify input strings indicating existing tasks (based on agreed format patterns).
        * If an existing task pattern is detected, the agent extracts the relevant path/name from the input and responds directly to the user with "This task already exists: [Extracted Folder Path/Name]" and does **not** invoke the `TaskSetupAgent`.
        * If the input does not appear to reference an existing task, the STO identifies it as a new task description.
        * For new tasks, the STO invokes its sub-agent, `TaskSetupAgent`, passing the original input string as the `current_task_description`.

* **PoC2-FR-002: Task Setup Agent (TSA) Operation**
    * **Function:** Invoked by the STO for new tasks. Responsible for determining the task type (prefix) and generating a slug via LLM reasoning, calculating the next sequence number (NNN format) for that type using a helper tool, creating the standard task directory structure, and creating initial files within it by orchestrating calls to generalized tools.
    * **ADK Type Suggestion:** `google.adk.agents.LlmAgent` (or `Agent`) is required to handle the LLM-based prefix inference and slug generation.
    * **Internal LLM Reasoning:**
        * Infers the correct prefix from the list: `Bug_`, `Polish_`, `Feature_`, `Refactor_`. Defaults to `Task_` if none seems appropriate based on the input description.
        * Generates a concise slug (<= 5 words, hyphen-separated) based on the input description.
    * **Required Generalized Tools:**
        * `get_next_task_number(base_path: str, prefix: str) -> dict`: (From `shared_tools/task_helpers/`) Gets the next available sequence number (as an integer) for the inferred prefix.
        * `create_directory(path: str, create_parents: bool = True) -> dict`: (From `shared_tools/file_system/`) Creates the main task folder.
        * `write_file(path: str, content: str, overwrite: bool = False) -> dict`: (From `shared_tools/file_system/`) Writes `changelog.md` and `task_description.md`.
    * **Acceptance Criteria:**
        * Receives the `current_task_description` from the STO.
        * Successfully performs internal LLM reasoning to determine the `prefix` and generate the `slug`.
        * Calls the `get_next_task_number` tool, providing the base task path (from constants) and the inferred `prefix`, receiving the next sequence number (e.g., `3`). Handles potential errors from the tool.
        * **Formats the received sequence number with three-digit zero-padding** (e.g., `3` becomes `003`).
        * Constructs the full target directory path: `<Workspaceroot>/ai-tasks/Prefix_NNN_slug/` (e.g., `/ai-tasks/Bug_003_fix-login-issue/`).
        * Calls the `create_directory` tool with the full path. Handles potential errors.
        * Calls the `write_file` tool to create an empty `changelog.md` inside the new directory. Handles potential errors.
        * Calls the `write_file` tool to create `task_description.md` inside the new directory, using the original `current_task_description` as content. Handles potential errors.
        * Upon successful completion of all steps, signals success back to the STO (or directly responds) enabling the final user confirmation message.

## 5. Non-Functional Requirements (PoC2 Scope)

* **Environment:** Must run locally within a standard Python virtual environment named `.venv`. Docker is explicitly excluded. Execution via `adk web`.
* **Usability:** User interaction via `adk web` chat provides clear feedback as defined (task created path or task already exists path).
* **Reliability:**
    * STO reliably uses LLM reasoning to differentiate input formats.
    * TSA robustly orchestrates calls to generalized tools (`get_next_task_number`, `create_directory`, `write_file`), handling potential errors.
    * Numbering logic within `get_next_task_number` tool is correct; formatting to NNN is correct.
    * LLM prefix inference/slug generation is reasonably consistent; fallback mechanism works.
* **Maintainability:** Code organized with clear separation between agents (STO, TSA) and generalized tools (in shared libraries). Use of constants file (`shared_libraries/constants.py`).

## 6. Design Considerations / Implementation Details (High-Level)

* **Framework:** Google Agent Development Kit (ADK).
* **Agent Strategy:**
    * `SingleTaskOrchestrator` (Root Agent, `LlmAgent`): Focuses on input interpretation (using LLM reasoning based on prompt) and delegation.
    * `TaskSetupAgent` (Sub-Agent, `LlmAgent`): Focuses on LLM-based reasoning (prefix/slug) and orchestrating calls to generalized tools (`get_next_task_number`, `create_directory`, `write_file`).
* **Tool Strategy:** Employs **generalized, shared tools** organized by function. Agents compose functionality by calling these specific tools.
* **Key Generalized Tools:**
    * `get_next_task_number` (task_helpers, likely uses `list_directories` and `parse_task_folder_name` internally)
    * `create_directory` (file_system)
    * `write_file` (file_system)
    * *Internal Tools Used by `get_next_task_number`*: `list_directories` (directory), `parse_task_folder_name` (parsing).
* **Number Formatting:** Sequence numbers must be formatted to three digits with leading zeros (NNN) before being used in folder names (handled by `get_next_task_number` tool or TSA agent).
* **Configuration:** Use `shared_libraries/constants.py` for the base task path (`/ai-tasks/`), agent names, model IDs.
* **Execution:** Via `adk web`.

## 7. Technical Constraints

* Requires Python 3.9+ (or as required by `google-adk`).
* Requires the `google-adk` library installed in the `.venv`.
* Requires file system read/write/create permissions for the process running `adk web` within the `/ai-tasks/` directory and its subdirectories.
* Requires LLM access (e.g., Gemini via API key) for both the `SingleTaskOrchestrator` (for input interpretation) and the `TaskSetupAgent` (for prefix/slug generation).

## 8. Data Requirements

* **Input Data:** User chat messages via `adk web`.
* **Intermediate Data:** Results from tool calls (e.g., `next_number`), inferred prefix, generated slug.
* **Output Data:**
    * Chat messages to the user ("Created task folder: ..." or "This task already exists: ...").
    * New directories (`/ai-tasks/Prefix_NNN_slug/`).
    * New files (`changelog.md`, `task_description.md`).

## 9. Potential Risks & Edge Cases (PoC2 Specific)

* **Risk:** STO's LLM reasoning fails to correctly distinguish input formats. (Mitigation: Careful prompt engineering for STO, clear user guidance on input formats).
* **Risk:** Failure in chained tool calls within TSA. (Mitigation: Robust error handling in TSA).
* **Risk:** `get_next_task_number` tool has bugs or doesn't handle NNN formatting correctly. (Mitigation: Thorough testing of the tool and formatting logic).
* **Risk:** LLM inconsistency in prefix inference or slug generation by TSA. (Mitigation: Prompt tuning, clear fallback logic).
* **Edge Case:** `/ai-tasks/` directory doesn't exist. (Mitigation: `get_next_task_number` or `create_directory` tool should handle this).

## 10. Release Criteria / Success Metrics (PoC2 Specific)

* **Release Criteria:**
    * The ADK application runs successfully via `adk web` within a local `.venv`.
    * STO agent correctly receives chat input.
    * STO correctly uses LLM reasoning to identify input referencing existing tasks and responds with the "already exists" message without calling TSA.
    * STO correctly uses LLM reasoning to identify input representing new tasks and delegates to TSA.
    * TSA, when invoked:
        * Successfully infers prefix and generates slug using LLM.
        * Successfully calls `get_next_task_number` and receives a valid number.
        * Correctly formats the number to three digits with zero-padding (NNN).
        * Successfully calls `create_directory` creating the correct folder (`/ai-tasks/Prefix_NNN_slug/`).
        * Successfully calls `write_file` twice creating `changelog.md` and `task_description.md`.
    * User receives the correct confirmation message ("Created task folder: ..." or "This task already exists: ...") in the `adk web` interface.
    * All necessary generalized tools (`get_next_task_number`, `create_directory`, `write_file`, plus those used internally by `get_next_task_number`) are implemented and function correctly.
* **Success Metrics (Qualitative):**
    * PoC demonstrates the intended workflow using LLM reasoning and generalized tools without errors for various inputs.
    * Provides confidence in using LLM agents for interpretation/generation and orchestrating fine-grained tools.