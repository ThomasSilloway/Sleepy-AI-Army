# sequential_failure_test_agent/callbacks/callbacks.py
import json
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

def check_outcome_and_skip_callback(context: CallbackContext, /) -> types.Content | None:
    """
    Checks the outcome of the previous agent in the sequence.

    If the previous agent's outcome (read from context.state as a JSON string)
    indicates a 'failure' or 'skipped' status, this callback will:
    1. Construct a JSON string indicating the current agent is 'skipped'.
    2. Write this 'skipped' JSON string to the context.state using the
       *current* agent's output_key.
    3. Return a types.Content object to signal ADK to skip the current agent.

    If the previous agent succeeded, or if its state cannot be read/parsed,
    it returns None, allowing the current agent to execute normally.
    """
    current_agent_name = context.agent_name
    previous_agent_state_key = None
    current_agent_output_key = None

    # Determine the state key of the *previous* agent and the output key for the *current* agent
    if current_agent_name == "AgentB":
        previous_agent_state_key = "agent_a_outcome"
        current_agent_output_key = "agent_b_outcome"
        previous_agent_name = "Agent A"
    elif current_agent_name == "AgentC":
        previous_agent_state_key = "agent_b_outcome"
        current_agent_output_key = "agent_c_outcome"
        previous_agent_name = "Agent B"
    else:
        # This callback shouldn't be configured for other agents in this PoC
        print(f"Callback Warning: check_outcome_and_skip_callback called for unexpected agent {current_agent_name}. Allowing execution.")
        return None

    print(f"Callback: Running for {current_agent_name}. Checking outcome of {previous_agent_name} (state key: {previous_agent_state_key}).")

    # Read the previous agent's outcome JSON string from state
    previous_outcome_json = context.state.get(previous_agent_state_key)

    if not previous_outcome_json:
        print(f"Callback Warning: State key '{previous_agent_state_key}' not found for {previous_agent_name}. Allowing {current_agent_name} execution.")
        # Decide if missing state should cause a skip or allow continuation.
        # For this PoC, let's allow continuation but log a warning.
        return None

    # Parse the JSON string
    try:
        previous_outcome = json.loads(previous_outcome_json)
        previous_status = previous_outcome.get("status")

        print(f"Callback: Parsed {previous_agent_name} outcome: status='{previous_status}'")

        # Check if the status requires skipping the current agent
        if previous_status in ["failure", "skipped"]:
            print(f"Callback: {previous_agent_name} status is '{previous_status}'. Skipping {current_agent_name}.")

            # Construct the skipped JSON for the *current* agent
            skip_message = f"Skipped due to {previous_agent_name} outcome ('{previous_status}')."
            skipped_outcome = {
                "status": "skipped",
                "message": skip_message
            }
            skipped_outcome_json = json.dumps(skipped_outcome)

            # Write the skipped outcome to the *current* agent's state key
            if current_agent_output_key:
                context.state[current_agent_output_key] = skipped_outcome_json
                print(f"Callback: Set state '{current_agent_output_key}' to: {skipped_outcome_json}")
            else:
                 print(f"Callback Warning: Cannot set skipped state for {current_agent_name} as its output key is unknown.")


            # Return Content to signal ADK to skip this agent's execution
            # Using a simple text part, the content doesn't really matter here,
            # just the fact that we are returning Content instead of None.
            return types.Content(parts=[types.Part(text=f"Skipping {current_agent_name}.")])
        else:
            # Previous agent succeeded, allow current agent to run
            print(f"Callback: {previous_agent_name} status is '{previous_status}'. Allowing {current_agent_name} execution.")
            return None

    except json.JSONDecodeError:
        print(f"Callback Error: Failed to parse JSON from state key '{previous_agent_state_key}': {previous_outcome_json}")
        # Decide behavior on JSON error. Skipping might be safer.
        print(f"Callback: Skipping {current_agent_name} due to JSON parsing error of previous state.")
        # Optionally set skipped state here too, similar to above
        skip_message = f"Skipped due to error parsing {previous_agent_name} state."
        skipped_outcome = {"status": "skipped", "message": skip_message}
        skipped_outcome_json = json.dumps(skipped_outcome)
        if current_agent_output_key:
             context.state[current_agent_output_key] = skipped_outcome_json
             print(f"Callback: Set state '{current_agent_output_key}' to: {skipped_outcome_json}")
        return types.Content(parts=[types.Part(text=f"Skipping {current_agent_name} due to JSON error.")])
    except Exception as e:
        print(f"Callback Error: An unexpected error occurred in check_outcome_and_skip_callback for {current_agent_name}: {e}")
        # Fallback: allow execution to prevent complete blockage? Or skip? Let's skip.
        print(f"Callback: Skipping {current_agent_name} due to unexpected callback error.")
        # Optionally set skipped state here too
        skip_message = f"Skipped due to unexpected error in callback checking {previous_agent_name} state."
        skipped_outcome = {"status": "skipped", "message": skip_message}
        skipped_outcome_json = json.dumps(skipped_outcome)
        if current_agent_output_key:
             context.state[current_agent_output_key] = skipped_outcome_json
             print(f"Callback: Set state '{current_agent_output_key}' to: {skipped_outcome_json}")
        return types.Content(parts=[types.Part(text=f"Skipping {current_agent_name} due to callback error.")])
