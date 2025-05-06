# poc6_sequential_failure/sub_agents/agent_a/tools.py
from google.adk.tools import FunctionTool


def _failing_tool_impl() -> dict:
    """
    Simulates a tool execution that fails.
    """
    print("Tool: _failing_tool_impl running (simulating failure).")
    # This simulates a tool encountering an error.
    return {"status": "error", "message": "Simulated tool failure"}
    # This simulates a tool executing successfully.
    # return {"status": "success", "message": "Simulated tool success"}


failing_tool = FunctionTool(func=_failing_tool_impl)
