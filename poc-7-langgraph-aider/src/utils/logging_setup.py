"""Utility for configuring the application's logging system."""
import datetime
import logging
import os
from pathlib import Path
import sys
from src.config import AppConfig

# Logging setup (placeholder). Actual file logging to be configured based on AppConfig
class LowercaseLevelnameFormatter(logging.Formatter):
    def format(self, record):
        record.levelname = record.levelname.lower()
        return super().format(record)

def setup_logging(app_config: AppConfig, log_level=logging.INFO):
    """Configures logging for the application with console and file outputs."""

    goal_root_path = Path(app_config.goal_root_path).resolve()
    log_subdirectory = goal_root_path / app_config.log_subdirectory_name
    # Ensure the log output subdirectory exists
    os.makedirs(log_subdirectory, exist_ok=True)

    overview_log_file_path = str(log_subdirectory / app_config.overview_log_filename)
    detailed_log_file_path = str(log_subdirectory / app_config.detailed_log_filename)
    
    # Create the custom formatter
    # Spec: fmt="[%(asctime)s.%(msecs)03d] (%(levelname)s) [%(name)s] %(message)s", datefmt="%H:%M:%S"
    file_formatter = LowercaseLevelnameFormatter(       

        fmt="[%(asctime)s.%(msecs)03d] (%(levelname)s) %(message)s",
        datefmt="%H:%M:%S"
    )

    console_formatter = LowercaseLevelnameFormatter(
        fmt="%(asctime)s.%(msecs)03d: (%(levelname)s) %(message)s",
        datefmt="%M:%S"
    )
    
    # Get the root logger
    root_logger = logging.getLogger()
    # Set root logger to DEBUG to allow detailed file handler to capture DEBUG messages
    # Individual handlers will filter messages at their configured levels.
    root_logger.setLevel(logging.DEBUG) 
    
    # Remove any existing handlers (like the one basicConfig might add)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    # Configure Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level) # Use the passed log_level for console
    root_logger.addHandler(console_handler)

    # Configure Overview File Handler
    overview_file_handler = logging.FileHandler(overview_log_file_path)
    overview_file_handler.setFormatter(file_formatter)
    overview_file_handler.setLevel(logging.INFO) # Overview log at INFO level
    root_logger.addHandler(overview_file_handler)

    # Configure Detailed File Handler
    detailed_file_handler = logging.FileHandler(detailed_log_file_path)
    detailed_file_handler.setFormatter(file_formatter)
    detailed_file_handler.setLevel(logging.DEBUG) # Detailed log at DEBUG level
    root_logger.addHandler(detailed_file_handler)

    # Print out today's date
    # print(f"Today's date: {datetime.now().strftime('%Y-%m-%d')}") # this doesn't work - AttributeError: module 'datetime' has no attribute 'now'
    logging.info(f"========= Today's date: {datetime.datetime.now().strftime('%Y-%m-%d')} ===========")
    
    # Example: logging.getLogger("aider_service").setLevel(logging.DEBUG)
    # This kind of specific logger level setting can still be done elsewhere if needed,
    # after this general setup.
