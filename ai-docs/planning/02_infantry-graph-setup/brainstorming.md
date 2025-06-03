# Brainstorming: `army-infantry` Graph and State Management

This document outlines the analysis of the existing `army-man-small-tweak` codebase and brainstorms solutions for the `army-infantry` project's graph builder and `WorkflowState`, along with radically different approaches to workflow orchestration.

## 1. Analysis of `army-man-small-tweak` Code

### 1.1. `army-man-small-tweak/src/graph_builder.py`

*   **Purpose:** This file defines the structure and flow of a task-oriented workflow using the `langgraph` library. It sets up a state machine where each state (node) performs a specific action, and transitions between states are determined by routing logic.
*   **Graph Definition:**
    *   **Nodes:** Functions imported from `src.nodes` (e.g., `initialize_workflow_node`, `execute_small_tweak_node`). Includes terminal nodes like `error_path_node` and `success_path_node`.
    *   **Edges:** Define transitions between nodes, mostly conditional, managed by the `RoutingLogic` class.
    *   **Entry/Exit Points:** Entry is `initialize_workflow_node`. Exits are via edges from `error_path` and `success_path` to `END`.
*   **Routing Logic:**
    *   The `RoutingLogic` class methods are called after each node's execution.
    *   The `_route_after_node` helper checks for an `error_message` in `WorkflowState` to route to `error_path` or a specified next node.
*   **Dependencies:**
    *   `langgraph.graph.StateGraph`, `langgraph.graph.END`.
    *   Node functions from `src.nodes`.
    *   `WorkflowState` from `src.state`: Critical for state updates, access, and routing decisions.

### 1.2. `army-man-small-tweak/src/state.py`

*   **Purpose of `WorkflowState`:** A `TypedDict` defining the schema for the shared state object in the `langgraph` workflow. It acts as a central data carrier for communication between nodes.
*   **Information it Holds:**
    *   `current_step_name`: Tracks the current node.
    *   Paths: Numerous absolute file/folder paths (e.g., `goal_folder_path`, `task_description_path`, `small_tweak_file_path`).
    *   Content: `task_description_content`.
    *   Status/Flags: `last_event_summary`, `error_message`, `is_manifest_generated`.
    *   Data Structures: `manifest_data` (a Pydantic model).
    *   Metrics: `total_aider_cost`.
*   **Areas Contributing to "Too Much Stuff":**
    *   **Numerous specific path variables:** Could be grouped or derived.
    *   **Content Duplication:** `task_description_content` alongside `task_description_path`.
    *   **Fine-grained status flags:** Many specific boolean flags.
    *   **Mixing Configuration and Runtime State:** e.g., `manifest_template_path` (config) vs. `error_message` (runtime).
    *   **Specific tool outputs:** `aider_last_exit_code` ties state to a particular tool.

## 2. Brainstormed Solutions for `army-infantry` Graph & State

Based on `ai-docs/planning/01_infantry-full/03_tech-design-considerations.md`, particularly "WorkflowState Philosophy: Lean & Focused".

### Solution 1: Minimalist State with Configuration Injection

*   **`army-infantry/src/graph_state.py` (Proposed `WorkflowState`)**
    *   **Structure:**
        ```python
        from typing import Optional, TypedDict, Dict, Any

        class MissionReportData(TypedDict): # Or a Pydantic model
            mission_title: Optional[str]
            mission_description: Optional[str]
            final_status: Optional[str] # SUCCESS, FAILURE, BLOCKED
            execution_summary: Optional[str]
            files_modified_created: Optional[list[str]]
            git_summary: Optional[list[str]] # list of "hash - message"
            total_cost_usd: Optional[float]
            error_details: Optional[str]
            timestamp: Optional[str]

        class WorkflowState(TypedDict):
            # === Core Mission Identifiers (Likely from AppConfig or initial setup) ===
            mission_id: str 
            mission_folder_path: str # Absolute path to /sleepy-ai-army/missions/mission_abc
            project_git_root: str 

            # === Dynamic Workflow State ===
            current_step_name: Optional[str]
            error_message: Optional[str]
            
            mission_report_data: MissionReportData 
        ```
    *   **How it's leaner:**
        *   Removes direct file paths for templates, specific tool outputs. Paths derived from `mission_folder_path`.
        *   Static configuration (paths, model names) assumed to be in `AppConfig`, not in state.
        *   Primary output data encapsulated in `MissionReportData`.
        *   Reduced specific status flags. `task_description_content` removed (read on demand).

*   **`army-infantry/src/graph_builder.py` (Proposed Structure)**
    *   Similar to `army-man-small-tweak`, using `langgraph.StateGraph`. Nodes would be `async def`.
    *   **Initial Node Functions (Example Logging):**
        ```python
        # In army-infantry/src/nodes/initial_nodes.py
        import logging
        # from .graph_state import WorkflowState # Assuming this is the state definition
        # logger = logging.getLogger(__name__)

        # async def initialize_mission_node(state: WorkflowState) -> WorkflowState:
        #     logger.info(f"Executing initialize_mission_node for mission: {state.get('mission_id')}")
        #     state['current_step_name'] = "initialize_mission"
        #     return state

        # async def plan_mission_node(state: WorkflowState) -> WorkflowState:
        #     logger.info(f"Executing plan_mission_node for mission: {state.get('mission_id')}")
        #     state['current_step_name'] = "plan_mission"
        #     return state
        ```
    *   `RoutingLogic` adapted for new flow (e.g., `initialize_mission` -> `plan_mission` -> `execute_mission` -> `finalize_report`).

### Solution 2: Context Object for Mission Data, Minimal Dynamic State

*   **`army-infantry/src/graph_state.py` (Proposed `WorkflowState`)**
    *   **Structure:**
        ```python
        from typing import Optional, TypedDict, Any
        from pydantic import BaseModel 

        class MissionContext(BaseModel): 
            mission_id: str
            mission_folder_path: str 
            project_git_root: str
            mission_spec_content: Optional[str] = None 
            mission_title: Optional[str] = None
            final_status: Optional[str] = None
            execution_summary: Optional[str] = None
            files_modified_created: list[str] = []
            git_summary: list[str] = []
            total_cost_usd: float = 0.0
            error_details: Optional[str] = None
            timestamp: Optional[str] = None

        class WorkflowState(TypedDict):
            mission_context: MissionContext 
            current_step_name: Optional[str]
            error_message: Optional[str] 
        ```
    *   **How it's leaner (for `WorkflowState` itself):**
        *   `WorkflowState` is extremely minimal. Most data (inputs and outputs) is in `MissionContext`.
        *   Clear separation: `MissionContext` for "what the mission is/produced," `WorkflowState` for "how the workflow is doing."

*   **`army-infantry/src/graph_builder.py` (Proposed Structure)**
    *   Similar to Solution 1. Nodes access `state['mission_context']` for mission data.
    *   **Initial Node Functions (Example Logging):**
        ```python
        # In army-infantry/src/nodes/initial_nodes.py
        import logging
        # from .graph_state import WorkflowState, MissionContext
        # logger = logging.getLogger(__name__)

        # async def initialize_mission_node(state: WorkflowState) -> WorkflowState:
        #     mission_context = state['mission_context']
        #     logger.info(f"Executing initialize_mission_node for: {mission_context.mission_id}")
        #     state['current_step_name'] = "initialize_mission"
        #     return state
        ```
    *   Routing logic identical to Solution 1.

## 3. Brainstormed Radically Different Approaches

### Radical Approach 1: Event-Driven Architecture (EDA) with Microservices/Functions

*   **Core Concept:**
    *   Workflow decomposed into independent services/functions communicating via an event bus (e.g., Kafka, Pub/Sub).
    *   Each service handles a specific task (e.g., `MissionSpecReader`, `Planner`, `CodeExecutor`).
    *   Events trigger services. State passed in event payloads or a shared fast-access DB (Redis, DynamoDB) keyed by `mission_id`.
*   **Potential Advantages:**
    *   High scalability, decoupling, flexibility, maintainability, resilience.
*   **Potential Disadvantages:**
    *   Complexity (event bus, distributed transactions, debugging), harder orchestration visualization.

### Radical Approach 2: Director Pattern with Dynamic Task Execution

*   **Core Concept:**
    *   A central "Director" manages mission flow, dynamically determining the next "Task" (self-contained execution units) based on mission state and goals.
    *   Director might use a "Task Registry" or LLM-driven planning.
    *   State (`MissionContext`) managed by the Director; Tasks receive only necessary state slices.
*   **Potential Advantages:**
    *   High flexibility, extensibility, potentially more "intelligent" if Director uses LLM for planning.
*   **Potential Disadvantages:**
    *   Complexity of the Director, less predictability, Director can be a state bottleneck.
