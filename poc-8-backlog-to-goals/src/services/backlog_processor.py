# poc-8-backlog-to-goals/src/services/backlog_processor.py
"""
Provides the BacklogProcessor class, responsible for parsing a backlog
markdown file, interacting with an LLM to sanitize task titles for
directory names, and creating a structured output of goal description files.
"""

import logging
import os
import re
from typing import Optional, Tuple, List # Added List for parsing_errors
from datetime import datetime

from config import AppConfig
from models.goal_models import SanitizedGoalInfo
from .llm_prompt_service import LlmPromptService
from .. import prompts

logger: logging.Logger = logging.getLogger(__name__)

class BacklogProcessor:
    """
    Processes a backlog file, extracts tasks, and creates a structured
    directory of goal description files, using an LLM for folder name generation.
    """
    TASK_DESCRIPTION_FILENAME: str = "task-description.md"

    def __init__(self, llm_service: LlmPromptService, output_dir: str, app_config: AppConfig) -> None:
        """
        Initializes the BacklogProcessor.

        Args:
            llm_service: An instance of LlmPromptService.
            output_dir: The root directory where goal folders will be created.
            app_config: The application configuration.
        """
        self.llm_service: LlmPromptService = llm_service
        self.output_dir: str = output_dir
        self.app_config: AppConfig = app_config

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")

    async def sanitize_title_with_llm(self, task_description: str, task_title: str = "") -> str:
        """
        Uses the LlmPromptService to generate a sanitized, filesystem-friendly
        folder name based on the task description or title.
        Includes a robust fallback mechanism that always returns a valid string.

        Args:
            task_description: The full description of the task.
            task_title: The title of the task (optional, can be part of the prompt).

        Returns:
            A sanitized folder name string.
        """
        # Use externalized prompts
        prompt_content: str = prompts.get_sanitize_folder_name_user_prompt(task_description, task_title)
        messages: List[dict[str, str]] = [
            {"role": "system", "content": prompts.SANITIZE_FOLDER_NAME_SYSTEM_PROMPT},
            {"role": "user", "content": prompt_content}
        ]

        llm_model_name: str = self.app_config.default_llm_model_name

        structured_output: Optional[SanitizedGoalInfo] = await self.llm_service.get_structured_output(
            messages=messages,
            output_pydantic_model_type=SanitizedGoalInfo,
            llm_model_name=llm_model_name
        )

        folder_name: str = ""
        if structured_output and structured_output.folder_name and structured_output.folder_name.strip():
            logger.info(f"LLM generated folder name: '{structured_output.folder_name}' for task: '{task_title[:50]}...'")
            # Apply basic sanitization even to LLM output for safety
            folder_name = re.sub(r'[^\w\-]+', '', structured_output.folder_name.lower().replace(' ', '-'))
            if folder_name.strip(): # Ensure not empty after sanitization
                 return folder_name
            else:
                 logger.warning(f"LLM generated folder name became empty after sanitization for task: '{task_title[:50]}...'. Using fallback.")
        
        # Fallback logic
        if not (structured_output and structured_output.folder_name and structured_output.folder_name.strip()): # Log error only if LLM didn't provide a usable name
            logger.error(f"Failed to generate a valid folder name from LLM for task: '{task_title[:50]}...'. Using timestamped fallback.")
        
        base_name_sanitized: str = re.sub(r'\s+', '-', task_title.lower() if task_title else "untitled-task")
        base_name_sanitized = re.sub(r'[^a-z0-9\-]', '', base_name_sanitized)
        base_name_sanitized = base_name_sanitized[:50] # Truncate
        if not base_name_sanitized: # Handle cases where title had only special chars or was empty
            base_name_sanitized = "untitled-task"
        
        timestamp: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3] # Format: YYYY-MM-DD_HH-MM-SS-mmm
        return f"{base_name_sanitized}_{timestamp}"


    def parse_task_from_section(self, task_section_content: str) -> Optional[Tuple[str, str]]:
        """
        Extracts the title and description from a markdown task section.
        A task section is expected to start with '## ' for the title.

        Args:
            task_section_content: A string block representing a single task.

        Returns:
            A tuple (title, description), or None if parsing fails.
        """
        lines: List[str] = task_section_content.strip().split('\n')
        if not lines:
            return None

        title: str = ""
        description_lines: List[str] = []

        if lines[0].startswith("## "):
            title = lines[0][3:].strip()
            description_lines = lines[1:]
        else:
            # This case should ideally be caught before calling this method if sections are pre-filtered
            logger.warning(f"Task section content does not start with '## ': '{task_section_content[:100]}...'")
            return None

        if not title: # Handle cases like "## " (empty title)
            logger.warning(f"Task section has '## ' but no title text: '{task_section_content[:100]}...'")
            return None 

        description: str = "\n".join(description_lines).strip()
        return title, description

    def _read_backlog_content(self, backlog_filepath: str) -> Optional[str]:
        """
        Reads the content of the backlog file.

        Args:
            backlog_filepath: Path to the backlog markdown file.

        Returns:
            The file content as a string, or None if an error occurs.
        """
        logger.info(f"Reading backlog file: {backlog_filepath}")
        try:
            with open(backlog_filepath, encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Backlog file not found: {backlog_filepath}")
            return None
        except Exception as e:
            logger.error(f"Error reading backlog file {backlog_filepath}: {e}", exc_info=True)
            return None

    async def _process_single_task_section(
        self, 
        task_section_content: str, 
        section_index: int, 
        full_content_for_context: str # Used to calculate approx line number
    ) -> bool:
        """
        Processes a single task section: parses, sanitizes title, creates folder & file.

        Args:
            task_section_content: The content of the individual task section.
            section_index: Index of the section for logging/error context.
            full_content_for_context: Full backlog content to help locate section for error reporting.

        Returns:
            True if successful, False otherwise.
        """
        parsed_info: Optional[Tuple[str, str]] = self.parse_task_from_section(task_section_content)
        
        if not parsed_info:
            # parse_task_from_section logs specific parsing issues.
            return False

        task_title, task_description = parsed_info
        logger.info(f"Processing task (section {section_index + 1}): '{task_title}' (description length: {len(task_description)} chars)")

        folder_name: str = await self.sanitize_title_with_llm(task_description, task_title)
        
        if not folder_name: # Should not happen given sanitize_title_with_llm's robust fallback
             logger.error(f"sanitize_title_with_llm unexpectedly returned empty for task: '{task_title}'. Skipping file creation for this task.")
             return False

        task_folder_path: str = os.path.join(self.output_dir, folder_name)

        try:
            if not os.path.exists(task_folder_path):
                os.makedirs(task_folder_path)
                logger.info(f"Created task folder: {task_folder_path}")
            else:
                logger.info(f"Task folder already exists: {task_folder_path}")

            description_filepath: str = os.path.join(task_folder_path, self.TASK_DESCRIPTION_FILENAME)
            with open(description_filepath, 'w', encoding='utf-8') as f:
                f.write(task_description)
            logger.info(f"Wrote task description to: {description_filepath}")
            return True
        except Exception as e:
            logger.error(f"Error creating folder or file for task '{task_title}': {e}", exc_info=True)
            return False

    async def process_backlog_file(self, backlog_filepath: str) -> None:
        """
        Reads the backlog file, parses tasks, generates folder names using LLM,
        and creates the directory structure.

        Args:
            backlog_filepath: Path to the backlog markdown file.
        """
        content: Optional[str] = self._read_backlog_content(backlog_filepath)
        if content is None:
            return 

        task_sections: List[str] = re.split(r'(?=^## )', content, flags=re.MULTILINE)
        
        processed_tasks_count: int = 0
        parsing_errors: List[str] = []

        for i, section_content in enumerate(task_sections):
            section_content = section_content.strip()
            if not section_content: 
                continue

            if not section_content.startswith("## "):
                if section_content: 
                    approx_line_start: int = content.count('\n', 0, content.find(section_content)) + 1 if content.find(section_content) != -1 else -1
                    error_detail: str = f"Section {i+1} (near line {approx_line_start}, content: '{section_content[:100]}...')"
                    parsing_errors.append(error_detail)
                    logger.warning(f"Skipping section not starting with '## ': {error_detail}")
                continue
            
            if await self._process_single_task_section(section_content, i, content):
                processed_tasks_count += 1
            else:
                # If _process_single_task_section failed, it might be due to parsing or file ops.
                # We re-parse here to specifically add parsing failures to the summary.
                # File op errors are logged within _process_single_task_section.
                if not self.parse_task_from_section(section_content): 
                    approx_line_start = content.count('\n', 0, content.find(section_content)) + 1 if content.find(section_content) != -1 else -1
                    parsing_errors.append(f"Malformed task section {i+1} (near line {approx_line_start}, content: '{section_content[:100]}...')")


        # Final logging based on outcome
        if processed_tasks_count > 0:
            logger.info(f"Successfully processed {processed_tasks_count} tasks. Output is in '{self.output_dir}'.")
        
        if parsing_errors:
            logger.warning(
                f"{len(parsing_errors)} task section(s) could not be properly parsed or had issues. "
                f"Review backlog file for formatting. First few problematic sections (or contexts): {parsing_errors[:3]}"
            )
        
        if processed_tasks_count == 0 and not parsing_errors:
            if not any(s.strip() for s in task_sections if s.strip()): 
                 logger.info(f"Backlog file '{backlog_filepath}' is empty or contains no processable content.")
            else: 
                 logger.info(f"No valid task sections (starting with '##') found in '{backlog_filepath}'.")
