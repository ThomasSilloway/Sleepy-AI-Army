"""Contains logic for the execute_small_tweak_node."""
import asyncio
import logging
import os
from pathlib import Path

from src.config import AppConfig
from src.services.aider_service import AiderService, AiderExecutionResult
from src.services.changelog_service import ChangelogService
from src.services.git_service import GitService # Keep for potential direct git ops if needed, though primary info via LLM
from src.services.llm_prompt_service import LlmPromptService
from src.models.aider_summary import AiderRunSummary
from src.state import WorkflowState

logger = logging.getLogger(__name__)

# TODO: Move this to a constants file or make it configurable via AppConfig
LLM_MODEL_FOR_SUMMARY = "gemini-1.5-flash-latest"

def _create_llm_messages_for_summary(aider_stdout: str, aider_stderr: str) -> list[dict]:
    """Helper function to create messages for the LLM summary."""
    system_prompt = """
You are an expert at analyzing the output of the 'aider' command-line tool.
Your task is to extract specific information from aider's stdout and stderr and return it in a structured JSON format
that matches the AiderRunSummary Pydantic model.

The AiderRunSummary model includes the following fields:
- changes_made: (list[str]) A bulleted list of actual changes applied by aider. Each item should be a clear, concise description of a change (e.g., "Added function `foo` to `bar.py`", "Modified `baz.py` to handle new error condition").
- commit_hash: (Optional[str]) The full git commit hash if aider made a commit *during this specific run*. If no commit was made by aider, this should be null.
- files_modified: (Optional[list[str]]) List of file paths that were modified by aider.
- files_created: (Optional[list[str]]) List of file paths that were newly created by aider.
- errors_reported: (Optional[list[str]]) Any error messages or significant warnings reported by aider.
- raw_output_summary: (Optional[str]) A brief, general summary of what aider did or reported, especially if specific details aren't available or applicable from its output.
- commit_message: (Optional[str]) The full commit message if aider made a commit. If no commit was made, this should be null.

Analyze the provided stdout and stderr from an aider execution.
Extract the information to populate these fields accurately.
If aider's output clearly indicates a commit, extract the hash and message.
If aider failed or no specific changes are identifiable, focus on `errors_reported` and `raw_output_summary`.
Pay close attention to whether a commit was actually made by aider in *this* run. Do not infer commits.
The output MUST be a JSON object matching the AiderRunSummary structure.
"""
    user_prompt_content = f"""
Please analyze the following output from an 'aider' command execution:

**Aider STDOUT:**
```
{aider_stdout}
```

**Aider STDERR:**
```
{aider_stderr}
```

Based on this output, provide a JSON summary matching the AiderRunSummary model.
"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_content},
    ]

def execute_small_tweak_node(state: WorkflowState, config) -> WorkflowState:
    """
    Executes a "Small Tweak" using AiderService based on instructions in
    task_description_path. It then uses an LLM to summarize Aider's output
    and updates WorkflowState with the outcome and extracted details.
    """
    state['current_step_name'] = "Execute Small Tweak"
    logger.info(f"Executing node: {state['current_step_name']}")

    # Initialize state fields for this run
    state['aider_last_exit_code'] = None
    state['last_change_commit_hash'] = None
    state['last_change_commit_summary'] = None
    state['is_code_change_committed'] = False
    state['error_message'] = None
    state['last_event_summary'] = "Small Tweak execution started."
    state['aider_run_summary'] = None # To store the AiderRunSummary object

    try:
        services_config = config["configurable"]
        app_config: AppConfig = services_config["app_config"]
        aider_service: AiderService = services_config["aider_service"]
        # git_service: GitService = services_config["git_service"] # Keep for now, might be needed for fallback or verification
        changelog_service: ChangelogService = services_config["changelog_service"]
        llm_prompt_service: LlmPromptService = services_config["llm_prompt_service"] # Added LlmPromptService

        task_description_path_str = state.get('task_description_path')
        small_tweak_file_path = state.get('small_tweak_file_path')

        if not task_description_path_str:
            error_msg = "[SmallTweakExecution] Critical information missing: task_description_path not found in state."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Missing task_description_path for Small Tweak."
            return state # is_code_change_committed already False

        if not os.path.exists(task_description_path_str):
            error_msg = f"[SmallTweakExecution] Task description file not found at: {task_description_path_str}"
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = f"Error: Task description file missing at {task_description_path_str}."
            return state # is_code_change_committed already False

        if not small_tweak_file_path:
            error_msg = "[SmallTweakExecution] Critical information missing: small_tweak_file_path not found in state."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Missing small_tweak_file_path for Small Tweak."
            state['is_code_change_committed'] = False
            return state

        task_desc_filename = Path(task_description_path_str).name
        aider_prompt = f"""

# File Update Task

> Given the Objective, implement every detail of every task.

## Objectives

 - Implement the changes described in the file '{task_desc_filename}'.

## Low-Level Tasks
> Ordered from start to finish. Implement the described functionality, using standard features in the given language, error handling, and logging as appropriate.

### Task 1: Analyze the changes
```
 - ANALYZE the changes requested as described in the file '{task_desc_filename}'.
```

### Task 2: Brainstorm how to apply changes
```
 - PRINT out in the chat 2-3 possible ways to apply the changes with pros and cons for each
```

### Task 3: Choose the best approach
```
 - CHOOSE the best approach from the options you printed out in Task 2.
 - FORMULATE a plan using this approach and integrating any ideas from the other plans that will maximize their pros and minimize their cons
```

### Task 4: Apply the changes
```
 - EXECUTE the plan formulated in the previous task to implement the changes specified in the file '{task_desc_filename}'.
```

### Task 5: Critique the changes
```
 - CRITIQUE the changes you made in Task 4 listing the pros and cons of the approach
```

### Task 6: Improve the changes
```
    - IMPROVE the changes you made in Task 4 based on the critique you made in Task 5.
    - If you think the changes are already perfect, print out `No changes needed`
```

"""  # noqa: E501

        logger.debug(f"Constructed aider prompt for small tweak:\n\n{aider_prompt}\n\n")

        files_to_edit_or_add_to_context = [
            small_tweak_file_path 
        ] 

        command_args = [
            "-m", aider_prompt,
            "--read", task_description_path_str,
            "--model", app_config.aider_code_model
        ]

        logger.info("Invoking AiderService to execute small tweak.")
        aider_result: AiderExecutionResult = aider_service.execute(
            command_args=command_args,
            files_to_add=files_to_edit_or_add_to_context
        )
        state['aider_last_exit_code'] = aider_result.exit_code
        logger.info(f"Aider execution finished. Exit Code: {aider_result.exit_code}")
        logger.debug(f"Aider STDOUT:\n{aider_result.stdout}")
        logger.debug(f"Aider STDERR:\n{aider_result.stderr}")

        # Attempt to get a structured summary from LLM regardless of aider exit code
        # as even on failure, stderr might contain useful info for the summary.
        aider_run_summary_obj: Optional[AiderRunSummary] = None
        try:
            logger.info("Attempting to extract Aider execution summary using LLM.")
            llm_messages = _create_llm_messages_for_summary(aider_result.stdout, aider_result.stderr)
            
            # Note: Using a placeholder for llm_model_name. This should come from app_config.
            # e.g., app_config.llm_model_for_summaries
            aider_run_summary_obj = asyncio.run(llm_prompt_service.get_structured_output(
                messages=llm_messages,
                output_pydantic_model_type=AiderRunSummary,
                llm_model_name=LLM_MODEL_FOR_SUMMARY, # Placeholder
                llm_temperature_value=0.1 # Low temp for factual extraction
            ))
            state['aider_run_summary'] = aider_run_summary_obj.dict() if aider_run_summary_obj else None
            if aider_run_summary_obj:
                logger.info("Successfully extracted Aider run summary.")
                logger.debug(f"Aider Run Summary: {aider_run_summary_obj.json(indent=2)}")
            else:
                logger.warning("LLM did not return a valid AiderRunSummary object.")
        except Exception as llm_exc:
            logger.error(f"Error during LLM summary extraction: {llm_exc}", exc_info=True)
            state['error_message'] = f"Error during LLM summary extraction: {llm_exc}"
            # Fallback summary if LLM fails, will be refined based on aider exit code later
            state['last_event_summary'] = "Aider execution completed, but summary extraction failed."


        if aider_result.exit_code == 0:
            logger.info("Aider executed successfully (exit code 0).")
            if aider_run_summary_obj:
                state['is_code_change_committed'] = bool(aider_run_summary_obj.commit_hash)
                state['last_change_commit_hash'] = aider_run_summary_obj.commit_hash
                state['last_change_commit_summary'] = aider_run_summary_obj.commit_message or "Commit message not extracted."

                changes_str = "\n - ".join(aider_run_summary_obj.changes_made) if aider_run_summary_obj.changes_made else "No specific changes listed by summary."
                event_summary = (
                    f"Small Tweak applied. Commit: {aider_run_summary_obj.commit_hash or 'N/A'}.\n"
                    f"Changes:\n - {changes_str}\n"
                    f"Summary: {aider_run_summary_obj.raw_output_summary or 'N/A'}"
                )
                state['last_event_summary'] = event_summary
                state['error_message'] = None # Clear previous errors if any

                logger.info("Attempting to record small tweak event in changelog.")
                changelog_success = changelog_service.record_event_in_changelog(
                    current_workflow_state=state, # Pass the entire state
                    preceding_event_summary=event_summary 
                )
                state['is_changelog_entry_added'] = changelog_success
                if changelog_success:
                    logger.info("Changelog entry successfully added for small tweak.")
                else:
                    logger.warning("Failed to add changelog entry for small tweak.")
            else:
                # Aider success, but LLM summary failed
                logger.warning("Aider executed successfully, but LLM summary extraction failed.")
                state['is_code_change_committed'] = False # Cannot confirm commit without summary
                state['last_event_summary'] = "Aider ran successfully, but summary extraction failed. Raw Aider output logged."
                # No commit hash or summary known
                state['last_change_commit_hash'] = None
                state['last_change_commit_summary'] = "Summary extraction failed."
                # Optionally, log to changelog with generic message or skip. For now, skipping.
                state['is_changelog_entry_added'] = False

        else: # Aider failed (exit_code != 0)
            error_msg_prefix = f"Failed to apply Small Tweak. Aider exit code: {aider_result.exit_code}."
            logger.error(error_msg_prefix)
            state['is_code_change_committed'] = False
            
            extracted_errors = ""
            raw_summary = ""
            if aider_run_summary_obj:
                if aider_run_summary_obj.errors_reported:
                    extracted_errors = "\n - ".join(aider_run_summary_obj.errors_reported)
                    logger.info(f"Extracted errors from Aider output: {extracted_errors}")
                raw_summary = aider_run_summary_obj.raw_output_summary or ""

            detailed_error_msg = f"{error_msg_prefix}"
            if extracted_errors:
                detailed_error_msg += f"\nExtracted Errors:\n - {extracted_errors}"
            elif raw_summary:
                 detailed_error_msg += f"\nAider Output Summary: {raw_summary}"
            else:
                # Fallback if LLM provides nothing useful or failed
                stderr_snippet = (aider_result.stderr[:500] + '...' if len(aider_result.stderr) > 500 else aider_result.stderr)
                detailed_error_msg += f"\nAider STDERR (first 500 chars): {stderr_snippet}"

            state['error_message'] = detailed_error_msg
            state['last_event_summary'] = detailed_error_msg
            # Clear git info fields on failure
            state['last_change_commit_hash'] = None
            state['last_change_commit_summary'] = None
            state['is_changelog_entry_added'] = False


    except Exception as e:
        error_msg = f"[SmallTweakExecution] Unexpected error during small tweak execution: {e}"
        logger.error(error_msg, exc_info=True)
        state['is_code_change_committed'] = False # Ensure this is false on unexpected error
        state['error_message'] = error_msg
        state['last_event_summary'] = f"Unexpected error during Small Tweak: {type(e).__name__} - {e}"
        if state.get('aider_last_exit_code') is None: # If aider didn't even run
            state['aider_last_exit_code'] = -1 
        state['last_change_commit_hash'] = None
        state['last_change_commit_summary'] = None
        state['is_changelog_entry_added'] = False


    logger.info(f"Finished node: {state['current_step_name']}. Last event summary: {state['last_event_summary']}")
    return state
