# sequential_failure_test_agent/callbacks/callbacks.py
import json
import re
from typing import Any, Optional, dict

from google.adk.agents.callback_context import CallbackContext
from google.genai import types


###
#  TODO: Consider refactoring this into having each agent's callback being
#  a separate function that calls a shared function in this file
###
def _get_agent_context(
    current_agent_name: str,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Determines the state keys and name for the previous agent based on the current one."""
    if current_agent_name == "AgentB":
        return "agent_a_outcome", "agent_b_outcome", "Agent A"
    elif current_agent_name == "AgentC":
        return "agent_b_outcome", "agent_c_outcome", "Agent B"
    else:
        # This callback shouldn't be configured for other agents in this PoC
        print(f"Callback Warning: _get_agent_context called for unexpected agent {current_agent_name}.")
        return None, None, None


def _parse_outcome_json(outcome_json: Optional[str], state_key: str) -> Optional[dict[str, Any]]:
    """Parses the JSON outcome string, attempting to strip markdown fences if necessary."""
    if not outcome_json:
        return None

    try:
        # Initial parse attempt
        return json.loads(outcome_json)
    except json.JSONDecodeError:
        print(
            f"Callback Info: Initial JSON parse failed for state key '{state_key}'. Raw content: '{outcome_json}'. Attempting to strip markdown fences."
        )
        # Attempt to strip markdown fences (```json ... ``` or ``` ... ```)
        stripped_json = outcome_json
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", outcome_json, re.IGNORECASE)
        if match:
            stripped_json = match.group(1).strip()
            print(f"Callback Info: Stripped markdown fences. Trying to parse: '{stripped_json}'")
        else:
            # Also try stripping potential leading/trailing quotes if no fences found
            stripped_json = outcome_json.strip().strip('"')
            if stripped_json != outcome_json:
                print(f"Callback Info: Stripped quotes. Trying to parse: '{stripped_json}'")
            else:
                print("Callback Info: No markdown fences or extra quotes found to strip.")

        try:
            # Try parsing again with the stripped content
            parsed_outcome = json.loads(stripped_json)
            print(f"Callback: Successfully parsed state key '{state_key}' after stripping.")
            return parsed_outcome
        except json.JSONDecodeError:
            print(
                f"Callback Error: Failed to parse JSON from state key '{state_key}' even after attempting to strip fences/quotes from: '{outcome_json}'"
            )
            return None  # Indicate persistent parsing failure


def _create_skip_return_value(
    callback_context: CallbackContext,
    current_agent_output_key: Optional[str],
    previous_agent_name: str,
    reason_status: str,
    skip_message_override: Optional[str] = None,
) -> types.Content:
    """Constructs skip outcome, sets state, and returns Content to signal skip."""
    current_agent_name = callback_context.agent_name
    print(f"Callback: Skipping {current_agent_name} due to {previous_agent_name} status '{reason_status}'.")

    if skip_message_override:
        skip_message = skip_message_override
    else:
        skip_message = f"Skipped due to {previous_agent_name} outcome ('{reason_status}')."

    skipped_outcome = {"status": "skipped", "message": skip_message}
    skipped_outcome_json = json.dumps(skipped_outcome)

    if current_agent_output_key:
        callback_context.state[current_agent_output_key] = skipped_outcome_json
        print(f"Callback: Set state '{current_agent_output_key}' to: {skipped_outcome_json}")
    else:
        print(f"Callback Warning: Cannot set skipped state for {current_agent_name} as its output key is unknown.")

    # Return Content to signal ADK to skip this agent's execution
    return types.Content(parts=[types.Part(text=f"Skipping {current_agent_name}.")])


def check_outcome_and_skip_callback(
    callback_context: CallbackContext,
) -> types.Content | None:
    """
    Checks the outcome of the previous agent in the sequence.

    If the previous agent's outcome (read from context.state as a JSON string)
    indicates a 'failure' or 'skipped' status, this callback will:
    1. Construct a JSON string indicating the current agent is 'skipped'.
    2. Write this 'skipped' JSON string to the context.state using the
       *current* agent's output_key.
    3. Return a types.Content object to signal ADK to skip the current agent.

    If the previous agent succeeded, or if its state cannot be read/parsed correctly,
    it returns None, allowing the current agent to execute normally.
    Handles potential JSON parsing errors and markdown code fences.
    """
    current_agent_name = callback_context.agent_name

    try:
        # 1. Determine context (previous agent keys/name)
        previous_agent_state_key, current_agent_output_key, previous_agent_name = _get_agent_context(current_agent_name)

        if not previous_agent_state_key or not previous_agent_name:
            # Warning already logged by _get_agent_context if agent is unexpected
            return None  # Allow execution for unexpected agents

        print(
            f"check_outcome_and_skip_callback: Running for {current_agent_name}. Checking outcome of {previous_agent_name} (state key: {previous_agent_state_key})."
        )

        # 2. Read previous outcome from state
        previous_outcome_json = callback_context.state.get(previous_agent_state_key)

        if not previous_outcome_json:
            print(
                f"Callback Warning: State key '{previous_agent_state_key}' not found for {previous_agent_name}. Allowing {current_agent_name} execution."
            )
            # Allow continuation if state is missing, could adjust this policy if needed
            return None

        # 3. Parse the outcome JSON (handles stripping)
        previous_outcome = _parse_outcome_json(previous_outcome_json, previous_agent_state_key)

        if previous_outcome is None:
            # Parsing failed completely, even after stripping attempts. Skip current agent.
            # Error logged by _parse_outcome_json
            skip_msg = f"Skipped due to error parsing {previous_agent_name} state (stripping failed)."
            return _create_skip_return_value(
                callback_context,
                current_agent_output_key,
                previous_agent_name,
                "parse_error",
                skip_message_override=skip_msg,
            )

        # 4. Check the status from the parsed outcome
        previous_status = previous_outcome.get("status")
        print(f"Callback: Parsed {previous_agent_name} outcome: status='{previous_status}'")

        # 5. Decide whether to skip based on status
        if previous_status in ["failure", "skipped"]:
            # Previous step failed or was skipped, so skip this one too
            return _create_skip_return_value(
                callback_context,
                current_agent_output_key,
                previous_agent_name,
                previous_status,
            )
        else:
            # Previous step succeeded (or had an unexpected status), allow current agent to run
            print(f"Callback: {previous_agent_name} status is '{previous_status}'. Allowing {current_agent_name} execution.")
            return None

    except Exception as e:
        # Catch any unexpected errors during callback execution
        print(f"Callback Error: An unexpected error occurred in check_outcome_and_skip_callback for {current_agent_name}: {e}")
        # Fallback: Skip the current agent for safety
        # Try to determine keys again for setting state, might fail if error was early
        _, current_agent_output_key, previous_agent_name = _get_agent_context(current_agent_name)
        previous_agent_name = previous_agent_name or "previous agent"  # Fallback name
        skip_msg = f"Skipped due to unexpected error in callback while checking {previous_agent_name} state."
        return _create_skip_return_value(
            callback_context,
            current_agent_output_key,
            previous_agent_name,
            "callback_error",
            skip_message_override=skip_msg,
        )
