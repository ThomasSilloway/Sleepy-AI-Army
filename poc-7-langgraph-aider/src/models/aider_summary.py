"""Defines the AiderRunSummary Pydantic model."""

from typing import List, Optional # Use List for compatibility if needed, but prefer list per CONVENTIONS.md

from pydantic import BaseModel, Field


class AiderRunSummary(BaseModel):
    """
    Summarizes the outcome of an Aider execution run.
    This model captures details about changes made, files affected, and any errors.
    """
    changes_made: List[str] = Field(
        default_factory=list,
        description="Bulleted list of actual changes applied by aider. Each item should be a clear, concise description of a change."
    )
    commit_hash: Optional[str] = Field(
        default=None,
        description="The git commit hash if aider made a commit during this run."
    )
    files_modified: Optional[List[str]] = Field(
        default_factory=list,
        description="List of file paths that were modified by aider."
    )
    files_created: Optional[List[str]] = Field(
        default_factory=list,
        description="List of file paths that were newly created by aider."
    )
    errors_reported: Optional[List[str]] = Field(
        default_factory=list,
        description="Any error messages or significant warnings reported by aider."
    )
    raw_output_summary: Optional[str] = Field(
        default=None,
        description="A brief, general summary of what aider did or reported, especially if specific details aren't available or applicable."
    )
    commit_message: Optional[str] = Field(
        default=None,
        description="The commit message if aider made a commit."
    )

    class Config:
        # Example of how to add example data for schema generation (optional)
        schema_extra = {
            "example": {
                "changes_made": [
                    "Refactored `process_data` function in `utils.py` for clarity.",
                    "Added new unit tests for `process_data`."
                ],
                "commit_hash": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
                "files_modified": ["src/utils.py", "tests/test_utils.py"],
                "files_created": [],
                "errors_reported": [],
                "raw_output_summary": "Aider refactored one function and added tests. Committed changes.",
                "commit_message": "Refactor: Improve clarity of process_data and add tests"
            }
        }
