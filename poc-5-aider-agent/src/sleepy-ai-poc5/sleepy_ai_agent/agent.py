
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool

from . import constants
from . import prompt as root_agent_prompt

# Import sub-agents
from .sub_agents.task_parsing.agent import task_parsing_agent
# Other sub-agents (FileLocator, GitSetup, AiderExecution, Reporting, Changelog) will be imported here later.

# Define the sequence of agents for the "Small Tweak" process.
# Initially, it only contains the TaskParsingAgent.
small_tweak_sequence = SequentialAgent(
    name=constants.SMALL_TWEAK_SEQUENCE_NAME,
    description="Perform a small code tweak: parse task, locate file, setup git, execute aider, and report.",
    sub_agents=[
        task_parsing_agent,
        # file_locator_agent, (to be added)
        # git_setup_agent, (to be added)
        # aider_execution_agent, (to be added)
        # reporting_agent, (to be added)
    ],
)

# Wrap the sequence in an AgentTool so the RootAgent can call it.
small_tweak_sequence_tool = AgentTool(
    agent=small_tweak_sequence
)

# Uncomment for final version that uses the sequence as an agent tool
# Define the RootAgent that initiates and oversees the sequence. 
# root_agent = Agent(
#     name=constants.ROOT_AGENT_NAME,
#     model=constants.DEFAULT_LLM_MODEL,
#     description="The root agent that initiates and oversees the Small Tweak PoC 5 sequence.",
#     instruction=root_agent_prompt.ROOT_AGENT_INSTRUCTION_TOOL,
#     tools=[
#         small_tweak_sequence_tool,
#     ],
# )

root_agent = Agent(
    name=constants.ROOT_AGENT_NAME,
    model=constants.DEFAULT_LLM_MODEL,
    description="The root agent that initiates and oversees the Small Tweak PoC 5 sequence.",
    instruction=root_agent_prompt.ROOT_AGENT_INSTRUCTION,
    sub_agents=[small_tweak_sequence],
)
