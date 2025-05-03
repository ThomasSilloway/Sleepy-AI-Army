"""Defines the ChangelogAgent."""

from google.cloud.aiplatform.agent_tooling.framework.agents import Agent
from google.cloud.aiplatform.agent_tooling.framework.tools import FunctionTool

# Import prompts and shared tools
from . import prompt
from sleepy_ai_army.shared_tools import file_system

# Define tools used by the ChangelogAgent
append_file_tool = FunctionTool(
    fn=file_system.append_file,
    description="Appends content to the specified file. Use this to add the formatted entry to the changelog.md file."
)

# Define the ChangelogAgent
# This agent is intended to be used as an AgentTool by other agents.
# It expects 'changelog_entry_text' to be passed in the input/arguments when called.
changelog_agent = Agent(
    model="gemini-2.0-flash", # Using Flash as specified in PRD FR-PoC3-004
    name="ChangelogAgent",
    description=(
        "Appends a timestamped entry to the task's changelog.md file. "
        "Expects 'changelog_entry_text' as input."
    ),
    instruction=prompt.CHANGELOG_AGENT_INSTRUCTIONS,
    tools=[append_file_tool],
    # Since this is used as a tool, disallow transfer to prevent unexpected delegation
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)
