import logging
from google.adk.agents import LlmAgent

# Import constants and sub-agent instance
from .shared_libraries import constants
from . import prompt as sto_prompt
from .sub_agents.task_setup_agent.agent import task_setup_agent # Import the instance

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Agent Definition ---
# Define the root agent as a standard LlmAgent.
# The routing logic (analyzing input and deciding whether to delegate or respond directly)
# is now driven by the prompt in prompt.py.
root_agent = LlmAgent(
    name=constants.ROOT_AGENT_NAME,
    model=constants.MODEL_NAME,
    instruction=sto_prompt.STO_PROMPT,
    sub_agents=[task_setup_agent], # Make the sub-agent available for delegation
    description="Analyzes user input via LLM. Routes new tasks to TaskSetupAgent or responds directly if task exists.",
    # No tools needed directly by this agent; LLM uses prompt to decide flow.
)

logger.info(f"Initialized {constants.ROOT_AGENT_NAME} with model {constants.MODEL_NAME}")