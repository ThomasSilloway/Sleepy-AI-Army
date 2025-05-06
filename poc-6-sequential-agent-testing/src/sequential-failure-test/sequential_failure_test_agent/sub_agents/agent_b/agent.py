# poc6_sequential_failure/sub_agents/agent_b/agent.py
from google.adk.agents import Agent
from . import prompt
# Note: Callback import and usage deferred to later step
# from sequential_failure_test_agent.callbacks import callbacks # Adjusted path

agent_b = Agent(
    name="AgentB",
    model="gemini-2.0-flash",
    description="Executes the second step in the sequence.",
    instruction=prompt.AGENT_B_INSTR,
    # before_agent_callback=callbacks.check_outcome_and_skip_callback, # Deferred
    output_key="agent_b_outcome"
)
