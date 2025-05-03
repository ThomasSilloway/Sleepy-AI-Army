# /// script
# dependencies = [
#   "PyYAML>=6.0.1",
#   "pathlib>=1.0.1"
# ]
# ///

"""Configuration management for template generation script."""

import os
from pathlib import Path
import yaml

class Config:
    """Configuration handler for template generation."""
    
    def __init__(self):
        """Initialize configuration with default values."""
        self._config = self._load_config()
        self._apply_env_overrides()
        
    def _load_config(self) -> dict:
        """Load configuration from config.yaml"""
        config_path = Path(__file__).parent / "config.yaml"
        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Error: Invalid config file - {e}")
            return self._get_default_config()

    def _get_default_config(self) -> dict:
        """Get default configuration values"""
        return {
            "paths": {
                "templates": "ai-specs/templates",
                "project_summary": "project-summary.md"
            },
            "template_files": [
                "spec-architecture-brainstorm-and-prd.md", 
                "spec-document-progress.md",
                "spec_bug_fixing_all.md",
                "spec_polish.md",
                "spec_polish_small.md"
            ],
            "required_dirs": [
                "generated",
                "generated/bugs",
                "generated/polish"
            ]
        }

    def _apply_env_overrides(self):
        """Apply environment variable overrides to config"""
        if templates_path := os.environ.get("TEMPLATE_PATH"):
            self._config["paths"]["templates"] = templates_path

    @property
    def templates_path(self) -> Path:
        """Get the configured templates directory path"""
        return Path(self._config["paths"]["templates"])

    @property
    def project_summary_path(self) -> Path:
        """Get the project summary file path"""
        return Path(self._config["paths"]["project_summary"])

    @property
    def template_files(self) -> list[str]:
        """Get list of template files to process"""
        return self._config["template_files"]

    @property
    def required_directories(self) -> list[str]:
        """Get list of required directories"""
        return self._config["required_dirs"]

# Global config instance
config = Config()