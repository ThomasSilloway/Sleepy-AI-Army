"""Pydantic model for application configuration."""
from pydantic import BaseModel
from typing import List, Optional

class AppConfig(BaseModel):
    workspace_root_path: str = r"C:\GithubRepos\Sleepy-AI-Army\poc-7-langgraph-aider"
    goal_root_path: str = "TODO"
    task_description_filename: str = "task-description.md"
    manifest_output_filename: str = "goal-manifest.md"
    changelog_output_filename: str = "changelog.md"
    log_subdirectory_name: str = "logs"
    overview_log_filename: str = "overview.log"
    detailed_log_filename: str = "detailed.log"
    # Example of a more complex field if needed later:
    # aider_model: Optional[str] = None 
    manifest_template_filename: str = "ai-docs/format-templates/format-goal-manifest.md"
    changelog_template_filename: str = "ai-docs/format-templates/format-changelog.md"
