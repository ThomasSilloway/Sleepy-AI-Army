from pydantic import BaseModel


class AiderExecutionResult(BaseModel):
    """Data class to hold the results of an Aider command execution."""
    exit_code: int
    stdout: str
    stderr: str