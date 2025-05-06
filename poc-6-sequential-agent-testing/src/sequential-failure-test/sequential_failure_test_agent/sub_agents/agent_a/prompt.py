# poc6_sequential_failure/sub_agents/agent_a/prompt.py
AGENT_A_INSTR = """
Perform the following steps every time:
1. Call the FailingTool. 
2. Analyze the tool response
3. If the tool indicates an error, output a JSON string like `{"status": "failure", "message": "Tool failed: [reason from tool response]"}`. Otherwise, output a JSON string like `{"status": "success", "result": "Tool call completed successfully."}` 
IMPORANT: Ensure your final output is *only* the valid JSON string.
"""
