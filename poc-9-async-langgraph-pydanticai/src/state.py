from typing import TypedDict, Optional

class WorkflowState(TypedDict):
    """
    Defines the state structure for the LangGraph workflow.
    This TypedDict holds all the data that will be passed between nodes in the graph.
    """
    input_text: str
    generated_summary: Optional[str] # The summary might not be generated if an error occurs
    error_message: Optional[str]     # To store any error messages encountered during processing
    error_details: Optional[str] # New field for traceback or detailed error

    # You can extend this state with more fields as the application grows.
    # For example:
    # current_step_name: Optional[str]
    # attempts_left: int
    # some_intermediate_result: Any

# Example of how this TypedDict might be initialized or used (for clarity):
if __name__ == '__main__':
    # Initializing a state (e.g., at the beginning of a graph invocation)
    initial_state = WorkflowState(
        input_text="This is the initial text to be processed.",
        generated_summary=None,
        error_message=None,
        error_details=None
    )
    print(f"Initial state: {initial_state}")

    # Simulating a state update after a node execution
    initial_state['generated_summary'] = "This is the summary produced by a node."
    # initial_state['current_step_name'] = "SummarizationComplete" # Example of adding another hypothetical field
    # The above line causes a type error if current_step_name is not in WorkflowState
    # For demonstration, let's assume it was added to WorkflowState for this example block
    
    # To correctly demonstrate adding a new field, you'd typically define it in the TypedDict
    # For now, this line is commented out to keep the example runnable with the defined WorkflowState
    
    print(f"Updated state: {initial_state}")

    # Accessing a potentially missing key (demonstrates Optional usage)
    # To safely access optional fields, you might use .get()
    error = initial_state.get('error_message', 'No error.') 
    print(f"Error status: {error}")
