# poc6_sequential_failure/sub_agents/agent_a/prompt.py
AGENT_A_INSTR = """
1. Call the FailingTool tool.
2. Analyze the dictionary returned by the tool.
3. Take note of this important note: **IMPORTANT** Do NOT wrap the JSON string in markdown code fences (like ```json ... ``` or ``` ... ```). Your entire output must be the JSON string itself and nothing else. Do not add any explanatory text before or after the JSON string.
4. Based *only* on the tool's response:
    - If the tool indicated failure (e.g., status key is "error"), your final output must be *only* a valid JSON string like: {"status": "failure", "message": "Tool failed: [reason from tool response]"}
    - Otherwise (if the tool indicated success), your final output must be *only* a valid JSON string like: {"status": "success", "result": "Tool call completed successfully."}
"""