"""Utility for configuring the application's logging system."""
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
    """Configures basic logging for the application with lowercase level names."""

    goal_root_path = Path(app_config.goal_root_path).resolve()
    log_subdirectory = goal_root_path / app_config.log_subdirectory_name
    # Ensure the log output subdirectory exists
    os.makedirs(log_subdirectory, exist_ok=True)
    # logger.info(f"Ensured log subdirectory exists: {log_subdirectory}")

    # Store resolved absolute paths for log files in WorkflowState
    # These keys 'overview_log_file_path' and 'detailed_log_file_path' are added
    # as per spec, assuming WorkflowState can accommodate them or will be updated.
    overview_log_file_path = str(log_subdirectory / app_config.overview_log_filename)
    detailed_log_file_path = str(log_subdirectory / app_config.detailed_log_filename)
    
    # Create a handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Create the custom formatter
    formatter = LowercaseLevelnameFormatter(
        fmt="%(asctime)s.%(msecs)03d: (%(levelname)s) %(message)s",
        # datefmt="%H:%M:%S"
        datefmt="%M:%S"
    )
    
    # Set the formatter for the handler
    handler.setFormatter(formatter)
    
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove any existing handlers (like the one basicConfig might add)
    if logger.hasHandlers():
        logger.handlers.clear()
        
    # Add our custom handler
    logger.addHandler(handler)
    
    # Example: logging.getLogger("aider_service").setLevel(logging.DEBUG)
    
