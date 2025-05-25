# AI Coding Agent Specification: Post-Refactor Enhancements for PoC 8

This document outlines improvements for the `poc-8-backlog-to-goals` project based on a recent CTO critique. The goal is to elevate the codebase from a B grade to an A+ grade by addressing identified shortcomings.

## Aspect 1: Comprehensive Testing

**Problem:**
The application currently lacks automated tests, which is critical for ensuring reliability, maintainability, and safe refactoring. This is the single biggest factor preventing an A+ grade.

**Solution:**
Implement a comprehensive test suite covering unit and integration tests for all key components of the application. Utilize `pytest` and `pytest-asyncio`.

**High-Level Implementation Plan:**
1.  **Setup Test Environment:**
    *   Ensure `pytest` and `pytest-asyncio` are in `pyproject.toml` (already present).
    *   Create a `tests/` directory at `poc-8-backlog-to-goals/tests/`.
    *   Configure `pytest.ini_options` in `pyproject.toml` to include `src` in `pythonpath` (already present).
2.  **Test `AppConfig` (`tests/test_config.py`):**
    *   Mock `os.getenv` and `yaml.safe_load`.
    *   Test successful loading of valid YAML and .env data.
    *   Test derivation of `backlog_file_path` and `goals_output_directory`.
    *   Test validation logic: missing keys, invalid paths (non-existent directory for `goal_git_path`, non-existent file for `backlog_file_path`).
    *   Test `FileNotFoundError` for missing `config.yaml`.
3.  **Test `LlmPromptService` (`tests/services/test_llm_prompt_service.py`):**
    *   Mock `pydantic_ai.direct.model_request`.
    *   Test `get_structured_output` with valid inputs:
        *   Successful response and parsing into `SanitizedGoalInfo`.
        *   Correct handling of different message roles.
        *   Correct application of `model_parameters`.
    *   Test error conditions: missing API key, missing `llm_model_name`, LLM call failure, response parsing failure.
    *   Test `_strip_json_fencing` with various inputs (with/without fencing, different casing).
4.  **Test `BacklogProcessor` (`tests/services/test_backlog_processor.py`):**
    *   Mock `LlmPromptService` to control `sanitize_title_with_llm` output.
    *   Mock file system operations (`open`, `os.makedirs`, `os.path.exists`).
    *   Test `parse_task_from_section`: valid inputs, sections without `##` title, empty sections.
    *   Test `sanitize_title_with_llm`:
        *   When LLM provides a name.
        *   When LLM fails and fallback (basic sanitization + timestamp) is used.
    *   Test `process_backlog_file`:
        *   Successful processing of a sample backlog file.
        *   Correct folder and file creation.
        *   Handling of file not found for backlog.
        *   Handling of empty backlog file or backlog with no valid tasks.
5.  **Test `goal_models.py` (`tests/models/test_goal_models.py`):**
    *   Test `SanitizedGoalInfo` model validation (e.g., instantiation, field requirements if any become more complex).
6.  **Integration Test (`tests/test_main_flow.py`):** (Optional, but recommended)
    *   Test the `main.run()` flow with a sample `config.yaml`, `.env` (mocked), and `backlog.md`.
    *   Verify that directories and files are created as expected.
    *   Mock external LLM calls.

## Aspect 2: Enhanced Error Handling & Resilience

**Problem:**
Current error handling is basic. Some errors are only logged, and the application might not always exit gracefully or provide sufficiently detailed feedback for all failure modes.

**Solution:**
Improve error handling globally and in specific services to make the application more robust and provide clearer diagnostics.

**High-Level Implementation Plan:**
1.  **Global Error Handling (`src/main.py`):**
    *   Wrap the main logic in `run()` within a `try...except Exception as e:` block.
    *   Log the exception with a traceback and exit gracefully with a non-zero status code.
2.  **`LlmPromptService` Error Handling (`src/services/llm_prompt_service.py`):**
    *   Catch more specific exceptions from `pydantic_ai` (e.g., `ModelRequestError`, API connection issues if distinguishable).
    *   Log these specific errors with more context before re-raising or returning `None`.
3.  **`BacklogProcessor` Error Reporting (`src/services/backlog_processor.py`):**
    *   In `process_backlog_file`, if `parse_task_from_section` returns `None` (due to malformed section), collect these instances (e.g., line number or first 50 chars of section) in a list.
    *   After processing, if this list is not empty, log a summary of parsing issues.
    *   Improve fallback for `folder_name` generation to ensure it's always non-empty and unique (current timestamped fallback is good, ensure it's robustly applied).

## Aspect 3: Configuration & Initialization Refinements

**Problem:**
Configuration, while improved, has minor areas for increased robustness and clarity (e.g., `default_llm_model_name` handling).

**Solution:**
Refine `AppConfig` and how configurations like `default_llm_model_name` are handled. Consider using Pydantic-Settings for more advanced configuration management.

**High-Level Implementation Plan:**
1.  **`default_llm_model_name` (`src/config.py`, `src/services/backlog_processor.py`):**
    *   Add `default_llm_model_name` as an optional field in `config.yaml` with a default value in `AppConfig` itself.
    *   Update `AppConfig` to load this, providing a clear default if not in YAML (e.g., "gemini-1.5-flash-latest").
    *   Remove the `getattr` fallback from `BacklogProcessor`; directly use `app_config.default_llm_model_name`.
    *   Add validation in `AppConfig.validate()` for `default_llm_model_name` if needed (e.g., ensure it's a non-empty string).
2.  **(Optional) Explore `pydantic-settings` (`src/config.py`):**
    *   Investigate replacing the manual YAML + dotenv loading with `pydantic-settings.BaseSettings`.
    *   This would allow defining config sources (env files, environment variables, YAML) more declaratively. This is a larger change, can be deferred if time-constrained.

## Aspect 4: Code Structure & Prompt Management

**Problem:**
Some methods are long, and LLM prompts are embedded directly in the code, making them harder to manage. Fallback logic for folder names is slightly duplicated.

**Solution:**
Refactor for better readability and maintainability by breaking down long methods and externalizing LLM prompts. Consolidate fallback logic.

**High-Level Implementation Plan:**
1.  **Refactor `BacklogProcessor.process_backlog_file` (`src/services/backlog_processor.py`):**
    *   Extract logic for reading file content into a helper method.
    *   Extract logic for handling a single task section (parsing, sanitizing name, creating folder/file) into a helper method.
2.  **Externalize LLM Prompts (`src/services/backlog_processor.py`, new `src/prompts.py`):**
    *   Create a new file, e.g., `src/prompts.py`.
    *   Define prompt templates as constants or functions in `prompts.py`. For example:
        ```python
        # src/prompts.py
        SANITIZE_FOLDER_NAME_SYSTEM_PROMPT = "You are an expert assistant..."
        def get_sanitize_folder_name_user_prompt(task_description: str, task_title: str = "") -> str:
            return f"Given the following task details..."
        ```
    *   Import and use these prompts in `BacklogProcessor.sanitize_title_with_llm`.
3.  **Consolidate Fallback Folder Name Logic (`src/services/backlog_processor.py`):**
    *   Ensure the fallback logic (basic sanitization + timestamp) in `sanitize_title_with_llm` is robust and used consistently.
    *   Remove the secondary fallback logic from `process_backlog_file` as `sanitize_title_with_llm` should always return a valid (fallback) name.

## Aspect 5: Constants and Naming

**Problem:**
Magic strings like "task-description.md" are used directly in code.

**Solution:**
Define such strings as constants for better maintainability and clarity.

**High-Level Implementation Plan:**
1.  **Define Constants (`src/services/backlog_processor.py` or `src/constants.py`):**
    *   In `BacklogProcessor` or a new `src/constants.py` file, define:
        `TASK_DESCRIPTION_FILENAME = "task-description.md"`
    *   Use this constant in `BacklogProcessor` when creating the task description file.

## Aspect 6: Docstrings and Typing (Final Pass)

**Problem:**
While generally good, a final review ensures completeness.

**Solution:**
Perform a final pass over the codebase to ensure all public modules, classes, functions, and methods have comprehensive docstrings and precise type hints.

**High-Level Implementation Plan:**
1.  **Review and Update Docstrings:** Check all components for clarity, correctness, and completeness of docstrings (args, returns, purpose).
2.  **Review and Update Type Hints:** Ensure all functions and methods have type hints for parameters and return values. Use `from typing import ...` as needed.
3.  **(Optional) Run MyPy:** Add `mypy` to dev dependencies and run it to catch any static typing errors.
