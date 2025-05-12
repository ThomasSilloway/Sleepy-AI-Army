"""Builds the LangGraph StateGraph for the PoC7 orchestrator."""
import logging
from langgraph.graph import StateGraph, END

from src.state import WorkflowState
from src.nodes import initialize_workflow_node, validate_inputs_node, error_path_node, success_path_node

logger = logging.getLogger(__name__)

def build_graph() -> StateGraph:
    """
    Builds the LangGraph StateGraph for the PoC7 orchestrator.
    """
    graph_builder = StateGraph(WorkflowState)

    # Add nodes
    graph_builder.add_node("initialize_workflow", initialize_workflow_node)
    graph_builder.add_node("validate_inputs", validate_inputs_node)
    graph_builder.add_node("error_path", error_path_node)
    graph_builder.add_node("success_path", success_path_node)

    # Set entry point
    graph_builder.set_entry_point("initialize_workflow")

    # Define conditional routing after initialization
    def route_after_initialization(state: WorkflowState):
        if state.get("error_message"):
            logger.error("[Workflow] Routing to error_path due to error_message after initialization.")
            return "error_path"
        logger.info("[Workflow] Initialization successful. Routing to validate_inputs.")
        return "validate_inputs" # Route key for success

    graph_builder.add_conditional_edges(
        "initialize_workflow",
        route_after_initialization,
        {
            "error_path": "error_path",
            "validate_inputs": "validate_inputs" # Map success key to validate_inputs node
        }
    )

    # Define conditional routing after validation
    def route_after_validation(state: WorkflowState):
        if state.get("error_message"):
            logger.error("[Workflow] Routing to error_path due to error_message after validation.")
            return "error_path"
        logger.info("[Workflow] Input validation successful. Routing to success_path.")
        return "validation_succeeded" # Route key for success

    graph_builder.add_conditional_edges(
        "validate_inputs",
        route_after_validation,
        {
            "error_path": "error_path",
            "validation_succeeded": "success_path" # Map success key to success_path node
        }
    )

    # Add edges from terminal nodes to END
    graph_builder.add_edge("error_path", END)
    graph_builder.add_edge("success_path", END)
    
    return graph_builder
