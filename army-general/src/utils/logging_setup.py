import logging
from pathlib import Path

from src.config import AppConfig  # Added import


class LowercaseLevelnameFormatter(logging.Formatter):
    """Custom formatter to output lowercase levelnames."""
    def format(self, record):
        record.levelname = record.levelname.lower()
        return super().format(record)

class LoggingSetup:
    """Handles the setup of logging configurations."""

    def __init__(self, app_config: AppConfig):
        self.app_config = app_config

        PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent.parent

        log_dir_name_str = self.app_config.default_log_directory
        log_file_name_str = self.app_config.default_log_filename

        self.log_dir_path = PROJECT_ROOT_DIR / log_dir_name_str
        self.log_file_path = self.log_dir_path / log_file_name_str

    def setup_logging(self):
        """Configures the logging system."""
        # Create the log directory if it doesn't exist
        self.log_dir_path.mkdir(parents=True, exist_ok=True)

        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # Set the lowest level for the root logger

        # Remove any existing handlers to avoid duplicate logs
        # This is important if setup_logging can be called multiple times
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = LowercaseLevelnameFormatter(
            "%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s", # Simplified format
            datefmt="%M:%S", # Shorter time format
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File Handler
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = LowercaseLevelnameFormatter(
            "%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logging.debug("Logging setup complete.")
        logging.info(f"Logs will be written to: {self.log_file_path.resolve()}")
