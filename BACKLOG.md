## Execution Summary Refactor

### Objective
To refactor the mission reporting system to generate a new, accurate "Execution Summary" based on `git` commits. This involves modifying the state management to pass only necessary data, and implementing a pure function within the reporting node to handle the summary generation.

### Phase 1: State & Context Preparation

#### Task 1.1: Finalize MissionContext Model
- **File to Modify:** `army-infantry/src/graph_state.py`
- **Required Changes:**
    - In the `MissionContext` Pydantic model:
        - Remove the `execution_summary: Optional[str]` field entirely.
        - Add the following fields to store a structured summary from Aider's execution:
            ```python
            aider_changes_made: list[str] = Field(default_factory=list)
            aider_questions_asked: list[str] = Field(default_factory=list)
            ```

#### Task 1.2: Finalize Context Population
- **File to Modify:** `army-infantry/src/nodes/code_modification/node.py`
- **Required Changes:**
    - In the `_update_mission_context_from_aider_summary` function:
        - Remove the line that sets the now-deleted `mission_context.execution_summary`.
        - Add logic to populate the new `MissionContext` fields from the `aider_summary` object:
            ```python
            mission_context.aider_changes_made = aider_summary.changes_made
            mission_context.aider_questions_asked = aider_summary.questions_asked
            ```

### Phase 2: Final Implementation

#### Task 2.1: Implement Pure Summarization Helper
- **File to Modify:** `army-infantry/src/nodes/mission_reporting/node.py`
- **Details:**
    - Create a new private `async` helper function within the file.
    - **Function Signature:** The function must not accept the `MissionContext`. It should be a pure utility function with a signature similar to:
        ```python
        from src.app_config import AppConfig
        from src.services.git_service import GitService
        from src.services.llm_prompt_service import LlmPromptService
        from typing import Optional

        async def _generate_execution_summary(
            commit_hashes: list[str],
            git_service: GitService,
            llm_service: LlmPromptService,
            app_config: AppConfig
        ) -> tuple[list[str], float]:
        ```
    - **Logic:**
        - If the `commit_hashes` list is empty, return `(["No commits submitted by aider"], 0.0)`.
        - Use the provided `git_service` instance to fetch and concatenate the `git diff` for each commit hash.
        - Use the provided `llm_service` instance to call the LLM with the appropriate prompts to summarize the concatenated diff.
        - If the LLM call fails, return `(["Unable to generate Execution Summary, see Aider summary below"], cost or 0.0)`.
        - On success, return a tuple containing the `list[str]` of summary points from the parsed LLM response and the `float` cost of the API call.

#### Task 2.2: Integrate into the Main Reporting Node
- **File to Modify:** `army-infantry/src/nodes/mission_reporting/node.py`
- **Details:**
    - In the main `_mission_reporting` function:
        - **Parse Hashes:** Before building `template_data`, parse the list of commit hashes from `mission_context.git_summary`.
        - **Instantiate Services:** Create instances of the `GitService` and `LlmPromptService`.
        - **Call Helper:** `await` the new `_generate_execution_summary` helper function, passing the required arguments.
        - **Process Results:** Receive the `summary_list` and `cost` from the helper's return tuple.
        - **Update Context:** Add the `cost` to `mission_context.total_cost_usd`.
        - **Build Report Data:** When creating the `template_data` dictionary, add the locally generated `summary_list` to it under the key `"execution_summary"`. Ensure the other required fields from `mission_context` (like `aider_changes_made` and `aider_questions_asked`) are also passed to the template.

### Reference Files
The executing agent should refer to the following files for context on service method signatures and data models:
- `army-infantry/src/services/git_service.py`
- `army-infantry/src/services/llm_prompt_service.py`
- `army-infantry/src/nodes/mission_reporting/prompts.py`
- `army-infantry/src/nodes/mission_reporting/models.py`
