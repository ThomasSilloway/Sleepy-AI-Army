# poc6_sequential_failure/sub_agents/agent_c/prompt.py
AGENT_C_INSTR = """
Perform the following steps every time:
1. Output a final JSON string like `{"status": "success", "result": "Agent B finished its task."}`
IMPORTANT: Do NOT wrap the JSON string in markdown code fences (like ```json ... ``` or ``` ... ```).
 - Your entire output must be the JSON string itself and nothing else.
 - Do not add any explanatory text before or after the JSON string.
"""
