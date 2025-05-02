# Defines the TaskSetupAgent
import logging
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

# Import constants and tools using relative paths
from ...shared_libraries import constants
from . import prompt as tsa_prompt
# Import shared tool functions directly for wrapping
from ...shared_tools.file_system import create_directory, write_file
from ...shared_tools.task_helpers import get_next_task_number

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Tool Instantiation ---
# Wrap the shared functions as FunctionTool instances for the agent
# These tools will be called by the LLM based on the instructions in prompt.py
get_next_task_number_tool = FunctionTool(func=get_next_task_number)
create_directory_tool = FunctionTool(func=create_directory)
write_file_tool = FunctionTool(func=write_file)

# --- Agent Definition ---
# Define the agent as a standard LlmAgent.
# The orchestration logic is now driven by the prompt in prompt.py
task_setup_agent = LlmAgent(
    name=constants.TASK_SETUP_AGENT_NAME,
    model=constants.MODEL_NAME,
    instruction=tsa_prompt.TASK_SETUP_AGENT_PROMPT,
	disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    tools=[ # Tools the LLM can orchestrate
        get_next_task_number_tool,
        create_directory_tool,
        write_file_tool,
    ],
    description="Generates prefix/slug, gets next number, creates task folder/files by orchestrating tools based on instructions.",
)

logger.info(f"Initialized {constants.TASK_SETUP_AGENT_NAME} with model {constants.MODEL_NAME}")