"""Contains logic for workflow finalization nodes (success, error)."""

def success_node(state: dict) -> dict:
    print("Workflow completed successfully.")
    # TODO: Log final success
    return state

def error_handler_node(state: dict) -> dict:
    print(f"Workflow failed. Error: {{state.get('error_message', 'Unknown error')}}")
    # TODO: Log detailed error information
    return state
