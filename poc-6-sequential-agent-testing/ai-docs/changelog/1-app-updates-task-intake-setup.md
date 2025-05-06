# Changelog: App Updates - Task Intake & Setup (PoC2)

## Overview

This document tracks the implementation progress for Proof-of-Concept 2 (PoC2), focusing on task intake and initial setup using the Google Agent Development Kit (ADK).

## Implemented Features (Based on PRD PoC-2.2 & Change Notes v01-v04)

*   **Project Structure:** Established the core project directories (`src/sleepy_dev_poc`, `shared_libraries`, `shared_tools`, `sub_agents/task_setup_agent`) and essential files (`README.md`, `.env`, `requirements.txt`, `__init__.py`).
*   **Shared Libraries & Tools:**
    *   Implemented `shared_libraries/constants.py` for configuration.
    *   Implemented generalized tools:
        *   `shared_tools/file_system.py`: `create_directory`, `write_file`.
        *   `shared_tools/task_helpers.py`: `get_next_task_number` (including NNN formatting logic).
*   **Single Task Orchestrator (STO) Agent (`src/sleepy_dev_poc/agent.py`, `prompt.py`):**
    *   Implemented as a prompt-driven `LlmAgent`.
    *   Receives user input via `adk web`.
    *   Uses LLM reasoning (guided by `STO_PROMPT`) to analyze input format.
    *   Determines if input refers to an existing task (path or `Prefix_NNN_slug` pattern) or describes a new task.
    *   Outputs JSON (`{"action": "exists", "detail": "<path/name>"}` or `{"action": "delegate", "sub_agent_name": "TaskSetupAgent_PoC2"}`).
    *   ADK framework handles delegation to the sub-agent based on the JSON output.
*   **Task Setup Agent (TSA) (`src/sleepy_dev_poc/sub_agents/task_setup_agent/agent.py`, `prompt.py`):**
    *   Implemented as a prompt-driven `LlmAgent`, invoked by STO for new tasks.
    *   Uses LLM reasoning (guided by `TASK_SETUP_AGENT_PROMPT`) to:
        *   Infer task prefix (`Bug_`, `Feature_`, etc., defaulting to `Task_`).
        *   Generate a concise slug (<= 5 words, hyphenated).
    *   Orchestrates calls to generalized tools via prompt instructions:
        *   Calls `get_next_task_number` tool.
        *   Formats the sequence number to NNN (e.g., `003`).
        *   Constructs the full directory path (`/ai-tasks/Prefix_NNN_slug/`).
        *   Calls `create_directory` tool.
        *   Calls `write_file` tool twice to create `changelog.md` and `task_description.md` (with original input) in the new directory.
*   **Execution:** Designed to run via `adk web` in a local `.venv`.