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

def _route_after_node(state: WorkflowState, next_node_name: str):
    if state.get("error_message"):
        logger.error(f"[Graph] Routing to error_path due to error_message after {state.get('current_step_name')}.")
        return "error_path"
    logger.overview(f"[Graph] {state.get('current_step_name')} successful. Routing to {next_node_name}.")
    return next_node_name

# Define conditional routing after initialization
def route_after_initialization(state: WorkflowState):
    return _route_after_node(state, "validate_inputs")

# Define conditional routing after validation
def route_after_validation(state: WorkflowState):
    return _route_after_node(state, "manifest_create_node")

# Define conditional routing after manifest generation
def route_after_manifest_generation(state: WorkflowState):
    return _route_after_node(state, "execute_small_tweak")

# Define conditional routing after small tweak execution
def route_after_small_tweak(state: WorkflowState):
    # No longer check for error_message here to decide path,
    # manifest_update_node will handle it.
    logger.overview("[Graph] Small tweak execution finished. Routing to manifest_update_node.")
    return "manifest_update_node" # Always go to manifest_update_node

def route_after_manifest_update(state: WorkflowState):
    return _route_after_node(state, "success_path")

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

    # Add conditional edges and the functions to call
    graph_builder.add_conditional_edges("initialize_workflow", route_after_initialization)
    graph_builder.add_conditional_edges("validate_inputs", route_after_validation)
    graph_builder.add_conditional_edges("manifest_create_node", route_after_manifest_generation)
    graph_builder.add_conditional_edges("execute_small_tweak", route_after_small_tweak)
    graph_builder.add_conditional_edges("manifest_update_node", route_after_manifest_update)

    # Add edges from terminal nodes to END
    graph_builder.add_edge("error_path", END)
    graph_builder.add_edge("success_path", END)

    return graph_builder
