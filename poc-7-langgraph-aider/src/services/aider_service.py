"""Defines the AiderService class."""
import logging
import subprocess
import sys
import threading
import os
from typing import List, Optional # Use List instead of list for older Python compatibility if needed, but stick to list per CONVENTIONS.md

from src.config import AppConfig

logger = logging.getLogger(__name__)


def stream_output(pipe, log_func):
    """Reads lines from a pipe and logs them using the provided logging function."""
    try:
        for line in iter(pipe.readline, ''):
            log_func(line.strip())
    finally:
        pipe.close()

class AiderService:
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config

    def execute(self, command_args: list[str], files_to_add: Optional[list[str]] = None) -> int:
        """
        Executes an aider command as a subprocess, streams its output, and returns the exit code.

        Args:
            command_args: A list of arguments to pass to the aider CLI.
            files_to_add: An optional list of file paths to be included in the aider command execution context.

        Returns:
            An integer representing the exit code of the aider command.
        """
        if files_to_add is None:
            files_to_add = []

        full_command = ["aider"] + files_to_add + command_args + [
            "--yes-always",
        ]
        
        logger.info(f"Executing aider command: {' '.join(full_command)}")
        # Consider adding: cwd=self.workspace_path if needed

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
                encoding='utf-8'
                # cwd=self.workspace_path # Uncomment if aider needs to run in workspace
            )

            # Create threads to stream stdout and stderr
            stdout_thread = threading.Thread(target=stream_output, args=(process.stdout, logger.info))
            stderr_thread = threading.Thread(target=stream_output, args=(process.stderr, logger.error))

            # Start the threads
            stdout_thread.start()
            stderr_thread.start()

            # Wait for the threads to finish (which they will when the streams close)
            stdout_thread.join()
            stderr_thread.join()

            # Wait for the subprocess to terminate and get the exit code
            exit_code = process.wait()
            logger.info(f"Aider command finished with exit code: {exit_code}")

            return exit_code

        except FileNotFoundError:
            logger.critical("Error: 'aider' command not found. Is aider installed and in the system PATH?")
            return -1 # Indicate a failure to even start the process
        except Exception as e:
            logger.critical(f"An unexpected error occurred while executing aider: {e}", exc_info=True)
            return -1 # Indicate a general failure
