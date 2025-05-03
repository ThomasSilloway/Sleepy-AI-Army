"""Defines the ContextResearchAgent."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool

# Import prompts and shared tools
from . import prompt
from ...shared_tools import file_system

# Import the ChangelogAgent to use as a tool (placeholder for now)
from ..changelog import changelog_agent # Placeholder import

# Define tools used by the ContextResearchAgent
read_file_tool = FunctionTool(
    func=file_system.read_file
)

list_directory_tool = FunctionTool(
    func=file_system.list_directory
)

write_file_tool = FunctionTool(
    func=file_system.write_file
)

# Wrap ChangelogAgent as a tool
changelog_agent_tool = AgentTool(
    agent=changelog_agent
)

# Define the ContextResearchAgent
context_research_agent = Agent(
    model="gemini-2.0-flash", # Using Flash as specified in PRD FR-PoC3-002
    name="ContextResearchAgent",
    description=(
        "Generates the initial task_context.md by reading task_description.md, "
        "optionally tech_architecture.md, and listing the directory contents. "
        "Creates task_status.md and logs the action to the changelog."
    ),
    instruction=prompt.CONTEXT_RESEARCH_AGENT_INSTRUCTIONS,
    tools=[
        read_file_tool,
        list_directory_tool,
        write_file_tool,
        changelog_agent_tool
    ]
)
