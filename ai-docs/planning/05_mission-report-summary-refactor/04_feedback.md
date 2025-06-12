We completed two more missions and made these updates to further the goal:

# Mission 1
 - Created `ExecutionSummary` model in `models.py`
 - Updated `prompts.py`
    - Added `get_system_prompt()` function
    - Added `get_user_prompt(diff: str)` function
    - Added import for the `ExecutionSummary` model

## Files Modified

- `army-infantry/src/nodes/mission_reporting/prompts.py`

## Files Created

- `army-infantry/src/nodes/mission_reporting/models.py`

# Mission 2

## Execution Summary

 - Updated `mission_report_template.md.j2`
    - Modified the `Execution Summary` section to render the `execution_summary` variable as a bulleted list.
    - Added a new `Aider Summary` section at the bottom of the template.

## Files Modified

- `army-infantry\src\templates\mission_report_template.md.j2`

