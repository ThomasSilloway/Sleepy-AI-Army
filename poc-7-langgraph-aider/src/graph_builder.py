"""Builds the LangGraph StateGraph for the PoC7 orchestrator."""
import logging
from langgraph.graph import StateGraph, END

from src.state import WorkflowState
from src.nodes import initialize_workflow_node, error_path_node, success_path_node

logger = logging.getLogger(__name__)

def build_graph() -> StateGraph:
    """
    Builds the LangGraph StateGraph for the PoC7 orchestrator.
    """
    graph_builder = StateGraph(WorkflowState)

    # Add nodes
    graph_builder.add_node("initialize_workflow", initialize_workflow_node)
    graph_builder.add_node("error_path", error_path_node)
    graph_builder.add_node("success_path", success_path_node) # Placeholder for now

    # Set entry point
    graph_builder.set_entry_point("initialize_workflow")

    # Define conditional routing after initialization
    def route_after_initialization(state: WorkflowState):
        if state.get("error_message"):
            logger.error("Routing to error_path due to error_message in state.")
            return "error_path"
        logger.debug("[Workflow] Routing to success_path after successful initialization.")
        return "success_path"

    graph_builder.add_conditional_edges(
        "initialize_workflow",
        route_after_initialization,
        {
            "error_path": "error_path",
            "success_path": "success_path" # This will lead to more nodes later
        }
    )

    # Add edges from placeholder terminal nodes to END
    graph_builder.add_edge("error_path", END)
    graph_builder.add_edge("success_path", END) # For now, success_path also ends. This will change.
    
    return graph_builder
