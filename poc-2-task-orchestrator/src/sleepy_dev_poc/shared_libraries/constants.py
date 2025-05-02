import os

ROOT_AGENT_NAME = "SingleTaskOrchestrator"
TASK_SETUP_AGENT_NAME = "TaskSetupAgent"
# Construct the absolute path relative to this file's location
# Assuming this file is in src/sleepy_dev_poc/shared_libraries/
# Go up two levels to src/sleepy_dev_poc/, then up one more to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BASE_TASK_PATH = os.path.join(project_root, "ai-tasks")
ALLOWED_PREFIXES = ["Bug_", "Polish_", "Feature_", "Refactor_"]
DEFAULT_PREFIX = "Task_"
MODEL_NAME = "gemini-1.5-flash" # Using flash as per tech arch, not 2.5 as per tech details
NNN_PADDING = 3