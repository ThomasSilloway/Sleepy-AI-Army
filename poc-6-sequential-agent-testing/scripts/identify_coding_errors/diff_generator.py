import os
import logging
from typing import List

import git # For type hinting Repo object
from git_handler import get_commit_details, CommitNotFoundError, GitHandlerError, _get_repo # Use internal repo getter if needed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class DiffGeneratorError(Exception):
    """Custom exception for errors during diff file generation."""
    pass

def generate_diff_files(commit_hashes: List[str], output_dir: str, repo: git.Repo) -> None:
    """
    Generates .diff files for a list of commit hashes.

    Each file contains the commit message followed by the code diff. Files are
    named sequentially (01_<short_hash>.diff, 02_<short_hash>.diff, ...).

    Args:
        commit_hashes: A list of commit hexshas in chronological order.
        output_dir: The directory where the .diff files will be saved.
        repo: The GitPython Repo object.

    Raises:
        DiffGeneratorError: If the output directory cannot be created or
                          if there's an error writing a file.
        CommitNotFoundError: If details for a specific commit cannot be retrieved.
        GitHandlerError: For other Git-related errors during detail retrieval.
    """
    if not commit_hashes:
        logging.warning("No commit hashes provided to generate diff files.")
        return

    try:
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Ensured output directory exists: {output_dir}")
    except OSError as e:
        raise DiffGeneratorError(f"Failed to create output directory '{output_dir}': {e}")

    num_commits = len(commit_hashes)
    max_digits = len(str(num_commits)) # For padding filenames like 01, 02... or 001, 002...

    for index, commit_hash in enumerate(commit_hashes):
        seq_num_str = str(index + 1).zfill(max_digits)
        short_hash = commit_hash[:7]
        filename = f"{seq_num_str}_{short_hash}.diff"
        filepath = os.path.join(output_dir, filename)

        logging.info(f"Processing commit {index + 1}/{num_commits}: {short_hash}")

        try:
            message, diff_content = get_commit_details(repo, commit_hash)

            # Ensure content ends with a newline
            if not message.endswith('\n'):
                message += '\n'
            if not diff_content.endswith('\n'):
                diff_content += '\n'

            file_content = f"Commit: {commit_hash}\n"
            file_content += f"Message:\n{message}\n"
            file_content += "---\n\n" # Separator between message and diff
            file_content += f"Diff:\n{diff_content}"

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_content)
            logging.debug(f"Successfully wrote diff file: {filepath}")

        except CommitNotFoundError as e:
            logging.error(f"Could not get details for commit {short_hash}. Skipping file generation. Error: {e}")
            # Decide whether to raise or just log and continue
            # Raising here to halt the process if a commit is problematic
            raise
        except GitHandlerError as e:
             logging.error(f"Git error processing commit {short_hash}. Skipping file generation. Error: {e}")
             raise
        except OSError as e:
            raise DiffGeneratorError(f"Failed to write diff file '{filepath}': {e}")
        except Exception as e:
            # Catch unexpected errors during processing of a single commit
            raise DiffGeneratorError(f"An unexpected error occurred while processing commit {short_hash}: {e}")

    logging.info(f"Successfully generated {num_commits} diff files in {output_dir}")


if __name__ == '__main__':
    # Example usage (requires manual setup of repo, hashes, and output dir)
    print("This script is intended to be called from main.py.")
    # Example:
    # try:
    #     repo_instance = _get_repo() # Assumes repo in current dir structure
    #     # Replace with actual hashes from git_handler output
    #     test_hashes = ["hash1", "hash2"]
    #     test_output_dir = "temp_diff_output"
    #     generate_diff_files(test_hashes, test_output_dir, repo_instance)
    #     print(f"Example diff files generated in {test_output_dir}")
    # except (DiffGeneratorError, CommitNotFoundError, GitHandlerError) as e:
    #     print(f"Error during example run: {e}")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")