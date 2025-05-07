# Product Requirements Document: Sleepy AI Army - PoC 5 (Aider Small Tweak Integration)

**Version:** 1.0-PoC5
**Date:** 2025-05-05

## 1. Introduction

This document outlines the Level 1 requirements for Proof-of-Concept 5 (PoC 5) within the "Sleepy AI Army" project. This PoC focuses on validating the fundamental mechanism of integrating the `aider` tool to reliably perform automated, small, single-file code modifications ("Small Tweaks") based on a task description provided in a structured way. It serves as a foundational step for more advanced AI-driven coding assistance. This document defines the 'What' and 'Why', avoiding implementation specifics ('How').

## 2. Goals & Objectives

* **Goal:** Demonstrate and validate the core workflow for automated single-file code modification using the `aider` tool within a controlled environment.
* **Objective:** Implement the capability to manage a dedicated Git feature branch for the modification task.
* **Objective:** Implement the capability to parse a simple task description to identify the target file and the requested change.
* **Objective:** Implement the capability to reliably locate the target file within a configured project workspace.
* **Objective:** Implement the capability to programmatically format and execute the correct `aider` command.
* **Objective:** Implement the capability to log the key steps of the process for traceability.
* **Objective:** Implement the capability to report the final success/failure outcome and intermediate progress to the user.

## 3. Target Audience / User Personas

* **Primary User:** The developer initiating the process, providing the initial setup (goal folder, task description), observing progress via the `adk web` interface, and reviewing the final outcome and resulting Git changes.

## 4. Functional Requirements

The core functionality revolves around processing a specific "Goal" defined in a pre-configured folder structure.

### FR-PoC5-001: Process Initiation and Setup

* **Trigger:** Developer initiates processing via interaction (e.g., typing "hi") in the `adk web` interface after the system is running.
* **Pre-conditions:**
    * The path to the target project workspace (containing the code and Git repository) is pre-configured (e.g., hardcoded).
    * The path to the specific "Goal" folder (e.g., `ai-goals/SmallTweak_NNN_slug/`) to be processed is pre-configured (e.g., hardcoded).
    * The specified "Goal" folder exists and contains a `task_description.md` file.
* **System Actions (Observable Behavior):**
    1.  The system identifies the target "Goal" folder based on the configuration.
    2.  The system interacts with the Git repository in the configured workspace to:
        * Check out the `main` branch.
        * Create a new feature branch with a name derived from the goal type and description (e.g., `small-tweak/goal-slug`).
    3.  Status updates indicating the progress of these setup steps should be visible in the `adk web` interface.
* **Error Handling:** If Git operations fail (e.g., repo inaccessible, checkout fails, branch already exists, other branch creation error), the process stops, and a specific error message is reported in the `adk web` interface.

### FR-PoC5-002: Task Processing and Execution

* **Trigger:** Successful completion of FR-PoC5-001.
* **System Actions (Observable Behavior):**
    1.  Read the `task_description.md` file from the "Goal" folder.
    2.  Parse the content to extract the target filename and the textual description of the requested code change.
    3.  Locate the full path of the target filename within the configured project workspace.
    4.  Format the necessary arguments for invoking the `aider` command.
    5.  Execute the `aider` command, targeting the specified file with the requested change.
    6.  Capture the success or failure outcome from the `aider` execution.
    7.  Status updates indicating the progress (parsing, locating, formatting, executing `aider`) should be visible in the `adk web` interface.
* **Error Handling:**
    * If `task_description.md` is missing or cannot be parsed correctly, the process stops, and a specific error is reported.
    * If the target file cannot be located, the process stops, and a specific error is reported.
    * If the `aider` command execution itself fails (e.g., `aider` returns an error status), this failure is captured. The process stops, and the failure is reported.

### FR-PoC5-003: Logging and Reporting

* **Trigger:** Occurs throughout the workflow (FR-PoC5-001, FR-PoC5-002) and upon completion or failure.
* **System Actions (Observable Behavior):**
    1.  Append entries detailing each significant step (Git checkout, branch creation, parsing, locating, formatting, `aider` execution, final result) and its outcome/relevant info to a `changelog.md` file located within the "Goal" folder.
    2.  Upon completion (successful or failed) of the entire process, display a final summary message in the `adk web` console/interface indicating:
        * Overall Success or Failure status.
        * The name of the Git branch that was created.
        * Advice for the user to check their Git repository for specific changes (if successful) or the `changelog.md`/error messages for details.
    3.  Intermediate status messages indicating the current step being processed are displayed in the `adk web` interface during the run.

### FR-PoC5-004: Input Task Description Constraint

* **Description:** The `task_description.md` file must contain sufficient information to identify the target filename and the desired code modification (e.g., "Add documentation to `file.py`").

## 5. Non-Functional Requirements

* **Reliability:** The execution of the workflow, particularly the Git interactions and `aider` command invocation, must be reliable. The system should handle expected errors gracefully (as defined in Functional Requirements).
* **Accuracy:** The `changelog.md` must provide an accurate and useful record of the steps performed and their outcomes.
* **Observability:** The user should be able to observe the progress of the task through intermediate status updates in the `adk web` interface.
* **Maintainability (Goal):** While specifics are Level 2/3, the design should aim for simplicity and modularity to support future extensions (related to Implementation Notes below).

## 6. Constraints

* **Platform:** Must be implemented using the Google Agent Development Kit (ADK).
* **Core Tool:** Must use the `aider` tool for performing code modifications.
* **Version Control:** Requires interaction with a Git repository.
* **Configuration:** Relies on pre-configured (e.g., hardcoded) paths for the target project workspace and the specific "Goal" folder being processed in this PoC.

## 7. Data Requirements (Level 1)

* **Input Data:**
    * User interaction trigger via `adk web`.
    * Pre-configured workspace path.
    * Pre-configured "Goal" folder path.
    * `task_description.md` file within the "Goal" folder.
    * Git repository state (branches, files).
* **Output Data:**
    * Intermediate status messages in `adk web` interface.
    * Final summary message in `adk web` interface.
    * `changelog.md` file within the "Goal" folder (created/updated).
    * A new Git branch with potentially modified code file(s).

## 8. Success Metrics (PoC Specific)

* Successful creation of the correct Git feature branch.
* Successful parsing of `task_description.md` to identify file and change.
* Successful location of the target file.
* Successful execution of the `aider` command targeting the correct file.
* Accurate logging of steps to `changelog.md`.
* Correct final status (Success/Failure) and branch name reported to the user.
* Graceful reporting of errors for all defined failure conditions (Git, parsing, file not found, `aider` failure).
* Visible intermediate status updates during processing in `adk web`.

---

## Implementation Notes & Considerations (Level 2/3 Guidance)

* **Agent Hierarchy:** Follow best practices for structuring agents (e.g., consider orchestrator agent, specialist agents for Git, file ops, `aider` interaction).
* **Agent Simplicity:** Aim for agents with simple, focused responsibilities.
* **Tool Reusability:** Design tools used by agents (e.g., read_file, write_file) to be as generic and reusable as possible. Certain aspects should not be generic though, like anything running a subprocess like aider. We want to ensure that the ai-agents don't have access to running arbitrary commandline commands.
* **LLM Usage:** Leverage appropriate LLMs based on task complexity. Consider smaller, faster models (gemini-2.0-flash-lite) for straightforward tasks like parsing or simple formatting, reserving more powerful models (e.g., gemini-2.5-pro-exp) for potential future, more complex reasoning or generation needs. (This PoC might only require simpler models).