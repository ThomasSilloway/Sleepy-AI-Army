# scaffold_project.py
# This script creates the basic folder structure and initial files
# for the PoC 6 Sequential Agent Failure Handling project,
# based on the Technical Architecture Document v1.4.

import os

# --- Configuration ---
PROJECT_ROOT_DIR = "poc6-sequential-failure"

# Define the structure: { 'path': 'content' }
# Use None for empty files (or files requiring more than minimal setup)
# Use "" for empty __init__.py files specifically
# Use string content for files with minimal placeholders
STRUCTURE = {
    # Root files
    ".env": None, # Keep secret, create empty
    ".env.example": 'GOOGLE_API_KEY="YOUR_API_KEY_HERE"',
    "README.md": '# PoC 6: Sequential Agent Failure Handling\n\nThis project demonstrates conditional skipping in ADK SequentialAgents.',
    "requirements.txt": 'google-adk\n',

    # Main package directory
    "poc6_sequential_failure": {
        "__init__.py": 'from .agent import root_agent',
        "agent.py": '# TODO: Define RootAgent and ErrorTestSequence (SequentialAgent)',
        "prompt.py": '# Root-level prompts or shared constants',

        # Callbacks subdirectory
        "callbacks": {
            "__init__.py": "",
            "callbacks.py": '# TODO: Define check_outcome_and_skip_callback function\nimport json\nfrom google.adk.agents.callback_context import CallbackContext\nfrom google.genai import types\n\ndef check_outcome_and_skip_callback(context: CallbackContext, /) -> types.Content | None:\n    """Checks previous step outcome and skips current agent if needed."""\n    # Implement logic here: read state, parse JSON, set skipped state, return Content or None\n    print(f"WARN: Callback logic not implemented in {__file__}")\n    return None\n'
        },

        # Sub-agents directory
        "sub_agents": {
            "agent_a": {
                "__init__.py": "",
                "agent.py": '# TODO: Define Agent A (LlmAgent)',
                "prompt.py": 'AGENT_A_INSTR = """Call the FailingTool. If the tool indicates an error, output a JSON string like \'{"status": "failure", "message": "Tool failed: [reason from tool response]"}\'. Otherwise, output a JSON string like \'{"status": "success", "result": "Tool call completed successfully."}\'. Ensure your final output is *only* the valid JSON string."""',
                "tools.py": '# TODO: Define FailingTool function and FunctionTool instance\nfrom google.adk.tools import FunctionTool\n\ndef _failing_tool_impl() -> dict:\n    """Simulates a tool failure."""\n    print("Simulating tool failure...")\n    return {"status": "error", "message": "Simulated tool failure"}\n\nfailing_tool = FunctionTool(\n    func=_failing_tool_impl,\n    description="A tool that always returns a failure status."\n)\n'
            },
            "agent_b": {
                "__init__.py": "",
                "agent.py": '# TODO: Define Agent B (LlmAgent)',
                "prompt.py": 'AGENT_B_INSTR = """Log \'Agent B running primary task.\' Then, output a JSON string like \'{"status": "success", "result": "Agent B finished its task."}\'. Ensure your final output is *only* the valid JSON string."""'
            },
            "agent_c": {
                "__init__.py": "",
                "agent.py": '# TODO: Define Agent C (LlmAgent)',
                "prompt.py": 'AGENT_C_INSTR = """Log \'Agent C running primary task.\' Then, output a JSON string like \'{"status": "success", "result": "Agent C finished its task."}\'. Ensure your final output is *only* the valid JSON string."""'
            },
            "agent_d": {
                "__init__.py": "",
                "agent.py": '# TODO: Define Agent D (LlmAgent)',
                "prompt.py": 'AGENT_D_INSTR = """Perform the following steps:\n1. Review the outcomes of the previous steps provided here: Agent A -> {agent_a_outcome}, Agent B -> {agent_b_outcome}, Agent C -> {agent_c_outcome}. These are JSON strings containing status information. Parse them and generate a concise summary sentence describing the overall result of the sequence (e.g., \'Agent A failed, B and C were skipped, D completed.\').\n2. Output *only* the summary sentence you generated as plain text. Your task is complete after providing the summary."""'
            }
        }
    }
}

# --- Scaffolding Logic ---

def create_structure(base_path, structure_dict):
    """Recursively creates directories and files."""
    for name, content in structure_dict.items():
        current_path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # It's a directory
            print(f"Creating directory: {current_path}")
            os.makedirs(current_path, exist_ok=True)
            create_structure(current_path, content) # Recurse
        else:
            # It's a file
            print(f"Creating file:      {current_path}")
            try:
                with open(current_path, 'w', encoding='utf-8') as f:
                    if content is None:
                        # Files specified as None will be empty
                        pass
                    elif isinstance(content, str):
                        # Write specified content
                        f.write(content)
                        # Ensure newline at end if content isn't empty and doesn't end with one
                        if content and not content.endswith('\n'):
                             f.write('\n')

            except IOError as e:
                print(f"Error creating file {current_path}: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    print(f"Starting project scaffolding in root directory: '{PROJECT_ROOT_DIR}'...")

    # Create the root project directory
    os.makedirs(PROJECT_ROOT_DIR, exist_ok=True)
    print(f"Created root directory: {PROJECT_ROOT_DIR}")

    # Create the rest of the structure relative to the root
    create_structure(PROJECT_ROOT_DIR, STRUCTURE)

    print("-" * 30)
    print("Project scaffolding complete.")
    print(f"Navigate to '{PROJECT_ROOT_DIR}' to start working.")
    print("Remember to:")
    print("  - Create a virtual environment.")
    print("  - Install dependencies from requirements.txt.")
    print("  - Populate the .env file with your API key.")
    print("  - Implement the TODO sections in the Python files.")
    print("-" * 30)