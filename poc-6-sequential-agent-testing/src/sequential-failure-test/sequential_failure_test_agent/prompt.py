# Root-level prompts or shared constants
ROOT_AGENT_INSTR = """
Execute the {error_test_sequence.name} tool. 
Wait for it to return a result. 
Then, format your final response exactly like this: 'Root Agent reporting: The sequence finished with result: [Insert the result from the tool here]'
"""