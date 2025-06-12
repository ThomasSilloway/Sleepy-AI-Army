**Objective:** Create the necessary Pydantic model and LLM prompt required to generate a new "Execution Summary" from a git diff.

### Description of Work

1.  **Create `army-infantry/src/nodes/mission_reporting/models.py`:**
    * Create a new file to house the Pydantic model for the execution summary.
    * Define a new Pydantic class named `ExecutionSummary`.
    * This class should have a single field: `summary: list[str]`.

2.  **Modify `army-infantry/src/nodes/mission_reporting/prompts.py`:**
    * Import the new `ExecutionSummary` model.
    * Create a new function `get_system_prompt()` that returns a string.
    * This prompt should instruct an LLM that it is an expert at summarizing `git diff` output.
    * It must instruct the LLM to return a JSON object that strictly conforms to the `ExecutionSummary.model_json_schema()`.
    * The prompt must specify that the `summary` field should be a bulleted list describing the changes. The formatting must be identical to the `## Changes Made` section from the `aider_service` prompt (see reference file), using ` - ` for each bullet point.

3.  **Create `get_user_prompt(diff: str)` in the same file:**
    * This function will take the combined git diff as a string and place it within a user-facing prompt, asking the LLM to perform the analysis on the provided text.

### Files to Create

* `army-infantry/src/nodes/mission_reporting/models.py`

### Files to Modify

* `army-infantry/src/nodes/mission_reporting/prompts.py`

### Reference Files

* `army-infantry/src/services/aider_service/prompts.py`
