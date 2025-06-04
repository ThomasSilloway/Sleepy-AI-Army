from .models import MissionData


def get_system_prompt(possible_git_branch_base_names: list[str]) -> str:
    return f"""
    You are an expert assistant that analyzes mission descriptions and extracts key information.

    Your goal is to extract specific pieces of information and structure them according to the provided JSON schema.
    The JSON schema to use for your response is:
    {MissionData.model_json_schema()}
    Ensure your output is a valid JSON object that conforms to this schema.

    Your tasks are:
    1. Extract the mission title from the provided mission specification content. The title should be concise and human-readable.
    2. Generate a 'git_branch_name' (referred to as 'git_branch_base_name' in some contexts) based on the mission's purpose or core task. This name **must** follow the format 'type/description'.
        - The 'type' must be one of the following: {", ".join(possible_git_branch_base_names)}.
        - The 'description' part should be in kebab-case (e.g., "update-user-profile", "fix-authentication-bug", "add-new-dashboard").
        - Example of a complete 'git_branch_name': "feature/add-user-login" or "fix/incorrect-calculation-logic" or "docs/update-readme".
        - The description should be short and descriptive.
    3. Identify all file paths explicitly mentioned in the mission specification. You must categorize these files into two lists:
       - 'files_to_edit': Include files that are mentioned for modification, improvement, refactoring, or any action that implies the file already exists.
       - 'files_to_create': Include files that are explicitly stated to be created, generated, or new. For example, "create a new file named 'src/services/new_service.py'" or "generate a component in 'src/components/new_widget.js'".
       If the mission spec says "work on file X" and doesn't explicitly state it's a new file, assume it's for 'files_to_edit'.
       If no files are mentioned for editing, 'files_to_edit' should be an empty list (`[]`).
       If no files are mentioned for creation, 'files_to_create' should be an empty list (`[]`).
       File paths should be relative to the project root (e.g., "src/module/file.py").

    Adhere strictly to the JSON schema for your output, ensuring 'git_branch_name' matches this 'type/description' format, 'files_to_edit' is a list of strings, and 'files_to_create' is a list of strings.
"""

def get_user_prompt(mission_spec_content: str) -> str:
    return f"""
        Mission Description: '{mission_spec_content}'
    """
