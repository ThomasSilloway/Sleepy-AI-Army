"""Pydantic model for application configuration."""
from pydantic import BaseModel
from typing import List, Optional

class AppConfig(BaseModel):
    workspace_root_path: str
    goal_root_path: str
    task_description_filename: str
    manifest_output_filename: str
    changelog_output_filename: str
    log_subdirectory_name: str
    overview_log_filename: str
    detailed_log_filename: str
    # Example of a more complex field if needed later:
    # aider_model: Optional[str] = None 
    manifest_template_filename: str
    changelog_template_filename: str
