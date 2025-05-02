import json
import logging
import os
from typing import AsyncGenerator, Dict, Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.events import Event, EventActions
from google.adk.agents.callback_context import InvocationContext

from ...shared_libraries import constants
from . import prompt as tsa_prompt
# Import shared tool functions directly
from ...shared_tools.file_system import create_directory, write_file
from ...shared_tools.task_helpers import get_next_task_number

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Tool Instantiation ---
# Wrap the shared functions as FunctionTool instances for the agent
get_next_task_number_tool = FunctionTool(func=get_next_task_number)
create_directory_tool = FunctionTool(func=create_directory)
write_file_tool = FunctionTool(func=write_file)

# --- Agent Definition ---
class TaskSetupAgent(LlmAgent):
    """
    Agent responsible for setting up the task folder structure.
    Infers prefix/slug, gets the next task number, creates the directory,
    and writes initial files.
    """
    async def _run_async_impl(
        self, parent_context: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Orchestrates the task setup process."""
        agent_name = self.name
        invocation_id = parent_context.invocation_id
        state = parent_context.state
        user_content = parent_context.user_content # Original task description

        if not user_content:
            logging.error(f"{agent_name}: No user_content (task description) found in context.")
            yield Event.agent_error(agent_name, invocation_id, "Missing task description.")
            return

        logging.info(f"{agent_name}: Received task description: '{user_content}'")
        yield Event.agent_start(agent_name, invocation_id, user_content)

        # 1. Call LLM to infer prefix and slug
        logging.info(f"{agent_name}: Calling LLM to infer prefix and slug...")
        llm_response_event = None
        try:
            # Use the agent's own run_async to leverage its LLM call mechanism
            # Pass user_content explicitly if needed, or rely on context propagation
            # For simplicity here, we assume the agent's instruction uses {{user_content}}
            async for event in super()._run_async_impl(parent_context):
                 yield event # Yield intermediate events like model start/end
                 if event.is_final_response():
                     llm_response_event = event
                     break # Stop after getting the final LLM response

            if not llm_response_event or not llm_response_event.content:
                raise ValueError("LLM did not provide a valid response for prefix/slug.")

            llm_output_str = llm_response_event.content.parts[0].text
            logging.info(f"{agent_name}: Received LLM response for prefix/slug: {llm_output_str}")
            prefix_slug_data = json.loads(llm_output_str)
            prefix = prefix_slug_data.get("prefix")
            slug = prefix_slug_data.get("slug")

            if not prefix or not slug:
                raise ValueError("LLM response missing 'prefix' or 'slug'.")

            logging.info(f"{agent_name}: Inferred prefix='{prefix}', slug='{slug}'")

        except json.JSONDecodeError as e:
            logging.error(f"{agent_name}: Failed to parse LLM JSON response: {llm_output_str} - {e}", exc_info=True)
            yield Event.agent_error(agent_name, invocation_id, f"Failed to parse LLM response: {e}")
            return
        except Exception as e:
            logging.error(f"{agent_name}: Error during LLM call for prefix/slug: {e}", exc_info=True)
            yield Event.agent_error(agent_name, invocation_id, f"LLM prefix/slug inference failed: {e}")
            return

        # 2. Call get_next_task_number tool
        logging.info(f"{agent_name}: Calling get_next_task_number tool...")
        tool_args = {"base_path": constants.BASE_TASK_PATH, "prefix": prefix}
        try:
            # Manually invoke the tool using its run_async method
            # Note: ADK might offer cleaner ways via internal mechanisms, but this is explicit
            tool_result_dict = await get_next_task_number_tool.run_async(args=tool_args, tool_context=parent_context) # Pass context if tool needs it
            yield Event.tool_end(agent_name, invocation_id, get_next_task_number_tool.name, tool_result_dict) # Simulate tool end event

            if tool_result_dict.get("status") != "success":
                raise ValueError(f"Tool failed: {tool_result_dict.get('message', 'Unknown error')}")

            next_number_int = tool_result_dict.get("next_number")
            if next_number_int is None:
                 raise ValueError("Tool did not return a 'next_number'.")

            logging.info(f"{agent_name}: Received next task number: {next_number_int}")

        except Exception as e:
            logging.error(f"{agent_name}: Error calling get_next_task_number tool: {e}", exc_info=True)
            yield Event.agent_error(agent_name, invocation_id, f"Failed to get next task number: {e}")
            return

        # 3. Format number with NNN padding
        try:
            nnn_number_str = str(next_number_int).zfill(constants.NNN_PADDING)
            logging.info(f"{agent_name}: Formatted number: {nnn_number_str}")
        except Exception as e:
             logging.error(f"{agent_name}: Error formatting number {next_number_int}: {e}", exc_info=True)
             yield Event.agent_error(agent_name, invocation_id, f"Failed to format task number: {e}")
             return

        # 4. Construct full directory path
        task_folder_name = f"{prefix}{nnn_number_str}_{slug}"
        full_task_path = os.path.join(constants.BASE_TASK_PATH, task_folder_name)
        logging.info(f"{agent_name}: Constructed full task path: {full_task_path}")

        # 5. Call create_directory tool
        logging.info(f"{agent_name}: Calling create_directory tool...")
        tool_args = {"path": full_task_path, "create_parents": True}
        try:
            tool_result_dict = await create_directory_tool.run_async(args=tool_args, tool_context=parent_context)
            yield Event.tool_end(agent_name, invocation_id, create_directory_tool.name, tool_result_dict)

            if tool_result_dict.get("status") != "success":
                raise ValueError(f"Tool failed: {tool_result_dict.get('message', 'Unknown error')}")

            logging.info(f"{agent_name}: Successfully created directory: {full_task_path}")

        except Exception as e:
            logging.error(f"{agent_name}: Error calling create_directory tool: {e}", exc_info=True)
            yield Event.agent_error(agent_name, invocation_id, f"Failed to create task directory: {e}")
            return

        # 6. Call write_file tool for changelog.md
        changelog_path = os.path.join(full_task_path, "changelog.md")
        logging.info(f"{agent_name}: Calling write_file tool for {changelog_path}...")
        tool_args = {"path": changelog_path, "content": "# Changelog\n\n", "overwrite": False}
        try:
            tool_result_dict = await write_file_tool.run_async(args=tool_args, tool_context=parent_context)
            yield Event.tool_end(agent_name, invocation_id, write_file_tool.name, tool_result_dict)

            if tool_result_dict.get("status") != "success":
                 # Log warning but continue to write task_description.md
                 logging.warning(f"{agent_name}: Failed to write changelog.md: {tool_result_dict.get('message')}")
            else:
                 logging.info(f"{agent_name}: Successfully wrote {changelog_path}")

        except Exception as e:
            # Log warning but continue
            logging.warning(f"{agent_name}: Error calling write_file tool for changelog.md: {e}", exc_info=True)


        # 7. Call write_file tool for task_description.md
        task_desc_path = os.path.join(full_task_path, "task_description.md")
        logging.info(f"{agent_name}: Calling write_file tool for {task_desc_path}...")
        tool_args = {"path": task_desc_path, "content": user_content, "overwrite": False}
        try:
            tool_result_dict = await write_file_tool.run_async(args=tool_args, tool_context=parent_context)
            yield Event.tool_end(agent_name, invocation_id, write_file_tool.name, tool_result_dict)

            if tool_result_dict.get("status") != "success":
                 # This is more critical, raise error if it fails
                 raise ValueError(f"Tool failed: {tool_result_dict.get('message', 'Unknown error')}")

            logging.info(f"{agent_name}: Successfully wrote {task_desc_path}")

        except Exception as e:
            logging.error(f"{agent_name}: Error calling write_file tool for task_description.md: {e}", exc_info=True)
            # If writing the description fails, the task setup is incomplete
            yield Event.agent_error(agent_name, invocation_id, f"Failed to write task_description.md: {e}")
            return

        # 8. Final Success Response
        final_message = f"Successfully created task folder: {full_task_path}"
        logging.info(f"{agent_name}: {final_message}")
        # Update state if needed, e.g., state['last_created_task_path'] = full_task_path
        actions = EventActions(state_delta={'last_created_task_path': full_task_path})
        yield Event.agent_end(agent_name, invocation_id, final_message, actions=actions)


# Instantiate the agent
task_setup_agent = TaskSetupAgent(
    name=constants.TASK_SETUP_AGENT_NAME,
    model=constants.MODEL_NAME,
    instruction=tsa_prompt.TASK_SETUP_AGENT_PROMPT,
    tools=[ # Tools it orchestrates (available for LLM if needed, but primarily used by _run_async_impl)
        get_next_task_number_tool,
        create_directory_tool,
        write_file_tool,
    ],
    description="Generates prefix/slug, gets next number, creates task folder/files.",
    # The core logic is now within the overridden _run_async_impl method
)