# Technical Architecture: PoC7 - LangGraph Orchestration for Automated Task Execution

**Version:** 1.0-PoC7-Phase2
**Date:** 2025-05-14
**Project Name:** PoC7 - LangGraph Orchestration for Automated Task Execution (Phase 2)

## 1. Overview

This document details the technical architecture for the second phase of Proof-of-Concept (PoC) 7. Building on the foundational document generation capabilities established in Phase 1, this phase's primary goal is to validate LangGraph's effectiveness in orchestrating a stateful, multi-step workflow involving automated file modification. Specifically, this PoC focuses on LangGraph orchestrating the `aider` tool to execute a "Small Tweak" (a defined code/file change), retrieve information about this change using Git commands, and subsequently update the `goal-manifest.md` and `changelog.md` to reflect these actions. This serves as a critical step in demonstrating end-to-end automated task handling for the broader "Sleepy Dev Team" project. The architecture prioritizes demonstrating these core orchestration mechanics, `aider` integration for modifications, and Git interaction, over exhaustive error recovery or advanced UI for this PoC phase.

The chosen architecture is an **Extended Sequential Workflow with Explicit Service Use**, leveraging LangGraph. Key aspects of this architecture include:
* Service-oriented interactions for external tools:
    * A dedicated `AiderService` encapsulates `aider` CLI interactions for both the file modification ("Small Tweak") and updates to the `goal-manifest.md`.
    * A new `GitService` encapsulates `git` CLI interactions (via `subprocess`) to retrieve information like commit hashes and summaries.
    * The existing `ChangelogService` (which may utilize `AiderService` or direct methods) handles structured updates to the `changelog.md` after significant events (tweak execution, manifest update).
* A formalized `AppConfig` Pydantic model for static configurations (as in Phase 1).
* Dependency injection of services and configurations into LangGraph nodes via `RunnableConfig` (as in Phase 1).
* A dual-logging mechanism (`overview.log` and `detailed.log`) with specified timestamp formats (as in Phase 1).
* Adherence to a modular Python file structure.

The main objectives are to demonstrate `aider` orchestration for automated file modifications, utilize `GitService` for capturing change metadata, ensure the `goal-manifest.md` is updated to reflect these changes, maintain comprehensive changelog entries, ensure clear observability, and provide further insights into LangGraph's capabilities for sequencing complex actions and managing state.

## 3. Technology Stack
*(Following your example's numbering)*

The following technologies are chosen for the development and execution of this PoC phase:

* **Primary Language:**
    * **Python:** Version 3.9 or higher (aligning with LangGraph best practices and previous phase setup).
* **Orchestration Framework:**
    * **LangGraph:** The core Python library for building the stateful, multi-step workflow.
* **Core Python Libraries:**
    * **Pydantic:** Utilized for defining the `AppConfig` data model.
    * **Python `subprocess` module:** Employed by `AiderService`, `ChangelogService` (if it calls `aider`), and the new `GitService` to interact with their respective command-line tools (`aider`, `git`).
    * **Python `logging` module:** Standard library module for the `Logging System`.
    * **Python `typing` module:** Used for type hints, including `TypedDict` for `WorkflowState`.
    * **Python `datetime` module:** Used for generating timestamps.
    * **Python `os` module:** Used for path manipulations and checks (e.g., in `GitService`).
* **External Tools & Services (CLI-based):**
    * **`aider`:** AI-powered tool used as a service by `AiderService`.
    * **`git`:** Distributed version control system, interacted with via the `GitService`.
    * **`uv`:** Python packaging tool for environment management and script execution.
* **Development & Version Control:**
    * **Git:** For source code version control of this PoC project itself.

