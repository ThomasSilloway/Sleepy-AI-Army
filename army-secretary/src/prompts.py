"""
Manages and provides prompt templates for interactions with the Language Model (LLM).

This module centralizes the definition of system and user prompts used in
various parts of the application, particularly for generating sanitized
folder names from task descriptions.
"""
from models.mission_models import SanitizedMissionFolderInfo

SANITIZE_MISSION_FOLDER_NAME_SYSTEM_PROMPT: str = f"""
    You are an expert assistant that generates filesystem-friendly folder names from task descriptions.

    Your objective is to extract specific pieces of information and structure them according to the provided JSON schema.
    The JSON schema to use for your response is:
    {SanitizedMissionFolderInfo.model_json_schema()}
    Ensure your output is a valid JSON object that conforms to this schema.
    From the user's task title and description, extract:
    1.  `folder_name`: A filesystem-friendly folder name derived from the task title or description.
"""

def get_sanitize_mission_folder_name_user_prompt(task_description: str, task_title: str) -> str:
    """
    Generates the user prompt content for requesting a sanitized folder name.

    Args:
        task_description: The full description of the task.
        task_title: The title of the task (optional).

    Returns:
        A string formatted as the user prompt to be sent to the LLM.
    """
    return f"""
        Task Title: '{task_title}'

        Task Description:
        {task_description}
    """
