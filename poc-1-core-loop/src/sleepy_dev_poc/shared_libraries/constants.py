# Constants for the Sleepy Dev Team PoC
import os

# --- Core Configuration ---
ROOT_AGENT_NAME = "SleepyDev_RootAgent_PoC"
BACKLOG_READER_AGENT_NAME = "BacklogReaderAgent_PoC"

# Path to the backlog file (as specified in PRD).
# Using an absolute path starting from root. Adjust if needed.
# Ensure this path is accessible from where the agent runs.
# NOTE: The tech spec uses an absolute path "/ai-tasks/backlog.md".
# This might cause issues on Windows or if the execution context isn't the project root.
# Using a relative path from the project root is generally safer.
# Assuming the agent runs from the project root (where ai-tasks/ exists).
BACKLOG_FILE_PATH = "ai-tasks/backlog.md" # Adjusted to relative path

# --- Optional Configuration ---
# Specify a model if LlmAgent is used and needs specific reasoning capabilities.
# For this PoC, a basic/free model might suffice, or even no model if using BaseAgent.
# Using gemini-2.0-flash as per best practices.
MODEL_NAME = "gemini-2.0-flash"