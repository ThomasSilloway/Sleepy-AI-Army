"""
Army General Main Orchestrator

This script serves as the main entry point for the Army General component.
It loads configuration, then orchestrates the execution of Secretary and
Army Man components to process development tasks.
"""
import asyncio
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

from config import AppConfig
from services.git_service import GitService
from utils.logging_setup import LoggingSetup

# 1. Initialize AppConfig first
app_config = AppConfig()

# 2. Initialize and setup logging using AppConfig
logging_setup = LoggingSetup(app_config=app_config)
logging_setup.setup_logging()

# Get the logger instance
logger = logging.getLogger(__name__)


# Initial log message to confirm setup and show date
logger.info(f"\n\n======== Logging initialized via LoggingSetup & AppConfig. Date: {datetime.now().strftime('%Y-%m-%d')} =========\n\n")
logger.debug("Debug level test message for detailed log from main.py.")


def _log_subprocess_details(
    process_name: str,
    stdout_content: str | bytes,
    stderr_content: str | bytes,
    return_code: int
) -> None:
    """Logs the stdout and stderr from a subprocess if log_flag is True.

    Args:
        process_name: Name of the subprocess (e.g., "Secretary") for log prefixes.
        stdout_content: The stdout content (str or bytes) from the subprocess.
        stderr_content: The stderr content (str or bytes) from the subprocess.
        return_code: The return code of the subprocess, used to determine
                     log level for stderr (ERROR if non-zero, WARNING if zero).
    """
    logger.info(f"--- Start of output from {process_name} ---")

    # Process stdout
    stdout_str = stdout_content.decode('utf-8', errors='replace') if isinstance(stdout_content, bytes) else stdout_content
    if stdout_str and stdout_str.strip():
        for line in stdout_str.splitlines():
            logger.info(f"[{process_name.upper()} STDOUT]: {line}")
    else:
        logger.info(f"[{process_name.upper()} STDOUT]: (empty)")

    # Process stderr
    stderr_str = stderr_content.decode('utf-8', errors='replace') if isinstance(stderr_content, bytes) else stderr_content
    if stderr_str and stderr_str.strip():
        log_level = logging.ERROR if return_code != 0 else logging.WARNING
        for line in stderr_str.splitlines():
            logger.log(log_level, f"[{process_name.upper()} STDERR]: {line}")
    else:
        # Log as INFO if stderr is empty, consistent with previous behavior for empty streams
        logger.info(f"[{process_name.upper()} STDERR]: (empty)")

    logger.info(f"--- End of output from {process_name} ---")


def _run_secretary() -> bool:
    # Implement Secretary execution:
    #    - Construct command and execute using app_config.secretary_run_command_template.
    command_to_run = app_config.secretary_run_command_template.format(
        target_folder=app_config.root_git_path
    )
    logger.info(f"Constructed Secretary run command: {command_to_run}")

    # Current project root directory
    current_root_directory = Path(__file__).resolve().parent.parent.parent
    secretary_directory = os.path.join(current_root_directory, "army-secretary")
    logger.info(f"Secretary directory: {secretary_directory}")

    # Run Secretary
    try:
        process = subprocess.run(
            command_to_run,
            cwd=secretary_directory,
            capture_output=True,
            text=True,        # Ensure text=True for str output
            check=True,       # Ensure check=True to raise CalledProcessError on non-zero
            encoding='utf-8'
        )
        if app_config.log_secretary_output:
            # If check=True, we only reach here if returncode is 0
            _log_subprocess_details(
                process_name="Secretary",
                stdout_content=process.stdout, # Will be str
                stderr_content=process.stderr, # Will be str
                return_code=process.returncode # Will be 0 here
            )
        logger.info("Secretary completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        # Log the primary error message first
        logger.error(f"Run Secretary failed with CalledProcessError: {e.returncode} - {e}")
        # Then log the detailed output if flag is set
        if app_config.log_secretary_output:
            _log_subprocess_details(
                process_name="Secretary",
                stdout_content=e.stdout, # Will be bytes
                stderr_content=e.stderr, # Will be bytes
                return_code=e.returncode
            )
        return False
    except FileNotFoundError:
        logger.error(f"Run Secretary command not found: {command_to_run}")
        return False

def _run_army_man(folder: str) -> bool:
    """
    Run the Army Man to work on a goal in the folder provided.  Implemented similar to _run_secretary
    """
    command_to_run = app_config.army_man_run_command_template.format(
        target_folder=app_config.root_git_path,
        goal_path=folder
    )
    logger.info(f"Constructed Army Man run command: {command_to_run}")
    logger.info("Executing Army Man...")

    # Current project root directory
    current_root_directory = Path(__file__).resolve().parent.parent.parent
    army_man_directory = os.path.join(current_root_directory, "army-man-small-tweak")
    logger.info(f"Army Man directory: {army_man_directory}")

    # Run Secretary
    try:
        logger.info("Running Army Man...")
        process = subprocess.run(
            command_to_run,
            cwd=army_man_directory,
            capture_output=True,
            text=True,        # Ensure text=True
            check=True,       # Ensure check=True
            encoding='utf-8'
        )
        if app_config.log_army_man_output:
            _log_subprocess_details(
                process_name="Army Man",
                stdout_content=process.stdout,
                stderr_content=process.stderr,
                return_code=process.returncode
            )
        logger.info("Army Man completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Run Army Man failed with CalledProcessError: {e.returncode} - {e}")
        if app_config.log_army_man_output:
            _log_subprocess_details(
                process_name="Army Man",
                stdout_content=e.stdout,
                stderr_content=e.stderr,
                return_code=e.returncode
            )
        return False
    except FileNotFoundError:
        logger.error(f"Run Army Man command not found: {command_to_run}")
        return False

async def run() -> None:
    logger.info("Army General orchestration started.")

    secretary_output_file = app_config.secretary_output_file_path
    secretary_executed_successfully = False 

    try:
        logger.info("Attempting to run Secretary...")
        if not _run_secretary():
            logger.error("Secretary execution failed. Further processing of its output will be skipped.")
        else:
            secretary_executed_successfully = True

        # Proceed only if Secretary was successful
        if not secretary_executed_successfully:
            logger.warning("Skipping processing of Secretary's output file due to earlier errors.")
            return # Exits run(), 'finally' block will execute.

        logger.info(f"Expecting Secretary output file at: {secretary_output_file}")
        if not os.path.exists(secretary_output_file):
            logger.error(f"Secretary output file does not exist at the expected path: {secretary_output_file}.")
            logger.error("\n\n\n ERROR: Are you sure BACKLOG.md was filled out with tasks?\n\n")
            return # Exits run(), 'finally' block will execute.

        # Parse the folders from the file
        folders = []
        try: # Nested try for file reading
            with open(secretary_output_file) as file:
                folders = [line.strip() for line in file if line.strip()]
            logger.info(f"Successfully read and parsed Secretary output file. Found {len(folders)} folders.")
        except Exception as e: # Catch any exception during file open/read
            logger.error(f"Failed to read or parse secretary output file {secretary_output_file}: {e}")
            return # Exits run(), 'finally' block will execute.

        if not folders:
            logger.warning("No folders found in Secretary output. No Army Man tasks to perform.")
            return # Exits run(), 'finally' block will execute.

        num_goals_worked_on = 0
        for folder_index, folder in enumerate(folders):
            logger.info(f"Processing folder {folder_index + 1}/{len(folders)}: {folder}")
            if _run_army_man(folder): # Assumes _run_army_man() returns bool
                num_goals_worked_on += 1
                logger.info(f"Successfully completed Army Man task for folder: {folder}")
            else:
                logger.warning(f"Army Man task failed for folder: {folder}. Continuing with next folder if any.")

        logger.info(f"Completed processing all folders. Total goals worked on: {num_goals_worked_on}/{len(folders)}.")

    finally:
        # Cleanup: Attempt to delete the secretary_output_file.
        # This block executes regardless of exceptions or return statements in the try block.
        logger.info(f"Initiating cleanup of Secretary output file: {secretary_output_file}")
        if os.path.exists(secretary_output_file):
            try:
                os.remove(secretary_output_file)
                logger.info(f"Successfully cleaned up Secretary output file: {secretary_output_file}")
                git_service = GitService(app_config.root_git_path)
                commit_message = "AI Army General - Work Completed"
                if await git_service.commit_changes(commit_message):
                    logger.info(f"Committed changes to git with message: {commit_message}")
                else:
                    logger.warning("Failed to commit changes to git.")
            except OSError as e:
                logger.error(f"Error deleting Secretary output file {secretary_output_file}: {e}. Manual cleanup might be required.")
        else:
            # This is not necessarily an error condition.
            # It could mean Secretary failed before creating it, or it was (unexpectedly) already cleaned.
            logger.info(f"Secretary output file {secretary_output_file} was not found during cleanup. This may be normal if Secretary did not produce it or if it was already handled.")

    logger.info("Army General finished all operations.") # This is after the try-finally structure.

if __name__ == "__main__":
    # Python 3.7+
    asyncio.run(run())
