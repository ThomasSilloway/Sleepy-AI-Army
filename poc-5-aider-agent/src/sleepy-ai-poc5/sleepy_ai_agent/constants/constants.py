# Default LLM Models
DEFAULT_LLM_MODEL = "gemini-2.0-flash-lite" # Example, adjust as needed
CHANGELOG_LLM_MODEL = "gemini-2.0-flash-lite" # Example, adjust as needed

# File Names
TASK_DESCRIPTION_FILE = "task_description.md"
CHANGELOG_FILE = "changelog.md"

# Pre-configured Paths

# For local testing, ensure these paths correctly point to your test project and goal folder.
DEFAULT_WORKSPACE_PATH = "workspace" # Example: "C:/Users/user/projects/target_project"
# IMPORTANT: This path is relative DEFAULT_WORKSPACE_PATH
DEFAULT_GOAL_FOLDER_NAME = "SmallTweak_001_ExampleGoal" # Example: "ai-goals/SmallTweak_001_FixTypo"

# Agent Friendly Names
ROOT_AGENT_NAME = "RootAgent"
SMALL_TWEAK_SEQUENCE_NAME = "SmallTweakSequence"
TASK_PARSING_AGENT_NAME = "TaskParsingAgent"
FILE_LOCATOR_AGENT_NAME = "FileLocatorAgent"
GIT_SETUP_AGENT_NAME = "GitSetupAgent"
AIDER_EXECUTION_AGENT_NAME = "AiderExecutionAgent"
REPORTING_AGENT_NAME = "ReportingAgent"
CHANGELOG_AGENT_NAME = "ChangelogAgent"

# State Output Keys
# These keys are used to store and retrieve agent outcomes in the session state.
TASK_PARSING_OUTCOME_KEY = "task_parsing_outcome"
FILE_LOCATOR_OUTCOME_KEY = "file_locator_outcome"
GIT_SETUP_OUTCOME_KEY = "git_setup_outcome"
AIDER_EXECUTION_OUTCOME_KEY = "aider_execution_outcome"
REPORTING_OUTCOME_KEY = "reporting_outcome" # Added for completeness, though ReportingAgent might not set a typical outcome key

# Standard Outcome Status Values
STATUS_SUCCESS = "success"
STATUS_FAILURE = "failure"
STATUS_SKIPPED = "skipped"
