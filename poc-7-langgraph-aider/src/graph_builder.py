"""Builds the LangGraph StateGraph for the PoC7 orchestrator."""
import logging

from langgraph.graph import END, StateGraph

from src.nodes import (
    error_path_node,
    execute_small_tweak_node,
    initialize_workflow_node,
    manifest_create_node,
    manifest_update_node,  # Add this
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
    graph_builder.add_node("manifest_update_node", manifest_update_node)
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

        if state.get("error_message"):
            logger.error("[Graph] Routing to error_path due to error_message after manifest update.")
            return "error_path"

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
