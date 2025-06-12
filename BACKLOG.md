## Update Mission Report Template

**Objective:** Refactor the mission report template to accommodate the new, accurate "Execution Summary" and re-label the old summary for clarity.

## Description of Work

1.  **Modify `army-infantry/src/templates/mission_report_template.md.j2`:**
    * Add a new section at the top of the report under the `## Execution Summary` heading. This section should render the `execution_summary` variable. The summary is expected to be a list of strings, so iterate through it to create a bulleted list.
    * Find the existing `## Execution Summary` section, which contains the `aider_run_summary.changes_made` block.
    * Rename this section's heading to `## Aider Summary`.
    * Ensure this renamed section still correctly renders the `aider_run_summary` details as it did before.
	* Move the `## Aider Summary` section to the bottom of the report.

## Files to Modify

* `army-infantry/src/templates/mission_report_template.md.j2`

## Add Execution Summary Model and Prompt

**Objective:** Create the necessary Pydantic model and LLM prompt required to generate a new "Execution Summary" from a git diff.

## Description of Work

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

## Files to Create

* `army-infantry/src/nodes/mission_reporting/models.py`

## Files to Modify

* `army-infantry/src/nodes/mission_reporting/prompts.py`

## Reference Files

* `army-infantry/src/services/aider_service/prompts.py`
