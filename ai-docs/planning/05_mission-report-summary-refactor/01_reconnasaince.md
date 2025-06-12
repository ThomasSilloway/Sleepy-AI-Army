# Reconnaissance Report: Mission Report Summary Refactor

**Objective:** Overhaul the mission reporting system in the `army-infantry` project to provide a more accurate and useful "Execution Summary".

## 1. Initial Analysis

The current "Execution Summary" in the mission report is generated from `aider`'s planned changes, which is misleading if `aider` asks a question and does not commit any code. The core goal is to refactor this process:

1.  **Rename "Execution Summary" to "Aider Summary"**: The existing summary, which includes `aider`'s raw output and any questions it asked, will be renamed and moved to the end of the report for full transparency.
2.  **Create a New, Accurate "Execution Summary"**: This new summary will be based on the actual `git` commits made by `aider` during its run.
3.  **Implementation**: This will be achieved by fetching the commit hashes from the `AiderRunSummary`, retrieving the `git diff` for those hashes, and using an LLM to generate a concise, human-readable summary of the actual changes.

## 2. Intelligence Gaps & Clarifications

Initial analysis identified several ambiguities. The following clarifications have been provided:

* **Mission Report Template Location:** Confirmed to be at `army-infantry/src/templates/mission_report_template.md.j2`.
* **Git Diff Summarization:** All new functionality will be developed within the `army-infantry` project to maintain service autonomy.
* **Handling of No Commits:** If `aider` makes no commits, the new "Execution Summary" will simply state: "No commits submitted by aider".
* **`AiderRunSummary` Model:** The Pydantic model (`AiderRunSummary`) will be updated with a new field to explicitly capture any questions `aider` asked. The corresponding LLM prompt will be modified to populate this field.
* **Summarization Logic Placement**: The logic for generating the new summary from git diffs will be implemented as a new function within `army-infantry/src/nodes/mission_reporting/node.py`, as this is where the data is consumed.

## 3. Revised Battlefield Plan

**Phase 1: Enhance Core Services & Models (Underway)**

* **Task 1.1: Enhance `GitService`**: Add a new method `get_diff_for_commit(commit_hash)` to `src/services/git_service.py`.
* **Task 1.2: Update `Aider` Summary**: Modify `src/models/aider_summary.py` to include a `questions_asked` field and update the LLM prompt in `src/services/aider_service/prompts.py` to extract these questions.

**Phase 2: Integrate New Summary into Mission Reporting**

* **Task 2.1: Implement Summarization Logic**: Create a new private helper function within `src/nodes/mission_reporting/node.py` that takes a list of commit hashes, uses the `GitService` to get the combined diff, and calls the `LlmPromptService` to generate the new "Execution Summary".
* **Task 2.2: Update Reporting Node**: Modify the main function in the `mission_reporting/node.py` to orchestrate the new summarization process and update the data passed to the template renderer.
* **Task 2.3: Update Report Template**: Edit `src/templates/mission_report_template.md.j2` to render the new `execution_summary` at the top and the renamed `aider_summary` (with its full details) at the bottom of the report.

## 4. Files to Modify/Create

* **Modify:**
    * `army-infantry/src/services/git_service.py`
    * `army-infantry/src/models/aider_summary.py`
    * `army-infantry/src/services/aider_service/prompts.py`
    * `army-infantry/src/nodes/mission_reporting/node.py`
    * `army-infantry/src/templates/mission_report_template.md.j2`