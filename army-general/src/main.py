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

async def _run_infantry_mission(mission_folder_path: str, root_git_path: str) -> bool:
    """
    Runs army-infantry for a single mission folder.
    """
    current_root_directory = Path(__file__).resolve().parent.parent.parent
    infantry_directory = current_root_directory / "army-infantry"

    command = [
        "uv", "run", "src/main.py",
        "--root_git_path", root_git_path,
        "--mission_folder_path", mission_folder_path
    ]
    logger.info(f"Constructed army-infantry run command: {' '.join(command)}")
    logger.info(f"Executing army-infantry from directory: {infantry_directory}")

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=str(infantry_directory),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if app_config.log_army_man_output: # Reusing old flag for infantry output
            _log_subprocess_details(
                process_name="army-infantry",
                stdout_content=stdout,
                stderr_content=stderr,
                return_code=process.returncode if process.returncode is not None else -1
            )

        if process.returncode != 0:
            logger.error(f"army-infantry execution failed for mission {mission_folder_path} with return code {process.returncode}.")
            return False
        logger.info(f"army-infantry completed successfully for mission {mission_folder_path}.")
        return True
    except FileNotFoundError:
        logger.error(f"Failed to run army-infantry: 'uv' command not found or army-infantry src not found at {infantry_directory / 'src/main.py'}. Ensure uv is installed and paths are correct.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while running army-infantry for {mission_folder_path}: {e}", exc_info=True)
        return False


async def _ensure_git_repo_state(
    git_service: GitService,
    original_branch: str,
    context_message_prefix: str,
    mission_folder_path: str | None = None
) -> None:
    """
    Ensures the Git repository is in a consistent state.
    Checks branch, stages, commits changes, and checks out the original branch.
    """
async def run() -> None:
    logger.info("Army General orchestration started.")
    git_service = GitService(app_config.root_git_path)
    original_branch = None

    try:
        # Get the original branch before running Secretary
        original_branch = await git_service.get_current_branch()
        if not original_branch:
            logger.error("Failed to determine the original Git branch. Aborting.")
            return
        logger.info(f"Original Git branch: {original_branch}")

        # Run Secretary to generate the missions and the output file
        secretary_output_file = app_config.secretary_output_file_path

        logger.info("Attempting to run Secretary...")
        if not _run_secretary():
            logger.error("Secretary execution failed. Further processing of its output will be skipped.")
            return

        logger.info(f"Expecting Secretary output file at: {secretary_output_file}")
        if not os.path.exists(secretary_output_file):
            logger.error(f"Secretary output file does not exist at the expected path: {secretary_output_file}.")
            logger.error("\n\n\n ERROR: Are you sure BACKLOG.md was filled out with tasks?\n\n")
            return

        # Get the mission folders to run the Infantry on
        folders = []
        try:
            with open(secretary_output_file) as file:
                folders = [line.strip() for line in file if line.strip()]
            logger.info(f"Successfully read and parsed Secretary output file. Found {len(folders)} mission folders.")
        except Exception as e:
            logger.error(f"Failed to read or parse secretary output file {secretary_output_file}: {e}")
            return

        if not folders:
            logger.warning("No mission folders found in Secretary output. No Infantry tasks to perform.")
            return

        # For each folder, run an infantry mission
        num_missions_worked_on = 0
        for folder_index, mission_folder_path_from_secretary in enumerate(folders):
            logger.info(f"Processing mission folder {folder_index + 1}/{len(folders)}: {mission_folder_path_from_secretary}")

            infantry_success = await _run_infantry_mission(mission_folder_path_from_secretary, app_config.root_git_path)

            if infantry_success:
                logger.info(f"army-infantry successfully processed mission: {mission_folder_path_from_secretary}")
            else:
                logger.warning(f"army-infantry failed to process mission: {mission_folder_path_from_secretary}. Continuing with cleanup.")

            # Ensure Git repo state after each infantry mission
            await _ensure_git_repo_state(
                git_service=git_service,
                original_branch=original_branch,
                context_message_prefix="Post-Infantry Cleanup",
                mission_folder_path=mission_folder_path_from_secretary
            )

            if infantry_success:
                 num_missions_worked_on +=1

        logger.info(f"Completed processing all mission folders. Total missions successfully processed by Infantry: {num_missions_worked_on}/{len(folders)}.")

    except Exception as e:
        logger.critical(f"An unhandled exception occurred in the main run loop: {e}", exc_info=True)
    finally:
        logger.info("Initiating cleanup procedures in the 'finally' block.")

        # Delete Secretary output file first, so its deletion can be part of the final commit
        secretary_file_to_delete = app_config.secretary_output_file_path
        logger.info(f"Attempting to delete Secretary output file: {secretary_file_to_delete}")
        if os.path.exists(secretary_file_to_delete):
            try:
                os.remove(secretary_file_to_delete)
                logger.info(f"Successfully deleted Secretary output file: {secretary_file_to_delete}")
            except OSError as e:
                logger.error(f"Error deleting Secretary output file {secretary_file_to_delete}: {e}. Manual cleanup might be required.")
        else:
            logger.info(f"Secretary output file {secretary_file_to_delete} was not found during cleanup; no deletion needed.")

        # Perform final Git cleanup and state check
        if original_branch and git_service:
            logger.info("Performing Army General final Git cleanup and state check.")
            await _ensure_git_repo_state(
                git_service=git_service,
                original_branch=original_branch,
                context_message_prefix="Army General Final Cleanup"
            )
        elif not original_branch:
            logger.info("Final cleanup: Original branch was not determined, skipping Git state check.")

    logger.info("Army General finished all operations.")

if __name__ == "__main__":
    # Python 3.7+
    asyncio.run(run())
