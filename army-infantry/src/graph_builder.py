import logging

from langgraph.graph import END, StateGraph

from .graph_state import WorkflowState
from .nodes import error_handling_node
from .nodes.code_modification import code_modification_node
from .nodes.git_branch import git_branch_node
from .nodes.git_checkout_original_branch import git_checkout_original_branch_node
from .nodes.initialize_mission import initialize_mission_node
from .nodes.mission_reporting import mission_reporting_node

logger = logging.getLogger(__name__)

# Define node names as constants for clarity
INITIALIZE_MISSION = "initialize_mission"
GIT_BRANCH = "git_branch"
CODE_MODIFICATION = "code_modification"
MISSION_REPORTING = "mission_reporting"
GIT_CHECKOUT_ORIGINAL_BRANCH = "git_checkout_original_branch"
ERROR_HANDLER = "error_handler"

class RoutingLogic:
    """
    Encapsulates the routing logic for the graph.
    """
    def _route_conditional(self, state: WorkflowState, next_node_on_success: str):
        if state.get("critical_error_message"):
            logger.error(f"Routing to {ERROR_HANDLER} due to critical_error_message from {state.get('current_step_name')}")
            return ERROR_HANDLER
        logger.info(f"Routing from {state.get('current_step_name')} to {next_node_on_success}")
        return next_node_on_success

    def after_initialize_mission(self, state: WorkflowState):
        return self._route_conditional(state, GIT_BRANCH)

    def after_git_branch(self, state: WorkflowState):
        return self._route_conditional(state, CODE_MODIFICATION)

    def after_code_modification(self, state: WorkflowState):
        return self._route_conditional(state, MISSION_REPORTING)

    def after_mission_reporting(self, state: WorkflowState):
        # This is the last main step in the happy path before cleanup or end
        return self._route_conditional(state, GIT_CHECKOUT_ORIGINAL_BRANCH)

    def after_git_checkout_original_branch(self, state: WorkflowState):
        return self._route_conditional(state, END)


def build_graph() -> StateGraph:
    """
    Builds the LangGraph StateGraph for the army-infantry agent.
    """
    graph_builder = StateGraph(WorkflowState)
    routing_logic = RoutingLogic()

    # Add nodes
    graph_builder.add_node(INITIALIZE_MISSION, initialize_mission_node)
    graph_builder.add_node(GIT_BRANCH, git_branch_node)
    graph_builder.add_node(CODE_MODIFICATION, code_modification_node)
    graph_builder.add_node(MISSION_REPORTING, mission_reporting_node)
    graph_builder.add_node(GIT_CHECKOUT_ORIGINAL_BRANCH, git_checkout_original_branch_node)
    graph_builder.add_node(ERROR_HANDLER, error_handling_node)

    # Set entry point
    graph_builder.set_entry_point(INITIALIZE_MISSION)

    # Add conditional edges
    graph_builder.add_conditional_edges(INITIALIZE_MISSION, routing_logic.after_initialize_mission)
    graph_builder.add_conditional_edges(GIT_BRANCH, routing_logic.after_git_branch)
    graph_builder.add_conditional_edges(CODE_MODIFICATION, routing_logic.after_code_modification)
    graph_builder.add_conditional_edges(MISSION_REPORTING, routing_logic.after_mission_reporting)
    graph_builder.add_conditional_edges(GIT_CHECKOUT_ORIGINAL_BRANCH, routing_logic.after_git_checkout_original_branch)

    # Add edge from terminal error node to END
    graph_builder.add_edge(ERROR_HANDLER, END)

    return graph_builder.compile()
