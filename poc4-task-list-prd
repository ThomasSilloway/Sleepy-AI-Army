# Product Requirements Document: Sleepy AI Army - PoC (Task List Mechanism)

**Version:** 1.0-PoC-TaskList
**Date:** 2025-05-03

## 1. Introduction

This document outlines the Level 1 requirements for a Proof-of-Concept (PoC) within the "Sleepy AI Army" project. The purpose of this PoC is to evaluate a **Task List** mechanism as a flexible approach for managing the steps involved in progressing a development **Goal**. This approach contrasts with previous, more rigid state management methods explored. This document focuses strictly on the 'What' and 'Why' (externally observable behaviors, user interactions, goals) and avoids implementation details ('How').

## 2. Goals & Objectives

* **Goal:** Demonstrate the basic viability and operation of using a **Task List** for orchestrating **Tasks** within a development **Goal**.
* **Objective:** Implement the system's ability to initialize a new **Task List** from a template when one does not exist for a given **Goal**.
* **Objective:** Implement the system's ability to read an existing **Task List** and identify the sequence of runnable **Tasks** up to the next point requiring human intervention.
* **Objective:** Validate this mechanism as a potentially simpler and more flexible alternative for **Goal** progression management.

## 3. Target Audience / User Personas

* **Primary User:** The developer (project author) initiating the process and observing the system's output via the `adk web` interface to validate the **Task List** mechanism.

## 4. Functional Requirements

This PoC focuses on two primary functional flows triggered by user interaction within the `adk web` environment, operating on a pre-configured **Goal** folder assumed to contain an initial description.

### FR-TLPoC-001: Task List Initialization Flow

* **Trigger:** User initiates processing for the specified **Goal** via the `adk web` interface.
* **Condition:** No **Task List** file exists within the target **Goal** folder.
* **System Action (Observable Behavior):**
    1.  The system creates a new **Task List** file within the **Goal** folder.
    2.  The system populates this **Task List** with a predefined sequence of initial **Tasks** based on an internal template. This template includes standard development **Tasks** and necessary **Tasks** explicitly marked as "HUMAN_IN_THE_LOOP". (The specific contents and format of the template are Level 2 details, outside the scope of this PRD).
* **Output:** The system displays a message in the `adk web` console confirming that the **Task List** has been initialized.

### FR-TLPoC-002: Runnable Task Identification Flow

* **Trigger:** User initiates processing for the specified **Goal** via the `adk web` interface.
* **Condition:** A **Task List** file *already exists* within the target **Goal** folder.
* **System Action (Observable Behavior):**
    1.  The system reads the existing **Task List**.
    2.  The system identifies the sequence of all **Tasks**, starting from the first **Task** (or the **Task** immediately following the last completed one - assumes no completion state tracked *in this PoC*), up until the very next **Task** that is explicitly marked as "HUMAN_IN_THE_LOOP".
* **Output:** The system displays the descriptions of the identified runnable **Tasks** (those occurring before the next "HUMAN_IN_THE_LOOP") as a list in the `adk web` console.

### FR-TLPoC-003: Task List Structure (Conceptual)

* **Description:** The **Task List** represents an ordered sequence of **Tasks** required to complete a **Goal**.
    * Each **Task** has a textual description.
    * **Tasks** requiring user review or action are explicitly identified by the description "HUMAN_IN_THE_LOOP".
    * The system processes **Tasks** based on their order in the list.
    * (Note: The specific file format or storage mechanism is a Level 2 implementation detail).

## 5. Non-Functional Requirements

* **Simplicity & Flexibility:** The primary driver is to demonstrate a mechanism that is conceptually simpler and more flexible for managing **Goal** progression compared to previous file-based status tracking methods.
* **Usability:** The user interacts with the PoC via the `adk web` interface, receiving clear textual feedback on the outcome (list initialized or runnable tasks identified).

## 6. Constraints & Considerations

* **Execution Environment:** This PoC must run within the Google Agent Development Kit (`adk`) `web` interface.
* **Goal Specification:** The specific **Goal** folder path to be processed is pre-configured (e.g., hardcoded) for this PoC.
* **Future Consideration:** The concept of a "generic advanced sub-agent" capable of handling arbitrary **Tasks** from the list is explicitly out of scope for this PoC but may be considered for future iterations.

## 7. Data Requirements (Level 1)

* **Input Data:**
    * User interaction trigger via `adk web`.
    * Pre-configured path to an existing **Goal** folder.
    * An assumed initial description file within the **Goal** folder (content not processed by this PoC).
    * An existing **Task List** file (for Flow 2).
* **Output Data:**
    * Textual messages displayed in the `adk web` console (confirmation or list of Task descriptions).
    * A created **Task List** file within the **Goal** folder (for Flow 1).

## 8. Success Metrics (PoC Specific)

* Successful execution of Flow 1: Given a **Goal** folder without a **Task List**, the system correctly creates the **Task List** file and outputs the initialization confirmation message.
* Successful execution of Flow 2: Given a **Goal** folder with a pre-existing **Task List**, the system correctly identifies and outputs the descriptions of all runnable **Tasks** occurring sequentially before the next "HUMAN_IN_THE_LOOP" **Task**.
* The system operates reliably within the `adk web` environment for both flows.

