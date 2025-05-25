from typing import TypedDict

from langgraph.graph import END, StateGraph


# 1. Define the state
# This TypedDict will hold the data that flows through our graph. [cite: 47, 48, 51]
class MyWorkflowState(TypedDict):
    messages: list[str]
    current_sender: str
    final_message: str # To store the combined message

# 2. Define the nodes (Python functions)
# Each node receives the current state and can return updates to it.

def node_one_hello(state: MyWorkflowState) -> MyWorkflowState:
    sender = "NodeHello"
    print(f"--- Executing Node One: {sender} ---")
    current_messages = state.get("messages", [])
    new_message = f"{sender}: Hello from Node One!"
    current_messages.append(new_message)

    # Update the state
    updated_state: MyWorkflowState = {
        **state, # type: ignore (Preserve existing state fields)
        "messages": current_messages,
        "current_sender": sender
    }
    print(f"Node One updated state: {updated_state['messages'][-1]}")
    return updated_state

def node_two_world(state: MyWorkflowState) -> MyWorkflowState:
    sender = "NodeWorld"
    print(f"--- Executing Node Two: {sender} ---")
    current_messages = state.get("messages", [])
    message_from_node_one = ""
    if state.get("current_sender") == "NodeHello" and current_messages:
        message_from_node_one = current_messages[-1]
        print(f"Node Two received from Node One: '{message_from_node_one}'")

    new_message = f"{sender}: World, received your hello!"
    current_messages.append(new_message)

    combined = ""
    if len(current_messages) >=2: # Simple combination
        combined = f"Combined: [{current_messages[-2].split(': ')[1]}] and [{current_messages[-1].split(': ')[1]}]"

    # Update the state
    updated_state: MyWorkflowState = {
        **state, # type: ignore
        "messages": current_messages,
        "current_sender": sender,
        "final_message": combined
    }
    print(f"Node Two updated state: {updated_state['messages'][-1]}")
    print(f"Final combined message: {updated_state['final_message']}")
    return updated_state

# 3. Set up the graph
workflow_builder = StateGraph(MyWorkflowState)

# Add the nodes
workflow_builder.add_node("node_hello", node_one_hello) # [cite: 69, 72]
workflow_builder.add_node("node_world", node_two_world) # [cite: 69, 72]

# Set the entry point
workflow_builder.set_entry_point("node_hello") # [cite: 69]

# Add edges to define the flow
workflow_builder.add_edge("node_hello", "node_world") # [cite: 69]
workflow_builder.add_edge("node_world", END) # End the workflow after node_world [cite: 72]

# 4. Compile the graph
app = workflow_builder.compile() # [cite: 72]

# 5. Prepare an initial state
initial_state: MyWorkflowState = {
    "messages": [],
    "current_sender": "",
    "final_message": ""
}

# 6. Run the graph and see the output
print("\n--- Running the LangGraph Workflow ---")
# .stream() executes the graph and yields events for each step
for event in app.stream(initial_state):
    for key, value in event.items():
        print(f"Output from node '{key}':")
        # print(f"  Full state update: {value}") # You can print the full state if needed
        if 'messages' in value and value['messages']:
             print(f"  Last message: {value['messages'][-1]}")
        if 'final_message' in value and value['final_message']:
            print(f"  Final Combined Message in State: {value['final_message']}")
        print("---")

# Alternative to run the graph to completion and get the final state
# .invoke() runs to completion and returns final state 
# final_run_state = app.invoke(initial_state) 
# print("\n--- Final State after Workflow ---")
# print(f"Messages in final state: {final_run_state.get('messages')}")
# print(f"Last sender in final state: {final_run_state.get('current_sender')}")
# print(f"Final combined message in final state: {final_run_state.get('final_message')}")
