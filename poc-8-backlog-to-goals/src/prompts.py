# src/prompts.py
"""
Manages and provides prompt templates for interactions with the Language Model (LLM).

This module centralizes the definition of system and user prompts used in
various parts of the application, particularly for generating sanitized
folder names from task descriptions.
"""

SANITIZE_FOLDER_NAME_SYSTEM_PROMPT: str = (
    "You are an expert assistant that generates filesystem-friendly folder names "
    "from task descriptions."
)

def get_sanitize_folder_name_user_prompt(task_description: str, task_title: str = "") -> str:
    """
    Generates the user prompt content for requesting a sanitized folder name.

    Args:
        task_description: The full description of the task.
        task_title: The title of the task (optional).

    Returns:
        A string formatted as the user prompt to be sent to the LLM.
    """
    return (
        f"Given the following task details, please generate a concise, "
        f"filesystem-friendly folder name. The folder name should be suitable for use in a URL or "
        f"directory path. It should be in lowercase, with spaces replaced by hyphens (-), "
        f"and any special characters (like apostrophes, colons, etc.) removed or appropriately replaced. "
        f"Avoid using characters that are problematic for file systems of major operating systems (Windows, macOS, Linux)."
        f"Focus on the core subject of the task for the folder name.\n\n"
        f"Task Title (if available): '{task_title}'\n\n"
        f"Task Description:\n{task_description}\n\n"
        f"Generate only the folder name based on these instructions."
    )
