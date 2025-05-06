# poc6_sequential_failure/sub_agents/agent_a/agent.py
from google.adk.agents import Agent # Using alias for LlmAgent
from . import prompt
from . import tools

agent_a = Agent(
    name="AgentA",
    model="gemini-2.0-flash", # As per TAD
    description="Executes the first step involving a tool call.",
    instruction=prompt.AGENT_A_INSTR,
    tools=[tools.failing_tool],
    output_key="agent_a_outcome" # Save output JSON string to state
)
