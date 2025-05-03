# Architecture Decision Report: Sleepy AI Army - PoC (Task List Mechanism)

**Date:** May 3, 2025
**Project:** Sleepy AI Army - PoC (Task List Mechanism)
**PRD Version:** 1.0-PoC-TaskList
**Status:** Approved Architectural Direction

## 1. Introduction

This report documents the selected high-level architectural approach for the Proof-of-Concept (PoC) focused on implementing a Task List mechanism within the Sleepy AI Army project. The decision follows an analysis of the requirements outlined in the PRD (`v1.0-PoC-TaskList`) and incorporates key development preferences discussed, including:

* Desire for granular, specialized agents.
* Flexibility in selecting AI models based on task complexity (e.g., utilizing `Gemini Flash` for simpler tasks and `Gemini Pro` for more complex ones).
* Emphasis on using generic, reusable tools.
* Defining specific agent behavior and logic primarily through prompts.

## 2. Chosen Architectural Approach

The selected architecture is **Option D: Orchestrator Agent invoking a Granular TaskList Agent as an AgentTool (using Generic Tools).**

This approach utilizes a simple hierarchical agent structure within the Google Agent Development Kit (`ADK`) framework. A primary `Orchestrator Agent` delegates specific tasks to a specialized `TaskList Agent` by invoking it as if it were a standard `ADK` Tool. Both agents leverage a separate, generic tool for file system interactions.

## 3. Conceptual Overview & Flow

The high-level interaction flow is as follows:

* **User Interaction:** The process is initiated via the `adk` web interface.
* **Orchestrator Agent:** Receives the trigger, identifies the `goal_path`, and determines that Task List processing is needed.
* **Delegation via AgentTool:** The `Orchestrator Agent` invokes the specialized `TaskList Agent` as an `AgentTool`, passing the `goal_path` as input.
* **TaskList Agent (as Tool) Execution:** The `TaskList Agent` (running on `Gemini Flash`) executes its prompt-driven logic within its own context:
    * Uses the generic `FileSystemTool` to check if the Task List file exists.
    * If not exists: Uses the tool to write the template (from its prompt) to the file. Formulates an "Initialized" status.
    * If exists: Uses the tool to read the file content. Parses the content based on prompt instructions to find runnable tasks (before `"HUMAN_IN_THE_LOOP"`). Formulates the list of tasks.
* **Result Return:** The `TaskList AgentTool` completes and returns the status message or the list of tasks to the calling `Orchestrator Agent`, just like any other tool call would.
* **Output Presentation:** The `Orchestrator Agent` formats the received result and displays it to the user via the `adk` web console.

## 4. Component Breakdown and Responsibilities

* **Orchestrator Agent:**
    * **Role:** High-level coordination, external interface handling, delegation via tool invocation, final result presentation.
    * **Potential Model:** `Gemini Pro` or `Flash` (depending on future complexity).
    * **Responsibilities:** Interface with `adk` web, identify the need for task list processing, invoke the `TaskList Agent` as an `AgentTool`, receive tool results, format output. Does not handle file I/O or task list parsing directly.
* **TaskList Agent (Implemented as Agent, Used as AgentTool):**
    * **Role:** Specialized execution of task list operations, packaged for invocation as a tool.
    * **Configured Model:** `Gemini Flash` (optimized for cost/speed on this focused task).
    * **Implementation:** Built as a distinct `ADK` Agent but exposed and invoked as an `AgentTool` by the `Orchestrator`.
    * **Responsibilities:** Accept input parameters (`goal_path`) via the tool invocation mechanism, execute specific prompt logic for checking/initializing/reading/parsing the task list file, interact with the generic `FileSystemTool`, handle template content, return structured results via the tool return mechanism. Is not aware of the overall application flow or user interface beyond its defined tool interface.
* **Generic `FileSystemTool` (`ADK` Tool):**
    * **Role:** Provide basic, reusable file system operations.
    * **Methods:** `check_file_exists(path)`, `read_file(path)`, `write_file(path, content)`.
    * **Responsibilities:** Encapsulate direct interaction with the local file system. Used by the `TaskList Agent`.

## 5. Alignment with Preferences

This architecture directly supports the stated development preferences:

* **Granular Agents:** Implements a two-agent structure where one agent acts as a specialized capability (Tool) for the other.
* **Model Flexibility:** Explicitly assigns the cost-effective `Gemini Flash` model to the focused `TaskList AgentTool`.
* **Generic Tools:** Relies on a simple, reusable `FileSystemTool` and leverages the Agent-as-Tool pattern for specialized logic encapsulation.
* **Prompt-Driven Logic:** The core logic for task list manipulation resides within the `TaskList Agent`'s prompt.

## 6. Rationale for Selection

**Option D**, utilizing the Agent-as-Tool pattern, was chosen as it best balances the PoC requirements with the preferred development style. It enables agent granularity and targeted model selection while simplifying inter-agent communication by using the standard `ADK` Tool invocation mechanism. This approach is more idiomatic and potentially less complex to implement than managing separate MAS communication protocols for this PoC. It provides specialization, model optimization, and strong alignment with the desired principles of using generic tools and prompt-driven logic, establishing a flexible and scalable foundation.

## 7. Next Steps

The immediate next step is to proceed with the implementation of this PoC based on the described architecture: defining the `Orchestrator Agent`, the `TaskList Agent` (and configuring it to be used as an `AgentTool`), the generic `FileSystemTool`, and the specific prompts for the agents.
