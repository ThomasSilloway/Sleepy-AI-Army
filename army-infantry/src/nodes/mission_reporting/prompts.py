# army-infantry/src/nodes/mission_reporting/prompts.py
"""Prompts for generating execution report summaries from git diffs."""
from .models import ExecutionSummary


def get_system_prompt() -> str:
    """
    Returns the system prompt for the LLM to generate an execution summary.
    """
    return f"""
You are an expert at analyzing and summarizing `git diff` output.
Your task is to provide a concise, bulleted list of changes based on the provided diff.
You must return a JSON object that strictly conforms to the `ExecutionSummary` Pydantic model.

The JSON schema to use for your response is:
{ExecutionSummary.model_json_schema()}

## Summary Formatting
The `summary` field must be a bulleted list describing the changes.
- Each item in the list should be a clear, concise description of a change.
- Each item must start with ` - ` to create a bullet point.
- When including file names, only include the file name, not the entire path.

Example of a valid `summary` list in the JSON output:
[
    " - Added function `foo` to `bar.py`",
    " - Modified `baz.py` to handle new error condition",
    " - Updated `faz.py`",
    "    - Handled edge case for `x == 0`",
    "    - Added function `do_something()`"
]
"""


def get_user_prompt(diff: str) -> str:
    """
    Returns the user prompt containing the git diff for the LLM to analyze.

    Args:
        diff: The git diff string.

    Returns:
        The user-facing prompt.
    """
    return f"""
Please analyze the following `git diff` output and generate an execution summary.

**Git Diff:**
```diff
{diff}
```

Based on this diff, provide a JSON summary conforming to the system prompt's instructions.
"""
