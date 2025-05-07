
import os
from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool

from ... import constants
from . import prompt as task_parsing_prompt
from ...shared_tools.file_system import read_file # Import the specific function

# Create a FunctionTool from the read_file function
# This tool will be used by the TaskParsingAgent to read the task_description.md file.
read_file_tool = FunctionTool(
    func=read_file
)

task_parsing_agent = Agent(
    name=constants.TASK_PARSING_AGENT_NAME,
    model=constants.DEFAULT_LLM_MODEL,
    description=(
        "Parses a task description file to extract the target file name, "
        "a description of the change, and a slug for a Git branch."
    ),
    instruction=task_parsing_prompt.TASK_PARSING_AGENT_PROMPT_TEMPLATE, 
    tools=[
        read_file_tool,
		# ChangelogAgent tool will be added here in a later step
    ],
    output_key=constants.TASK_PARSING_OUTCOME_KEY,
)
