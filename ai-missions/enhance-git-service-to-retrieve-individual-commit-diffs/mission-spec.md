**Project:** army-infantry
**Title:** Enhance GitService to Retrieve Individual Commit Diffs

**Description:**
To build an accurate execution summary, we first need the ability to get the specific changes from each commit `aider` makes. This mission is to add a new method to the `GitService` that can retrieve the full diff for a single commit hash.

**Files to Modify:**
- `army-infantry/src/services/git_service.py`

**Implementation Details:**
1.  In `army-infantry/src/services/git_service.py`, add a new `async` method: `get_diff_for_commit(self, commit_hash: str) -> str`.
2.  This method should execute the git command `git show --pretty=format:"%h - %s" --stat <commit_hash>` to get the diff and summary information for the specified commit hash.
3.  The method should return the `stdout` of the command as a string.
4.  Include robust error handling in case the commit hash is not found or the command fails.
