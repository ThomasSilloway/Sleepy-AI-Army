import asyncio
import logging
import os
import shlex

logger = logging.getLogger(__name__)

class GitServiceError(Exception):
    """Custom exception for GitService errors."""
    def __init__(self, message: str, stderr: str | None = None):
        super().__init__(message)
        self.stderr = stderr

    def __str__(self):
        if self.stderr:
            return f"{super().__str__()} - Stderr: {self.stderr}"
        return super().__str__()

class GitService:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        if not os.path.isdir(os.path.join(repo_path, '.git')):
            logger.error(f"'{repo_path}' is not a valid Git repository.")
            raise ValueError(f"'{repo_path}' is not a valid Git repository.")
        logger.info(f"GitService initialized for repository: {repo_path}")

    async def _run_git_command(self, command_str: str) -> tuple[str, str]:
        """
        Runs a git command asynchronously and returns stdout and stderr.
        """
        git_path = "git" # Assuming git is in PATH

        # Ensure the command is properly split for subprocess
        # shlex.split is good for this, but git_path needs to be prepended
        full_command_list = [git_path] + shlex.split(command_str)

        logger.debug(f"Running git command: {' '.join(full_command_list)} in {self.repo_path}")

        process = await asyncio.create_subprocess_exec(
            *full_command_list,
            cwd=self.repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        stdout_str = stdout.decode('utf-8').strip()
        stderr_str = stderr.decode('utf-8').strip()

        if process.returncode != 0:
            error_message = f"Git command '{' '.join(full_command_list)}' failed with exit code {process.returncode}"
            logger.error(f"{error_message} - Stderr: {stderr_str}")
            raise GitServiceError(error_message, stderr=stderr_str)

        logger.debug(f"Git command stdout: {stdout_str}")
        if stderr_str: # Log stderr even on success if it's not empty
            logger.debug(f"Git command stderr: {stderr_str}")

        return stdout_str, stderr_str

    async def get_current_branch(self) -> str:
        """
        Gets the current active branch name.
        Example: git rev-parse --abbrev-ref HEAD
        """
        try:
            stdout, _ = await self._run_git_command("rev-parse --abbrev-ref HEAD")
            if not stdout:
                raise GitServiceError("`get_current_branch` returned empty or unexpected stdout and not 'HEAD'.")
            logger.info(f"Current branch: {stdout}")
            return stdout
        except GitServiceError as e:
            logger.error(f"Error getting current branch: {e}")
            raise

    async def create_branch(self, branch_name: str) -> bool:
        """
        Creates a new local branch.
        Example: git branch <branch_name>
        Fails if the branch already exists.
        """
        if not branch_name:
            raise ValueError("Branch name cannot be empty for create_branch.")

        # Check if branch already exists using show-ref
        try:
            await self._run_git_command(f"show-ref --verify --quiet refs/heads/{shlex.quote(branch_name)}")
            # If the above command succeeds, it means the branch exists.
            logger.warning(f"Attempted to create branch '{branch_name}', but it already exists.")
            raise GitServiceError(f"Branch '{branch_name}' already exists.")
        except GitServiceError:
            # We expect a GitServiceError if show-ref fails (branch does not exist)
            # The error from _run_git_command for "not found" is what we want to ignore here.
            # This happens if `show-ref` exits with a non-zero status because the ref doesn't exist.
            pass # Branch does not exist, proceed to create.

        # Try to create the branch
        try:
            await self._run_git_command(f"branch {shlex.quote(branch_name)}")
            logger.info(f"Successfully created local branch: {branch_name}")
            return True
        except GitServiceError as e:
            # This error is if `git branch <name>` command itself fails for other reasons
            logger.error(f"Error creating local branch '{branch_name}': {e}")
            raise # Re-raise the error from the branch creation attempt

    async def checkout_branch(self, branch_name: str, create_new: bool = False) -> bool:
        """
        Checks out a branch. If create_new is True, uses 'git checkout -b <branch_name>'.
        Otherwise, uses 'git checkout <branch_name>'.
        'git checkout -b <name>' will fail if branch <name> already exists.
        'git checkout <name>' will fail if branch <name> does not exist.
        """
        if not branch_name:
            raise ValueError("Branch name cannot be empty for checkout_branch.")

        command_parts = ["checkout"]
        if create_new:
            command_parts.append("-b")

        command_parts.append(shlex.quote(branch_name))
        command_str = " ".join(command_parts)

        try:
            await self._run_git_command(command_str)
            logger.info(f"Successfully checked out {'new ' if create_new else ''}branch: {branch_name} using command '{command_str}'")
            return True
        except GitServiceError as e:
            logger.error(f"Error during checkout operation for branch '{branch_name}' (create_new={create_new}): {e}")
            # The error 'e' already contains stderr and message from _run_git_command
            raise # Re-raise the original GitServiceError to be handled by the node

    async def get_last_commit_hash(self) -> str | None:
        try:
            stdout, _ = await self._run_git_command("rev-parse HEAD")
            return stdout
        except GitServiceError:
            return None

    async def get_last_commit_summary(self) -> str | None:
        try:
            stdout, _ = await self._run_git_command("log -n 1 --pretty=format:%s")
            return stdout
        except GitServiceError:
            return None

    async def commit_changes(self, commit_message: str) -> bool:
        try:
            # Check for changes
            stdout_status, _ = await self._run_git_command("status --porcelain")
            if not stdout_status:
                logger.info("No changes to commit.")
                return True # No changes, so "commit" is successful in a way

            await self._run_git_command("add .")
            await self._run_git_command(f"commit -m {shlex.quote(commit_message)}")
            logger.info(f"Successfully committed changes with message: {commit_message}")
            return True
        except GitServiceError as e:
            logger.error(f"Git commit failed: {e}")
            return False

    # Example of adapting another method, if needed
    async def get_last_commit_file_stats(self) -> str | None:
        try:
            num_commits_str, _ = await self._run_git_command("rev-list --count HEAD")
            if int(num_commits_str) > 1:
                stdout, _ = await self._run_git_command("diff --stat HEAD~1 HEAD")
            else:
                stdout, _ = await self._run_git_command("show --stat --pretty=format:\"\" HEAD")
            return stdout
        except (GitServiceError, ValueError):
            return None
