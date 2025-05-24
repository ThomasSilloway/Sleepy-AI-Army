"""Contains logic for the manifest_update_node."""
import logging
import re
import os
from datetime import datetime
from typing import Any # Any will be replaced by any if used

from src.config import AppConfig
from src.services.changelog_service import ChangelogService
from src.state import WorkflowState

logger = logging.getLogger(__name__)

def manifest_update_node(state: WorkflowState, config) -> WorkflowState:
    """
    Updates the existing goal manifest file based on the outcome of previous steps,
    particularly the small tweak execution. It updates status fields, timestamps,
    and potentially adds AI questions if errors occurred. Records the update
    event in the changelog.
    """
    state['current_step_name'] = "Update Manifest"
    logger.info(f"Executing node: {state['current_step_name']}")

    # Store original error message if any from previous steps
    original_error_message_from_tweak = state.get('error_message')
    # Clear error message for this node's execution, will be reset if this node fails
    state['error_message'] = None 

    try:
        services_config = config["configurable"]
        # app_config: AppConfig = services_config["app_config"] # Not directly used, but good to have if config evolves
        changelog_service: ChangelogService = services_config["changelog_service"]

        manifest_output_path_str = state.get('manifest_output_path')
        small_tweak_file_path = state.get('small_tweak_file_path') # This is the artifact path

        # 3. Error Handling Pre-check
        if not manifest_output_path_str or not small_tweak_file_path:
            error_msg = "[ManifestUpdate] Critical information missing: manifest_output_path or small_tweak_file_path not found in state."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Missing critical info for manifest update."
            return state

        # 4. Read the existing manifest file
        manifest_content: str
        try:
            with open(manifest_output_path_str, 'r', encoding='utf-8') as f:
                manifest_content = f.read()
            logger.info(f"Successfully read manifest file: {manifest_output_path_str}")
        except FileNotFoundError:
            error_msg = f"[ManifestUpdate] Manifest file not found at {manifest_output_path_str}."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Manifest file not found for update."
            return state
        except IOError as e:
            error_msg = f"[ManifestUpdate] IOError reading manifest file {manifest_output_path_str}: {e}"
            logger.error(error_msg, exc_info=True)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Could not read manifest file for update."
            return state

        # 5. Determine new status based on state['error_message'] from previous step (tweak execution)
        task_had_error = bool(original_error_message_from_tweak)
        logger.info(f"Task had error (from previous step): {task_had_error}")


        # 6. Update Manifest Content (String Manipulation)
        updated_manifest_content = manifest_content

        # Overall Status
        new_overall_status = "Error in Execution" if task_had_error else "Complete"
        updated_manifest_content = re.sub(
            r"^(Overall Status: ).*$",
            f"\\1{new_overall_status}",
            updated_manifest_content,
            flags=re.MULTILINE
        )
        logger.debug(f"Set Overall Status to: {new_overall_status}")

        # Artifact Status
        # Escape the file path for regex and ensure it's treated as a literal string
        escaped_artifact_path = re.escape(small_tweak_file_path)
        artifact_status_pattern = re.compile(
            r"^(\* \[(?:in-progress|Complete|Error)\] )(.*" + escaped_artifact_path + r".*)$",
            re.MULTILINE
        )
        
        new_artifact_status_text = "[Complete]"
        if task_had_error:
            # If there was an error, the tweak node might not have even started,
            # or it might have failed mid-way.
            # We want to ensure it's marked as in-progress or error, not complete.
            # For simplicity, if an error occurred in the tweak step, we'll mark it as in-progress
            # as the manifest update is about the overall goal.
            # A more nuanced approach might involve different error statuses.
            new_artifact_status_text = "[in-progress]" # Or "[Error]" if we want to be more specific

        match = artifact_status_pattern.search(updated_manifest_content)
        if match:
            updated_manifest_content = artifact_status_pattern.sub(
                f"\\1{new_artifact_status_text} \\2", # Ensure space after status
                updated_manifest_content,
                count=1 # Replace only the first occurrence, should be unique
            )
            # Correct potential double status like "* [in-progress] [Complete] path/to/file"
            # by specifically targeting the status part of the matched line.
            # The previous regex was too broad and could lead to issues if the file path itself contained "[Complete]"
            
            # More precise replacement using re.sub with a function for replacement
            def replace_artifact_status(m):
                current_status_and_prefix = m.group(1) # e.g., "* [in-progress] "
                file_path_and_suffix = m.group(2)    # e.g., "path/to/file"
                # Replace only the status part within current_status_and_prefix
                new_prefix = re.sub(r"\[.*?\]", new_artifact_status_text, current_status_and_prefix)
                return f"{new_prefix}{file_path_and_suffix}"

            updated_manifest_content = re.sub(
                r"^(\* \[[^\]]+\]\s+)(" + re.escape(small_tweak_file_path) + r".*)$",
                replace_artifact_status,
                updated_manifest_content,
                flags=re.MULTILINE,
                count=1
            )
            logger.debug(f"Updated artifact status for '{small_tweak_file_path}' to '{new_artifact_status_text}'")
        else:
            logger.warning(f"Could not find artifact line for '{small_tweak_file_path}' to update its status.")


        # AI Questions for User
        if task_had_error:
            error_details = original_error_message_from_tweak # Use the error from the tweak step
            ai_question = f"Error occurred during the automated task, can you review it please?\n\nError details:\n{error_details}"
            
            # Try to replace "AI Questions for User\nNONE" first
            ai_questions_replacement_pattern = re.compile(
                r"^(AI Questions for User:?\s*\n)NONE\s*$",
                re.MULTILINE | re.IGNORECASE
            )
            if ai_questions_replacement_pattern.search(updated_manifest_content):
                updated_manifest_content = ai_questions_replacement_pattern.sub(
                    f"\\1{ai_question}\n", # Add a newline after the question
                    updated_manifest_content,
                    count=1
                )
                logger.debug("Replaced 'AI Questions for User: NONE' with new error question.")
            else:
                # If "NONE" is not found, or the section has other content,
                # append the question under the heading. This is a simple append.
                # A more robust solution would parse existing questions.
                ai_section_heading_pattern = re.compile(r"^(AI Questions for User:?\s*\n)", re.MULTILINE | re.IGNORECASE)
                match_heading = ai_section_heading_pattern.search(updated_manifest_content)
                if match_heading:
                    insert_position = match_heading.end()
                    updated_manifest_content = (
                        updated_manifest_content[:insert_position] +
                        f"{ai_question}\n" + # Add the new question
                        updated_manifest_content[insert_position:]
                    )
                    logger.debug("Appended new error question under 'AI Questions for User'.")
                else:
                    # If the section doesn't exist at all, append it. This is less likely given manifest_create.
                    updated_manifest_content += f"\n\nAI Questions for User:\n{ai_question}\n"
                    logger.debug("Appended 'AI Questions for User' section with new error question.")
        else:
            logger.debug("No task error, AI Questions for User section not changed.")

        # Last Updated Timestamp
        current_timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        updated_manifest_content = re.sub(
            r"^(Last Updated: ).*$",
            f"\\1{current_timestamp}",
            updated_manifest_content,
            flags=re.MULTILINE
        )
        logger.debug(f"Updated Last Updated timestamp to: {current_timestamp}")

        # 7. Write the updated content back to the manifest file
        try:
            with open(manifest_output_path_str, 'w', encoding='utf-8') as f:
                f.write(updated_manifest_content)
            logger.info(f"Successfully wrote updated manifest to: {manifest_output_path_str}")
            manifest_update_successful = True
        except IOError as e:
            error_msg = f"[ManifestUpdate] IOError writing updated manifest to {manifest_output_path_str}: {e}"
            logger.error(error_msg, exc_info=True)
            state['error_message'] = error_msg # This node's specific error
            state['last_event_summary'] = "Error: Could not write updated manifest file."
            # Do not clear original_error_message_from_tweak here
            return state
        
        # 8. If manifest update is successful
        if manifest_update_successful:
            state['last_event_summary'] = "Goal Manifest updated successfully."
            # The manifest update itself was successful, so this node has no error.
            # The original_error_message_from_tweak should persist if it existed.
            state['error_message'] = original_error_message_from_tweak 


        # 9. Invoke Changelog Service
        if manifest_update_successful: # This check implies file was written
            changelog_summary = "Goal Manifest Updated"
            if task_had_error: # task_had_error refers to the tweak step
                # Include a sanitized version of the tweak error in changelog summary
                tweak_error_summary = (original_error_message_from_tweak or "Unknown error in previous step").splitlines()[0]
                changelog_summary += f" (with error in previous step: {tweak_error_summary})"
            
            try:
                # Pass the state that includes the original_error_message_from_tweak if it existed
                success_changelog = changelog_service.record_event_in_changelog(
                    current_workflow_state=state, # state still contains original error if tweak failed
                    preceding_event_summary=changelog_summary
                )
                if success_changelog:
                    logger.info("Successfully recorded manifest update in changelog.")
                    state['last_event_summary'] = "Goal Manifest updated and changelog entry added."
                    # If task_had_error, state['error_message'] still holds that original error.
                else:
                    error_msg_changelog = "[ManifestUpdate][ChangelogError] ChangelogService failed to record manifest update event."
                    logger.error(error_msg_changelog)
                    # Append to existing error_message (which might be the tweak error or None)
                    current_errors = state.get('error_message', "")
                    state['error_message'] = f"{current_errors} {error_msg_changelog}".strip() if current_errors else error_msg_changelog
                    state['last_event_summary'] = "Goal Manifest updated, but changelog recording failed."

            except Exception as e:
                error_msg_changelog_exc = f"[ManifestUpdate][ChangelogError] Exception during changelog service call for manifest update: {e}"
                logger.error(error_msg_changelog_exc, exc_info=True)
                current_errors = state.get('error_message', "")
                state['error_message'] = f"{current_errors} {error_msg_changelog_exc}".strip() if current_errors else error_msg_changelog_exc
                state['last_event_summary'] = "Goal Manifest updated, but changelog recording failed with an exception."

    except Exception as e:
        error_msg_unexpected = f"[ManifestUpdate] Unexpected error during manifest update: {e}"
        logger.error(error_msg_unexpected, exc_info=True)
        # Preserve original tweak error if this node had an unrelated crash
        if original_error_message_from_tweak and not state.get('error_message'):
            state['error_message'] = original_error_message_from_tweak + f" | Additionally, ManifestUpdate node failed: {error_msg_unexpected}"
        elif not state.get('error_message'): # If no specific error was set by this node yet
             state['error_message'] = error_msg_unexpected

        state['last_event_summary'] = f"Unexpected error in manifest update: {e}"
        if state.get('aider_last_exit_code') is None: # Aider not directly used here
            state['aider_last_exit_code'] = -1 

    return state

[end of poc-7-langgraph-aider/src/nodes/manifest_update.py]
