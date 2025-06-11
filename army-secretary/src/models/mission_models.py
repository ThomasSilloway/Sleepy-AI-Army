"""
Defines Pydantic models used for structuring data within the application,
particularly for interactions with the LLM and representing mission-related information.
"""

from pydantic import BaseModel, Field


class SanitizedMissionFolderInfo(BaseModel):
    """
    Pydantic model to structure the output from the LLM
    when generating a sanitized folder name for a mission.

    Attributes:
        folder_name (str): A filesystem-friendly folder name.
    """
    folder_name: str = Field(
        ...,
        description="A filesystem-friendly folder name for the mission, derived from the task title or description. "
                    "It should be lowercase, with spaces replaced by hyphens, "
                    "and special characters removed or replaced appropriately. "
                    "Example: 'implement-user-login'"
    )
