import logging
import re
from typing import List, Optional, Tuple

import git
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Constants
MAIN_BRANCH = "main"
FIRST_PASS_COMMIT_MSG_START = "First pass"
COMMIT_SEARCH_LIMIT = 50

class GitHandlerError(Exception):
    """Custom exception for Git handling errors."""
    pass

class CommitNotFoundError(GitHandlerError):
    """Exception raised when a specific commit cannot be found."""
    pass

class NoCommitsFoundError(GitHandlerError):
    """Exception raised when no commits are found in the specified range."""
    pass


def _get_repo() -> git.Repo:
    """Gets the Git repository object for the current directory."""
    try:
        repo = git.Repo(".", search_parent_directories=True)
        if repo.bare:
            raise GitHandlerError("Cannot operate on a bare repository.")
        return repo
    except (InvalidGitRepositoryError, NoSuchPathError) as e:
        raise GitHandlerError(f"Could not find a valid Git repository: {e}")
    except Exception as e:
        raise GitHandlerError(f"An unexpected error occurred while accessing the repository: {e}")

def find_merge_base(repo: git.Repo) -> git.Commit:
    """Finds the merge base commit between the current HEAD and the main branch."""
    try:
        head_commit = repo.head.commit
        main_commit = repo.commit(MAIN_BRANCH)
        merge_bases = repo.merge_base(head_commit, main_commit)
        if not merge_bases:
            raise GitHandlerError(f"Could not find a merge base between HEAD and '{MAIN_BRANCH}'.")
        # Typically returns a list, take the first one
        merge_base_commit = merge_bases[0]
        logging.info(f"Merge base with '{MAIN_BRANCH}' found: {merge_base_commit.hexsha[:7]}")
        return merge_base_commit
    except GitCommandError as e:
        raise GitHandlerError(f"Git command failed while finding merge base: {e}")
    except ValueError as e: # Handle case where main branch doesn't exist or has no commits
         raise GitHandlerError(f"Error finding merge base (is '{MAIN_BRANCH}' a valid branch with commits?): {e}")


def find_first_pass_commit(repo: git.Repo, merge_base: git.Commit) -> Optional[git.Commit]:
    """
    Searches the last COMMIT_SEARCH_LIMIT commits since the merge base
    for the most recent commit starting with "First pass".
    """
    try:
        head_commit = repo.head.commit
        commits_to_search = list(repo.iter_commits(f"{merge_base.hexsha}..{head_commit.hexsha}", max_count=COMMIT_SEARCH_LIMIT, reverse=True))
        # Iterate backwards (most recent first)
        for commit in reversed(commits_to_search):
            if commit.message.strip().lower().startswith(FIRST_PASS_COMMIT_MSG_START.lower()):
                logging.info(f"Found '{FIRST_PASS_COMMIT_MSG_START}' commit: {commit.hexsha[:7]}")
                return commit
        logging.warning(f"'{FIRST_PASS_COMMIT_MSG_START}' commit not found within the last {COMMIT_SEARCH_LIMIT} commits since merge base.")
        return None
    except GitCommandError as e:
        raise GitHandlerError(f"Git command failed while searching for '{FIRST_PASS_COMMIT_MSG_START}' commit: {e}")


def get_commit_after(repo: git.Repo, target_commit: git.Commit) -> Optional[git.Commit]:
    """Gets the commit immediately following the target commit in the current branch history."""
    try:
        # Get commits from target (exclusive) to HEAD (inclusive), take the first one (oldest)
        commits_after = list(repo.iter_commits(f"{target_commit.hexsha}..HEAD", reverse=True))
        if commits_after:
            return commits_after[0]
        else:
            # This means the target_commit *is* HEAD
            return None
    except GitCommandError as e:
        raise GitHandlerError(f"Git command failed while getting commit after {target_commit.hexsha[:7]}: {e}")


def get_commit_range(start_commit_exclusive_hex: Optional[str] = None, end_commit_inclusive_hex: Optional[str] = "HEAD") -> List[str]:
    """
    Determines the range of commits to analyze and returns their hashes.

    Args:
        start_commit_exclusive_hex: The hexsha of the commit *before* the first commit to include.
                                     If None, attempts to find the "First pass" commit automatically.
        end_commit_inclusive_hex: The hexsha of the last commit to include (defaults to HEAD).

    Returns:
        A list of commit hexshas in chronological order.

    Raises:
        GitHandlerError: If Git operations fail.
        CommitNotFoundError: If a specified commit hash is invalid.
        NoCommitsFoundError: If no commits are found in the range.
        RequiresUserInputError: If the "First pass" commit isn't found and no start hash is provided.
    """
    repo = _get_repo()
    merge_base = find_merge_base(repo)
    end_commit = repo.commit(end_commit_inclusive_hex) # Resolve HEAD or provided hash

    start_commit_inclusive = None

    if start_commit_exclusive_hex:
        try:
            start_exclusive_commit = repo.commit(start_commit_exclusive_hex)
            logging.info(f"Using provided start commit (exclusive): {start_exclusive_commit.hexsha[:7]}")
            start_commit_inclusive = get_commit_after(repo, start_exclusive_commit)
            if start_commit_inclusive is None:
                 raise NoCommitsFoundError(f"No commits found after the provided start commit {start_exclusive_commit.hexsha[:7]}.")
            logging.info(f"Actual analysis starts at commit: {start_commit_inclusive.hexsha[:7]}")
        except (ValueError, GitCommandError) as e:
            raise CommitNotFoundError(f"Invalid start commit hash provided '{start_commit_exclusive_hex}': {e}")
    else:
        # Attempt to find "First pass" commit
        first_pass_commit = find_first_pass_commit(repo, merge_base)
        if first_pass_commit:
            start_commit_inclusive = get_commit_after(repo, first_pass_commit)
            if start_commit_inclusive is None:
                raise NoCommitsFoundError(f"No commits found after the 'First pass' commit {first_pass_commit.hexsha[:7]} (it might be HEAD).")
            logging.info(f"Analysis starts after 'First pass' commit: {start_commit_inclusive.hexsha[:7]}")
        else:
            # Signal that user input is required - this will be handled in main.py
            raise CommitNotFoundError("'First pass' commit not found automatically.")


    # Ensure start commit is not before merge base (sanity check, though get_commit_after should handle this implicitly)
    if repo.is_ancestor(start_commit_inclusive, merge_base) and start_commit_inclusive != merge_base:
         logging.warning(f"Start commit {start_commit_inclusive.hexsha[:7]} is an ancestor of the merge base {merge_base.hexsha[:7]}. Analysis will proceed but might include unexpected commits.")


    # Get the list of commits in the range [start_commit_inclusive, end_commit]
    try:
        # iter_commits range is specified as older..newer
        commit_iterator = repo.iter_commits(f"{start_commit_inclusive.hexsha}^..{end_commit.hexsha}", reverse=True)
        commit_hashes = [c.hexsha for c in commit_iterator]
    except GitCommandError as e:
        raise GitHandlerError(f"Failed to retrieve commits between {start_commit_inclusive.hexsha[:7]} and {end_commit.hexsha[:7]}: {e}")

    if not commit_hashes:
        raise NoCommitsFoundError(f"No commits found between {start_commit_inclusive.hexsha[:7]} and {end_commit.hexsha[:7]}.")

    logging.info(f"Identified {len(commit_hashes)} commits for analysis (from {commit_hashes[0][:7]} to {commit_hashes[-1][:7]}).")
    return commit_hashes


def get_commit_details(repo: git.Repo, commit_hash: str) -> Tuple[str, str]:
    """Gets the full commit message and diff for a given commit hash."""
    try:
        commit = repo.commit(commit_hash)
        message = commit.message

        # Get the diff against the parent commit(s)
        # For merge commits, this shows the combined diff. For regular commits, it shows diff against the parent.
        # Using --full-index to ensure unambiguous blob identification.
        # Using -U10 for more context lines, adjust if needed.
        diff = repo.git.show(commit.hexsha, "--full-index", "-U10", "--pretty=format:%b", "--", ".", ":(exclude)*.md", ":(exclude)*.diff") # %b gets body only, message is separate

        # Handle potential empty diff for the very first commit if it's included
        if not commit.parents:
             diff = repo.git.show(commit.hexsha, "--full-index", "-U10", "--pretty=format:%b", "--", ".", ":(exclude)*.md", ":(exclude)*.diff") # Show initial content

        return message, diff
    except (ValueError, GitCommandError) as e:
        raise CommitNotFoundError(f"Could not get details for commit '{commit_hash}': {e}")


if __name__ == '__main__':
    # Example usage when run directly (requires a Git repo in the current or parent dir)
    try:
        print("Attempting to find commit range automatically...")
        hashes = get_commit_range()
        print(f"Found {len(hashes)} commits:")
        for h in hashes:
            print(f"- {h}")

        if hashes:
            print("\nGetting details for the first commit...")
            repo_instance = _get_repo()
            msg, diff_content = get_commit_details(repo_instance, hashes[0])
            print(f"\nMessage:\n{msg}")
            # print(f"\nDiff:\n{diff_content[:500]}...") # Print start of diff

    except CommitNotFoundError as e:
         print(f"Commit Not Found Error: {e}")
         print("This might require user input for the start commit hash.")
    except GitHandlerError as e:
        print(f"Git Error: {e}")
    except NoCommitsFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")