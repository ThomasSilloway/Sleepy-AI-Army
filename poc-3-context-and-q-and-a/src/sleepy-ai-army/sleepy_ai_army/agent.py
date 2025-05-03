"""Defines the root agent (TaskPlannerAgent) for the Sleepy AI Army."""

from google.cloud.aiplatform.agent_tooling.framework.agents import Agent
from google.cloud.aiplatform.agent_tooling.framework.tools import FunctionTool

# Import prompts and tools
from . import prompt
from .shared_tools import file_system

# Import sub-agents (placeholders for now, will be defined later)
# Assuming they will be defined in their respective agent.py files and exported via __init__.py
from .sub_agents.context_research import context_research_agent # Placeholder import
from .sub_agents.questions_and_answers import qna_agent # Placeholder import

# Define tools used by the TaskPlannerAgent
read_file_tool = FunctionTool(
    fn=file_system.read_file,
    description="Reads the entire content of a specified file. Use this to read the task status file."
)

# Define the root agent (TaskPlannerAgent)
root_agent = Agent(
    model="gemini-1.0-pro", # Using Gemini Pro as it needs to follow routing logic precisely
    name="TaskPlannerAgent",
    description=(
        "Acts as the entry point for processing a task. Reads the task status file "
        "and delegates control to the appropriate sub-agent (ContextResearchAgent or QnAAgent) "
        "or reports status to the user based on the content."
    ),
    instruction=prompt.TASK_PLANNER_AGENT_INSTRUCTIONS,
    tools=[read_file_tool],
    sub_agents=[
        context_research_agent, # Will handle initial context generation
        qna_agent               # Will handle Q&A iterations
    ],
    enable_logging=True # Enable logging for better debugging
)