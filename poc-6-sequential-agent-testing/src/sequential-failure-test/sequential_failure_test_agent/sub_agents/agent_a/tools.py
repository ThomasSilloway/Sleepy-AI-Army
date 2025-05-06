# TODO: Define FailingTool function and FunctionTool instance
from google.adk.tools import FunctionTool

def _failing_tool_impl() -> dict:
    """Simulates a tool failure."""
    print("Simulating tool failure...")
    return {"status": "error", "message": "Simulated tool failure"}

failing_tool = FunctionTool(
    func=_failing_tool_impl,
    description="A tool that always returns a failure status."
)
