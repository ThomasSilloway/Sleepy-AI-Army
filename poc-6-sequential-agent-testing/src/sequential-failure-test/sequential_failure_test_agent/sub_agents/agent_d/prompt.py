# poc6_sequential_failure/sub_agents/agent_d/prompt.py
AGENT_D_INSTR = """
Agent Outcome Info: Agent A -> {agent_a_outcome}, Agent B -> {agent_b_outcome}, Agent C -> {agent_c_outcome}.

Perform the following steps:
1. Review the outcomes of the previous steps provided here
  - These are JSON strings containing status information.
  - Parse them and generate a concise summary sentence describing the overall result of the sequence 
     - (e.g., 'Agent A failed, B and C were skipped, D completed.', or 'Agent A, B, C, D completed successfully.').
2. Output *only* the summary sentence you generated as plain text.
"""
