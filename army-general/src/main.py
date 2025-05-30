"""
Army General Main Orchestrator

This script serves as the main entry point for the Army General component.
It loads configuration, then orchestrates the execution of Secretary and
Army Man components to process development tasks.
"""
import asyncio
import logging
from datetime import datetime

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


async def run() -> None:
    """
    Main function for the Army General orchestrator.
    """
    logger.info("Orchestration logic will go here.")
    # TODO:
    # 1. Implement Secretary execution:
    #    - Construct command and execute using app_config.secretary_run_command_template.
    # 2. Implement Army Man execution loop:
    #    - For each folder from Secretary:
    #        - Construct command using app_config.army_man_run_command_template.
    #        - Execute subprocess, handle errors.
    #        - Log result.

    logger.info("Army General finished.")

if __name__ == "__main__":
    # Python 3.7+
    asyncio.run(run())
