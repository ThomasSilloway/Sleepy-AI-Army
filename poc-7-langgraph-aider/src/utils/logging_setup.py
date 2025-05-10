"""Utility for configuring the application's logging system."""
import logging
import sys
# from .config import AppConfig # Assuming AppConfig is accessible

# Logging setup (placeholder). Actual file logging to be configured based on AppConfig

class LowercaseLevelnameFormatter(logging.Formatter):
    def format(self, record):
        record.levelname = record.levelname.lower()
        return super().format(record)

def setup_logging(log_level=logging.INFO):
    """Configures basic logging for the application with lowercase level names."""
    
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
    
