#!/usr/bin/env python3
import os
from pathlib import Path

# --- Configuration ---
PROJECT_NAME = "poc7_langgraph_orchestrator"
PYTHON_VERSION_REQ = ">=3.9"
# Basic dependencies from the architecture document
DEPENDENCIES = [
    "langgraph",
    "pydantic",
    # Add other core dependencies here if known, e.g., "python-dotenv" if used for config loading
]

# --- Helper Function for Content ---
def get_file_content(file_type: str) -> str:
    """Returns placeholder content for different file types."""
    if file_type == "init":
        return ""
    if file_type == "main_py":
        return (
            "\"\"\"Main application entry point for the PoC7 Orchestrator.\"\"\"\n\n"
            "def main():\n"
            "    print(\"PoC7 LangGraph Orchestrator Starting...\")\n"
            "    # TODO: Load AppConfig\n"
            "    # TODO: Instantiate Services (AiderService, ChangelogService)\n"
            "    # TODO: Define LangGraph graph and nodes\n"
            "    # TODO: Compile graph\n"
            "    # TODO: Prepare initial WorkflowState and RunnableConfig\n"
            "    # TODO: Invoke graph execution\n"
            "    print(\"PoC7 LangGraph Orchestrator Finished (placeholder).\")\n\n"
            "if __name__ == \"__main__\":\n"
            "    main()\n"
        )
    if file_type == "config_py":
        return (
            "\"\"\"Pydantic model for application configuration.\"\"\"\n"
            "from pydantic import BaseModel\n"
            "from typing import List, Optional\n\n"
            "class AppConfig(BaseModel):\n"
            "    workspace_root_path: str\n"
            "    goal_root_path: str\n"
            "    task_description_filename: str = \"task-description.md\"\n"
            "    manifest_template_filename: str = \"templates/goal-manifest-template.md\"\n"
            "    manifest_output_filename: str = \"goal-manifest.md\"\n"
            "    changelog_template_filename: str = \"templates/changelog-template.md\"\n"
            "    changelog_output_filename: str = \"changelog.md\"\n"
            "    log_subdirectory_name: str = \"logs\"\n"
            "    overview_log_filename: str = \"overview.log\"\n"
            "    detailed_log_filename: str = \"detailed.log\"\n"
            "    # Example of a more complex field if needed later:\n"
            "    # aider_model: Optional[str] = None \n"
        )
    if file_type == "state_py":
        return (
            "\"\"\"TypedDict definition for the workflow's dynamic state.\"\"\"\n"
            "from typing import TypedDict, Optional, List, Any\n\n"
            "class WorkflowState(TypedDict):\n"
            "    current_step_name: Optional[str]\n"
            "    goal_folder_path: Optional[str]  # Absolute path\n"
            "    workspace_folder_path: Optional[str]  # Absolute path\n"
            "    task_description_path: Optional[str]\n"
            "    task_description_content: Optional[str]\n"
            "    manifest_template_path: Optional[str]\n"
            "    changelog_template_path: Optional[str]\n"
            "    manifest_output_path: Optional[str]\n"
            "    changelog_output_path: Optional[str]\n"
            "    generated_manifest_filepath: Optional[str]\n"
            "    last_event_summary: Optional[str]\n"
            "    aider_last_exit_code: Optional[int]\n"
            "    error_message: Optional[str]\n"
            "    is_manifest_generated: bool\n"
            "    is_changelog_entry_added: bool\n"
            "    # Add other state fields as they become necessary\n"
        )
    if file_type == "constants_py":
        return (
            "\"\"\"Project-wide internal constants.\"\"\"\n\n"
            "# Example: If LOG_SUBDIRECTORY_NAME is always 'logs' and not from config\n"
            "# LOG_SUBDIRECTORY_NAME = \"logs\"\n\n"
            "# Add other true constants here, not configurable parameters.\n"
            "PASS_PLACEHOLDER = \"pass # Placeholder for actual constants\"\n"
        )
    if file_type == "logging_setup_py":
        return (
            "\"\"\"Utility for configuring the application's logging system.\"\"\"\n"
            "import logging\n"
            "import sys\n"
            "# from .config import AppConfig # Assuming AppConfig is accessible\n\n"
            "def setup_logging(log_level=logging.INFO):\n"
            "    \"\"\"Configures basic logging for the application.\"\"\"\n"
            "    # This is a basic setup. In a real app, you'd use AppConfig\n"
            "    # to get log file paths, levels, etc.\n"
            "    logging.basicConfig(\n"
            "        level=log_level,\n"
            "        format=\"[%(asctime)s.%(msecs)03d] [%(levelname)-8s] [%(name)-12s] - %(message)s\",\n"
            "        datefmt=\"%H:%M:%S\",\n"
            "        handlers=[\n"
            "            logging.StreamHandler(sys.stdout) # Basic console logging\n"
            "        ]\n"
            "    )\n"
            "    # Example: logging.getLogger(\"aider_service\").setLevel(logging.DEBUG)\n"
            "    print(\"Logging setup (placeholder). Actual file logging to be configured based on AppConfig.\")\n"
        )
    # Placeholder for node files
    node_template = "\"\"\"Contains logic for the {} node.\"\"\"\n\n" \
                    "def {}(state: dict) -> dict:\n" \
                    "    print(f\"Executing node: {{}}\")\n" \
                    "    # TODO: Implement node logic\n" \
                    "    return state\n"
    if file_type == "initialization_node_py":
        return node_template.format("initialize_workflow", "initialize_workflow_node", "initialize_workflow_node")
    if file_type == "validation_node_py":
        return node_template.format("validate_inputs", "validate_inputs_node", "validate_inputs_node")
    if file_type == "manifest_generation_node_py":
        return node_template.format("generate_manifest", "generate_manifest_node", "generate_manifest_node")
    if file_type == "finalization_nodes_py":
        return (
            "\"\"\"Contains logic for workflow finalization nodes (success, error).\"\"\"\n\n"
            "def success_node(state: dict) -> dict:\n"
            "    print(\"Workflow completed successfully.\")\n"
            "    # TODO: Log final success\n"
            "    return state\n\n"
            "def error_handler_node(state: dict) -> dict:\n"
            "    print(f\"Workflow failed. Error: {{state.get('error_message', 'Unknown error')}}\")\n"
            "    # TODO: Log detailed error information\n"
            "    return state\n"
        )
    # Placeholder for service files
    service_template = "\"\"\"Defines the {} class.\"\"\"\n\n" \
                       "class {}:\n" \
                       "    def __init__(self, config=None):\n" \
                       "        self.config = config\n" \
                       "        print(f\"{{}} initialized.\")\n\n" \
                       "    # Add service methods here\n"
    if file_type == "aider_service_py":
        return service_template.format("AiderService", "AiderService", "AiderService")
    if file_type == "changelog_service_py":
        return service_template.format("ChangelogService", "ChangelogService", "ChangelogService")

    # Content for specific text/config files
    if file_type == "readme_md":
        return (
            f"# {PROJECT_NAME}\n\n"
            "Proof-of-Concept for LangGraph Orchestration (PoC7).\n\n"
            "## Setup\n\n"
            "1. Ensure Python {PYTHON_VERSION_REQ} is installed.\n"
            "2. Install `uv`: `pip install uv` (or `pipx install uv`).\n"
            "3. Create virtual environment: `uv venv`\n"
            "4. Activate environment: `source .venv/bin/activate` (or `.venv\\Scripts\\activate` on Windows).\n"
            "5. Install dependencies: `uv pip install -r requirements.txt` (or `uv pip install .` if pyproject.toml is fully configured for editable install)\n"
            "   (Note: `requirements.txt` would be generated by `uv pip freeze > requirements.txt` after `uv pip install ...`)\n\n"
            "## Running\n\n"
            "`uv run src/poc7_orchestrator/main.py` (or `python src/poc7_orchestrator/main.py` if environment is active)\n"
        )
    if file_type == "config_yml":
        return (
            "# Application configuration for PoC7 Orchestrator\n"
            "workspace_root_path: \"./workspace_examples\" # Adjust to your actual workspace path\n"
            "goal_root_path: \"./goal_examples/poc7_initial_setup_goal\" # Adjust to your actual goal path\n\n"
            "# Filenames (relative to paths above or defaults in AppConfig model)\n"
            "task_description_filename: \"task-description.md\"\n"
            "manifest_template_filename: \"templates/goal-manifest-template.md\" # Relative to workspace_root_path\n"
            "manifest_output_filename: \"goal-manifest.md\" # Relative to goal_root_path\n"
            "changelog_template_filename: \"templates/changelog-template.md\" # Relative to workspace_root_path\n"
            "changelog_output_filename: \"changelog.md\" # Relative to goal_root_path\n\n"
            "# Logging configuration (filenames relative to goal_root_path/log_subdirectory_name)\n"
            "log_subdirectory_name: \"logs\"\n"
            "overview_log_filename: \"overview.log\"\n"
            "detailed_log_filename: \"detailed.log\"\n"
        )
    if file_type == "pyproject_toml":
        dependencies_str = "".join([f"    \"{dep}\",\n" for dep in DEPENDENCIES])
        return (
            f"[project]\n"
            f"name = \"{PROJECT_NAME.replace('_', '-')}\"\n" # PEP 8 compliant package name
            f"version = \"0.1.0\"\n"
            f"description = \"PoC7 LangGraph Orchestrator for initial document generation.\"\n"
            f"authors = [\n"
            f"  {{ name = \"Your Name\", email = \"your.email@example.com\" }},\n"
            f"]\n"
            f"readme = \"README.md\"\n"
            f"requires-python = \"{PYTHON_VERSION_REQ}\"\n"
            f"license = {{ text = \"MIT\" }} # Or your chosen license\n"
            f"classifiers = [\n"
            f"    \"Programming Language :: Python :: 3\",\n"
            f"    \"License :: OSI Approved :: MIT License\",\n"
            f"    \"Operating System :: OS Independent\",\n"
            f"]\n"
            f"dependencies = [\n{dependencies_str}"
            f"]\n\n"
            f"[project.urls]\n"
            f"\"Homepage\" = \"https://github.com/yourusername/{PROJECT_NAME}\" # Example\n"
            f"\"Bug Tracker\" = \"https://github.com/yourusername/{PROJECT_NAME}/issues\" # Example\n\n"
            f"[build-system]\n"
            f"requires = [\"hatchling\"]\n"
            f"build-backend = \"hatchling.build\"\n"
            f"backend-path = [\".\"] # Specifies that pyproject.toml is at the root\n"
        )
    if file_type == "gitignore":
        return (
            "# Python\n"
            "__pycache__/\n"
            "*.pyc\n"
            "*.pyo\n"
            "*.pyd\n"
            ".Python\n"
            "build/\n"
            "develop-eggs/\n"
            "dist/\n"
            "downloads/\n"
            "eggs/\n"
            ".eggs/\n"
            "lib/\n"
            "lib64/\n"
            "parts/\n"
            "sdist/\n"
            "var/\n"
            "wheels/\n"
            "share/python-wheels/\n"
            "*.egg-info/\n"
            ".installed.cfg\n"
            "*.egg\n"
            "MANIFEST\n\n"
            "# Virtualenv\n"
            ".venv/\n"
            "venv/\n"
            "ENV/\n"
            "env/\n"
            "env.bak/\n"
            "venv.bak/\n\n"
            "# IDEs and editors\n"
            ".idea/\n"
            ".vscode/\n"
            "*.swp\n"
            "*.swo\n"
            ".DS_Store\n\n"
            "# Logs and runtime outputs within example/goal directories\n"
            "goal_examples/**/logs/\n"
            "goal_examples/**/goal-manifest.md\n"
            "goal_examples/**/changelog.md\n"
            "# Ensure example inputs are NOT ignored if they are part of the repo\n"
            "!goal_examples/**/task-description.md\n\n"
            "# Runtime logs at project root (if any, though configured for goal_examples)\n"
            "*.log\n"
        )
    if file_type == "task_description_md":
        return (
            "# Task Description: PoC7 Initial Setup\n\n"
            "This goal is to set up the initial project structure and generate the first\n"
            "version of the `goal-manifest.md` and `changelog.md` for this PoC itself.\n"
        )
    if file_type == "goal_manifest_template_md":
        return (
            "\n"
            "# Goal: {{ goal_title }}\n\n"
            "Last Updated: {{ last_updated_timestamp }}\n\n"
            "## Overall Status\n"
            "[ ] TODO\n[ ] In Progress\n[ ] Blocked\n[ ] User Review Required\n[ ] Approved\n\n"
            "## Current Focus\n"
            "- N/A\n\n"
            "## Artifacts\n"
            "\n"
            "\n\n"
            "## AI Questions for User\n"
            "\n\n"
            "## Human Input & Go-Ahead\n"
            "\n"
        )
    if file_type == "changelog_template_md":
        return (
            "\n"
            "## [{{ timestamp }}] - {{ entry_title }}\n\n"
            "{{#each changes}}\n"
            "- {{this}}\n"
            "{{/each}}\n"
        )
    return f"# Placeholder for {file_type}\n"

def create_project_scaffolding():
    """
    Creates the project directory structure and placeholder files
    for the PoC7 LangGraph Orchestrator.
    """
    project_root = Path(PROJECT_NAME)

    # --- Define Directory Structure ---
    # These are directories that should explicitly exist, especially package directories.
    # Parent directories are created automatically by Path.mkdir(parents=True).
    directories_to_create = [
        project_root / "src",
        project_root / "src" / "poc7_orchestrator",
        project_root / "src" / "poc7_orchestrator" / "nodes",
        project_root / "src" / "poc7_orchestrator" / "services",
        project_root / "src" / "poc7_orchestrator" / "utils",
        project_root / "goal_examples",
        project_root / "goal_examples" / "poc7_initial_setup_goal",
        project_root / "goal_examples" / "poc7_initial_setup_goal" / "logs", # Create logs dir, but not log files
        project_root / "workspace_examples",
        project_root / "workspace_examples" / "templates",
    ]

    # --- Define File Structure with Initial Content ---
    # (path_relative_to_project_root_constructor, content_type_key)
    files_to_create_map = [
        # Root files
        (lambda p: p / "pyproject.toml", "pyproject_toml"),
        (lambda p: p / "config.yml", "config_yml"),
        (lambda p: p / "README.md", "readme_md"),
        (lambda p: p / ".gitignore", "gitignore"),

        # Source files
        (lambda p: p / "src" / "poc7_orchestrator" / "__init__.py", "init"),
        (lambda p: p / "src" / "poc7_orchestrator" / "main.py", "main_py"),
        (lambda p: p / "src" / "poc7_orchestrator" / "config.py", "config_py"),
        (lambda p: p / "src" / "poc7_orchestrator" / "state.py", "state_py"),
        (lambda p: p / "src" / "poc7_orchestrator" / "constants.py", "constants_py"),

        (lambda p: p / "src" / "poc7_orchestrator" / "nodes" / "__init__.py", "init"),
        (lambda p: p / "src" / "poc7_orchestrator" / "nodes" / "initialization.py", "initialization_node_py"),
        (lambda p: p / "src" / "poc7_orchestrator" / "nodes" / "validation.py", "validation_node_py"),
        (lambda p: p / "src" / "poc7_orchestrator" / "nodes" / "manifest_generation.py", "manifest_generation_node_py"),
        (lambda p: p / "src" / "poc7_orchestrator" / "nodes" / "finalization_nodes.py", "finalization_nodes_py"),

        (lambda p: p / "src" / "poc7_orchestrator" / "services" / "__init__.py", "init"),
        (lambda p: p / "src" / "poc7_orchestrator" / "services" / "aider_service.py", "aider_service_py"),
        (lambda p: p / "src" / "poc7_orchestrator" / "services" / "changelog_service.py", "changelog_service_py"),

        (lambda p: p / "src" / "poc7_orchestrator" / "utils" / "__init__.py", "init"),
        (lambda p: p / "src" / "poc7_orchestrator" / "utils" / "logging_setup.py", "logging_setup_py"),

        # Example input files
        (lambda p: p / "goal_examples" / "poc7_initial_setup_goal" / "task-description.md", "task_description_md"),
        (lambda p: p / "workspace_examples" / "templates" / "goal-manifest-template.md", "goal_manifest_template_md"),
        (lambda p: p / "workspace_examples" / "templates" / "changelog-template.md", "changelog_template_md"),
    ]

    print(f"Starting project scaffolding for: {PROJECT_NAME}\n")

    # Create the main project directory if it doesn't exist
    project_root.mkdir(exist_ok=True)
    print(f"Ensured project root directory exists: {project_root.resolve()}")

    # Create all defined subdirectories
    print("\n--- Creating Directories ---")
    for dir_path in directories_to_create:
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created/Ensured directory: {dir_path.resolve()}")
        except OSError as e:
            print(f"Error creating directory {dir_path.resolve()}: {e}")
            return # Stop if a critical directory can't be made

    # Create all defined files
    print("\n--- Creating Files ---")
    for path_constructor, content_key in files_to_create_map:
        file_path = path_constructor(project_root)
        content = get_file_content(content_key)
        try:
            # Ensure parent directory exists (should be covered by above, but good for safety)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created file: {file_path.resolve()}")
        except IOError as e:
            print(f"Error creating file {file_path.resolve()}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred with file {file_path.resolve()}: {e}")


if __name__ == "__main__":
    create_project_scaffolding()
    print(f"\nScaffolding creation complete for project '{PROJECT_NAME}'.")
    print("Please review the generated files and customize as needed.")
    print(f"To get started, navigate to the '{PROJECT_NAME}' directory.")
    print("Consider running `uv pip freeze > requirements.txt` after installing dependencies with `uv pip install .` or individual packages.")
