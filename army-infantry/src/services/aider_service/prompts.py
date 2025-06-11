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
If aider's output clearly indicates a commit, extract the hash and message.
If aider failed or no specific changes are identifiable, focus on `errors_reported` and `raw_output_summary`.
Pay close attention to whether a commit was actually made by aider in *this* run. Do not infer commits.
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
