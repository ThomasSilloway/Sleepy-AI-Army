Acknowledged, Commander. Your clarifications have been received and integrated. The operational parameters are now clear.

Here is the updated plan of attack.

### Updated Battlefield Plan

**Objective:** Implement the new `git` commit-based "Execution Summary" and integrate it into the final `mission-report.md`.

**Status:** Phase 1 (Core Service Enhancement) is partially complete. `GitService` and `AiderRunSummary` have been updated. Your clarifications have resolved all outstanding intelligence gaps.

**Updated Next Steps (Phase 2 - Integration):**

1.  **Task 2.1: Define Summarization Model and Prompt:**
    * Create a new Pydantic model in a `models.py` file within `army-infantry/src/nodes/mission_reporting/`. This model, let's call it `ExecutionSummary`, will define the structured output for our summary, containing a single field: `summary: list[str]`.
    * Update `army-infantry/src/nodes/mission_reporting/prompts.py`. Create a system prompt that instructs an LLM to analyze a concatenated `git diff` and return a JSON object matching the `ExecutionSummary` model.
    * The prompt will specify that the `summary` field should be a bulleted list of changes, formatted exactly like the `changes_made` field in the `aider_service` prompt, using ` - ` for bullets and sub-bullets for multiple changes to a single file.

2.  **Task 2.2: Implement Summarization Logic:**
    * In `army-infantry/src/nodes/mission_reporting/node.py`, create a new private helper function.
    * This function will:
        * Accept a list of commit hashes as input.
        * Loop through the hashes, calling `GitService.get_diff_for_commit()` for each and concatenating the diff strings.
        * Call the `LlmPromptService` with the new prompt and the combined diff to generate the structured `ExecutionSummary`.
        * If the LLM call fails or any other error occurs, it will return a default summary: "Unable to generate Execution Summary, see Aider summary below".
        * If no commit hashes are provided, it will return: "No commits submitted by aider".

3.  **Task 2.3: Update Mission Reporting Node:**
    * Modify the main function in `army-infantry/src/nodes/mission_reporting/node.py` to call the new helper function and pass the resulting summary list to the template rendering service.

4.  **Task 2.4: Update Report Template:**
    * Modify the Jinja2 template at `army-infantry/src/templates/mission_report_template.md.j2`.
    * Render the new `execution_summary` at the top of the report.
    * Rename the existing summary section to "Aider Summary".

### Files to Modify/Create

* **Create:**
    * `army-infantry/src/nodes/mission_reporting/models.py`
* **Modify:**
    * `army-infantry/src/nodes/mission_reporting/prompts.py`
    * `army-infantry/src/nodes/mission_reporting/node.py`
    * `army-infantry/src/templates/mission_report_template.md.j2`

---

### Ready-to-Execute Mission Plans

The following mission plans are now fully defined and ready for execution by an Infantry Agent:

* **`mission_plan_01.md`**: Updates the mission report template (`mission_report_template.md.j2`) to render the new `execution_summary` and rename the old summary section to `Aider Summary`.
* **`mission_plan_02.md`**: Creates `army-infantry/src/nodes/mission_reporting/models.py` and updates `army-infantry/src/nodes/mission_reporting/prompts.py` with the new Pydantic model and LLM prompt for generating the execution summary, as per your specifications.

Your orders are clear, Commander. We are prepared to advance on your command.