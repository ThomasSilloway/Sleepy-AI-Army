"""Utility for configuring the application's logging system."""
from datetime import datetime
import logging
import os
from pathlib import Path
import sys

OVERVIEW_LEVEL_NUM = 25  # Positioned between INFO (20) and WARNING (30)
OVERVIEW_LEVEL_NAME = "OVERVIEW"
logging.addLevelName(OVERVIEW_LEVEL_NUM, OVERVIEW_LEVEL_NAME)

def overview_log_method(self, message, *args, **kws):
    if self.isEnabledFor(OVERVIEW_LEVEL_NUM):
        # Yes, logger takes its '*args' as 'args'.
        self._log(OVERVIEW_LEVEL_NUM, message, args, **kws)

logging.Logger.overview = overview_log_method
# Now you can use logger.overview("Your message")

class LowercaseLevelnameFormatter(logging.Formatter):
    def format(self, record):
        record.levelname = record.levelname.lower()
        return super().format(record)

def setup_logging(app_config, log_level=logging.INFO):
    """Configures logging for the application with console and file outputs."""

    goal_root_path = Path(app_config.goal_root_path).resolve()
    log_subdirectory = goal_root_path / app_config.log_subdirectory_name
    os.makedirs(log_subdirectory, exist_ok=True)

    overview_log_file_path = str(log_subdirectory / app_config.overview_log_filename)
    detailed_log_file_path = str(log_subdirectory / app_config.detailed_log_filename)
    
    # Spec mentioned: fmt="[%(asctime)s.%(msecs)03d] (%(levelname)s) [%(name)s] %(message)s", datefmt="%H:%M:%S"
    # Adding [%(name)s] to file_formatter as per typical detailed logging.
    file_formatter = LowercaseLevelnameFormatter(     
        fmt="[%(asctime)s.%(msecs)03d] (%(levelname)s) %(message)s",
        datefmt="%H:%M:%S"
    )

    console_formatter = LowercaseLevelnameFormatter(
        fmt="%(asctime)s.%(msecs)03d: (%(levelname)s) %(message)s", # Keeping console simpler
        datefmt="%M:%S" # Console uses MM:SS for brevity as per your current code
    )
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG) # Set root to lowest level to allow handlers to filter
    
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    # Configure Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level) # Console level controlled by passed-in log_level
    root_logger.addHandler(console_handler)

    # Configure Overview File Handler
    overview_file_handler = logging.FileHandler(overview_log_file_path, mode='a') # Use 'a' for append
    overview_file_handler.setFormatter(file_formatter)
    # Set this handler to only capture OVERVIEW level and above (WARNING, ERROR, CRITICAL)
    overview_file_handler.setLevel(OVERVIEW_LEVEL_NUM) 
    root_logger.addHandler(overview_file_handler)

    # Configure Detailed File Handler
    detailed_file_handler = logging.FileHandler(detailed_log_file_path, mode='a') # Use 'a' for append
    detailed_file_handler.setFormatter(file_formatter)
    # This handler captures DEBUG and above (so DEBUG, INFO, OVERVIEW, WARNING, ERROR, CRITICAL)
    detailed_file_handler.setLevel(logging.DEBUG) 
    root_logger.addHandler(detailed_file_handler)

    # Initial log message to confirm setup and show date
    # Changed to use the newly defined logger.overview for this prominent message
    root_logger.overview(f"\n\n======== Logging initialized. Date: {datetime.now().strftime('%Y-%m-%d')} =========\n\n")
    root_logger.info("Detailed logging started (includes INFO, DEBUG, OVERVIEW, etc.).")
    root_logger.debug("Debug level test message for detailed log.")
