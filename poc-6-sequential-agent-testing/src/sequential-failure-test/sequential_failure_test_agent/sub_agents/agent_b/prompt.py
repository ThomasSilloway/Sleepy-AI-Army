# poc6_sequential_failure/sub_agents/agent_b/prompt.py
AGENT_B_INSTR = """
Perform the following steps every time:
1. Output a final JSON string like `{"status": "success", "result": "Agent B finished its task."}` 
IMPORANT: Ensure your final output is *only* the valid JSON string.
"""
