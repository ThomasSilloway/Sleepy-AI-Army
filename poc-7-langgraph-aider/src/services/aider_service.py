"""Defines the AiderService class."""
import logging
import subprocess
import threading
from typing import Optional  # Use List instead of list for older Python compatibility if needed, but stick to list per CONVENTIONS.md

from pydantic import BaseModel

from src.config import AppConfig

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
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config
        self.workspace_path = app_config.goal_git_path

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
