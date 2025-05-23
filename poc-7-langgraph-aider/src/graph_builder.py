"""Builds the LangGraph StateGraph for the PoC7 orchestrator."""
import logging

from langgraph.graph import END, StateGraph

from src.nodes import (
    error_path_node,
    execute_small_tweak_node,
    generate_manifest_node,
    initialize_workflow_node,
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
    graph_builder.add_node("generate_manifest_node", generate_manifest_node)
    graph_builder.add_node("execute_small_tweak", execute_small_tweak_node) 
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
        logger.overview("[Graph] Input validation successful. Routing to generate_manifest_node.")
        return "validation_succeeded" 

    graph_builder.add_conditional_edges(
        "validate_inputs",
        route_after_validation,
        {
            "error_path": "error_path",
            "validation_succeeded": "generate_manifest_node" 
        }
    )

    # Define conditional routing after manifest generation
    def route_after_manifest_generation(state: WorkflowState):
        if state.get("error_message"):
            logger.error("[Graph] Routing to error_path due to error_message after manifest generation.")
            return "error_path"
        logger.overview("[Graph] Manifest generation successful. Routing to execute_small_tweak.")
        # Route to execute_small_tweak instead of success_path
        return "manifest_generation_succeeded" 

    graph_builder.add_conditional_edges(
        "generate_manifest_node",
        route_after_manifest_generation,
        {
            "error_path": "error_path",
            "manifest_generation_succeeded": "execute_small_tweak" 
            # "manifest_generation_succeeded": "success_path" 
        }
    )

    # Define conditional routing after small tweak execution
    def route_after_small_tweak(state: WorkflowState):
        if state.get("error_message"):
            logger.error("[Graph] Routing to error_path due to error_message after small tweak execution.")
            return "error_path"
        logger.overview("[Graph] Small tweak execution successful. Routing to success_path.")
        return "tweak_execution_succeeded"

    graph_builder.add_conditional_edges(
        "execute_small_tweak",
        route_after_small_tweak,
        {
            "error_path": "error_path",
            "tweak_execution_succeeded": "success_path" # Route to success on success
        }
    )

    # Add edges from terminal nodes to END
    graph_builder.add_edge("error_path", END)
    graph_builder.add_edge("success_path", END)

    return graph_builder
