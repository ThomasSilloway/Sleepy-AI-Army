"""Builds the LangGraph StateGraph for the PoC7 orchestrator."""
import logging

from langgraph.graph import END, StateGraph

from src.nodes import (
    error_path_node,
    execute_small_tweak_node,
    manifest_create_node,
    initialize_workflow_node,
    manifest_update_node, # Add this
    success_path_node,
    validate_inputs_node,
)
from src.state import WorkflowState

logger = logging.getLogger(__name__)

def build_graph() -> StateGraph:
    """
    Builds the LangGraph StateGraph for the PoC7 orchestrator.
    """
    graph_builder = StateGraph(WorkflowState)

    # Add nodes
    graph_builder.add_node("initialize_workflow", initialize_workflow_node)
    graph_builder.add_node("validate_inputs", validate_inputs_node)
    graph_builder.add_node("manifest_create_node", manifest_create_node)
    graph_builder.add_node("execute_small_tweak", execute_small_tweak_node)
    graph_builder.add_node("manifest_update_node", manifest_update_node) # Add this
    graph_builder.add_node("error_path", error_path_node)
    graph_builder.add_node("success_path", success_path_node)

    # Set entry point
    graph_builder.set_entry_point("initialize_workflow")

    # Define conditional routing after initialization
    def route_after_initialization(state: WorkflowState):
        if state.get("error_message"):
            logger.error("[Graph] Routing to error_path due to error_message after initialization.")
            return "error_path"
        logger.overview("[Graph] Initialization successful. Routing to validate_inputs.")
        return "validate_inputs" 

    graph_builder.add_conditional_edges(
        "initialize_workflow",
        route_after_initialization,
        {
            "error_path": "error_path",
            "validate_inputs": "validate_inputs"
        }
    )

    # Define conditional routing after validation
    def route_after_validation(state: WorkflowState):
        if state.get("error_message"):
            logger.error("[Graph] Routing to error_path due to error_message after validation.")
            return "error_path"
        logger.overview("[Graph] Input validation successful. Routing to manifest_create_node.") # Updated log and target
        return "validation_succeeded" 

    graph_builder.add_conditional_edges(
        "validate_inputs",
        route_after_validation,
        {
            "error_path": "error_path",
            "validation_succeeded": "manifest_create_node" # Updated target node
        }
    )

    # Define conditional routing after manifest generation
    def route_after_manifest_generation(state: WorkflowState):
        if state.get("error_message"):
            logger.error("[Graph] Routing to error_path due to error_message after manifest creation.") # Updated log
            return "error_path"
        logger.overview("[Graph] Manifest creation successful. Routing to execute_small_tweak.") # Updated log
        # Route to execute_small_tweak instead of success_path
        return "manifest_generation_succeeded" 

    graph_builder.add_conditional_edges(
        "manifest_create_node", # Updated source node
        route_after_manifest_generation,
        {
            "error_path": "error_path",
            "manifest_generation_succeeded": "execute_small_tweak" 
            # "manifest_generation_succeeded": "success_path" 
        }
    )

    # Define conditional routing after small tweak execution
    def route_after_small_tweak(state: WorkflowState):
        # No longer check for error_message here to decide path,
        # manifest_update_node will handle it.
        logger.overview("[Graph] Small tweak execution finished. Routing to manifest_update_node.")
        return "manifest_update_node" # Always go to manifest_update_node

    graph_builder.add_conditional_edges(
        "execute_small_tweak",
        route_after_small_tweak,
        {
            "manifest_update_node": "manifest_update_node" # Add this unique target
        }
    )

    # Define conditional routing after manifest update
    def route_after_manifest_update(state: WorkflowState):
        # Check if error_message is set AND if the error is specifically from manifest_update_node.
        # The manifest_update_node is designed to preserve error_message from previous steps (like tweak_execution)
        # if the manifest_update_node itself succeeds.
        # So, we only route to error_path if manifest_update_node itself failed.
        # A simple way to check this is to look for a specific phrase in last_event_summary
        # that manifest_update_node would set upon its own failure.
        # Or, if manifest_update_node clears error_message at its start and only sets it upon its own failure.
        # Based on manifest_update_node's logic, it sets its own error_message if it fails.
        # It also preserves the error from the tweak node.
        # We need to distinguish if the error is from the manifest_update step or a prior step.
        # For now, let's assume if error_message is present, and last_event_summary indicates manifest update failure.
        
        # A more robust check might involve manifest_update_node setting a specific flag or error type.
        # The current manifest_update_node sets state['last_event_summary'] to something like "Error: Could not write updated manifest file."
        # if it fails to write.
        if state.get("error_message"):
            # Check if the error is due to manifest update failure specifically
            # The manifest_update_node sets specific error messages for its own failures.
            # For example, "[ManifestUpdate] Critical information missing", "[ManifestUpdate] Manifest file not found"
            # "[ManifestUpdate] IOError reading manifest file", "[ManifestUpdate] IOError writing updated manifest"
            # "[ManifestUpdate][ChangelogError]"
            # If the error_message contains these prefixes, it's likely from manifest_update itself.
            # Or check `current_step_name` if it was updated by manifest_update and then an error occurred.
            # The prompt suggests checking `state.get("last_event_summary", "")`
            # Let's use the prompt's condition.
            last_event_summary = state.get("last_event_summary", "")
            if "Manifest update failed" in last_event_summary or \
               "Could not write updated manifest" in last_event_summary or \
               "Changelog recording failed" in last_event_summary or \
               (state.get("current_step_name") == "Update Manifest" and state.get("error_message")): # Generic check if error is from current manifest update step
                logger.error(f"[Graph] Routing to error_path due to error_message after manifest update: {state.get('error_message')}")
                return "error_path"
            
            # If there's an error_message but it's not from manifest_update_node, it means a previous node (e.g., tweak) failed,
            # but manifest_update_node itself succeeded in processing/logging that. In this case, we go to success_path
            # as the workflow up to manifest update (which handles errors) completed.
            logger.info(f"[Graph] Manifest update node completed (possibly handling a previous error: {state.get('error_message')}). Routing to success_path.")
            return "success_path"
        
        logger.overview("[Graph] Manifest update successful. Routing to success_path.")
        return "success_path"

    graph_builder.add_conditional_edges(
        "manifest_update_node",
        route_after_manifest_update,
        {
            "error_path": "error_path",
            "success_path": "success_path"
        }
    )

    # Add edges from terminal nodes to END
    graph_builder.add_edge("error_path", END)
    graph_builder.add_edge("success_path", END)

    return graph_builder
