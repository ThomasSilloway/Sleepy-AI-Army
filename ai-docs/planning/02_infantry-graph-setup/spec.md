# Technical Specification: `army-infantry` Graph Scaffolding

## 1. Problem

The `army-infantry` project requires a foundational graph structure to orchestrate its tasks. This involves defining a graph builder and a corresponding graph state (`WorkflowState`). A key requirement is for the `WorkflowState` to be significantly leaner and more focused than the one used in the `army-man-small-tweak` project, which serves as a structural template. This initial scaffolding will include five specific nodes: `code-modification`, `git-branch`, `git-checkout-original-branch`, `initialize-mission`, and `mission-reporting`. Each of these nodes will initially only contain a Python logging statement to indicate its execution. The overall goal is to establish a robust and maintainable LangGraph-based workflow foundation that aligns with the "Lean & Focused WorkflowState" philosophy outlined in the project's design considerations.

## 2. Solution

The solution is based entirely on the "A+ Enhanced Solution" detailed in `ai-docs/planning/02_infantry-graph-setup/critique.md`.

### 2.1. Graph State (`army-infantry/src/graph_state.py`)

This file will define the state objects for the LangGraph workflow.

*   **`StructuredError(BaseModel)`:** A Pydantic model to represent errors in a structured way.
    ```python
    from typing import Optional, List, Dict, Any, TypedDict
    from pydantic import BaseModel, Field
    import datetime # Ensure datetime is imported

    class StructuredError(BaseModel):
        node_name: str
        message: str
        details: Optional[Dict[str, Any]] = None
        timestamp: str # ISO format timestamp
    ```

*   **`MissionContext(BaseModel)`:** A Pydantic model holding all mission-specific data. It is designed to be "frozen" to encourage immutable update patterns (nodes create copies with updates).
    ```python
    class MissionContext(BaseModel):
        # Core Identifiers (populated once at workflow start from AppConfig/CLI)
        mission_id: str
        mission_folder_path: str 
        project_git_root: str
        
        # Loaded from mission-spec.md
        mission_spec_content: Optional[str] = None 
        
        # Fields directly mapping to mission-report.md sections
        mission_title: Optional[str] = None
        final_status: Optional[str] = None # SUCCESS, FAILURE, BLOCKED
        execution_summary: Optional[str] = None
        files_modified_created: List[str] = Field(default_factory=list)
        git_summary: List[str] = Field(default_factory=list) # list of "hash - message"
        total_cost_usd: float = 0.0
        report_timestamp: Optional[str] = None # Timestamp for the report generation

        # Operational data & structured errors
        mission_errors: List[StructuredError] = Field(default_factory=list)
        
        class Config:
            frozen: bool = True
    ```

*   **`WorkflowState(TypedDict)`:** The actual state object for LangGraph. It is kept extremely lean.
    ```python
    class WorkflowState(TypedDict):
        mission_context: MissionContext 
        current_step_name: Optional[str] # Name of the current/last executed node
        critical_error_message: Optional[str] # For immediate routing/critical failure
    ```
    The `WorkflowState` primarily holds the `MissionContext` (which contains the bulk of the data) and essential flow control variables. Node implementations should practice immutable-style updates for `MissionContext` by using its `.copy(update={...})` method.

### 2.2. Graph Builder (`army-infantry/src/graph_builder.py`)

This file will define how the `StateGraph` is constructed.

*   It will import `StateGraph`, `END` from `langgraph.graph`, all defined node functions, and `WorkflowState` from `graph_state.py`.
*   A `build_graph()` function will be the main entry point for creating the graph instance.
*   Inside `build_graph()`:
    *   An instance of `StateGraph(WorkflowState)` will be created.
    *   Nodes will be added using `graph_builder.add_node("node_name", node_function)`. The planned nodes are:
        *   `initialize_mission_node` (from `src.nodes.initialize-mission.node`)
        *   `git_branch_node` (from `src.nodes.git-branch.node`)
        *   `code_modification_node` (from `src.nodes.code-modification.node`)
        *   `mission_reporting_node` (from `src.nodes.mission-reporting.node`)
        *   `git_checkout_original_branch_node` (from `src.nodes.git-checkout-original-branch.node`)
        *   An `error_node` (placeholder for handling critical errors)
    *   A `RoutingLogic` class (similar to `army-man-small-tweak`) will be defined with methods to determine transitions. Initially, these methods can define a simple linear flow or placeholder logic. Routing will primarily check `state.get("critical_error_message")` for diversions to the `error_node`.
    *   The entry point will be set using `graph_builder.set_entry_point("initialize_mission_node")`.
    *   Conditional edges will be added using `graph_builder.add_conditional_edges(...)` linking the nodes based on the `RoutingLogic`.
    *   Terminal edges from `mission_reporting_node` (on success) and `error_node` (on failure) to `END` will be added using `graph_builder.add_edge(...)`.

### 2.3. Node Implementations (Initial Logging)

Five new node modules will be created in `army-infantry/src/nodes/`:

*   `army-infantry/src/nodes/initialize-mission/`
    *   `node.py`:
        ```python
        import logging
        from ...graph_state import WorkflowState, MissionContext # Adjust import as per final structure

        logger = logging.getLogger(__name__)

        async def initialize_mission_node(state: WorkflowState) -> WorkflowState:
            logger.info("Executing initialize_mission_node")
            # Example of updating state (current_step_name and immutable MissionContext update)
            # current_context = state['mission_context']
            # new_context = current_context.copy(update={}) # No actual change yet
            # return {
            #     "mission_context": new_context,
            #     "current_step_name": "initialize_mission_node",
            #     "critical_error_message": state.get("critical_error_message")
            # }
            # For initial scaffolding, just updating current_step_name is sufficient
            return {**state, "current_step_name": "initialize_mission_node"}

        ```
    *   `__init__.py`: `from .node import initialize_mission_node`

*   `army-infantry/src/nodes/code-modification/`
    *   `node.py`:
        ```python
        import logging
        from ...graph_state import WorkflowState # Adjust import

        logger = logging.getLogger(__name__)

        async def code_modification_node(state: WorkflowState) -> WorkflowState:
            logger.info("Executing code_modification_node")
            return {**state, "current_step_name": "code_modification_node"}
        ```
    *   `__init__.py`: `from .node import code_modification_node`

*   `army-infantry/src/nodes/git-branch/`
    *   `node.py`:
        ```python
        import logging
        from ...graph_state import WorkflowState # Adjust import

        logger = logging.getLogger(__name__)

        async def git_branch_node(state: WorkflowState) -> WorkflowState:
            logger.info("Executing git_branch_node")
            return {**state, "current_step_name": "git_branch_node"}
        ```
    *   `__init__.py`: `from .node import git_branch_node`

*   `army-infantry/src/nodes/git-checkout-original-branch/`
    *   `node.py`:
        ```python
        import logging
        from ...graph_state import WorkflowState # Adjust import

        logger = logging.getLogger(__name__)

        async def git_checkout_original_branch_node(state: WorkflowState) -> WorkflowState:
            logger.info("Executing git_checkout_original_branch_node")
            return {**state, "current_step_name": "git_checkout_original_branch_node"}
        ```
    *   `__init__.py`: `from .node import git_checkout_original_branch_node`

*   `army-infantry/src/nodes/mission-reporting/`
    *   `node.py`:
        ```python
        import logging
        from ...graph_state import WorkflowState # Adjust import

        logger = logging.getLogger(__name__)

        async def mission_reporting_node(state: WorkflowState) -> WorkflowState:
            logger.info("Executing mission_reporting_node")
            return {**state, "current_step_name": "mission_reporting_node"}
        ```
    *   `__init__.py`: `from .node import mission_reporting_node`

All node functions will be `async def`, accept `state: WorkflowState` as input, and return the (potentially modified) `WorkflowState` dictionary. The initial modification will be to update `current_step_name`.

## 3. High-Level Implementation Plan (SPR)

1.  **Directory Structure:**
    *   Create `army-infantry/src/`.
    *   Create `army-infantry/src/nodes/`.
    *   Create `army-infantry/src/nodes/initialize-mission/`.
    *   Create `army-infantry/src/nodes/code-modification/`.
    *   Create `army-infantry/src/nodes/git-branch/`.
    *   Create `army-infantry/src/nodes/git-checkout-original-branch/`.
    *   Create `army-infantry/src/nodes/mission-reporting/`.

2.  **`graph_state.py`:**
    *   Create `army-infantry/src/graph_state.py`.
    *   Define `StructuredError(BaseModel)`.
    *   Define `MissionContext(BaseModel)` with `frozen=True` in `Config`.
    *   Define `WorkflowState(TypedDict)`.
    *   Include necessary imports (`typing`, `pydantic`, `datetime`).

3.  **Node: `initialize-mission`**
    *   Create `army-infantry/src/nodes/initialize-mission/node.py`.
        *   Implement `async def initialize_mission_node(state: WorkflowState) -> WorkflowState:`.
        *   Add `logger.info("Executing initialize_mission_node")`.
        *   Return ` {**state, "current_step_name": "initialize_mission_node"}`.
    *   Create `army-infantry/src/nodes/initialize-mission/__init__.py`.
        *   Add `from .node import initialize_mission_node`.

4.  **Node: `code-modification`**
    *   Create `army-infantry/src/nodes/code-modification/node.py`.
        *   Implement `async def code_modification_node(state: WorkflowState) -> WorkflowState:`.
        *   Add `logger.info("Executing code_modification_node")`.
        *   Return ` {**state, "current_step_name": "code_modification_node"}`.
    *   Create `army-infantry/src/nodes/code-modification/__init__.py`.
        *   Add `from .node import code_modification_node`.

5.  **Node: `git-branch`**
    *   Create `army-infantry/src/nodes/git-branch/node.py`.
        *   Implement `async def git_branch_node(state: WorkflowState) -> WorkflowState:`.
        *   Add `logger.info("Executing git_branch_node")`.
        *   Return ` {**state, "current_step_name": "git_branch_node"}`.
    *   Create `army-infantry/src/nodes/git-branch/__init__.py`.
        *   Add `from .node import git_branch_node`.

6.  **Node: `git-checkout-original-branch`**
    *   Create `army-infantry/src/nodes/git-checkout-original-branch/node.py`.
        *   Implement `async def git_checkout_original_branch_node(state: WorkflowState) -> WorkflowState:`.
        *   Add `logger.info("Executing git_checkout_original_branch_node")`.
        *   Return ` {**state, "current_step_name": "git_checkout_original_branch_node"}`.
    *   Create `army-infantry/src/nodes/git-checkout-original-branch/__init__.py`.
        *   Add `from .node import git_checkout_original_branch_node`.

7.  **Node: `mission-reporting`**
    *   Create `army-infantry/src/nodes/mission-reporting/node.py`.
        *   Implement `async def mission_reporting_node(state: WorkflowState) -> WorkflowState:`.
        *   Add `logger.info("Executing mission_reporting_node")`.
        *   Return ` {**state, "current_step_name": "mission_reporting_node"}`.
    *   Create `army-infantry/src/nodes/mission-reporting/__init__.py`.
        *   Add `from .node import mission_reporting_node`.
    
8.  **Placeholder `error_node` (Optional but Recommended for `graph_builder`)**
    *   Create `army-infantry/src/nodes/error_node.py` (or similar, can be a simple file for now).
        *   Implement `async def error_node(state: WorkflowState) -> WorkflowState:`.
        *   Add `logger.error(f"Critical error encountered: {state.get('critical_error_message')}")`.
        *   Return state.
    *   Update `army-infantry/src/nodes/__init__.py` to export it if placed in a separate file.

9.  **`graph_builder.py`:**
    *   Create `army-infantry/src/graph_builder.py`.
    *   Import `StateGraph`, `END` from `langgraph.graph`.
    *   Import `WorkflowState` from `.graph_state`.
    *   Import node functions:
        *   `from .nodes.initialize-mission import initialize_mission_node`
        *   `from .nodes.code-modification import code_modification_node`
        *   `from .nodes.git-branch import git_branch_node`
        *   `from .nodes.git-checkout-original-branch import git_checkout_original_branch_node`
        *   `from .nodes.mission-reporting import mission_reporting_node`
        *   (Import `error_node` if created)
    *   Define `class RoutingLogic:` (or functional equivalents for routing).
        *   Initial methods can define a linear flow:
            *   `initialize_mission_node` -> `git_branch_node`
            *   `git_branch_node` -> `code_modification_node`
            *   `code_modification_node` -> `mission_reporting_node`
            *   `mission_reporting_node` -> `git_checkout_original_branch_node` (or END, depending on desired final state)
            *   `git_checkout_original_branch_node` -> `END`
        *   Each routing method checks `state.get("critical_error_message")` and routes to `"error_node"` if set, otherwise proceeds to the next logical node.
    *   Define `def build_graph() -> StateGraph:`.
        *   Instantiate `graph_builder = StateGraph(WorkflowState)`.
        *   Add all nodes: `initialize_mission_node`, `code_modification_node`, `git_branch_node`, `git_checkout_original_branch_node`, `mission_reporting_node`, `error_node`.
        *   Set entry point: `graph_builder.set_entry_point("initialize_mission_node")`.
        *   Add conditional edges using `RoutingLogic` instance.
        *   Add edge from `error_node` to `END`.
        *   (Adjust terminal edges based on final node in happy path, e.g., `mission_reporting_node` or `git_checkout_original_branch_node` to `END`).
    *   Return `graph_builder.compile()`.

10. **Root `__init__.py` files:**
    *   Ensure `army-infantry/src/__init__.py` exists.
    *   Ensure `army-infantry/src/nodes/__init__.py` exists (and can be used to simplify imports in `graph_builder.py`, e.g. `from .nodes import initialize_mission_node`).

```
