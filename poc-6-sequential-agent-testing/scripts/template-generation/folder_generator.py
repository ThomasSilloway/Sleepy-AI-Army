# /// script
# dependencies = [
#   "rich>=13.0.0"
# ]
# ///

"""Folder structure generator for template generation.

This module handles creating the folder structure for new feature specs.
"""

from pathlib import Path
from typing import List
from rich.console import Console

console = Console()

class FolderGenerator:
    """Handles creation of feature spec folder structure."""
    
    def __init__(self, base_path: str = "ai-specs"):
        self.base_path = Path(base_path)
        
    def create_folder_structure(self, folder_name: str, required_dirs: List[str]) -> Path:
        """Create the feature spec folder structure.
        
        Args:
            folder_name: Name of the feature folder
            required_dirs: List of required subdirectories to create
            
        Returns:
            Path: Path to the created feature folder
            
        Raises:
            FileExistsError: If folder already exists
            PermissionError: If unable to create folders
        """
        # Create feature folder path
        feature_path = self.base_path / folder_name
        
        # Check if folder already exists
        if feature_path.exists():
            raise FileExistsError(f"Feature folder already exists: {feature_path}")
        
        try:
            # Create main feature folder
            feature_path.mkdir(parents=True)
            console.print(f"Created feature folder: [bold green]{feature_path}[/]")
            
            # Create required subdirectories
            for dir_name in required_dirs:
                dir_path = feature_path / dir_name
                dir_path.mkdir(parents=True)
                console.print(f"Created directory: [blue]{dir_path.relative_to(self.base_path)}[/]")
                
            return feature_path
            
        except PermissionError as e:
            console.print(f"[bold red]Error:[/] Permission denied creating folders: {e}")
            raise
        except Exception as e:
            console.print(f"[bold red]Error:[/] Failed to create folder structure: {e}")
            # Clean up any partially created folders
            if feature_path.exists():
                try:
                    for dir_path in feature_path.glob("**/*"):
                        if dir_path.is_dir():
                            dir_path.rmdir()
                    feature_path.rmdir()
                except Exception as cleanup_error:
                    console.print(f"[yellow]Warning:[/] Failed to clean up folders: {cleanup_error}")
            raise