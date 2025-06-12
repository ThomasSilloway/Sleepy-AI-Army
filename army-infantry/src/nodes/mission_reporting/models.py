"""Pydantic models for mission reporting."""
from pydantic import BaseModel


class ExecutionSummary(BaseModel):
    """
    A Pydantic model to structure the execution summary generated from a git diff.
    """
    summary: list[str]
