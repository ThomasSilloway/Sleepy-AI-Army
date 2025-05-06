# Root-level prompts or shared constants
ROOT_AGENT_INSTR = """
Whenever the user says anything, execute the tool called `error_test_tool`. 
Wait for it to return a result. 
Then, format your final response exactly like this: 'Root Agent reporting: The sequence finished with result: [Insert the result from the tool here]'
"""

ROOT_AGENT_INSTR_SUBAGENT = """
Transfer to the error_test_sequence subagent. 
Wait for it to return a result. 
Then, format your final response exactly like this: 'Root Agent reporting: The sequence finished with result: [Insert the result from the tool here]'
"""