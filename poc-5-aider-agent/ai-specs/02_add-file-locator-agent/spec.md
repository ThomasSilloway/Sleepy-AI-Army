# Features: Implement FileLocatorAgent

> Given the Objective, implement every detail of every task for the FileLocatorAgent.

## Objectives

* Implement the FileLocatorAgent which is the second agent in the SmallTweakSequence.
* The agent will take the target\_file\_name (e.g., "utils.py", "src/module/file.go") extracted by the TaskParsingAgent as input. This input will be available from the previous agent's output stored in the session state under `constants.TASK_PARSING_OUTCOME_KEY`.
* It will use a tool to find the full absolute path of this target\_file\_name within the `constants.DEFAULT_WORKSPACE_PATH`.
* It will output the `target_file_full_path` if found, or an error status if not, into the session state under `constants.FILE_LOCATOR_OUTCOME_KEY`.
* Note: This implementation does not yet include the ChangelogAgent or the `_core_check_and_skip_logic` callback. These will be integrated in later stages.

## Context

```python
# Assumed outcome from TaskParsingAgent (available in context.state[constants.TASK_PARSING_OUTCOME_KEY])
# {
#   "status": "success",
#   "target_file_name": "src/app/main.py",
#   "change_description": "Add a new function to calculate fibonacci.",
#   "branch_slug": "add-fibonacci-func"
# }
```

```
/add poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\sub_agents\file_locator\agent.py
/add poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\sub_agents\file_locator\prompt.py
/add poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\sub_agents\file_locator\__init__.py

/add poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\agent.py # To update SmallTweakSequence

/read-only poc-5-aider-agent\ai-docs\03-prd.md
/read-only poc-5-aider-agent\ai-docs\06_tech-architecture.md

/read-only poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\constants\constants.py
/read-only poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\shared_tools\file_system.py
```

## Low-Level Tasks

> Ordered from start to finish

### Implement FileLocatorAgent

* **CREATE** `sleepy_ai_agent\sub_agents\file_locator\__init__.py`.

  * It should contain:

    ```python
    from .agent import file_locator_agent
    ```

* **CREATE** `sleepy_ai_agent\sub_agents\file_locator\prompt.py`.

  * Define `FILE_LOCATOR_AGENT_PROMPT_TEMPLATE`. This prompt will guide the LLM.
  * The prompt should instruct the LLM:

    * Its role is to locate a file.
    * It has access to a tool named `find_file_in_workspace`.
    * This tool takes one argument: `filename` (which is the `target_file_name` obtained from the TaskParsingAgent's output).
    * The tool will automatically search within the pre-configured `DEFAULT_WORKSPACE_PATH`.
    * The tool will return a JSON string: `{"status": "success", "path": "full_absolute_path_if_found"}` or `{"status": "failure", "message": "error_description"}`.
    * Based on the tool's result, the agent must format its own output as a single JSON string:

      ```json
      {
        "status": "success" or "failure",
        "message": "Optional: Human-readable message.",
        "target_file_full_path": "full_absolute_path_or_null_if_not_found"
      }
      ```
    * If `find_file_in_workspace` succeeds, the agent's status is "success", and `target_file_full_path` contains the path.
    * If `find_file_in_workspace` fails, the agent's status is "failure", `target_file_full_path` is null, and the message should reflect the tool's error.
    * Emphasize that the final response must ONLY be the JSON string.
  * Include an example interaction with the tool and the expected agent output for both success and failure scenarios.

* **UPDATE** `sleepy_ai_agent\sub_agents\file_locator\agent.py`.

  * Import `Agent`, `FunctionTool` from `google.adk`.
  * Import `constants` from `sleepy_ai_agent`.
  * Import `FILE_LOCATOR_AGENT_PROMPT_TEMPLATE` from `.prompt`.
  * Import the `find_file_in_directory` function from `sleepy_ai_agent.shared_tools.file_system`.
  * Define a wrapper function `find_file_in_workspace_tool_wrapper(filename: str) -> dict`:

    * This wrapper will call `find_file_in_directory(directory=constants.DEFAULT_WORKSPACE_PATH, filename=filename)`.
    * It ensures the `find_file_in_directory` tool is always called with the correct `DEFAULT_WORKSPACE_PATH` from constants.
  * Create:

    ```python
    find_file_tool = FunctionTool(
        fn=find_file_in_workspace_tool_wrapper,
        description="Finds a specific file within the pre-configured project workspace. Input must be a dictionary {'filename': 'name_of_file_to_find'}."
    )
    ```
  * Define:

    ```python
    file_locator_agent = Agent(
        name=constants.FILE_LOCATOR_AGENT_NAME,
        model=constants.DEFAULT_LLM_MODEL,
        description="Locates the full path of a target file within the project workspace using the target_file_name from the task parsing step.",
        instruction=FILE_LOCATOR_AGENT_PROMPT_TEMPLATE,
        tools=[find_file_tool],
        output_key=constants.FILE_LOCATOR_OUTCOME_KEY
    )
    ```

* **UPDATE** `sleepy_ai_agent\agent.py`.

  * Import `file_locator_agent` from `.sub_agents.file_locator.agent`.
  * Add `file_locator_agent` to the `sub_agents` list of the `small_tweak_sequence`, immediately after `task_parsing_agent`.
