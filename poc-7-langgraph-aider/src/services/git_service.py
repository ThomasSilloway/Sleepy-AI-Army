import subprocess
import os

class GitService:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        if not os.path.isdir(os.path.join(repo_path, '.git')):
            raise ValueError(f"'{repo_path}' is not a valid Git repository.")

    def _run_git_command(self, command: list[str]) -> str:
        try:
            process = subprocess.run(
                ["git"] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True, # Will raise CalledProcessError for non-zero exit codes
                encoding='utf-8' # Explicitly set encoding
            )
            return process.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise # Re-raise the exception or handle it as appropriate
        except FileNotFoundError:
            raise

    def get_last_commit_hash(self) -> str | None:
        try:
            return self._run_git_command(["rev-parse", "HEAD"])
        except subprocess.CalledProcessError:
            return None # Or handle more specifically

    def get_last_commit_summary(self) -> str | None:
        try:
            return self._run_git_command(["log", "-n", "1", "--pretty=format:%s"])
        except subprocess.CalledProcessError:
            return None

    def get_last_commit_file_stats(self) -> str | None:
        try:
            # This assumes there's more than one commit. If it's the very first commit,
            # HEAD~1 won't exist. A more robust way for the first commit might be needed
            # or ensure your repo always has an initial commit before aider runs.
            # For a first commit, `git show --stat --pretty=format:"" HEAD` might be better.
            num_commits_str = self._run_git_command(["rev-list", "--count", "HEAD"])
            if int(num_commits_str) > 1:
                return self._run_git_command(["diff", "--stat", "HEAD~1", "HEAD"])
            else: # Handle the case of a single commit (initial commit)
                return self._run_git_command(["show", "--stat", "--pretty=format:\"\"", "HEAD"]) # Get stat for the initial commit
        except (subprocess.CalledProcessError, ValueError):
            return None
