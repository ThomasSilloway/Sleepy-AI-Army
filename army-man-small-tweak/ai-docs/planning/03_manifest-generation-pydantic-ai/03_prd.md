# Product Requirements Document: PoC7 - Automated Document Scaffolding

**Version:** 0.1-PoC7-DocScaffold
**Date:** 2025-05-17
**Status:** Draft

## 1. Introduction

This document outlines the Level 1 requirements for a specific feature within Proof of Concept 7 (PoC7): the automated scaffolding of initial project tracking documents. PoC7 itself is designed to validate the use of LangGraph as a foundational orchestration technology for the broader "Sleepy Dev Team" project. This feature focuses on LangGraph's ability to orchestrate a multi-step workflow involving Large Language Model (LLM) interaction for data extraction, template-based document generation, and calls to existing services for specific tasks.

The "Sleepy Dev Team" project envisions an AI-assisted development orchestrator making incremental progress on tasks. This PoC7 feature lays groundwork by automating the creation of a `goal-manifest.md` (a task-specific tracking document) and an initial `changelog.md` entry.

## 2. Goals and Objectives

### 2.1. Primary Goal
To validate LangGraph's capability to orchestrate a defined sequence of actions to:
* Generate an initial `goal-manifest.md` file by interpreting a user-provided `task-description.md` using an LLM for data extraction and a templating engine for rendering.
* Create an initial `changelog.md` entry for the manifest creation event by invoking an existing `ChangelogService`.

### 2.2. Objectives
* **Objective 1:** Demonstrate successful orchestration by LangGraph of the `goal-manifest.md` generation process, including LLM interaction for data extraction (e.g., goal title, target file path) and templated file creation.
* **Objective 2:** Demonstrate successful orchestration by LangGraph of a call to the existing `ChangelogService` to create the initial `changelog.md` entry.
* **Objective 3:** Ensure the generated documents (`goal-manifest.md`, `changelog.md`) adhere to specified formats and accurately reflect the input `task-description.md` and defined initial states.
* **Objective 4:** Provide clear observability into the process via console output and logs.
* **Objective 5:** Confirm that the system correctly identifies and handles cases where the `task-description.md` lacks required information, populating the "AI Questions for User" section of the manifest accordingly.

## 3. Target User

* **Primary User:** The developer initiating the PoC7 script. This user provides the initial configuration (including the path to the `task-description.md` file) and observes the system's output (console messages, generated files, logs) to validate the successful orchestration and document generation.

## 4. User Journeys & Functional Requirements

### 4.1. User Journey: Initiating Document Scaffolding
1.  **Precondition:** The User has a "goal folder" containing a `task-description.md` file. A system configuration file specifies the path to this goal folder.
2.  **Trigger:** The User executes the PoC7 Python script (e.g., via `uv run main.py`).
3.  **System Action (FR-P7DS-001):** The system, orchestrated by LangGraph, reads the `task-description.md` from the specified goal folder.
4.  **System Action (FR-P7DS-002):** The system invokes an LLM (Google Gemini via `pydantic-ai`) to:
    * Parse the `task-description.md`.
    * Extract the full task description text.
    * Extract the target file path (relative to git root) for the task.
    * Infer and generate a concise "Goal Title."
5.  **System Action (FR-P7DS-003):** The system generates the `goal-manifest.md` file in the goal folder using a Jinja2 template and the data from the LLM, adhering to the structure in `format-goal-manifest.md` and the initial values defined in section 7.2.
6.  **System Action (FR-P7DS-004):** The system invokes the existing `ChangelogService` (which uses `aider`) to create/update the `changelog.md` file in the goal folder with an initial entry detailing the `goal-manifest.md` creation, adhering to `format-changelog.md`.
7.  **System Response:** The system outputs status messages to the console during operation.
8.  **Postcondition:** A `goal-manifest.md` file and an updated `changelog.md` file exist in the goal folder. The User can inspect these files and any logs.

### 4.2. Functional Requirements

**FR-P7DS-001: Process `task-description.md` Input**
* The system must locate and read the `task-description.md` file from the goal folder specified in the system configuration.
* **Input:** `task-description.md` file content.
* **Expected Content in `task-description.md`:**
    * The exact file path (relative to the project's git root) of the file to be modified by the task.
    * A description of the work/change that needs to occur in that file.

**FR-P7DS-002: LLM-based Data Extraction and Analysis**
* The system must use an LLM (Google Gemini via `pydantic-ai`) to process the content of `task-description.md`.
* The LLM interaction must aim to populate a structured data model (e.g., a Pydantic model) with:
    * A concise "Goal Title" summarized from the task description.
    * The full original task description.
    * The target file path for the task.

**FR-P7DS-003: Generate `goal-manifest.md`**
* The system must generate a new `goal-manifest.md` file in the specified goal folder.
* The file must be rendered using a Jinja2 template.
* The content and structure must adhere to the `format-goal-manifest.md` (see section 7.1).
* The fields must be populated with data extracted by the LLM and defined initial values (see section 7.2).
* **Output:** A `goal-manifest.md` file.

**FR-P7DS-004: Create Initial Changelog Entry**
* The system must make a call to the pre-existing `ChangelogService` (which utilizes `aider`).
* This service call will result in the creation or update of a `changelog.md` file in the goal folder.
* The entry must record the event of the `goal-manifest.md` creation.
* The entry's content and structure must adhere to `format-changelog.md` (see section 7.1).
    * **Change Title:** e.g., "Goal Manifest Created"
    * **Timestamp:** Current timestamp of generation.
    * **Details:** A bullet point referencing the manifest creation and its Goal Title (e.g., "- Initial Goal Manifest generated for task: '[Extracted Goal Title]'").
* **Output:** An updated `changelog.md` file.

**FR-P7DS-005: Error Handling and Reporting**
* The system must gracefully handle common errors (e.g., missing `task-description.md`, failure to connect to LLM, failure during file writing, error reported by `ChangelogService`).
* In case of unrecoverable errors during the process, the system should stop and provide a clear error message to the user via console output and logs.

## 5. Non-Functional Requirements

* **NFR-P7DS-001: Correctness:**
    * The `goal-manifest.md` content must accurately reflect the information from `task-description.md` and the defined initial state values.
    * The `changelog.md` entry must accurately record the manifest creation event.
* **NFR-P7DS-002: Observability:**
    * The system must provide informative status messages to the console during its operation.
    * Key events, decisions, and errors should be logged for diagnostic purposes.
* **NFR-P7DS-003: Usability (Developer Focus):**
    * The process for initiating the PoC feature should be straightforward for a developer (i.e., running a single script with prerequisite files in place).
* **NFR-P7DS-004: Idempotency (for manifest generation):**
    * If the manifest generation part of the script is run multiple times targeting a goal folder where the manifest does not yet exist, it should produce the same `goal-manifest.md` each time, given the same `task-description.md`. (Note: The `ChangelogService` might have its own idempotency behavior).

## 6. Data Requirements (Level 1)

### 6.1. Input Data
* **Configuration File:** Contains the path to the "goal folder."
* **`task-description.md` file:** Located within the goal folder. Content includes:
    * Target file path (from git root).
    * Description of the task.
* **`format-goal-manifest.md` (Template):** Predefined structure for the goal manifest.
* **`format-changelog.md` (Template/Guideline for `ChangelogService`):** Predefined structure for changelog entries.

### 6.2. Output Data
* **`goal-manifest.md` file:** Created in the goal folder. Contains:
    * `Goal Title` (LLM summarized)
    * `Task Description` (from input file)
    * `Last Updated` (timestamp)
    * `Overall Status`: "New"
    * `Current Focus`: Content of `task-description.md`
    * `Artifacts`: File path extracted from `task-description.md`
    * `AI Questions for User`: Empty
    * `Human Responses`: "NONE"
* **`changelog.md` file:** Created/updated in the goal folder by `ChangelogService`, containing an entry for the manifest creation.
* **Console Output:** Real-time status messages and error reports.
* **Log Files:** Detailed logs for diagnostics.

## 7. Document Formats & Initial Values

### 7.1. Referenced Document Formats
* **`format-goal-manifest.md`:**

* **`format-changelog.md`:**


### 7.2. Initial Values for `goal-manifest.md` upon Creation
* **`[Goal Title]`:** Summarized by LLM from `task-description.md`.
* **`[task description from backlog]`:** Full content of `task-description.md`.
* **`Last Updated`:** Current timestamp of manifest generation.
* **`Overall Status`:** "New"
* **`Current Focus`:** The full content of `task-description.md`.
* **`Artifacts`:** The file path identified in `task-description.md` as the target for the task. (Represented as a bullet point, e.g., `* [in-progress] path/to/file.ext`).
* **`AI Questions for User`:**
    * Empty by default
* **`Human Responses & Go-Ahead`:**
    * "NONE"


## 8. Constraints & Technical Considerations

* **C-P7DS-001: Must use LangGraph:** LangGraph must be the primary orchestrator for the defined workflow.
* **C-P7DS-002: LLM for Manifest Data:** Google Gemini (via `pydantic-ai`) must be used for parsing `task-description.md` and generating the Goal Title for the manifest.
* **C-P7DS-003: Templating for Manifest:** Jinja2 must be used for rendering the `goal-manifest.md`.
* **C-P7DS-004: Existing Changelog Service:** The pre-existing `ChangelogService` (which uses `aider`) must be used for creating the changelog entry.
* **C-P7DS-005: Execution Environment:** The PoC will be run as a Python script within an environment managed by `uv`.
* **Consideration:** The LLM's ability to accurately extract the file path and determine if the task description is "sufficient" is key. Prompt engineering will be important.

## 9. Success Metrics (for this PoC7 Feature)

* Successful generation of `goal-manifest.md` that accurately reflects the `task-description.md` and adheres to the specified format and initial values.
* Successful generation of an initial `changelog.md` entry by the `ChangelogService` correctly detailing the manifest creation event.
* LangGraph successfully orchestrates the sequence of LLM calls, manifest templating, and `ChangelogService` invocation.
* The system correctly identifies insufficient `task-description.md` content and populates the "AI Questions for User" and "Human Responses" fields accordingly.
* Clear error messages are provided for common failure scenarios (e.g., missing input file).
* Operational output is visible on the console and detailed logs are available.

## 10. Future Considerations (Out of Scope for this PRD)
* Updating the Goal Manifest based on further task progress.
* User interaction with the "AI Questions for User" or "Human Responses" fields.
* More complex logic for determining task sufficiency by the LLM.
* Handling multiple artifacts or more complex task descriptions.