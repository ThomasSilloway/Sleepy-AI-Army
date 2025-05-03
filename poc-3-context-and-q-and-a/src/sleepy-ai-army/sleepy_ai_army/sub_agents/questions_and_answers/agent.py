"""Defines the QnAAgent."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool

# Import prompts and shared tools
from . import prompt
from ...shared_tools import file_system

# Import the ChangelogAgent to use as a tool (placeholder for now)
from ..changelog import changelog_agent # Placeholder import

# Define tools used by the QnAAgent
read_file_tool = FunctionTool(
    func=file_system.read_file
)

write_file_tool = FunctionTool(
    func=file_system.write_file
)

# Wrap ChangelogAgent as a tool
changelog_agent_tool = AgentTool(
    agent=changelog_agent
)

# Define the QnAAgent
qna_agent = Agent(
    model="gemini-2.5-pro-exp-03-25", 
    name="QnAAgent",
    description=(
        "Generates assumptions and questions based on task context, processes user feedback "
        "from questions-and-answers.md, updates the Q&A and status files, determines task readiness, "
        "and logs actions to the changelog."
    ),
    instruction=prompt.QNA_AGENT_INSTRUCTIONS,
    tools=[
        read_file_tool,
        write_file_tool,
        changelog_agent_tool
    ]
)
