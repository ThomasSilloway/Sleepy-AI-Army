# poc6_sequential_failure/sub_agents/agent_a/tools.py
from google.adk.tools import FunctionTool
import json # Using json import for potential future use, though not strictly needed for dict

def _failing_tool_impl() -> dict:
    """
    Simulates a tool execution.
    *** MVP Step 1: For initial setup, this simulates SUCCESS. ***
    """
    print("Tool: _failing_tool_impl running (simulating success).")
    # In later steps, this will be modified to return failure.
    return {"status": "success", "message": "Tool executed successfully (MVP1)"}

failing_tool = FunctionTool(
    func=_failing_tool_impl,
    description="A tool that simulates an operation (returns success in MVP1)."
)
