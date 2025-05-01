Report for AI Coding Agent: Sleepy Dev Team PoC Implementation

Objective:

Implement the Proof-of-Concept (PoC) for the Sleepy Dev Team project using the Google Agent Development Kit (ADK). This PoC focuses on demonstrating a core agent loop that reads tasks from a backlog file until it's empty.

Core Requirements (Based on PRD PoC-1.0):

    Root Agent (LoopAgent - PRD-FR-001): A top-level LoopAgent that orchestrates the process.
    Sub-Agent (BacklogReaderAgent - PRD-FR-002): An agent responsible for interacting with the backlog file.
    Backlog Interaction: The BacklogReaderAgent must use an ADK FunctionTool to:
        Target the file at /ai-tasks/backlog.md.
        Read the first line of the file.
        Rewrite the file without the first line.
        Return the content of the removed line to the agent.
    Termination:
        If the backlog file is empty or doesn't exist, the tool must inform the BacklogReaderAgent.
        The BacklogReaderAgent (via the tool's ToolContext) must set actions.escalate = True when the backlog is empty.
        The root LoopAgent must terminate when actions.escalate is set to True.
    Output:
        If a task is read, the BacklogReaderAgent should output: Next backlog item: [Task Description].
        If the backlog is empty, it should output: Backlog is empty. Signaling termination.
    Environment: Run locally in a Python venv using adk web or a custom runner script. Docker is excluded for the PoC.

Target Project Structure (Mimicking sellers_motivation):

sleepy_dev_poc_project/  # Root folder for the entire PoC
├── .env                   # Store API Keys, etc. (Not strictly needed for PoC unless using paid models)
├── .example.env           # Example environment variables
├── README.md              # Project setup and execution instructions
├── requirements.txt       # Python dependencies (google-adk)
├── ai-tasks/              # Directory for backlog file (as per PRD)
│   └── backlog.md         # The input backlog file (must be created manually)
└── sleepy_dev_poc/        # Main Python package
    ├── __init__.py        # Makes 'sleepy_dev_poc' a package, imports root_agent
    ├── agent.py           # Defines the root LoopAgent ('SleepyDev_RootAgent_PoC')
    ├── main.py            # Optional but recommended: Script to configure/run ADK Runner
    ├── shared_libraries/  # Shared utilities/constants (like in sellers_motivation)
    │   ├── __init__.py    # Package init
    │   └── constants.py   # Defines paths, agent names, etc.
    ├── sub_agents/        # Directory for sub-agents
    │   ├── __init__.py    # Package init
    │   └── backlog_reader/ # Sub-agent specific files
    │       ├── __init__.py    # Package init
    │       ├── agent.py     # Defines BacklogReaderAgent (LlmAgent)
    │       ├── prompt.py    # Defines the instruction prompt for BacklogReaderAgent
    │       └── tools.py     # Defines the 'process_backlog_file' FunctionTool logic
    └── tools/             # Optional: General reusable tools (like sellers_motivation/tools)
        ├── __init__.py    # Package init
        └── file_io_tools.py # Example for general file helpers (not strictly needed for PoC)

File Implementation Details:

1. Root Directory Files:

    .env: (Create if using API keys)
    Code snippet

# Example: If using a model that requires an API key
# GEMINI_API_KEY=YOUR_API_KEY_HERE

.example.env:
Code snippet

# GEMINI_API_KEY=

README.md:
Markdown

# Sleepy Dev Team - Core Loop PoC

Proof-of-Concept demonstrating a basic ADK agent loop reading tasks from a backlog file.

## Setup

1.  Create a Python virtual environment: `python -m venv venv`
2.  Activate the environment: `source venv/bin/activate` (Linux/macOS) or `.\venv\Scripts\activate` (Windows)
3.  Install requirements: `pip install -r requirements.txt`
4.  Create the backlog directory and file:
    * `mkdir ai-tasks`
    * Create `ai-tasks/backlog.md` with tasks (one per line, starting with `* `):
        ```markdown
        * Task 1: First item.
        * Task 2: Second item.
        ```
5.  (Optional) Create a `.env` file based on `.example.env` if needed.

## Execution

You can run the PoC using the ADK web interface or the provided main script:

* **Using ADK Web:** `adk web` (Navigate to the web UI and start a new session)
* **Using Main Script:** `python -m sleepy_dev_poc.main`

requirements.txt:
Plaintext

    google-adk
    python-dotenv # If using main.py with .env loading

2. ai-tasks/backlog.md:

    Create this file manually inside the ai-tasks directory.
    Example Content:
    Markdown

    * Task 1: Implement the core loop.
    * Task 2: Define the backlog reader agent.
    * Task 3: Create the file processing tool.
    * Task 4: Test the termination logic.

3. sleepy_dev_poc/ Package Files:

    sleepy_dev_poc/__init__.py:
    Python

# Expose the root agent for easy import
from .agent import root_agent

print("Initializing sleepy_dev_poc package...") # Optional: confirm import

sleepy_dev_poc/shared_libraries/__init__.py:
Python

# Package initialization for shared_libraries

sleepy_dev_poc/shared_libraries/constants.py: (Defines key configuration)
Python

# Constants for the Sleepy Dev Team PoC
import os

# --- Core Configuration ---
ROOT_AGENT_NAME = "SleepyDev_RootAgent_PoC"
BACKLOG_READER_AGENT_NAME = "BacklogReaderAgent_PoC"

# Path to the backlog file (as specified in PRD).
# Using an absolute path starting from root. Adjust if needed.
# Ensure this path is accessible from where the agent runs.
BACKLOG_FILE_PATH = "/ai-tasks/backlog.md" # PRD Requirement

# --- Optional Configuration ---
# Specify a model if LlmAgent is used and needs specific reasoning capabilities.
# For this PoC, a basic/free model might suffice, or even no model if using BaseAgent.
# MODEL_NAME = "gemini-1.5-flash"

sleepy_dev_poc/sub_agents/__init__.py:
Python

# Package initialization for sub_agents

sleepy_dev_poc/sub_agents/backlog_reader/__init__.py:
Python

# Package initialization for backlog_reader sub-agent

sleepy_dev_poc/sub_agents/backlog_reader/tools.py: (The core file interaction logic)
Python

# Tool for processing the backlog file
import logging
import os
from typing import Dict, Any, Optional

# Critical import for accessing actions like escalate
from google.adk.tools import ToolContext

# Import constants from the shared library using relative path
from ...shared_libraries import constants

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# This function MUST accept tool_context to signal escalation
def process_backlog_file(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Reads the first line from the backlog file, removes it, and returns it.

    If the file is empty or doesn't exist, it signals for escalation via the
    tool_context to terminate the parent LoopAgent. It requires ToolContext.

    Args:
        tool_context: The ADK ToolContext, automatically injected by the framework.
                      Crucial for setting actions.escalate.

    Returns:
        A dictionary containing:
        - 'status': 'ok', 'empty', or 'error'
        - 'task_description': The content of the first line (if status is 'ok')
        - 'message': A descriptive message about the outcome or error.
    """
    file_path = constants.BACKLOG_FILE_PATH
    logger.info(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Processing backlog file: {file_path}")

    # --- Context Check ---
    if tool_context is None:
         logger.error(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: ToolContext was not provided. Cannot escalate.")
         # Cannot escalate without context, return error status but loop might continue incorrectly.
         return {"status": "error", "message": "Critical Error: ToolContext is missing."}

    try:
        # --- File Check ---
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            logger.info(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Backlog file is empty or does not exist. Signaling escalation.")
            # Signal to the LoopAgent to stop
            tool_context.actions.escalate = True
            return {"status": "empty", "message": "Backlog is empty or not found."}

        # --- Read and Modify File ---
        lines = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            logger.info(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Backlog file not found during read. Signaling escalation.")
            tool_context.actions.escalate = True
            return {"status": "empty", "message": "Backlog file not found."}


        if not lines: # Double-check if file was empty after opening
             logger.info(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Backlog file contained no lines. Signaling escalation.")
             tool_context.actions.escalate = True
             return {"status": "empty", "message": "Backlog file is empty."}

        # Get the first line and remove leading/trailing whitespace (incl. newline)
        first_line = lines[0].strip()
        remaining_lines = lines[1:] # Get all lines except the first

        # Rewrite the file with the remaining lines
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(remaining_lines)

        logger.info(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Successfully processed task: '{first_line}'")
        # IMPORTANT: Ensure escalation is FALSE if a task was processed
        tool_context.actions.escalate = False
        return {"status": "ok", "task_description": first_line, "message": "Task processed successfully."}

    except Exception as e:
        logger.error(f"{constants.BACKLOG_READER_AGENT_NAME} - Tool: Error processing backlog file {file_path}: {e}", exc_info=True)
        # Signal escalation on error to prevent potential infinite loops
        tool_context.actions.escalate = True
        return {"status": "error", "message": f"An error occurred: {str(e)}"}

sleepy_dev_poc/sub_agents/backlog_reader/prompt.py: (Instructions for the LLM Agent)
Python

# Prompt for the BacklogReaderAgent
from ...shared_libraries import constants

BACKLOG_READER_AGENT_PROMPT = f"""
You are the {constants.BACKLOG_READER_AGENT_NAME}. Your ONLY job is to manage the task backlog file located at '{constants.BACKLOG_FILE_PATH}'.

Follow these steps precisely:
1. Call the `process_backlog_file` tool. This tool handles reading the first task, removing it from the file, and indicating if the backlog is empty.
2. Analyze the 'status' field returned by the tool:
   - If 'status' is 'ok': Respond ONLY with: `Next backlog item: [Task Description]` (replace [Task Description] with the value from the tool's 'task_description' field).
   - If 'status' is 'empty': Respond ONLY with: `Backlog is empty. Signaling termination.` (The tool has already signaled termination via escalate=True).
   - If 'status' is 'error': Respond ONLY with the error message from the tool's 'message' field.

Do NOT add any conversational text, greetings, or explanations. Your output must strictly follow the formats described above based on the tool's result.
"""

sleepy_dev_poc/sub_agents/backlog_reader/agent.py: (Defines the sub-agent)
Python

# Defines the BacklogReaderAgent
import logging
from google.adk.agents import LlmAgent # Using LlmAgent as it simplifies tool calling
from google.adk.tools import FunctionTool

# Import constants and tools using relative paths
from ...shared_libraries import constants
from . import tools
from .prompt import BACKLOG_READER_AGENT_PROMPT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an instance of the FunctionTool
process_backlog_tool = FunctionTool(func=tools.process_backlog_file)

# Define the agent using LlmAgent
# LlmAgent handles invoking the tool based on the prompt and tool definition.
backlog_reader_agent = LlmAgent(
    name=constants.BACKLOG_READER_AGENT_NAME,
    # model=constants.MODEL_NAME, # Specify model if needed for more complex prompts or decisions
    instruction=BACKLOG_READER_AGENT_PROMPT,
    tools=[process_backlog_tool],
    description="Reads tasks one by one from the backlog file using a tool and signals when empty.",
    # No output_key needed; the agent's response is based on the tool output / prompt
)

logger.info(f"Initialized {constants.BACKLOG_READER_AGENT_NAME}")

sleepy_dev_poc/agent.py: (Defines the root agent)
Python

# Defines the root LoopAgent for the PoC
import logging
from google.adk.agents import LoopAgent

# Import the sub-agent and constants using relative paths
from .sub_agents.backlog_reader.agent import backlog_reader_agent
from .shared_libraries import constants

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the root agent as a LoopAgent
root_agent = LoopAgent(
    name=constants.ROOT_AGENT_NAME,
    description="Root agent that loops through sub-agents until backlog is empty (escalation).",
    # max_iterations=10, # Optional: uncomment to add a safety limit
    sub_agents=[
        backlog_reader_agent,
        # In the full Sleepy Dev Team project, other agents like
        # SingleTaskOrchestrator would be added here.
    ]
    # Termination is primarily handled by backlog_reader_agent setting
    # tool_context.actions.escalate = True, which LoopAgent listens for.
)

logger.info(f"Initialized {constants.ROOT_AGENT_NAME} with sub-agent: {backlog_reader_agent.name}")

sleepy_dev_poc/main.py: (Optional but helpful runner script)
Python

# Script to configure and run the ADK Runner for the PoC
import asyncio
import logging
import os
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Import the root agent and constants using relative paths
from .agent import root_agent
from .shared_libraries import constants

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_agent():
    """Configures and runs the ADK agent PoC."""
    load_dotenv() # Load .env file if it exists

    # --- Pre-run Checks & Setup ---
    # Ensure the backlog directory and a sample file exist for the PoC run
    backlog_dir = os.path.dirname(constants.BACKLOG_FILE_PATH)
    try:
        if not os.path.exists(backlog_dir):
            os.makedirs(backlog_dir)
            logger.info(f"Created backlog directory: {backlog_dir}")
        if not os.path.exists(constants.BACKLOG_FILE_PATH):
             with open(constants.BACKLOG_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write("* Sample Task 1: Run the PoC application.\n")
                f.write("* Sample Task 2: Verify file modification.\n")
             logger.info(f"Created sample backlog file: {constants.BACKLOG_FILE_PATH}")
        else:
             logger.info(f"Using existing backlog file: {constants.BACKLOG_FILE_PATH}")
    except OSError as e:
        logger.error(f"Error setting up backlog directory/file at {constants.BACKLOG_FILE_PATH}: {e}. Check permissions.")
        return # Cannot proceed without backlog setup


    # --- ADK Runner Setup ---
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="SleepyDevTeam_PoC",
        agent=root_agent,
        session_service=session_service,
        # Provide API key if required by the model/ADK version
        # api_key=os.getenv("GEMINI_API_KEY") # Example
    )

    logger.info(f"Starting run for agent: {runner.agent.name}...")
    session = session_service.create_session(app_name=runner.app_name)
    logger.info(f"Created session ID: {session.id}")

    # --- Agent Execution Loop ---
    try:
        # Start the agent run with an initial message or empty content
        async for event in runner.run_async(session_id=session.id, user_content="Start processing backlog."):
            if event.content:
                 # Log agent's textual response
                 if event.content.parts and event.content.parts[0].text:
                     logger.info(f"Agent ({event.author}): {event.content.parts[0].text}")
                 # Log tool calls/responses for debugging
                 if event.content.parts and event.content.parts[0].function_call:
                     logger.debug(f"Agent ({event.author}) calling tool: {event.content.parts[0].function_call.name}")
                 if event.content.parts and event.content.parts[0].function_response:
                      # Log the response dict from the tool
                      tool_resp = event.content.parts[0].function_response.response
                      logger.debug(f"Agent ({event.author}) received tool response: {tool_resp}")


            # Check for escalation signal (primary loop termination condition)
            if event.actions and event.actions.escalate:
                 logger.info(f"Agent ({event.author}) signaled escalate=True. Loop terminating.")
                 # LoopAgent should handle this, but we log it here too.
                 break # Explicitly break if needed, though LoopAgent should stop yielding


        logger.info(f"Agent run finished for session {session.id}.")

    except Exception as e:
        logger.error(f"An error occurred during the agent run: {e}", exc_info=True)
    finally:
        # Optional: Clean up session if needed, though InMemorySessionService is ephemeral
        logger.info("Cleanup complete.")

if __name__ == "__main__":
    logger.info("Executing PoC main script...")
    asyncio.run(run_agent())
    logger.info("PoC main script finished.")

sleepy_dev_poc/tools/__init__.py:
Python

# Package initialization for general tools

sleepy_dev_poc/tools/file_io_tools.py: (Empty or add general file functions if needed later)
Python

    # Optional: General file I/O utility functions
    # Not strictly required for this PoC as the logic is specific
    # and contained within the backlog_reader tool.
    import logging

    logger = logging.getLogger(__name__)

    # Example:
    # def read_text_file(file_path: str) -> str | None:
    #     """Reads entire content of a text file."""
    #     try:
    #         with open(file_path, 'r', encoding='utf-8') as f:
    #             return f.read()
    #     except Exception as e:
    #         logger.error(f"Error reading file {file_path}: {e}")
    #         return None

Setup and Execution:

    Ensure Python 3.9+ and pip are installed.
    Create the project directory sleepy_dev_poc_project.
    Place the files as outlined in the structure above.
    Follow the Setup steps in the generated README.md (create venv, install requirements, create ai-tasks/backlog.md).
    Run using python -m sleepy_dev_poc.main or adk web. Observe the console logs for agent messages and file processing confirmation. Verify that ai-tasks/backlog.md is modified correctly after each run.

Key ADK Concepts Used:

    LoopAgent: Manages the iteration over sub-agents. Automatically terminates when a sub-agent sets actions.escalate = True.
    LlmAgent: Used for the BacklogReaderAgent to interpret instructions and call the appropriate tool.
    FunctionTool: Wraps the Python function process_backlog_file so the ADK agent can invoke it.
    ToolContext: Passed to the process_backlog_file function, providing access to actions.escalate which is essential for controlling the LoopAgent.
    Relative Imports: Used within the sleepy_dev_poc package (e.g., from ...shared_libraries import constants).
    Constants: Centralized configuration (shared_libraries/constants.py) following the pattern in sellers_motivation.

This report provides the necessary structure and code snippets to guide the AI coding agent in implementing the Sleepy Dev Team PoC according to the specified requirements and desired format.