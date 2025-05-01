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
    description="Root agent that loops through the BacklogReaderAgent until the backlog is empty (escalation).",
    # max_iterations=10, # Optional: uncomment to add a safety limit
    sub_agents=[
        backlog_reader_agent,
        # In the full Sleepy Dev Team project, other agents like
        # SingleTaskOrchestrator would be added here.
    ]
    # Termination is primarily handled by backlog_reader_agent setting
    # tool_context.actions.escalate = True via its tool, which LoopAgent listens for.
)

logger.info(f"Initialized {constants.ROOT_AGENT_NAME} with sub-agent: {backlog_reader_agent.name}")