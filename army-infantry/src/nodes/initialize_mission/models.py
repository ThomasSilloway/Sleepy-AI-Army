
from pydantic import BaseModel, Field


class MissionData(BaseModel):
    mission_title: str = Field(..., description="The concise and human-readable title of the mission.")
