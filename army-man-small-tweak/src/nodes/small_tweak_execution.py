"""Contains logic for the execute_small_tweak_node."""
import logging
import os
from pathlib import Path
from typing import Optional

from src.config import AppConfig
from src.models.aider_summary import AiderRunSummary
from src.services.aider_service import AiderExecutionResult, AiderService
from src.services.changelog_service import ChangelogService
from src.state import WorkflowState

logger = logging.getLogger(__name__)

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
    state['error_message'] = None
    state['last_event_summary'] = "Small Tweak execution started."
    state['aider_run_summary'] = None # To store the AiderRunSummary object

    try:
        services_config = config["configurable"]
        app_config: AppConfig = services_config["app_config"]
        aider_service: AiderService = services_config["aider_service"]
        # git_service: GitService = services_config["git_service"] # Keep for now, might be needed for fallback or verification
        changelog_service: ChangelogService = services_config["changelog_service"]

        task_description_path_str = state.get('task_description_path')
        small_tweak_file_path = state.get('small_tweak_file_path')

        if not task_description_path_str:
            error_msg = "[SmallTweakExecution] Critical information missing: task_description_path not found in state."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Missing task_description_path for Small Tweak."
            return state

        if not os.path.exists(task_description_path_str):
            error_msg = f"[SmallTweakExecution] Task description file not found at: {task_description_path_str}"
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = f"Error: Task description file missing at {task_description_path_str}."
            return state

        if not small_tweak_file_path:
            error_msg = "[SmallTweakExecution] Critical information missing: small_tweak_file_path not found in state."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Missing small_tweak_file_path for Small Tweak."
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
        aider_run_summary_obj: Optional[AiderRunSummary] = aider_service.get_summary(aider_result)
        state['aider_run_summary'] = aider_run_summary_obj.model_dump() if aider_run_summary_obj else None

        if aider_result.exit_code == 0:
            logger.info("Aider executed successfully (exit code 0).")
            if aider_run_summary_obj:
                state['is_code_change_committed'] = bool(aider_run_summary_obj.commit_hash)
                state['last_change_commit_hash'] = aider_run_summary_obj.commit_hash
                state['last_change_commit_summary'] = aider_run_summary_obj.commit_message or "Commit message not extracted."

                changes_str = "\n  - ".join(aider_run_summary_obj.changes_made) if aider_run_summary_obj.changes_made else aider_run_summary_obj.raw_output_summary

                event_summary = f"{changes_str}\n\n"
                if aider_run_summary_obj.commit_hash:
                    event_summary += f"  - Commit: {aider_run_summary_obj.commit_hash or 'N/A'} - {aider_run_summary_obj.commit_message or 'N/A'}\n"
                else:
                    event_summary += "  - No commit made by aider."

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
            state['is_changelog_entry_added'] = False

    except Exception as e:
        error_msg = f"[SmallTweakExecution] Unexpected error during small tweak execution: {e}"
        logger.error(error_msg, exc_info=True)
        state['error_message'] = error_msg
        state['last_event_summary'] = f"Unexpected error during Small Tweak: {type(e).__name__} - {e}"
        if state.get('aider_last_exit_code') is None: # If aider didn't even run
            state['aider_last_exit_code'] = -1 
        state['is_changelog_entry_added'] = False


    logger.info(f"Finished node: {state['current_step_name']}. Last event summary: {state['last_event_summary']}")
    return state
