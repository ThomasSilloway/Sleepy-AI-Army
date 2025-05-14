"""Builds the LangGraph StateGraph for the PoC7 orchestrator."""
import logging
from langgraph.graph import StateGraph, END

from src.state import WorkflowState
from src.nodes import (
    initialize_workflow_node, 
    validate_inputs_node, 
    error_path_node, 
    success_path_node,
    generate_manifest_node # Import the new node
)

logger = logging.getLogger(__name__)

def build_graph() -> StateGraph:
    """
    Builds the LangGraph StateGraph for the PoC7 orchestrator.
    """
    graph_builder = StateGraph(WorkflowState)

    # Add nodes
    graph_builder.add_node("initialize_workflow", initialize_workflow_node)
    graph_builder.add_node("validate_inputs", validate_inputs_node)
    graph_builder.add_node("generate_manifest_node", generate_manifest_node) # Add new node
    graph_builder.add_node("error_path", error_path_node)
    graph_builder.add_node("success_path", success_path_node)

    # Set entry point
    graph_builder.set_entry_point("initialize_workflow")

    # Define conditional routing after initialization
    def route_after_initialization(state: WorkflowState):
        if state.get("error_message"):
            logger.error("[Graph] Routing to error_path due to error_message after initialization.")
            return "error_path"
        logger.info("[Graph] Initialization successful. Routing to validate_inputs.")
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
        logger.info("[Graph] Input validation successful. Routing to generate_manifest_node.")
        return "validation_succeeded" 

    graph_builder.add_conditional_edges(
        "validate_inputs",
        route_after_validation,
        {
            "error_path": "error_path",
            "validation_succeeded": "generate_manifest_node" # Route to manifest generation
        }
    )

    # Define conditional routing after manifest generation
    def route_after_manifest_generation(state: WorkflowState):
        if state.get("error_message"):
            logger.error("[Graph] Routing to error_path due to error_message after manifest generation.")
            return "error_path"
        logger.info("[Graph] Manifest generation successful. Routing to success_path.")
        return "manifest_generation_succeeded"

    graph_builder.add_conditional_edges(
        "generate_manifest_node",
        route_after_manifest_generation,
        {
            "error_path": "error_path",
            "manifest_generation_succeeded": "success_path" # Route to success on success
        }
    )

    # Add edges from terminal nodes to END
    graph_builder.add_edge("error_path", END)
    graph_builder.add_edge("success_path", END)
    
    return graph_builder
