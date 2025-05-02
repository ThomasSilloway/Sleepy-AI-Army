from .shared_libraries import constants

STO_PROMPT = """
Analyze user input: Is it a new task description OR reference to existing task
(contains '/ai-tasks/' or 'Prefix_NNN_slug' format)?
Respond ONLY JSON: {"action": "exists", "detail": "Path/Name"} OR {"action": "new_task"}
Input: {{user_content}}
"""