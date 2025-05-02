import json
import logging
from typing import AsyncGenerator

from google.adk.agents import LlmAgent
from google.adk.events import Event
from google.adk.agents.callback_context import InvocationContext

from .shared_libraries import constants
from . import prompt as sto_prompt
from .sub_agents.task_setup_agent.agent import task_setup_agent # Keep reference for instantiation

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SingleTaskOrchestrator(LlmAgent):
    """
    Root agent that analyzes user input via LLM and routes to TaskSetupAgent
    for new tasks or responds directly if the task exists.
    """
    async def _run_async_impl(
        self, parent_context: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Overrides the default run to implement custom routing logic."""
        agent_name = self.name
        invocation_id = parent_context.invocation_id
        user_content = parent_context.user_content

        if not user_content:
            logging.error(f"{agent_name}: No user_content found in context.")
            yield Event.agent_error(agent_name, invocation_id, "Missing user input.")
            return

        logging.info(f"{agent_name}: Received input: '{user_content}'")
        yield Event.agent_start(agent_name, invocation_id, user_content)

        # Call the LLM using the standard LlmAgent mechanism
        logging.info(f"{agent_name}: Calling LLM to analyze input format...")
        llm_response_event = None
        try:
            # Use super()._run_async_impl to get the LLM response based on instruction
            async for event in super()._run_async_impl(parent_context):
                yield event # Yield intermediate events (model start/end, etc.)
                if event.is_final_response():
                    llm_response_event = event
                    break # Got the final LLM output

            if not llm_response_event or not llm_response_event.content:
                 raise ValueError("LLM did not provide a valid response for input analysis.")

            llm_output_str = llm_response_event.content.parts[0].text
            logging.info(f"{agent_name}: Received LLM analysis: {llm_output_str}")

            # Parse the JSON response from the LLM
            analysis_data = json.loads(llm_output_str)
            action = analysis_data.get("action")
            detail = analysis_data.get("detail") # Path/Name if action is 'exists'

        except json.JSONDecodeError as e:
            logging.error(f"{agent_name}: Failed to parse LLM JSON response: {llm_output_str} - {e}", exc_info=True)
            yield Event.agent_error(agent_name, invocation_id, f"Failed to parse LLM analysis response: {e}")
            return
        except Exception as e:
            logging.error(f"{agent_name}: Error during LLM input analysis: {e}", exc_info=True)
            yield Event.agent_error(agent_name, invocation_id, f"LLM input analysis failed: {e}")
            return

        # Route based on the parsed action
        if action == "exists":
            response_message = f"This task already exists: {detail}"
            logging.info(f"{agent_name}: Responding directly - {response_message}")
            yield Event.agent_end(agent_name, invocation_id, response_message)
            return # Stop processing

        elif action == "new_task":
            logging.info(f"{agent_name}: Identified as new task. Delegating to TaskSetupAgent...")
            # Find the sub-agent
            tsa = self.find_sub_agent(constants.TASK_SETUP_AGENT_NAME)
            if not tsa:
                logging.error(f"{agent_name}: Could not find sub-agent '{constants.TASK_SETUP_AGENT_NAME}'.")
                yield Event.agent_error(agent_name, invocation_id, "TaskSetupAgent not found.")
                return

            # Delegate to the sub-agent by calling its run_async
            # Pass the original context so it gets the user_content
            try:
                async for sub_event in tsa.run_async(parent_context):
                    yield sub_event # Yield events from the sub-agent

                # Note: The final response to the user will come from the sub-agent's agent_end event
                logging.info(f"{agent_name}: Delegation to TaskSetupAgent complete.")

            except Exception as e:
                 logging.error(f"{agent_name}: Error occurred during TaskSetupAgent execution: {e}", exc_info=True)
                 yield Event.agent_error(agent_name, invocation_id, f"Error during task setup: {e}")
                 return

        else:
            # LLM provided an unexpected action
            logging.error(f"{agent_name}: Received unknown action '{action}' from LLM analysis.")
            yield Event.agent_error(agent_name, invocation_id, f"Unknown action from LLM: {action}")
            return


# Instantiate the custom agent class
root_agent = SingleTaskOrchestrator(
    name=constants.ROOT_AGENT_NAME,
    model=constants.MODEL_NAME,
    instruction=sto_prompt.STO_PROMPT,
    sub_agents=[task_setup_agent], # Pass the imported instance
    description="Routes user input to task setup or responds if task exists."
)