# /// script
# dependencies = [
#   "prompt-toolkit>=3.0.0",
#   "rich>=13.0.0"
# ]
# ///

"""Input collection manager for template generation.

This module handles user input collection and validation for template variables.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError
from rich.console import Console
from rich.panel import Panel

console = Console()

class FeatureNameValidator(Validator):
    """Validator for feature names"""
    
    def validate(self, document):
        text = document.text
        
        if not text:
            raise ValidationError(message="Feature name cannot be empty")
        
        if len(text) > 50:
            raise ValidationError(message="Feature name must be 50 characters or less")
        
        # Check for invalid characters
        invalid_chars = '<>:"|?*'
        if any(char in text for char in invalid_chars):
            raise ValidationError(message=f"Feature name cannot contain any of: {invalid_chars}")

class InputManager:
    """Handles user input collection and validation."""
    
    def __init__(self):
        self.feature_name: Optional[str] = None
        self.feature_overview: Optional[str] = None
        self._current_date = datetime.now()
        
    def collect_inputs(self) -> tuple[str, str, str]:
        """Collect all required inputs from user.
        
        Returns:
            tuple[str, str, str]: (folder_name, feature_name, feature_overview)
        """
        # Get feature name
        self.feature_name = self._get_feature_name()
        
        # Get feature overview
        self.feature_overview = self._get_feature_overview()
        
        # Generate folder name
        folder_name = self._generate_folder_name()
        
        return folder_name, self.feature_name, self.feature_overview
    
    def _get_feature_name(self) -> str:
        """Get and validate feature name from user."""
        console.print(Panel("Enter a short descriptive name for the feature"))
        while True:
            try:
                name = prompt(
                    "Feature name: ",
                    validator=FeatureNameValidator()
                )
                return name
            except KeyboardInterrupt:
                console.print("\nCancelled by user")
                raise
            
    def _get_feature_overview(self) -> str:
        """Get feature overview from user."""
        console.print(Panel(
            "Enter the feature overview. This will be used in feature_overview.md\n"
            "Press Enter twice when done."
        ))
        
        lines = []
        while True:
            try:
                line = prompt("| ")
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            except KeyboardInterrupt:
                console.print("\nCancelled by user")
                raise
            
        return "\n".join(lines)
    
    def _generate_folder_name(self) -> str:
        """Generate folder name based on date and feature name."""
        date_prefix = self._current_date.strftime("%m-%d")
        
        # Find existing folders for today
        base_path = Path("ai-specs")
        existing = list(base_path.glob(f"{date_prefix}_*"))
        
        # Get next number
        next_num = 1
        if existing:
            numbers = []
            for path in existing:
                try:
                    num = int(path.name.split("_")[1][:2])
                    numbers.append(num)
                except (IndexError, ValueError):
                    continue
            if numbers:
                next_num = max(numbers) + 1
                
        # Format name
        folder_name = f"{date_prefix}_{next_num:02d}_{self.feature_name.lower().replace(' ', '-')}"
        
        return folder_name