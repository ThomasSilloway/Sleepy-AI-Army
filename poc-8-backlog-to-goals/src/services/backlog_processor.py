import logging
import os
import re
from typing import Optional

from ..config import AppConfig  # AppConfig might be needed by LlmPromptService
from ..models.goal_models import SanitizedGoalInfo

# Assuming LlmPromptService and SanitizedGoalInfo will be importable
# Adjust these imports based on the final location if they differ
from .llm_prompt_service import LlmPromptService

logger = logging.getLogger(__name__)

class BacklogProcessor:
    """
    Processes a backlog file, extracts tasks, and creates a structured
    directory of goal description files, using an LLM for folder name generation.
    """
    def __init__(self, llm_service: LlmPromptService, output_dir: str, app_config: AppConfig):
        """
        Initializes the BacklogProcessor.

        Args:
            llm_service: An instance of LlmPromptService.
            output_dir: The root directory where goal folders will be created.
            app_config: The application configuration.
        """
        self.llm_service = llm_service
        self.output_dir = output_dir
        self.app_config = app_config # LlmPromptService might need it

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")

    async def sanitize_title_with_llm(self, task_description: str, task_title: str = "") -> Optional[str]:
        """
        Uses the LlmPromptService to generate a sanitized, filesystem-friendly
        folder name based on the task description or title.

        Args:
            task_description: The full description of the task.
            task_title: The title of the task (optional, can be part of the prompt).

        Returns:
            A sanitized folder name string, or None if generation fails.
        """
        prompt_content = (
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

        messages = [
            {"role": "system", "content": "You are an expert assistant that generates filesystem-friendly folder names from task descriptions."},
            {"role": "user", "content": prompt_content}
        ]

        llm_model_name = getattr(self.app_config, 'default_llm_model_name', 'gemini-1.5-flash-latest')


        structured_output: Optional[SanitizedGoalInfo] = await self.llm_service.get_structured_output(
            messages=messages,
            output_pydantic_model_type=SanitizedGoalInfo,
            llm_model_name=llm_model_name
        )

        if structured_output and structured_output.folder_name:
            logger.info(f"LLM generated folder name: '{structured_output.folder_name}' for task: '{task_title[:50]}...'")
            folder_name = re.sub(r'[^\w\-]+', '', structured_output.folder_name.lower().replace(' ', '-'))
            return folder_name
        else:
            logger.error(f"Failed to generate sanitized folder name from LLM for task: '{task_title[:50]}...'")
            logger.info("Using basic sanitization as fallback.")
            sanitized_title_fallback = re.sub(r'\s+', '-', task_title.lower())
            sanitized_title_fallback = re.sub(r'[^a-z0-9\-]', '', sanitized_title_fallback)
            return f"task-{sanitized_title_fallback[:50]}" if task_title else "untitled-task"


    def parse_task_from_section(self, task_section: str) -> Optional[tuple[str, str]]:
        """
        Extracts the title and description from a markdown task section.
        A task section is expected to start with '## ' for the title.

        Args:
            task_section: A string block representing a single task.

        Returns:
            A tuple (title, description), or None if parsing fails.
        """
        lines = task_section.strip().split('\n')
        if not lines:
            return None

        title = ""
        description_lines = []

        if lines[0].startswith("## "):
            title = lines[0][3:].strip()
            description_lines = lines[1:]
        else:
            logger.warning(f"Task section does not start with '## ': '{task_section[:100]}...' Skipping.")
            return None

        description = "\n".join(description_lines).strip()
        return title, description

    async def process_backlog_file(self, backlog_filepath: str):
        """
        Reads the backlog file, parses tasks, generates folder names using LLM,
        and creates the directory structure.

        Args:
            backlog_filepath: Path to the backlog markdown file.
        """
        logger.info(f"Starting processing of backlog file: {backlog_filepath}")
        try:
            with open(backlog_filepath, encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            logger.error(f"Backlog file not found: {backlog_filepath}")
            print(f"Error: Backlog file not found at {backlog_filepath}")
            return
        except Exception as e:
            logger.error(f"Error reading backlog file {backlog_filepath}: {e}")
            print(f"Error: Could not read backlog file {backlog_filepath}: {e}")
            return

        task_sections = re.split(r'(?=^## )', content, flags=re.MULTILINE)

        processed_tasks = 0
        for section in task_sections:
            section = section.strip()
            if not section or not section.startswith("## "):
                if section: # Log if it's not empty but doesn't start with ##
                    logger.debug(f"Skipping section not starting with '## ': {section[:50]}...")
                continue

            parsed_info = self.parse_task_from_section(section)
            if not parsed_info:
                continue

            task_title, task_description = parsed_info
            logger.info(f"\n\nProcessing task: {task_title}\n\n{task_description}\n\n")

            folder_name = await self.sanitize_title_with_llm(task_description, task_title)

            if not folder_name: # Should be handled by fallback in sanitize_title_with_llm, but as safeguard
                logger.warning(f"Folder name is None for task: '{task_title}'. Using emergency fallback.")
                sanitized_title = re.sub(r'\s+', '-', task_title.lower())
                sanitized_title = re.sub(r'[^a-z0-9\-]', '', sanitized_title)
                folder_name = f"{sanitized_title[:50]}" if task_title else "unknown-title" # TODO: Add a timestamp to the end - format: 2025-02-25_01-53-49-999 - last part is hours, minutes, seconds, milliseconds

            task_folder_path = os.path.join(self.output_dir, folder_name)

            try:
                if not os.path.exists(task_folder_path):
                    os.makedirs(task_folder_path)
                    logger.info(f"Created task folder: {task_folder_path}")
                else:
                    logger.info(f"Task folder already exists: {task_folder_path}")

                description_filepath = os.path.join(task_folder_path, "task-description.md")
                with open(description_filepath, 'w', encoding='utf-8') as f:
                    f.write(task_description) # Write the original full description
                logger.info(f"Wrote task description to: {description_filepath}")
                processed_tasks +=1
            except Exception as e:
                logger.error(f"Error creating folder or file for task '{task_title}': {e}")
                print(f"Error creating structure for task '{task_title}': {e}")

        if processed_tasks > 0:
            logger.info(f"Successfully processed {processed_tasks} tasks.")
            print(f"Successfully processed {processed_tasks} tasks. Output is in '{self.output_dir}'.")
        else:
            logger.info(f"No tasks were processed. Check backlog file format or content: {backlog_filepath}")
            print(f"No tasks found or processed. Please ensure '{backlog_filepath}' contains tasks starting with '## '.")
