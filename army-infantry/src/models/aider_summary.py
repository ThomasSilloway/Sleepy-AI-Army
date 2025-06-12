"""Defines the AiderRunSummary Pydantic model."""

from typing import Optional

from pydantic import BaseModel, Field


class AiderRunSummary(BaseModel):
    """
    Summarizes the outcome of an Aider execution run.
    This model captures details about changes made, files affected, and any errors.
    """
    changes_made: list[str] = Field(
        default_factory=list,
        description="Bulleted list of actual changes applied by aider. Each item should be a clear, concise description of a change."\
                    "(e.g., \" - Added function `foo` to `bar.py`\", \" - Modified `baz.py` to handle new error condition\""
    )
    files_modified: Optional[list[str]] = Field(
        default_factory=list,
        description="List of file paths that were modified by aider."
    )
    files_created: Optional[list[str]] = Field(
        default_factory=list,
        description="List of file paths that were newly created by aider."
    )
    errors_reported: Optional[list[str]] = Field(
        default_factory=list,
        description="Any error messages or significant warnings reported by aider."
    )
    raw_output_summary: Optional[str] = Field(
        default=None,
        description="A brief, general summary of what aider did or reported, especially if specific details aren't available or applicable."
    )
    commits: Optional[list[str]] = Field(
        default=None,
        description="list of \"hash - message\" strings for each commit made by aider. If no commit was made by aider, this should be []"
    )
    total_cost: Optional[float] = Field(
        default=None,
        description="""
        The total session cost of the Aider run in USD. Formatted as a float. Default to 0.0 if not found.
        Cost will be near the end of the Aider STDOUT. 
        Ex. `Tokens: 8.0k sent, 374 received. Cost: $0.01 message, $0.04 session.` - total_cost = 0.04, the session cost. 
        If there are multiple lines with this information, choose the one with the highest session cost.
        """
    )
    questions_asked: Optional[list[str]] = Field(
        default_factory=list,
        description="A list of any specific questions that aider asked the user before stopping."
    )
