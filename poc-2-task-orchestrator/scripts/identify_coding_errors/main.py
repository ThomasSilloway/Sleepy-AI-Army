# /// script
# dependencies = [
#   "GitPython>=3.1.0"
# ]
# ///

import sys
import os
import logging

# Ensure the script's directory is in the path for relative imports
# This might be needed if running as 'python scripts/identify_coding_errors/main.py'
# instead of 'python -m scripts.identify_coding_errors.main'
# script_dir = os.path.dirname(os.path.abspath(__file__))
# if script_dir not in sys.path:
#     sys.path.insert(0, os.path.dirname(script_dir)) # Add parent ('scripts') to path

from feature_finder import find_latest_feature_folder, FeatureFinderError
from git_handler import (
    get_commit_range, _get_repo, GitHandlerError, CommitNotFoundError,
    NoCommitsFoundError
)
from diff_generator import generate_diff_files, DiffGeneratorError


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
GENERATED_DIR_NAME = "generated"
GIT_CHANGES_DIR_NAME = "git_changes"

def run_analysis():
    """
    Main function to orchestrate the Git commit analysis process.
    Finds the latest feature, determines the commit range, and generates diff files.
    Handles interactive prompting if the start commit cannot be found automatically.
    """
    logging.info("Starting Git commit analysis...")
    start_commit_hash_exclusive = None
    commit_hashes = []
    repo = None

    try:
        # 1. Find the latest feature folder
        logging.info("Identifying latest feature specification folder...")
        latest_feature_dir = find_latest_feature_folder()
        output_dir = os.path.join(latest_feature_dir, GENERATED_DIR_NAME, GIT_CHANGES_DIR_NAME)
        logging.info(f"Target output directory for diffs: {output_dir}")

        # 2. Get Git Repo object
        repo = _get_repo()

        # 3. Determine commit range
        logging.info("Determining commit range for analysis...")
        try:
            commit_hashes = get_commit_range()
        except CommitNotFoundError as e:
            # Specific handling for when "First pass" is not found
            if "'First pass' commit not found automatically" in str(e):
                logging.warning(f"{e} Please provide the commit hash *before* the analysis should start.")
                while not start_commit_hash_exclusive:
                    start_commit_hash_exclusive = input("Enter the short or full commit hash (exclusive): ").strip()
                    if not start_commit_hash_exclusive:
                        logging.warning("Commit hash cannot be empty.")
                try:
                    logging.info(f"Retrying commit range determination with provided start hash: {start_commit_hash_exclusive}")
                    commit_hashes = get_commit_range(start_commit_exclusive_hex=start_commit_hash_exclusive)
                except (CommitNotFoundError, NoCommitsFoundError, GitHandlerError) as inner_e:
                    # Handle errors specifically related to the user-provided hash
                    logging.error(f"Failed to determine commit range using provided hash '{start_commit_hash_exclusive}': {inner_e}")
                    sys.exit(1) # Exit if user input leads to error
            else:
                # Re-raise if it's a different CommitNotFoundError (e.g., invalid hash provided initially)
                raise e

        # Check if we have hashes before proceeding
        if not commit_hashes:
             logging.error("Failed to obtain a list of commits for analysis.")
             sys.exit(1)

        # 4. Generate diff files
        logging.info(f"Generating diff files for {len(commit_hashes)} commits...")
        generate_diff_files(commit_hashes, output_dir, repo)

        logging.info("Git commit analysis completed successfully.")
        logging.info(f"Diff files generated in: {output_dir}")

    except FeatureFinderError as e:
        logging.error(f"Error finding feature folder: {e}")
        sys.exit(1)
    except CommitNotFoundError as e:
         # Catch errors not handled by the interactive prompt logic (e.g., invalid HEAD)
         logging.error(f"Error related to commit finding: {e}")
         sys.exit(1)
    except NoCommitsFoundError as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    except GitHandlerError as e:
        logging.error(f"Git interaction error: {e}")
        sys.exit(1)
    except DiffGeneratorError as e:
        logging.error(f"Error generating diff files: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
         logging.warning("\nAnalysis interrupted by user.")
         sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True) # Log traceback for unexpected errors
        sys.exit(1)

if __name__ == "__main__":
    run_analysis()