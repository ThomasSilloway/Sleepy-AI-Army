"""Defines the AiderService class."""
import asyncio
import logging
import subprocess
import threading
from typing import Optional  # Use List instead of list for older Python compatibility if needed, but stick to list per CONVENTIONS.md

from pydantic import BaseModel

from src.app_config import AppConfig
from src.models.aider_summary import AiderRunSummary
from src.services.llm_prompt_service import LlmPromptService

logger = logging.getLogger(__name__)


class AiderExecutionResult(BaseModel):
    """Data class to hold the results of an Aider command execution."""
    exit_code: int
    stdout: str
    stderr: str


def stream_output(pipe, log_func, output_lines_list: list[str]):
    """Reads lines from a pipe, logs them, and appends them to a list."""
    try:
        for line in iter(pipe.readline, ''):
            stripped_line = line.strip()
            log_func(stripped_line)
            output_lines_list.append(stripped_line)
    finally:
        pipe.close()

class AiderService:
    def __init__(self, app_config: AppConfig, llm_prompt_service: LlmPromptService):
        self.app_config = app_config
        self.workspace_path = app_config.goal_git_path
        self.llm_prompt_service = llm_prompt_service

    def execute(self, command_args: list[str], files_to_add: Optional[list[str]] = None) -> AiderExecutionResult:
        """
        Executes an aider command as a subprocess, streams its output, captures stdout and stderr,
        and returns an AiderExecutionResult.

        Args:
            command_args: A list of arguments to pass to the aider CLI.
            files_to_add: An optional list of file paths to be included in the aider command execution context.

        Returns:
            An AiderExecutionResult object containing the exit code, stdout, and stderr.
        """
        if files_to_add is None:
            files_to_add = []

        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        full_command = ["aider"] + files_to_add + command_args + [
            "--yes-always",
            "--no-fancy-input",
            "--no-pretty",
        ]

        logger.info(f"Executing aider command: {' '.join(full_command)}")

        try:
            # Start the subprocess
            # Use text=True for easier handling of stdout/stderr as strings
            # Use bufsize=1 for line buffering
            process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                encoding='utf-8',
                cwd=self.workspace_path,
            )

            # Create threads to stream stdout and stderr
            stdout_thread = threading.Thread(target=stream_output, args=(process.stdout, logger.info, stdout_lines))
            stderr_thread = threading.Thread(target=stream_output, args=(process.stderr, logger.error, stderr_lines))

            # Start the threads
            stdout_thread.start()
            stderr_thread.start()

            # Wait for the threads to finish (which they will when the streams close)
            stdout_thread.join()
            stderr_thread.join()

            # Wait for the subprocess to terminate and get the exit code
            exit_code = process.wait()
            logger.info(f"Aider command finished with exit code: {exit_code}")

            stdout_str = "\n".join(stdout_lines)
            stderr_str = "\n".join(stderr_lines)

            return AiderExecutionResult(exit_code=exit_code, stdout=stdout_str, stderr=stderr_str)

        except FileNotFoundError:
            error_msg = "Error: 'aider' command not found. Is aider installed and in the system PATH?"
            logger.critical(error_msg)
            return AiderExecutionResult(exit_code=-1, stdout="", stderr=error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred while executing aider: {e}"
            logger.critical(error_msg, exc_info=True)
            return AiderExecutionResult(exit_code=-1, stdout="", stderr=error_msg)

    def get_summary(self, result: AiderExecutionResult) -> AiderRunSummary:
        system_prompt = """
You are an expert at analyzing the output of the 'aider' command-line tool.
Your task is to extract specific information from aider's stdout and stderr and return it in a structured JSON format
that matches the AiderRunSummary Pydantic model.

The AiderRunSummary model includes the following fields:
- changes_made: (list[str]) A bulleted list of actual changes applied by aider. Each item should be a clear, concise description of a change (e.g., "Added function `foo` to `bar.py`", "Modified `baz.py` to handle new error condition").
- commit_hash: (Optional[str]) The full git commit hash if aider made a commit *during this specific run*. If no commit was made by aider, this should be null.
- files_modified: (Optional[list[str]]) List of file paths that were modified by aider.
- files_created: (Optional[list[str]]) List of file paths that were newly created by aider.
- errors_reported: (Optional[list[str]]) Any error messages or significant warnings reported by aider.
- raw_output_summary: (Optional[str]) A brief, general summary of what aider did or reported, especially if specific details aren't available or applicable from its output.
- commit_message: (Optional[str]) The full commit message if aider made a commit. If no commit was made, this should be null.
- total_cost: (Optional[float]) The total session cost of the Aider run in USD. Formatted as a float. Default to 0.0 if not found. Cost will be near the end of the Aider STDOUT. Ex. `Tokens: 8.0k sent, 374 received. Cost: $0.01 message, $0.04 session.` - total_cost = 0.04, the session cost. If there are multiple lines with this information, choose the one with the highest session cost.

Analyze the provided stdout and stderr from an aider execution.
Extract the information to populate these fields accurately.
If aider's output clearly indicates a commit, extract the hash and message.
If aider failed or no specific changes are identifiable, focus on `errors_reported` and `raw_output_summary`.
Pay close attention to whether a commit was actually made by aider in *this* run. Do not infer commits.
The output MUST be a JSON object matching the AiderRunSummary structure.
"""
        user_prompt_content = f"""
Please analyze the following output from an 'aider' command execution:

**Aider STDOUT:**
```
{result.stdout}
```

**Aider STDERR:**
```
{result.stderr}
```

Based on this output, provide a JSON summary matching the AiderRunSummary model.
"""
        llm_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt_content},
        ]
        try:
            logger.info("Attempting to extract Aider execution summary using LLM.")

            # Note: Using a placeholder for llm_model_name. This should come from app_config.
            # e.g., app_config.llm_model_for_summaries
            aider_run_summary_obj = asyncio.run(self.llm_prompt_service.get_structured_output(
                messages=llm_messages,
                output_pydantic_model_type=AiderRunSummary,
                llm_model_name=self.app_config.aider_summary_model
            ))

            if aider_run_summary_obj:
                logger.info("Successfully extracted Aider run summary.")
                logger.debug(f"Aider Run Summary: {aider_run_summary_obj.model_dump_json(indent=2)}")
                return aider_run_summary_obj
            else:
                logger.warning("LLM did not return a valid AiderRunSummary object.")
        except Exception as llm_exc:
            logger.error(f"Error during LLM summary extraction: {llm_exc}", exc_info=True)

        return None
