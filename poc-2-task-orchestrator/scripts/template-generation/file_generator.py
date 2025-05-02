# /// script
# dependencies = [
#   "rich>=13.0.0",
#   "pathlib>=1.0.1"
# ]
# ///

"""File generation for template files."""

import logging
from pathlib import Path
from typing import Dict
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)

class FileGenerator:
    """Handles template file generation."""
    
    def __init__(self, templates_path: str = "ai-specs/templates"):
        self.templates_path = Path(templates_path)
        
    def generate_files(
        self, 
        target_path: Path,
        template_files: list[str],
        variables: Dict[str, str]
    ) -> None:
        """Generate files from templates with variable replacement."""
        # Handle feature_overview.md separately
        self._generate_feature_overview(target_path, variables)
        
        # Process remaining template files
        for template_file in template_files:
            self._process_template_file(target_path, template_file, variables)
    
    def _generate_feature_overview(self, target_path: Path, variables: Dict[str, str]) -> None:
        """Generate feature_overview.md from user input."""
        target_file = target_path / "feature_overview.md"
        try:
            target_file.write_text(variables["feature_overview"], encoding='utf-8')
            console.print(f"Generated file: [green]{target_file.relative_to(target_path)}[/]")
        except Exception as e:
            logger.error(f"Failed to generate feature_overview.md: {e}")
            raise

    def _process_template_file(
        self,
        target_path: Path,
        template_file: str,
        variables: Dict[str, str]
    ) -> None:
        """Process a single template file."""
        source_path = self.templates_path / template_file
        target_file = target_path / template_file
        
        try:
            if not source_path.exists():
                logger.error(f"Template file not found: {source_path}")
                raise FileNotFoundError(f"Template file not found: {source_path}")
            
            content = source_path.read_text(encoding='utf-8')
            
            # Two passes to handle nested template variables
            for _ in range(2):
                for var_name, var_value in variables.items():
                    placeholder = "{{" + f" {var_name} " + "}}"
                    # If var_value is a filepath, format it as linux path with forward slashes
                    print(f"Replacing {placeholder} with {var_value}") # Use f-string for consistency

                    # --- Refined Path Detection Logic ---
                    is_likely_path = False
                    var_value_processed = var_value # Default to original value

                    if isinstance(var_value, str): # Only process strings
                        # Check 1: No newlines AND no spaces
                        if '\n' not in var_value and ' ' not in var_value:
                            # Check 2: Contains path separators (this is a strong indicator)
                            if '/' in var_value or '\\' in var_value:
                                is_likely_path = True # If it has separators, no newlines, and no spaces, treat as path

                    if is_likely_path:
                        try:
                            # Convert to Path and format as POSIX
                            path_obj = Path(var_value)
                            var_value_processed = path_obj.as_posix()
                            print(f"Value '{var_value}' identified as path, using formatted: {var_value_processed}")
                        except Exception as e:
                            # Handle potential errors during Path conversion if the string is invalid despite checks
                            print(f"[yellow]Warning:[/yellow] Could not convert '{var_value}' to Path object despite checks: {e}. Using original value.")
                            var_value_processed = var_value # Revert to original on error
                    else:
                         print(f"Value '{var_value}' not identified as path, using original value.")
                    # --- End Refined Path Detection Logic ---

                    content = content.replace(placeholder, var_value_processed)
            
            target_file.write_text(content, encoding='utf-8')
            console.print(f"Generated file: [green]{target_file.relative_to(target_path)}[/]")
        except Exception as e:
            logger.error(f"Error processing {template_file}: {e}")
            raise