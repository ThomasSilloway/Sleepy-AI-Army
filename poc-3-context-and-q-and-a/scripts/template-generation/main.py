# /// script
# dependencies = [
#   "rich>=13.0.0",
#   "prompt-toolkit>=3.0.0",
#   "PyYAML>=6.0.1",
#   "pathlib>=1.0.1"
# ]
# ///

"""Main script for feature spec generation."""

import logging
import sys
from pathlib import Path
from typing import NoReturn
from rich.console import Console
from rich.panel import Panel

from config import config
from input_manager import InputManager
from folder_generator import FolderGenerator
from project_manager import ProjectManager
from file_generator import FileGenerator

console = Console()

def main() -> NoReturn:
    """Main entry point for template generation."""
    try:        
        # Print welcome message
        console.print(Panel(
            "[bold blue]Feature Spec Generator[/]\n\n"
            "This tool will help you create a new feature specification structure."
        ))
        
        # Initialize components
        input_manager = InputManager()
        folder_generator = FolderGenerator()
        project_manager = ProjectManager(config.project_summary_path)
        file_generator = FileGenerator(config.templates_path)
        
        # Collect user input
        folder_name, feature_name, feature_overview = input_manager.collect_inputs()
        
        # Create folder structure
        feature_path = folder_generator.create_folder_structure(
            folder_name,
            config.required_directories
        )
        
        # Get template variables
        variables = project_manager.get_template_variables(
            feature_name,
            feature_overview,
            feature_path
        )
        
        # Generate files from templates
        file_generator.generate_files(
            feature_path,
            config.template_files,
            variables
        )
        
        # Print success message
        console.print(Panel(
            "[bold green]Feature spec structure created successfully![/]\n\n"
            f"Location: {feature_path}\n"
            "You can now start working on your feature specification."
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
