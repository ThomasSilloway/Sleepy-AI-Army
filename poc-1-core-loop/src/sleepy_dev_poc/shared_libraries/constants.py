# Constants for the Sleepy Dev Team PoC
import os

# --- Core Configuration ---
ROOT_AGENT_NAME = "SleepyDev_RootAgent_PoC"
BACKLOG_READER_AGENT_NAME = "BacklogReaderAgent_PoC"

# Path to the backlog file (as specified in PRD).
# Using an absolute path starting from root. Adjust if needed.
# Ensure this path is accessible from where the agent runs.
# TODO: Update this to be gathered when we specify which project we want it to work on
BACKLOG_FILE_PATH = "C:\\GithubRepos\\Sleepy-Dev-Team\\poc-1-core-loop\\ai-tasks\\backlog.md"

# --- Optional Configuration ---
# Specify a model if LlmAgent is used and needs specific reasoning capabilities.
# For this PoC, a basic/free model might suffice, or even no model if using BaseAgent.
# Using gemini-2.0-flash as per best practices.
MODEL_NAME = "gemini-2.0-flash"