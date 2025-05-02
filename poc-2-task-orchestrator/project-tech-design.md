# Project Technical Design: PoC2 - Task Intake & Setup

## Overview

This document outlines the technical architecture of the PoC2 system, designed to guide developers in understanding the codebase for feature additions or bug fixes. The system uses the Google Agent Development Kit (ADK) and follows a modular approach with agents and shared tools.

## Core Components & Workflow

1.  **Execution Entry Point:** The application is run using `adk web`.
2.  **Root Agent (`SingleTaskOrchestrator` - STO):**
    *   **Location:** `src/sleepy_dev_poc/agent.py` (Agent definition), `src/sleepy_dev_poc/prompt.py` (LLM instructions - `STO_PROMPT`).
    *   **Type:** `LlmAgent`.
    *   **Function:** Receives user chat input. Uses LLM reasoning (defined in `STO_PROMPT`) to analyze the input format.
    *   **Routing Logic:** Determines if the input refers to an existing task (based on path or `Prefix_NNN_slug` format) or is a new task description. Outputs JSON (`{"action": "exists", ...}` or `{"action": "delegate", ...}`). ADK framework handles delegation based on this output.
3.  **Sub-Agent (`TaskSetupAgent` - TSA):**
    *   **Location:** `src/sleepy_dev_poc/sub_agents/task_setup_agent/agent.py` (Agent definition), `src/sleepy_dev_poc/sub_agents/task_setup_agent/prompt.py` (LLM instructions - `TASK_SETUP_AGENT_PROMPT`).
    *   **Type:** `LlmAgent`.
    *   **Function:** Invoked by STO (via ADK delegation) for new tasks. Orchestrates the creation of the task folder structure and initial files.
    *   **Orchestration Logic:** Uses LLM reasoning (defined in `TASK_SETUP_AGENT_PROMPT`) to:
        *   Infer task prefix and generate a slug.
        *   Call the `get_next_task_number` tool.
        *   Format the number to NNN (three-digit padding).
        *   Construct the full directory path.
        *   Call the `create_directory` tool.
        *   Call the `write_file` tool (twice) for `changelog.md` and `task_description.md`.

## Shared Resources

*   **Constants:** `src/sleepy_dev_poc/shared_libraries/constants.py` - Contains base paths (like `/ai-tasks/`), agent names, model IDs, etc.
*   **Generalized Tools:** Located in `src/sleepy_dev_poc/shared_tools/`. These are designed to be reusable.
    *   `file_system.py`: Contains `create_directory_tool` and `write_file_tool`.
    *   `task_helpers.py`: Contains `get_next_task_number_tool` (handles directory scanning, parsing, and NNN formatting).

## Key Files for Modification/Debugging

*   **STO Logic:** Modify `src/sleepy_dev_poc/prompt.py` (`STO_PROMPT`) to change input analysis or routing rules. Check `src/sleepy_dev_poc/agent.py` for agent definition and sub-agent connections.
*   **TSA Logic:** Modify `src/sleepy_dev_poc/sub_agents/task_setup_agent/prompt.py` (`TASK_SETUP_AGENT_PROMPT`) to change prefix/slug generation, tool usage sequence, or file contents. Check `src/sleepy_dev_poc/sub_agents/task_setup_agent/agent.py` for agent definition and tool registration.
*   **File System Operations:** Modify `src/sleepy_dev_poc/shared_tools/file_system.py` if changes are needed to how directories are created or files are written.
*   **Task Numbering/Naming:** Modify `src/sleepy_dev_poc/shared_tools/task_helpers.py` if changes are needed to how task numbers are determined or folder names are parsed/formatted.
*   **Configuration:** Update `src/sleepy_dev_poc/shared_libraries/constants.py` for path changes, agent name changes, etc. Use `.env` (based on `.env.example`) for API keys.

## Execution Environment

*   Python virtual environment (`.venv`).
*   Dependencies listed in `src/sleepy_dev_poc/requirements.txt`.
*   Run via `adk web`.