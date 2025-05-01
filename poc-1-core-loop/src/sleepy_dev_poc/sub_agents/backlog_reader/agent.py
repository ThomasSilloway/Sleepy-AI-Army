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
# The ADK framework will automatically inject ToolContext if the function signature includes it
process_backlog_tool = FunctionTool(func=tools.process_backlog_file)

# Define the agent using LlmAgent
# LlmAgent handles invoking the tool based on the prompt and tool definition.
backlog_reader_agent = LlmAgent(
    name=constants.BACKLOG_READER_AGENT_NAME,
    model=constants.MODEL_NAME, # Use the model defined in constants
    instruction=BACKLOG_READER_AGENT_PROMPT,
    tools=[process_backlog_tool],
    description="Reads tasks one by one from the backlog file using a tool and signals when empty.",
    # No output_key needed; the agent's response is based on the tool output / prompt
)

logger.info(f"Initialized {constants.BACKLOG_READER_AGENT_NAME} with model {constants.MODEL_NAME}")