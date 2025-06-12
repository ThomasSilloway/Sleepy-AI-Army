"""Defines the AiderService class."""
import asyncio
import logging
from typing import Optional

from src.app_config import AppConfig
from src.models.aider_summary import AiderRunSummary
from src.services.aider_service.aider_execution_result import AiderExecutionResult
from src.services.aider_service.prompts import get_system_prompt, get_user_prompt
from src.services.llm_prompt_service import LlmPromptService

logger = logging.getLogger(__name__)

async def stream_output(
    pipe: asyncio.StreamReader, log_func, output_lines_list: list[str]
):
    """Reads lines from an asyncio StreamReader, logs them, and appends them to a list."""
    while True:
        try:
            line_bytes = await pipe.readline()
            if not line_bytes:  # EOF
                break
            line = line_bytes.decode('utf-8').strip()
            log_func(line)
            output_lines_list.append(line)
        except Exception as e:
            # Log errors during streaming, e.g., if the pipe breaks unexpectedly
            logger.error(f"Error reading stream: {e}")
            break


class AiderService:
    def __init__(self, app_config: AppConfig, llm_prompt_service: LlmPromptService):
        self.app_config = app_config
        self.workspace_path = app_config.root_git_path
        self.llm_prompt_service = llm_prompt_service

    async def execute(
        self,
        command_args: list[str],
        files_editable: Optional[list[str]] = None,
        files_read_only: Optional[list[str]] = None,
    ) -> AiderExecutionResult:
        """
        Executes an aider command as an asyncio subprocess, streams its output,
        captures stdout and stderr, and returns an AiderExecutionResult.

        Args:
            command_args: A list of arguments to pass to the aider CLI.
            files_editable: An optional list of file paths to be added to aider.
            files_read_only: An optional list of file paths for aider to read.

        Returns:
            An AiderExecutionResult object containing the exit code, stdout, and stderr.
        """
        if files_editable is None:
            files_editable = []
        if files_read_only is None:
            files_read_only = []

        # Update command arguments
        for file_path in files_read_only:
            command_args.append("--read")
            command_args.append(file_path)

        for file_path in files_editable:
            command_args.append(file_path)

        full_command = ["aider"] + command_args + [
            "--yes-always",
            "--no-fancy-input",
            "--no-pretty",
        ]

        # Execute the aider command
        logger.info(f"Executing aider command: {' '.join(full_command)}")

        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        try:
            process = await asyncio.create_subprocess_exec(
                *full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace_path,
            )

            # Concurrently stream stdout and stderr
            # process.stdout and process.stderr are asserted to be non-None
            # because we passed PIPE to create_subprocess_exec.
            await asyncio.gather(
                stream_output(process.stdout, logger.info, stdout_lines),
                stream_output(process.stderr, logger.error, stderr_lines),
            )

            # Wait for the subprocess to terminate and get the exit code
            exit_code = await process.wait()
            logger.info(f"Aider command finished with exit code: {exit_code}")

            stdout_str = "\n".join(stdout_lines)
            stderr_str = "\n".join(stderr_lines)

            return AiderExecutionResult(
                exit_code=exit_code, stdout=stdout_str, stderr=stderr_str
            )

        except FileNotFoundError:
            error_msg = "Error: 'aider' command not found. Is aider installed and in the system PATH?"
            logger.critical(error_msg)
            return AiderExecutionResult(exit_code=-1, stdout="", stderr=error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred while executing aider: {e}"
            logger.critical(error_msg, exc_info=True)
            return AiderExecutionResult(exit_code=-1, stdout="", stderr=error_msg)

    async def get_summary(self, result: AiderExecutionResult) -> Optional[AiderRunSummary]:
        """
        Analyzes AiderExecutionResult using an LLM to produce an AiderRunSummary.
        (This method was already async and is largely unchanged functionally,
         but it will now be called with the result of an async `execute` method).
        """

        llm_messages = [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": get_user_prompt(result)},
        ]
        try:
            logger.info("Attempting to extract Aider execution summary using LLM.")

            aider_run_summary_obj, cost = await self.llm_prompt_service.get_structured_output(
                messages=llm_messages,
                output_pydantic_model_type=AiderRunSummary,
                llm_model_name=self.app_config.aider_summary_model # This should exist in AppConfig
            )

            if aider_run_summary_obj:
                aider_run_summary_obj.total_cost += cost
                logger.info("Successfully extracted Aider run summary.")
                logger.debug(f"Aider Run Summary: {aider_run_summary_obj.model_dump_json(indent=2)}")
                return aider_run_summary_obj
            else:
                logger.warning("LLM did not return a valid AiderRunSummary object.")
                return None
        except Exception as llm_exc:
            logger.error(f"Error during LLM summary extraction: {llm_exc}", exc_info=True)
            return None
