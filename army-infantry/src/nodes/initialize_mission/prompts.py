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
    3. Identify all file paths that are explicitly mentioned in the mission specification as needing modification. These should be listed in the 'editable_files' field.
        - File paths should be relative to the project root (e.g., "src/module/file.py").
        - If no files are explicitly mentioned for modification, the 'editable_files' field should be an empty list (`[]`).

    Adhere strictly to the JSON schema for your output, ensuring 'git_branch_name' matches this 'type/description' format and 'editable_files' is a list of strings.
"""

def get_user_prompt(mission_spec_content: str) -> str:
    return f"""
        Mission Description: '{mission_spec_content}'
    """
