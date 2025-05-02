# /// script
# dependencies = [
#   "rich>=13.0.0"
# ]
# ///

"""Project details management for template generation.

This module handles loading and parsing project details from project-summary.md.
"""

from pathlib import Path
from typing import Optional
from rich.console import Console

console = Console()

class ProjectManager:
    """Handles loading and managing project details."""
    
    def __init__(self, project_summary_path: Path):
        self.project_summary_path = project_summary_path
        self._project_details: Optional[str] = None

    def _load_template_content(self, template_path: Path) -> str:
        """Load content from a template file.
        
        Args:
            template_path: Path to the template file
            
        Returns:
            str: Template content, or empty string if file not found
        """
        try:
            if not template_path.exists():
                raise FileNotFoundError(f"Template file not found: {template_path}")
            
            content = template_path.read_text(encoding='utf-8')
            console.print(f"Loaded template from: [green]{template_path}[/]")
            return content
            
        except FileNotFoundError:
            console.print(f"[yellow]Warning: Template not found: {template_path}, using empty string[/]")
            return ""
            
    def get_template_variables(self, feature_name: str, feature_overview: str, folder_path: Path) -> dict:
        """Get dictionary of template variables.
        
        Args:
            feature_name: Name of the feature
            feature_overview: Feature overview content
            folder_path: Path to generated feature folder
            
        Returns:
            dict: Template variables
        """
        project_details = self._load_template_content(self.project_summary_path)
        common_errors = self._load_template_content(Path("ai-specs/templates/task_common_errors.md"))
        change_notes_template = self._load_template_content(Path("ai-specs/templates/task_change_notes.md"))
        boomerang_template = self._load_template_content(Path("ai-specs/templates/task_boomerang_mode.md"))

        # Ensure forward slashes in path strings
        folder_path = Path(str(folder_path).replace('\\', '/'))
        
        return {
            "feature_name": feature_name,
            "feature_overview": feature_overview,
            "project_details": project_details,
            "generated_folder": str(folder_path),
            "prd_link": str(folder_path / "generated/prd.md"),
            "change_notes": str(folder_path / "generated/change_notes.md"),
            "api_reference": str(folder_path / "generated/api_reference.md"),
            "task_common_errors": common_errors,
            "task_change_notes": change_notes_template,
            "task_boomerang_mode": boomerang_template,
        }

