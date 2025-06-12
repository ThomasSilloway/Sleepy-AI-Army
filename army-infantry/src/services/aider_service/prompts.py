from src.models.aider_summary import AiderRunSummary
from src.services.aider_service.aider_execution_result import AiderExecutionResult


def get_system_prompt() -> str:

    return f"""
You are an expert at analyzing the output of the 'aider' command-line tool.
Your task is to extract specific information from aider's stdout and stderr and return it in a structured JSON format
that matches the AiderRunSummary Pydantic model.

The JSON schema to use for your response is:
    {AiderRunSummary.model_json_schema()}

Analyze the provided stdout and stderr from an aider execution.
Extract the information to populate these fields accurately.

## Commits
If aider's output clearly indicates a commit, extract the hash and message.
Pay close attention to whether a commit was actually made by aider in *this* run. Do not infer commits.
If aider did not make a commit, the commits field should be an empty list.

## Errors
If aider failed or no specific changes are identifiable, focus on `errors_reported` and `raw_output_summary`.

## Changes Made
`changes_made` - Bulleted list of actual changes applied by aider. Each item should be a clear, concise description of a change. 
   - Make sure to include ` - ` before each line so it becomes a bullet list.
   - When including file names, only include the file name, not the entire path to the file 

Example 1:
 - Added function `foo` to `bar.py`
Example 2:
 - Modified `baz.py` to handle new error condition
Example 3:
 - Removed comment for `_ready()` in `shoot_component.gd`
Example 4: (multiple changes to same file - use a sub-bullet for each change and each line in the list should be its own string in the list)
 - Updated `faz.py` 
    - Handled edge case for `x == 0`
    - Added function `do_something()`
    - Updated `do_something()` to handle new parameter `y`

Bad Example - Avoid doing this:
 - Added function `foo` to `src/utils/bar.py`

## Final instructions
The output MUST be a JSON object matching the AiderRunSummary structure.
"""

def get_user_prompt(result: AiderExecutionResult) -> str:
    return f"""
Please analyze the following output from an 'aider' command execution:

**Aider STDOUT:**
```
{result.stdout}
```

**Aider STDERR:**
```
{result.stderr}
```

Based on this output, provide a JSON summary matching the AiderRunSummary model.
"""
