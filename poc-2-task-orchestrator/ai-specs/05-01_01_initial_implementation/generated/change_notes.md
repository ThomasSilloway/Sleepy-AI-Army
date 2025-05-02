# Change Notes

## v01
- **Description:** Initial implementation of PoC2 project structure and core agent/tool logic based on the technical architecture document (PoC-2.2-TechArch-v3).
- **Details:**
    - Created project directory structure (`src/sleepy_dev_poc`, `shared_libraries`, `shared_tools`, `sub_agents/task_setup_agent`).
    - Implemented `README.md`, `.env`, `.example.env`, `requirements.txt`.
    - Created `__init__.py` files for packages.
    - Implemented `SingleTaskOrchestrator` (STO) agent (`agent.py`, `prompt.py`, placeholder `tools.py`).
    - Implemented shared `constants.py`.
    - Implemented shared tools (`file_system.py` with `create_directory`, `write_file`; `task_helpers.py` with `get_next_task_number`).
    - Implemented `TaskSetupAgent` (TSA) agent (`agent.py` with orchestration logic, `prompt.py`, placeholder `tools.py`).
    - Created `ai-tasks` directory.
## v02
- **Description:** Reviewed initial implementation against PRD and Tech Arch. Refactored SingleTaskOrchestrator (STO) agent.
- **Details:**
    - Reviewed code structure, file contents, and tool implementations.
    - Identified missing conditional routing logic in the STO agent based on LLM analysis output.
    - Refactored `src/sleepy_dev_poc/agent.py` to create a custom `SingleTaskOrchestrator` class inheriting from `LlmAgent`.
    - Implemented custom `_run_async_impl` in `SingleTaskOrchestrator` to:
        - Call the LLM for input analysis.
        - Parse the JSON response.
        - Conditionally delegate to `TaskSetupAgent` if `action` is "new_task".
        - Respond directly if `action` is "exists".
        - Handle errors during LLM call or parsing.
    - Ensured trailing newlines in created files.
## v03
- **Description:** Refactored TaskSetupAgent (TSA) based on feedback to use prompt-driven orchestration instead of custom Python logic.
- **Details:**
    - Rewrote `src/sleepy_dev_poc/sub_agents/task_setup_agent/agent.py` to define `task_setup_agent` as a standard `LlmAgent`, removing the custom class and `_run_async_impl` method.
    - Updated `src/sleepy_dev_poc/sub_agents/task_setup_agent/prompt.py` (`TASK_SETUP_AGENT_PROMPT`) with detailed, step-by-step instructions for the LLM to:
        - Infer prefix and slug.
        - Call `get_next_task_number` tool with correct arguments.
        - Format the returned number (NNN padding).
        - Construct the full task directory path.
        - Call `create_directory` tool.
        - Call `write_file` tool for `changelog.md`.
        - Call `write_file` tool for `task_description.md`.
        - Handle errors and provide appropriate final responses.
    - Ensured the agent definition in `agent.py` correctly references the updated prompt and necessary tools (`get_next_task_number_tool`, `create_directory_tool`, `write_file_tool`).
## v04
- **Description:** Refactored SingleTaskOrchestrator (STO) based on feedback to use prompt-driven routing instead of custom Python logic.
- **Details:**
    - Rewrote `src/sleepy_dev_poc/agent.py` to define `root_agent` as a standard `LlmAgent`, removing the custom `SingleTaskOrchestrator` class and `_run_async_impl` method.
    - Updated `src/sleepy_dev_poc/prompt.py` (`STO_PROMPT`) with detailed instructions for the LLM to:
        - Analyze user input for existing task patterns (`/ai-tasks/` path or `Prefix_NNN_slug` format).
        - Output JSON `{"action": "exists", "detail": "<path/name>"}` if an existing task is detected.
        - Output JSON `{"action": "delegate", "sub_agent_name": "TaskSetupAgent_PoC2"}` if a new task is detected, allowing the ADK framework to handle delegation.
    - Ensured the agent definition in `agent.py` correctly references the updated prompt and the `TaskSetupAgent` sub-agent instance.