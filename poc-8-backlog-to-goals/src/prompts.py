"""
Manages and provides prompt templates for interactions with the Language Model (LLM).

This module centralizes the definition of system and user prompts used in
various parts of the application, particularly for generating sanitized
folder names from task descriptions.
"""

SANITIZE_FOLDER_NAME_SYSTEM_PROMPT: str = """
    You are an expert assistant that generates filesystem-friendly folder names from task descriptions.
    You only return the folder name and nothing else. You do not include any extra commentary.
"""

def get_sanitize_folder_name_user_prompt(task_description: str, task_title: str) -> str:
    """
    Generates the user prompt content for requesting a sanitized folder name.

    Args:
        task_description: The full description of the task.
        task_title: The title of the task (optional).

    Returns:
        A string formatted as the user prompt to be sent to the LLM.
    """
    return f"""
        Given the following task details, please generate a concise, filesystem-friendly folder name. 
         IMPORTANT: 
          - The folder name should be suitable for use in a URL or directory path. 
          - It should be in lowercase, with spaces replaced by hyphens (-), and any special characters (like apostrophes, colons, etc.) removed or appropriately replaced. 
          - Avoid using characters that are problematic for file systems of major operating systems (Windows, macOS, Linux).
          - The folder name should be short, ideally less than 50 characters.
          - Focus on the core subject of the task for the folder name.

        Task Title: '{task_title}'

        Task Description:
        {task_description}

        Generate only the folder name based on these instructions. Do not include any extra commentary.
    """
