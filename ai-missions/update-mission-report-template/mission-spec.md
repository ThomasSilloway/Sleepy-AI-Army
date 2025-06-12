**Objective:** Refactor the mission report template to accommodate the new, accurate "Execution Summary" and re-label the old summary for clarity.

### Description of Work

1.  **Modify `army-infantry/src/templates/mission_report_template.md.j2`:**
    * Add a new section at the top of the report under the `## Execution Summary` heading. This section should render the `execution_summary` variable. The summary is expected to be a list of strings, so iterate through it to create a bulleted list.
    * Find the existing `## Execution Summary` section, which contains the `aider_run_summary.changes_made` block.
    * Rename this section's heading to `## Aider Summary`.
    * Ensure this renamed section still correctly renders the `aider_run_summary` details as it did before.
	* Move the `## Aider Summary` section to the bottom of the report.

### Files to Modify

* `army-infantry/src/templates/mission_report_template.md.j2`
