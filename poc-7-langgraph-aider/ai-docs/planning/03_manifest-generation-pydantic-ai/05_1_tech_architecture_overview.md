# Technical Architecture: PoC7 - Goal Manifest Generation - Pydantic AI / Jinja

**Version:** 1.1 (Revised based on existing codebase)
**Date:** 2025-05-17

## 1. Overview

This document details the technical architecture for the "PoC7 - Goal Manifest Generation - Pydantic AI / Jinja" feature. This project involves enhancing an existing LangGraph-based orchestration system (evident in the provided `src` directory) to incorporate a new methodology for `goal-manifest.md` generation.

The primary goal is to **refactor the existing `generate_manifest_node`** (located in `src/nodes/manifest_generation.py`). This refactoring will replace its current placeholder or prior logic with a new approach that utilizes:
1.  A new **`LlmPromptService`** to interact with Google Gemini (via `pydantic-ai`) for structured data extraction and inference from a `task-description.md` file. This service will populate a new Pydantic model, `ManifestConfigLLM`, with data like Goal Title and target file path.
2.  A new **`WriteFileFromTemplateService`** to render the `goal-manifest.md` using a Jinja2 template (specified in `AppConfig` as `manifest_template_filename`) and the data obtained from the `LlmPromptService`.

Following successful manifest generation by these new services, the refactored `generate_manifest_node` will then invoke the **existing `ChangelogService`** (from `src/services/changelog_service.py`, which internally uses `AiderService`) to record the manifest creation event in `changelog.md`, as per its current capabilities.

This initiative aligns with the objectives in the Product Requirements Document (`03_prd.md`) and the strategy outlined in `04_brainstorming-gemini-web.md`. Key objectives include validating LangGraph's orchestration of these new services, ensuring reliable document generation adhering to specified formats, and maintaining clear observability through the existing logging setup (`src/utils/logging_setup.py`). The system is executed as a Python script (`src/main.py`) within an environment managed by `uv`.

## 3. Technology Stack

This section lists the chosen languages, frameworks, libraries, tools, and services that constitute the technology stack for the "PoC7 - Goal Manifest Generation - Pydantic AI / Jinja" feature. Versions are specified where critical and known; otherwise, the latest stable versions available at the time of development are assumed.

* **Core Programming Language:**
    * **Python:** Version >=3.9 (>=3.10 recommended, aligning with examples in `uv_project_setup.md` and ensuring compatibility with contemporary features of dependent libraries).

* **Orchestration Framework:**
    * **LangGraph:** For defining and managing the stateful workflow. (Version: Latest stable)

* **LLM Interaction:**
    * **Google Gemini API:** The Large Language Model service used for text analysis and structured data extraction.
        * **Model:** A specific text-based model (e.g., "gemini-1.5-flash-latest" or similar) will be configured in `AppConfig` (e.g., as `gemini_text_model_name`).
    * **`pydantic-ai`:** Python library for interacting with LLMs and parsing their responses into Pydantic models. (Version: Latest stable)

* **Templating Engine:**
    * **Jinja2:** For rendering the `goal-manifest.md` file from a template. (Version: Latest stable)

* **Data Handling, Validation & Configuration:**
    * **Pydantic:** For data validation, settings management (`AppConfig`), and defining structured data models (e.g., `ManifestConfigLLM`). (Version: Latest stable)
    * **OmegaConf:** For loading and managing YAML configuration files (`config.yml`). (Version: Latest stable)
    * **`python-dotenv`:** For loading environment variables (e.g., `GEMINI_API_KEY`) from a `.env` file. (Version: Latest stable)

* **CLI Tools & Associated Services (Invoked by the application):**
    * **`aider`:** CLI tool used by the existing `AiderService` and subsequently by the `ChangelogService` for file modifications, including `changelog.md` updates. (Version: Latest stable of the `aider-chat` client)

* **Version Control System:**
    * **Git:** For source code management and tracking changes in the target repository where documents are generated.

* **Environment & Dependency Management:**
    * **`uv`:** Python package installer and resolver, used for managing project dependencies and the virtual environment, as per `uv_project_setup.md`.

* **Key File Formats:**
    * **YAML:** For application configuration (`config.yml`).
    * **Markdown:** For input (`task-description.md`) and outputs (`goal-manifest.md`, `changelog.md`).
    * **JSON:** Implicitly used for LLM API communications (handled by `pydantic-ai`).

* **Python Standard Libraries (Notable Usage):**
    * **`logging`:** For application-wide logging, configured via `src/utils/logging_setup.py`.
    * **`pathlib`:** For object-oriented file system path manipulations.
    * **`os`:** For interacting with the operating system, including environment variables and path operations.
    * **`datetime`:** For generating timestamps.
    * **`subprocess`:** Used by `AiderService` (for `aider`) and `GitService` (for `git`) to run external commands.
    * **`threading`:** Used within `AiderService` for streaming output from subprocesses.
    * **`asyncio`:** For asynchronous operations, expected to be used by the new `LlmPromptService` when calling `pydantic-ai`'s `model_request` (which is typically `async`).
