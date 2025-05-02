import os
import re
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Constants
AI_SPECS_DIR = "ai-specs"
FOLDER_PATTERN = re.compile(r"(\d{2}-\d{2})_(\d{2})_.*") # MM-DD_NN_*

class FeatureFinderError(Exception):
    """Custom exception for errors during feature folder finding."""
    pass

def find_latest_feature_folder(base_dir: str = AI_SPECS_DIR) -> str:
    """
    Scans the base directory for feature specification folders matching the
    MM-DD_NN_* pattern, sorts them, and returns the path to the latest one.

    Args:
        base_dir: The directory to scan (defaults to AI_SPECS_DIR).

    Returns:
        The absolute path to the latest feature folder.

    Raises:
        FeatureFinderError: If the base directory doesn't exist, is not a directory,
                          or if no matching feature folders are found.
    """
    if not os.path.isdir(base_dir):
        raise FeatureFinderError(f"Base directory '{base_dir}' not found or is not a directory.")

    matching_folders = []
    try:
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path):
                match = FOLDER_PATTERN.match(item)
                if match:
                    date_str = match.group(1)
                    seq_str = match.group(2)
                    try:
                        # Use a fixed year (e.g., current year) for consistent sorting
                        # Assuming features don't span across year boundaries for sorting purposes
                        current_year = datetime.now().year
                        folder_date = datetime.strptime(f"{current_year}-{date_str}", "%Y-%m-%d")
                        sequence_num = int(seq_str)
                        matching_folders.append((folder_date, sequence_num, item_path))
                    except ValueError:
                        logging.warning(f"Could not parse date/sequence from folder name: {item}")
                        continue # Skip folders with invalid date/sequence format
    except OSError as e:
        raise FeatureFinderError(f"Error accessing directory '{base_dir}': {e}")

    if not matching_folders:
        raise FeatureFinderError(f"No feature folders matching the pattern 'MM-DD_NN_*' found in '{base_dir}'.")

    # Sort by date (descending), then by sequence number (descending)
    matching_folders.sort(key=lambda x: (x[0], x[1]), reverse=True)

    latest_folder_path = matching_folders[0][2]
    logging.info(f"Latest feature folder identified: {os.path.basename(latest_folder_path)}")
    return os.path.abspath(latest_folder_path)

if __name__ == '__main__':
    # Example usage when run directly
    try:
        latest_folder = find_latest_feature_folder()
        print(f"Found latest feature folder: {latest_folder}")
    except FeatureFinderError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")