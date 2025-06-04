
import re

from pydantic import BaseModel, Field


class MissionData(BaseModel):
    mission_title: str = Field(..., description="The concise and human-readable title of the mission.")
    git_branch_name: str = Field(..., description="The base name for the git branch, extracted from the mission spec. Should be short, descriptive, and dash-separated (e.g., update-user-profile).")

    @staticmethod
    def sanitize(self):
        # Make sure git_branch_name is in kebab-case
        # Make sure git_branch_name only contains letters, dashes and forward slash
        self.git_branch_name = self.git_branch_name.lower().replace(" ", "-")
        self.git_branch_name = re.sub(r'[^a-zA-Z0-9/-]', '', self.git_branch_name)

        if not self.git_branch_name:
            raise ValueError("git_branch_name is empty after sanitization.")
