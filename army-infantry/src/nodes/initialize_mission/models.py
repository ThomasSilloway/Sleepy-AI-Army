
import re

from pydantic import BaseModel, Field


class MissionData(BaseModel):
    mission_title: str = Field(..., description="The concise and human-readable title of the mission.")
    git_branch_name: str = Field(..., description="The base name for the git branch, extracted from the mission spec. Should be short, descriptive, and dash-separated (e.g., update-user-profile).")
    files_to_edit: list[str] = Field(default_factory=list, description="A list of file paths that are expected to exist and will be modified by Aider.")
    files_to_read: list[str] = Field(default_factory=list, description="A list of file paths that are expected to exist and will be read, but not modified by Aider.")
    files_to_create: list[str] = Field(default_factory=list, description="A list of file paths for new files that will be created by Aider.")

    def sanitize(self):
        # Make sure git_branch_name is in kebab-case
        # Make sure git_branch_name only contains letters, dashes and forward slash
        self.git_branch_name = self.git_branch_name.lower().replace(" ", "-")
        self.git_branch_name = re.sub(r'[^a-zA-Z0-9/-]', '', self.git_branch_name)

        if not self.git_branch_name:
            raise ValueError("git_branch_name is empty after sanitization.")

        # Sanitize editable_files: strip whitespace and remove empty strings
        if self.files_to_edit is None: # Should not happen with default_factory
            self.files_to_edit = []
        self.files_to_edit = [f.strip() for f in self.files_to_edit if f.strip()]

        if self.files_to_create is None: # Should not happen with default_factory
            self.files_to_create = []
        self.files_to_create = [f.strip() for f in self.files_to_create if f.strip()]

        if self.files_to_read is None: # Should not happen with default_factory
            self.files_to_read = []
        self.files_to_read = [f.strip() for f in self.files_to_read if f.strip()]
