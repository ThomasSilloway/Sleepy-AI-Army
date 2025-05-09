# Technical Architecture: PoC7 - LangGraph Orchestration for Initial Document Generation

**Version:** 0.3
**Date:** 2025-05-09

## 1. Overview

This document outlines the technical architecture for Proof-of-Concept 7 (PoC7). The project's primary goal is to validate LangGraph's effectiveness in orchestrating a stateful, multi-step workflow involving the `aider` tool for the initial generation of a `goal-manifest.md` and a `changelog.md`. This serves as a foundational step for the broader "Sleepy Dev Team" project.

The chosen architecture is a **Direct Sequential Workflow** leveraging LangGraph. Key aspects of this architecture include the use of a dedicated `AiderService` for `aider` CLI interactions, a formalized `AppConfig` Pydantic model for static configurations, and dependency injection of these services/configurations into the LangGraph execution environment. The system will also implement a dual-logging mechanism (high-level and detailed logs) and follow a modular Python file structure. The main objectives are to demonstrate `aider` orchestration for document creation, ensure clear observability, and provide insights into LangGraph's capabilities for sequencing, state management, and basic error handling, all within a `uv`-managed Python environment.

## 2. Component Breakdown

The system is comprised of the following major components, which interact to fulfill the project's requirements:

### 2.1. LangGraph Orchestrator
* **Description:** The central component responsible for managing and executing the defined sequence of operations for the PoC. It is implemented as a LangGraph `StateGraph`.
* **Responsibilities:**
    * Define and execute the workflow steps (initialization, input validation, document generation via `aider`, and finalization/error handling) as a sequence of connected nodes.
    * Manage the flow of control and data (via the `WorkflowState`) between different stages of the process.
    * Make decisions based on the outcome of previous steps (e.g., proceeding to the next step or branching to an error handler).
* **Key Interactions:**
    * Manipulates and transitions the `WorkflowState` object.
    * Invokes the `AiderService` to perform document generation tasks.
    * Utilizes the `Logging System` to record its progress and any issues.
    * Accesses configuration parameters from the `AppConfig` (via dependency injection).
    * Is initialized and run by the `Main Execution Script`.

### 2.2. `AppConfig` (Configuration Model)
* **Description:** A Pydantic `BaseModel` that holds all static configurations for the PoC.
* **Responsibilities:**
    * Provide a structured and type-safe way to define and access configuration parameters such as file paths (goal folder, templates, logs), `aider` settings, and logging levels.
* **Key Interactions:**
    * Loaded by the `Main Execution Script` at startup.
    * Injected into the `LangGraph Orchestrator` and potentially the `AiderService` to provide necessary configuration details.

### 2.3. `AiderService` (Tool Interaction Service)
* **Description:** A dedicated Python class abstracting the command-line interactions with the `aider` tool.
* **Responsibilities:**
    * Constructing `aider` CLI commands based on parameters provided by the `LangGraph Orchestrator`.
    * Executing `aider` as a subprocess, managing its lifecycle.
    * **Real-time Output Handling:** Reading `aider`'s `stdout` and `stderr` streams incrementally as output is produced. For each piece of output:
        * Stream it directly to the console for real-time visibility.
        * Record it in the detailed log file via the `Logging System`.
    * Capturing `aider`'s final exit status upon completion.
    * Optionally, collecting the full `stdout` and `stderr` as complete strings for storage in `WorkflowState` or further programmatic use if needed, in addition to the live streaming and logging.
* **Key Interactions:**
    * Instantiated by the `Main Execution Script`.
    * Injected into and invoked by the `LangGraph Orchestrator` when `aider`'s functionality is required for document generation.
    * Uses the `Logging System` to log `aider` command details, its streamed output, and any execution errors.

### 2.4. `WorkflowState` (LangGraph State Object)
* **Description:** A `typing.TypedDict` defining the dynamic data structure that is passed between nodes within the `LangGraph Orchestrator`.
* **Responsibilities:**
    * Hold all information that changes during the workflow, such as paths to generated files, content of input files, results from `aider` calls (exit status, potentially full output strings if explicitly collected), and error messages.
* **Key Interactions:**
    * Read from and updated by various nodes within the `LangGraph Orchestrator` as the workflow progresses.

### 2.5. Logging System
* **Description:** A utility or set of configured Python loggers responsible for generating application logs.
* **Responsibilities:**
    * Provide mechanisms for recording timestamped logs at different levels of detail.
    * Output logs to both the console (for real-time feedback from the orchestrator and `AiderService`) and to two distinct files: one for high-level workflow events and one for detailed operational trace (including the streamed `aider` I/O).
* **Key Interactions:**
    * Configured and initialized by the `LangGraph Orchestrator` (likely in its initial setup node) using settings from `AppConfig`.
    * Utilized by the `LangGraph Orchestrator` and `AiderService` to record events, errors, and diagnostic information.

### 2.6. Main Execution Script (`poc7_script.py`)
* **Description:** The primary Python script that serves as the entry point for running the PoC.
* **Responsibilities:**
    * Loading the `AppConfig`.
    * Instantiating the `AiderService`.
    * Defining the `LangGraph Orchestrator` (nodes and edges).
    * Compiling the LangGraph graph.
    * Preparing the initial `WorkflowState`.
    * Setting up dependency injection for `AppConfig` and `AiderService` into the graph's execution context.
    * Invoking the `LangGraph Orchestrator` to start the workflow.
* **Key Interactions:**
    * Serves as the overall application driver.
    * Coordinates the setup of all major components and initiates the process.