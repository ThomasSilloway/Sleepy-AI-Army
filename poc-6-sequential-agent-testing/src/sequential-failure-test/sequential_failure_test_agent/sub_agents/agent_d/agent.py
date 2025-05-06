# poc6_sequential_failure/sub_agents/agent_d/agent.py
from google.adk.agents import Agent
from . import prompt

agent_d = Agent(
    name="AgentD",
    model="gemini-2.0-flash",
    description="Summarizes the results of the sequence.",
    instruction=prompt.AGENT_D_INSTR
    # No output_key needed as per final TAD
)
