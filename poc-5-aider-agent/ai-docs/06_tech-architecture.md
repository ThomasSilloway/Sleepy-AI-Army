# Technical Architecture: Sleepy AI Army - PoC 5 (Aider Small Tweak Integration)

**Version**: 1.0
**Date**: 2025-05-06

## 1. Overview

This document details the technical architecture for Proof-of-Concept 5 (PoC 5) of the "Sleepy AI Army" project. The goal is to validate a core workflow for automated, small, single-file code modifications using the aider tool in a controlled Google Agent Development Kit (ADK) environment.

It includes:

* Git branch management
* Task parsing
* File location
* Aider execution
* Logging/reporting

### Architecture Summary

* Based on "Approach 3" refined via `05-architecture-brainstorming-feedback.md`
* Uses a RootAgent with a SequentialAgent (`SmallTweakSequence`)
* Reuses error handling/conditional skipping from PoC 6

### Error Handling Pattern

* Agents output structured JSON strings using `output_key` from `constants.py`
* `before_agent_callback` functions (created via `functools.partial`) inspect prior agent outputs
* If skipped, current agent updates state accordingly
* Final agent (`ReportingAgent`) always runs to summarize and verify process
* Centralized logging via `ChangelogAgent`

## 2. Component Breakdown

### RootAgent (Type: LlmAgent)

* **File**: `sleepy_ai_agent/agent.py`
* **Role**: Triggers `SmallTweakSequence`; returns final summary
* **Model**: `constants.DEFAULT_LLM_MODEL`

### SmallTweakSequence (Type: SequentialAgent)

* **File**: `sleepy_ai_agent/agent.py`
* **Sub-agents**:

  1. TaskParsingAgent
  2. FileLocatorAgent
  3. GitSetupAgent
  4. AiderExecutionAgent
  5. ReportingAgent
* **Callback config**: Uses `functools.partial(_core_check_and_skip_logic)` with state keys from `constants.py`

### TaskParsingAgent

* **File**: `sleepy_ai_agent/sub_agents/task_parsing/agent.py`
* **Role**: Parses `task_description.md` for `target_file_name`, `change_description`, `branch_slug`
* **Tools**: `FileTool`, `ChangelogAgent`
* **Output key**: `constants.TASK_PARSING_OUTCOME_KEY`

### FileLocatorAgent

* **File**: `sleepy_ai_agent/sub_agents/file_locator/agent.py`
* **Role**: Locates file path from parsed output
* **Tools**: `FileTool`, `ChangelogAgent`
* **Output key**: `constants.FILE_LOCATOR_OUTCOME_KEY`
* **Callback**: Checks `TASK_PARSING_OUTCOME_KEY`

### GitSetupAgent

* **File**: `sleepy_ai_agent/sub_agents/git_setup/agent.py`
* **Role**: Creates feature branch based on `branch_slug`
* **Tools**: `GitTool`, `ChangelogAgent`
* **Output key**: `constants.GIT_SETUP_OUTCOME_KEY`
* **Callback**: Checks `FILE_LOCATOR_OUTCOME_KEY`

### AiderExecutionAgent

* **File**: `sleepy_ai_agent/sub_agents/aider_execution/agent.py`
* **Role**: Runs aider on target file with description
* **Tools**: `AiderTool`, `ChangelogAgent`
* **Output key**: `constants.AIDER_EXECUTION_OUTCOME_KEY`
* **Callback**: Checks `GIT_SETUP_OUTCOME_KEY`

### ReportingAgent

* **File**: `sleepy_ai_agent/sub_agents/reporting/agent.py`
* **Role**: Always runs; summarizes outcomes and compares with `changelog.md`
* **Tools**: `ChangelogAgent`, `FileTool`

### ChangelogAgent

* **File**: `sleepy_ai_agent/sub_agents/changelog/agent.py`
* **Role**: Appends timestamped log entries to `changelog.md`
* **Tools**: `FileTool`
* **Config**: `disallow_transfer_to_parent=True`, `disallow_transfer_to_peers=True`
* **Model**: `constants.CHANGELOG_LLM_MODEL`

### Tools

* **FileTool**: `shared_tools/file_system.py` — read/write/find/append
* **GitTool**: `sub_agents/git_setup/tools.py` — git operations
* **AiderTool**: `sub_agents/aider_execution/tools.py` — run aider

### Callbacks

* **Core logic**: `_core_check_and_skip_logic` in `callbacks/callbacks.py`
* **Wrapped via**: `functools.partial` in `agent.py`

### Constants

* **File**: `constants/constants.py`
* **Includes**: Output keys, filenames, default paths, model names

## 3. Technology Stack

### Languages & Frameworks

* Python 3.9+
* Google ADK (for Vertex AI)

### ADK Components

* **Agents**:

  * `LlmAgent` (core agent type)
  * `SequentialAgent` (sequence orchestrator)
* **Tools**:

  * `FunctionTool`
  * `AgentTool`
* **Callbacks**:

  * `before_agent_callback`
  * `functools.partial`
  * `CallbackContext`, `ToolContext`
* **State**:

  * `context.state`
  * `output_key`
* **Execution**:

  * `Runner`
  * `InMemorySessionService`

### Models

* `constants.DEFAULT_LLM_MODEL` (e.g., gemini-2.0-flash)
* `constants.CHANGELOG_LLM_MODEL`

### External Tools

* CLI: `git`, `aider`
* Libraries: `os`, `json`, `subprocess`, `datetime`, `functools`, `re`

### Dev Environment

* Virtualenv (`venv`)
* `.env` config
* `requirements.txt`

## Data Models / Structures

This section defines the key data structures, formats, and conventions used for communication between agents, tool interactions, and overall state management within PoC 5.

### Session State (`context.state`)

* Stores JSON strings representing structured outcomes from agents.
* **State Keys**: Defined in `sleepy_ai_agent/constants/constants.py` (e.g., `constants.TASK_PARSING_OUTCOME_KEY`).

#### Standard Agent Outcome JSON Structure

Agents (e.g., `TaskParsingAgent`, `FileLocatorAgent`, `GitSetupAgent`, `AiderExecutionAgent`) output a JSON string:

```json
{
  "status": "success" | "failure",
  "message": "Optional: Human-readable message."
  // Agent-specific result fields, e.g.:
  // For TaskParsingAgent: "target_file_name", "change_description", "branch_slug"
  // For FileLocatorAgent: "target_file_full_path"
  // For GitSetupAgent: "branch_name"
  // For AiderExecutionAgent: "details"
}
```

* `TaskParsingAgent` must output `"status": "failure"` if essential fields cannot be extracted.

#### Standard "Skipped" JSON Structure (set by callbacks)

```json
{
  "status": "skipped",
  "message": "Skipped due to [reason]."
}
```

### Prompt Injection for ReportingAgent

* Uses ADK's `{state_key_from_constants}` syntax to receive prior JSON string outcomes.

### `task_description.md` (Source of Task Input)

* Located in `Goal` folder (path from `constants.DEFAULT_WORKSPACE_PATH` and `constants.DEFAULT_GOAL_FOLDER_NAME`).
* Contains literal string (user's backlog item).
* Parsed by `TaskParsingAgent` for `target_file_name`, `change_description`, and `branch_slug`.

### `changelog.md` (Output File)

* Located in `Goal` folder. Maintained by `ChangelogAgent`.
* Format:

```markdown
## <Calling Agent Name from constants.py>
YYYY-MM-DD HH:MM:SS

- <Detail 1>
- <Detail 2>
```

* `ReportingAgent` reads this to check for inconsistencies.

### Tool Input/Output (Custom FunctionTools)

* Return format:

```python
{"status": "success" | "failure", "result": <data> | "message": <error>}
```

### `constants.py` File Content

* Defines:

  * State output keys
  * File names (`TASK_DESCRIPTION_FILE`, `CHANGELOG_FILE`)
  * Pre-configured paths (`DEFAULT_WORKSPACE_PATH`, `DEFAULT_GOAL_FOLDER_NAME`)
  * Agent friendly names
  * Default LLM model names

## Non-Functional Requirements (NFR) Fulfillment

* **Reliability**: Callback skipping, secure CLI tool wrappers, robust JSON handling
* **Accuracy**: `ChangelogAgent` logging, state as machine-readable source of truth, `ReportingAgent` cross-referencing
* **Observability**: ADK web UI (events, state), `changelog.md`, optional Python logging
* **Maintainability**: Modular agents, centralized constants, reusable callback logic, generic `FileTool`
* **Simplicity**: Focused agents, standardized PoC6-style flow control

## Key Interaction Flows

### A. Successful ("Happy Path") Execution Flow

1. **Initiation**: User triggers `RootAgent` via ADK web
2. **Sequence**: `RootAgent` invokes `SmallTweakSequence`
3. **`TaskParsingAgent`**: Parses `task_description.md` → success JSON → `ChangelogAgent`
4. **`FileLocatorAgent`**: Parses success → finds file → success JSON → `ChangelogAgent`
5. **`GitSetupAgent`**: Parses success → creates branch → success JSON → `ChangelogAgent`
6. **`AiderExecutionAgent`**: Parses success → runs aider → success JSON → `ChangelogAgent`
7. **`ReportingAgent`**: Always runs → parses state/changelog → outputs summary → `ChangelogAgent`
8. **Completion**: Sequence and `RootAgent` complete with summary

### B. Execution Flow with Failure (e.g., `FileLocatorAgent` Fails)

1. Same as above up to `FileLocatorAgent`
2. **`FileLocatorAgent`**: Fails → failure JSON → `ChangelogAgent`
3. **`GitSetupAgent`**: Skipped via callback → skipped JSON
4. **`AiderExecutionAgent`**: Skipped via callback → skipped JSON
5. **`ReportingAgent`**: Runs → detects failure/skips → outputs failure summary → `ChangelogAgent`
6. **Completion**: Sequence and `RootAgent` conclude with failure summary

## Error Handling Strategy

* **Mechanism**: `before_agent_callback` pattern (via `_core_check_and_skip_logic`)
* **Agent Output**: JSON with `"status": "success" | "failure"`
* **Tool Output**: Dict with `status` and `result`/`message`
* **Callback Action**: On `failure`/`skipped`/invalid JSON → write skipped JSON → prevent execution
* **Finalizer**: `ReportingAgent` always runs → reads all states + changelog → generates final report
* **ChangelogAgent**: Maintains audit log
* **LLM Output**: Robust JSON parsing. Failures treated as step failure.

## Proposed Folder and File Structure

```
/sleepy-ai-poc5                  # Project Root Directory
├── .env
├── .env.example
├── README.md
├── requirements.txt
└── src/
    └── sleepy_ai_agent/         # Main Python package
        ├── __init__.py
        ├── agent.py             # RootAgent, SmallTweakSequence, callbacks
        ├── constants/
        │   ├── __init__.py
        │   └── constants.py
        ├── callbacks/
        │   ├── __init__.py
        │   └── callbacks.py     # _core_check_and_skip_logic
        ├── shared_tools/
        │   ├── __init__.py
        │   └── file_system.py
        └── sub_agents/
            ├── task_parsing/
            │   ├── __init__.py
            │   ├── agent.py
            │   └── prompt.py
            ├── file_locator/
            │   ├── __init__.py
            │   ├── agent.py
            │   └── prompt.py
            ├── git_setup/
            │   ├── __init__.py
            │   ├── agent.py
            │   ├── prompt.py
            │   └── tools.py     # GitTool
            ├── aider_execution/
            │   ├── __init__.py
            │   ├── agent.py
            │   ├── prompt.py
            │   └── tools.py     # AiderTool
            ├── reporting/
            │   ├── __init__.py
            │   ├── agent.py
            │   └── prompt.py
            └── changelog/
                ├── __init__.py
                ├── agent.py
                └── prompt.py
```

## Risks & Dependencies

### Risks

* **LLM JSON Output**: Mitigated via robust parsing, clear prompting
* **TaskParsing Accuracy**: Mitigated via failure status + prompt design
* **Tool Security**: Validated inputs, limited execution scope
* **Tool Reliability**: Subprocess wrapper resilience
* **Callback Complexity**: Centralized logic, constants usage, testing
* **Path Config Management**: Clear documentation, constants.py
* **State Key Consistency**: constants.py

### Dependencies

* Google Agent Development Kit (ADK)
* Python 3.9+
* External CLI tools: `git`, `aider`
* LLM API access (e.g., `gemini-2.0-flash`)
* File system structure with `Goal/task_description.md`
