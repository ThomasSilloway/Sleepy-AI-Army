"""Contains logic for the manifest_update_node."""
import logging
from datetime import datetime

from src.pydantic_models.core_schemas import ManifestData
from src.services.changelog_service import ChangelogService
from src.services.git_service import GitService
from src.services.write_file_from_template_service import WriteFileFromTemplateService
from src.state import WorkflowState

logger = logging.getLogger(__name__)

def manifest_update_node(state: WorkflowState, config) -> WorkflowState:
    """
    Updates the goal manifest by modifying the ManifestData object in the workflow state
    and then re-rendering the goal-manifest.md file from this updated state.
    Records the update event in the changelog.
    """
    state['current_step_name'] = "Update Manifest"
    logger.info(f"Executing node: {state['current_step_name']}")

    original_error_message_from_tweak = state.get('error_message')
    state['error_message'] = None # Clear for this node's execution

    try:
        services_config = config["configurable"]
        changelog_service: ChangelogService = services_config["changelog_service"]
        # Ensure WriteFileFromTemplateService is available in config
        write_file_service: WriteFileFromTemplateService = services_config.get("write_file_service")
        git_service: GitService = services_config.get("git_service")

        manifest_data : ManifestData = state.get('manifest_data')
        manifest_output_path_str = state.get('manifest_output_path')
        manifest_template_path_str = state.get('manifest_template_path') # Needed for re-rendering
        small_tweak_file_path = state.get('small_tweak_file_path')

        if not manifest_data:
            error_msg = "[ManifestUpdate] ManifestData not found in workflow state. Cannot update."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Manifest data missing for update."
            if original_error_message_from_tweak:
                 state['error_message'] = f"{original_error_message_from_tweak} | {error_msg}"
            return state

        if not all([manifest_output_path_str, manifest_template_path_str, small_tweak_file_path]):
            error_msg = "[ManifestUpdate] Critical path information missing: manifest_output_path, manifest_template_path, or small_tweak_file_path not found in state."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Missing critical path info for manifest update."
            if original_error_message_from_tweak:
                 state['error_message'] = f"{original_error_message_from_tweak} | {error_msg}"
            return state

        # Modify ManifestData instance directly
        logger.info("Updating ManifestData object in state.")

        # Update timestamp # TODO: Move the formatting to manifest data class since this is duplicated
        manifest_data.last_updated_timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        # Update overall status
        small_tweak_had_error = bool(original_error_message_from_tweak)
        manifest_data.overall_status = "Failed" if small_tweak_had_error else "Complete"
        logger.debug(f"Set ManifestData.overall_status to: {manifest_data.overall_status}")

        # Update artifact status
        artifact_updated = False
        for artifact in manifest_data.artifacts:
            if artifact.path == small_tweak_file_path:
                artifact.status = "[Error]" if small_tweak_had_error else "[Complete]" # More specific error status
                logger.debug(f"Updated artifact '{artifact.path}' status to '{artifact.status}' in ManifestData.")
                artifact_updated = True
                break
        if not artifact_updated:
            logger.warning(f"Could not find artifact for '{small_tweak_file_path}' in ManifestData to update its status.")
            # Optionally, add it if missing, or log as an inconsistency
            # For now, just log. If it's critical, an error could be raised.

        # Update AI questions
        if small_tweak_had_error:
            error_details = original_error_message_from_tweak
            ai_question = f"Error occurred during the automated task for '{small_tweak_file_path}'. Can you review it please?\n - Error details: {error_details}"
            if not manifest_data.ai_questions_list: # Ensure list exists
                manifest_data.ai_questions_list = []
            manifest_data.ai_questions_list.append(ai_question)
            logger.debug("Appended new error question to ManifestData.ai_questions_list.")
        else:
            logger.debug("No task error, ManifestData.ai_questions_list not changed.")

        # Store updated ManifestData back to state (it's mutable, so already updated, but good for clarity)
        state['manifest_data'] = manifest_data
        logger.info("ManifestData object updated in state.")

        # Re-render the manifest file using WriteFileFromTemplateService
        logger.info(f"Attempting to re-render and overwrite manifest file: {manifest_output_path_str}")
        template_context = {"manifest_data": manifest_data.model_dump()}

        try:
            success_write = write_file_service.render_and_write_file(
                template_abs_path_str=manifest_template_path_str,
                context=template_context,
                output_abs_path_str=manifest_output_path_str
            )
        except Exception as e:
            error_msg = f"[ManifestUpdate] Error during template re-rendering or file writing: {e}"
            logger.error(error_msg, exc_info=True)
            state['error_message'] = error_msg # This node's specific error
            state['last_event_summary'] = "Error: Failed to re-write updated manifest file."
            if original_error_message_from_tweak: # Preserve original error
                 state['error_message'] = f"{original_error_message_from_tweak} | {error_msg}"
            return state

        manifest_update_successful = success_write
        if manifest_update_successful:
            logger.info(f"Successfully re-rendered and wrote updated manifest to: {manifest_output_path_str}")
            state['last_event_summary'] = "Goal Manifest updated successfully by re-rendering."
            # Persist the original error message from the tweak step if it existed
            state['error_message'] = original_error_message_from_tweak
        else:
            error_msg = f"[ManifestUpdate] WriteFileFromTemplateService failed to re-write manifest to '{manifest_output_path_str}'."
            logger.error(error_msg)
            state['error_message'] = error_msg # This node's specific error
            state['last_event_summary'] = "Error: Failed to re-write manifest file (service reported failure)."
            if original_error_message_from_tweak: # Preserve original error
                 state['error_message'] = f"{original_error_message_from_tweak} | {error_msg}"
            return state # Stop if manifest re-writing failed

        # Invoke Changelog Service
        if manifest_update_successful:
            changelog_summary = "Goal Manifest updated after small tweak execution."
            if small_tweak_had_error:
                tweak_error_summary = (original_error_message_from_tweak or "Unknown error in previous step").splitlines()[0]
                changelog_summary += f" (reflecting error in previous step: {tweak_error_summary})"

            try:
                success_changelog = changelog_service.record_event_in_changelog(
                    current_workflow_state=state, # state contains original error if tweak failed
                    preceding_event_summary=changelog_summary
                )
                if success_changelog:
                    logger.info("Successfully recorded manifest update in changelog.")
                    state['last_event_summary'] = "Goal Manifest updated (re-rendered) and changelog entry added."
                    # state['error_message'] already holds original_error_message_from_tweak if any
                else:
                    error_msg_changelog = "[ManifestUpdate][ChangelogError] ChangelogService failed to record manifest update event."
                    logger.error(error_msg_changelog)
                    current_errors = state.get('error_message', "") # Could be original_error_message_from_tweak
                    state['error_message'] = f"{current_errors} {error_msg_changelog}".strip() if current_errors else error_msg_changelog
                    state['last_event_summary'] = "Goal Manifest updated (re-rendered), but changelog recording failed."

            except Exception as e:
                error_msg_changelog_exc = f"[ManifestUpdate][ChangelogError] Exception during changelog service call for manifest update: {e}"
                logger.error(error_msg_changelog_exc, exc_info=True)
                current_errors = state.get('error_message', "") # Could be original_error_message_from_tweak
                state['error_message'] = f"{current_errors} {error_msg_changelog_exc}".strip() if current_errors else error_msg_changelog_exc
                state['last_event_summary'] = "Goal Manifest updated (re-rendered), but changelog recording failed with an exception."

            # Attempt to commit changes
            commit_message = f"AI Army Man - Updated goal manifest for: {manifest_data.goal_title}"
            logger.info(f"Attempting to commit changes with message: '{commit_message}'")
            try:
                commit_success = git_service.commit_changes(commit_message)
                if commit_success:
                    logger.info("Successfully committed manifest and changelog changes.")
                else:
                    logger.error("Failed to commit manifest and changelog changes.")
                    state['last_event_summary'] += ", but git commit failed."
            except Exception as e:
                logger.error(f"Error during git commit: {e}", exc_info=True)
                state['last_event_summary'] += f", but git commit failed: {e}"

    except Exception as e:
        error_msg_unexpected = f"[ManifestUpdate] Unexpected error during manifest update: {e}"
        logger.error(error_msg_unexpected, exc_info=True)

        current_node_error = state.get('error_message') # Error set by this node before unexpected crash
        if original_error_message_from_tweak:
            if current_node_error: # If this node already set an error, append unexpected
                 state['error_message'] = f"{original_error_message_from_tweak} | {current_node_error} | Unexpected: {error_msg_unexpected}"
            else: # If this node hadn't set an error yet, combine original and unexpected
                 state['error_message'] = f"{original_error_message_from_tweak} | Unexpected: {error_msg_unexpected}"
        elif current_node_error: # No original error, but this node set one
            state['error_message'] = f"{current_node_error} | Unexpected: {error_msg_unexpected}"
        else: # No original error, no error set by this node before crash
            state['error_message'] = error_msg_unexpected

        state['last_event_summary'] = f"Unexpected error in manifest update: {e}"
        if state.get('aider_last_exit_code') is None:
            state['aider_last_exit_code'] = -1

    return state
