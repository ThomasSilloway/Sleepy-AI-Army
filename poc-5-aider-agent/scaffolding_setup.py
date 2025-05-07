# scaffold_project.py
# This script creates the basic folder structure and initial files
# for the "Sleepy AI Army - PoC 5 (Aider Small Tweak Integration)" project,
# based on the Technical Architecture Document v1.0.
#
# Instructions:
# 1. Create a root directory for your project (e.g., "poc-5-aider-agent").
# 2. Place this script (`scaffold_project.py`) inside that root directory.
# 3. Run this script from that root directory (e.g., from within "poc-5-aider-agent"):
#    python scaffold_project.py
#
# This will create a subdirectory named "sleepy-ai-poc5" containing the scaffolded project.

import os

# --- Configuration ---
PROJECT_ROOT_DIR_NAME = "sleepy-ai-poc5"  # This will be created inside the dir where the script is run

# Define the structure: { 'path_segment': 'content_or_None_or_sub_structure' }
# - Use a string for content if <= 5 lines.
# - Use None for files that should be stubbed with a TODO comment.
# - Use "" for empty __init__.py files.
STRUCTURE = {
    # Top-level files in sleepy-ai-poc5
    ".env": None,  # Will be created empty
    ".env.example": 'GOOGLE_API_KEY="YOUR_API_KEY_HERE"',
    "README.md": "# PoC 5: Aider Small Tweak Integration\n\nADK project for PoC 5: Aider Small Tweak Integration.",
    "requirements.txt": 'google-adk',
    "src": {
        "sleepy_ai_agent": {
            "__init__.py": 'from .agent import root_agent',
            "agent.py": None,  # Stub: Defines RootAgent, SmallTweakSequence, partial callbacks
            "constants": {
                "__init__.py": "",
                "constants.py": None,  # Stub: Defines state keys, paths, etc.
            },
            "callbacks": {
                "__init__.py": "",
                "callbacks.py": None,  # Stub: Defines _core_check_and_skip_logic
            },
            "shared_tools": {
                "__init__.py": "",
                "file_tool.py": None,  # Stub: Defines FileTool methods
            },
            "sub_agents": {
                "task_parsing": {
                    "__init__.py": "",
                    "agent.py": None,    # Stub
                    "prompt.py": None,   # Stub
                },
                "file_locator": {
                    "__init__.py": "",
                    "agent.py": None,    # Stub
                    "prompt.py": None,   # Stub
                },
                "git_setup": {
                    "__init__.py": "",
                    "agent.py": None,    # Stub
                    "prompt.py": None,   # Stub
                    "tools.py": None,    # Stub: Defines GitTool
                },
                "aider_execution": {
                    "__init__.py": "",
                    "agent.py": None,    # Stub
                    "prompt.py": None,   # Stub
                    "tools.py": None,    # Stub: Defines AiderTool
                },
                "reporting": {
                    "__init__.py": "",
                    "agent.py": None,    # Stub
                    "prompt.py": None,   # Stub
                },
                "changelog": {
                    "__init__.py": "",
                    "agent.py": None,    # Stub: Defines ChangelogAgent
                    "prompt.py": None,   # Stub
                },
            },
        }
    },
}

# --- Scaffolding Logic ---
STUB_COMMENT = "# TODO: Implement content as per Technical Architecture Document.\n"

def count_lines(text_content):
    """Counts lines in a string. Empty or None is 0 lines for content decision."""
    if not text_content:
        return 0
    return len(text_content.splitlines())

def create_structure_recursive(base_path, structure_dict):
    """Recursively creates directories and files."""
    os.makedirs(base_path, exist_ok=True) # Ensure base_path itself is created if it's the first call

    for name, content_or_sub_structure in structure_dict.items():
        current_path = os.path.join(base_path, name)
        if isinstance(content_or_sub_structure, dict):
            # It's a directory
            print(f"Creating directory: {current_path}")
            os.makedirs(current_path, exist_ok=True)
            create_structure_recursive(current_path, content_or_sub_structure)  # Recurse
        else:
            # It's a file
            print(f"Creating file:      {current_path}")
            try:
                with open(current_path, 'w', encoding='utf-8') as f:
                    if content_or_sub_structure is None:
                        if name == ".env": # Special case for .env to be truly empty
                            pass
                        else:
                            f.write(STUB_COMMENT)
                    elif isinstance(content_or_sub_structure, str):
                        num_lines = count_lines(content_or_sub_structure)
                        if content_or_sub_structure == "" : # For empty __init__.py
                             pass # Write nothing, effectively an empty file
                        elif num_lines > 0 and num_lines <= 5:
                            f.write(content_or_sub_structure)
                            if not content_or_sub_structure.endswith('\n'):
                                f.write('\n')
                        else: # Longer than 5 lines or complex content not suitable for direct inclusion
                            f.write(STUB_COMMENT)
            except IOError as e:
                print(f"Error creating file {current_path}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred for file {current_path}: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    # The script is expected to be in "poc-5-aider-agent".
    # It will create "sleepy-ai-poc5" inside "poc-5-aider-agent".
    script_dir = os.getcwd() # Assumes script is run from its location
    project_target_path = os.path.join(script_dir, PROJECT_ROOT_DIR_NAME)

    print(f"Starting project scaffolding for '{PROJECT_ROOT_DIR_NAME}' inside '{script_dir}'...")

    if os.path.exists(project_target_path):
        print(f"Warning: Directory '{project_target_path}' already exists.")
        # You might want to add a confirmation here if overwriting is a concern,
        # but for scaffolding, usually creating if not exists is fine.
        # For this script, it will proceed and potentially overwrite stubs/small files.

    create_structure_recursive(project_target_path, STRUCTURE)

    print("-" * 30)
    print(f"Project scaffolding complete in: '{project_target_path}'")
    print("Next steps:")
    print(f"  1. Navigate to '{project_target_path}'.")
    print("  2. Create and activate a Python virtual environment.")
    print("  3. Install dependencies: pip install -r requirements.txt")
    print("  4. Configure your '.env' file with necessary API keys (e.g., GOOGLE_API_KEY).")
    print("  5. Implement the # TODO sections in the generated Python files based on the TAD.")
    print("-" * 30)
