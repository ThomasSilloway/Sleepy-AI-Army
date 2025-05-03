"""Defines the ContextResearchAgent."""

from google.cloud.aiplatform.agent_tooling.framework.agents import Agent
from google.cloud.aiplatform.agent_tooling.framework.tools import FunctionTool, AgentTool

# Import prompts and shared tools
from . import prompt
from sleepy_ai_army.shared_tools import file_system

# Import the ChangelogAgent to use as a tool (placeholder for now)
from sleepy_ai_army.sub_agents.changelog import changelog_agent # Placeholder import

# Define tools used by the ContextResearchAgent
read_file_tool = FunctionTool(
    fn=file_system.read_file,
    description="Reads the entire content of a specified file. Use this for task_description.md and tech_architecture.md."
)

list_directory_tool = FunctionTool(
    fn=file_system.list_directory,
    description="Lists files and directories within a specified path. Use this to list the task folder contents."
)

write_file_tool = FunctionTool(
    fn=file_system.write_file,
    description="Writes content to a file, overwriting if it exists. Use this to create task_context.md and task_status.md."
)

# Wrap ChangelogAgent as a tool
changelog_agent_tool = AgentTool(
    agent=changelog_agent, # The actual agent instance
    description=(
        "Appends a provided text entry to the task's changelog.md file. "
        "Use this tool *after* successfully creating the context and status files. "
        "Pass the changelog message as the 'changelog_entry_text' argument."
    )
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
