"""Contains logic for the generate_manifest_node."""
import logging
import os
from pathlib import Path

from src.state import WorkflowState
from src.config import AppConfig
from src.services.aider_service import AiderService
from src.services.changelog_service import ChangelogService

logger = logging.getLogger(__name__)

def generate_manifest_node(state: WorkflowState, config) -> WorkflowState:
    """
    Generates the goal manifest file using AiderService based on the task
    description and templates. Records the event in the changelog upon success.
    Updates WorkflowState with the outcome.
    """
    state['current_step_name'] = "generate_manifest_node"
    logger.info(f"Executing node: {state['current_step_name']}")

    try:
        services_config = config["configurable"]
        app_config: AppConfig = services_config["app_config"]
        changelog_service: ChangelogService = services_config["changelog_service"]

        task_description_content = state.get('task_description_content')
        manifest_template_path_str = state.get('manifest_template_path')
        manifest_output_path_str = state.get('manifest_output_path')

        if not all([task_description_content, manifest_template_path_str, manifest_output_path_str]):
            error_msg = "[ManifestGeneration] Critical information missing in state for manifest generation (task_description_content, manifest_template_path, or manifest_output_path)."
            logger.error(error_msg)
            state['error_message'] = error_msg
            state['last_event_summary'] = "Error: Missing critical info for manifest generation."
            state['is_manifest_generated'] = False
            return state
        
        # TODO Generate the manifest
        # TODO Record the changelog entry

    except Exception as e:
        error_msg = f"[ManifestGeneration] Unexpected error during manifest generation: {e}"
        logger.error(error_msg, exc_info=True)
        state['is_manifest_generated'] = False
        state['error_message'] = error_msg
        state['last_event_summary'] = f"Unexpected error: {e}"
        # Ensure aider_last_exit_code is set if exception occurs before aider call or if it's not set by aider_service
        if state.get('aider_last_exit_code') is None:
            state['aider_last_exit_code'] = -1 # Generic error code

    return state
