# sequential_failure_test_agent/__init__.py

# Note: Defining root agent and sequence here based on observed structure.
# Consider moving to a dedicated agent.py if preferred later.

from google.adk.agents import Agent, SequentialAgent

# Import sub-agents relatively
from .sub_agents.agent_a.agent import agent_a
from .sub_agents.agent_b.agent import agent_b
from .sub_agents.agent_c.agent import agent_c
from .sub_agents.agent_d.agent import agent_d

# Define the sequence
error_test_sequence = SequentialAgent(
    name="ErrorTestSequence",
    sub_agents=[
        agent_a,
        agent_b,
        agent_c,
        agent_d,
    ]
)

# Define the root agent to run the sequence
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="The root agent that initiates and oversees the PoC 6 sequence.",
    instruction=f"Run the {error_test_sequence.name} subagent. Report completion when it's done.",
    sub_agents=[error_test_sequence] # Make sequence accessible
)
