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

def _run_secretary() -> bool:
    # Implement Secretary execution:
    #    - Construct command and execute using app_config.secretary_run_command_template.
    command_to_run = app_config.secretary_run_command_template.format(
        target_folder=app_config.root_git_path
    )
    logger.info(f"Constructed Secretary run command: {command_to_run}")
    logger.info("Executing Secretary...")

    # Current project root directory
    current_root_directory = Path(__file__).resolve().parent.parent.parent
    secretary_directory = os.path.join(current_root_directory, "army-secretary")
    logger.info(f"Secretary directory: {secretary_directory}")

    # Run Secretary
    try:
        logger.info("Running Secetary...")
        process = subprocess.run(
            command_to_run,
            cwd=secretary_directory,
            capture_output=True,
            text=True,
            check=True, # Will raise CalledProcessError for non-zero exit codes
            encoding='utf-8' # Explicitly set encoding
        )
        if process.returncode != 0:
            logger.error("Secretary returned non-zero exit code. Exiting.")
            return False
        logger.info("Secretary completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Run Secretary failed: {e}")
        return False
    except FileNotFoundError:
        logger.error("Run Secretary failed")
        return False

    return True

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
            text=True,
            check=True, # Will raise CalledProcessError for non-zero exit codes
            encoding='utf-8' # Explicitly set encoding
        )
        if process.returncode != 0:
            logger.error("Army Man returned non-zero exit code. Exiting.")
            return False
        logger.info("Army Man completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Run Army Man failed: {e}")
        return False
    except FileNotFoundError:
        logger.error("Run Army Man failed")
        return False

    return True

async def run() -> None:
    """
    Main function for the Army General orchestrator.
    """
    logger.info("Orchestration logic will go here.")

    if not _run_secretary():
        logger.error("Secretary execution failed. Exiting Army General.")
        return

    # Get the secretary output file that contains the folders to operate on
    secretary_output_file = app_config.secretary_output_file_path
    logger.info(f"Secretary output file: {secretary_output_file}")
    if not os.path.exists(secretary_output_file):
        logger.error(f"Secretary output file does not exist: {secretary_output_file}")
        return

    # Parse the folders from the file, each folder path is a single line in the file
    with open(secretary_output_file) as file:
        folders = [line.strip() for line in file if line.strip()]

    logger.info(f"Found {len(folders)} folders to process from Secretary output.")
    if not folders:
        logger.warning("No folders found in Secretary output. Exiting Army General.")
        return

    num_goals_worked_on = 0

    # For each folder, run the Army Man
    for folder in folders:
        logger.info(f"Processing folder: {folder}")
        if _run_army_man(folder):
            num_goals_worked_on += 1
            logger.info(f"Successfully worked on goal in folder: {folder}")

    logger.info("Army General finished.")

if __name__ == "__main__":
    # Python 3.7+
    asyncio.run(run())
