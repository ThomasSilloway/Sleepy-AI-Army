# Sleepy Dev Team - Detailed Technical Specifications (Based on Google ADK)

**Version:** 1.4
**Date:** 2025-05-01

## 1. Introduction

This document provides detailed technical specifications for the "Sleepy Dev Team" application, focusing on the specific Google Agent Development Kit (ADK) components, classes, properties, and methods relevant to the planned implementation. It expands upon the previous technical details document (v1.2) using the comprehensive API information extracted from the provided ADK documentation. **It includes detailed guidance on leveraging ADK features and best practices to guide an external AI coding agent (e.g., Roo Code) during implementation, aiming to minimize framework-specific hallucinations.** This serves as a technical reference guide for development.

## 2. Core ADK Concepts Leveraged

The project will utilize several fundamental ADK primitives:

* **Multi-Agent Architecture:** Implemented as a hierarchical system. The `SleepyDev_RootAgent` (`LoopAgent`) contains sub-agents `BacklogReaderAgent` and `SingleTaskOrchestrator`. The `SingleTaskOrchestrator` further delegates to specialized `Execution Agents` (e.g., `PRDAgent`, `CodeExecutionAgent`). This modular design, explicitly supported by ADK's `sub_agents` and agent hierarchy features, allows for specialized logic and scalability. (Ref: ADK Docs - Multi-Agent Architecture, Multi-Agent System Design).
* **Agent Types:**
    * **`LlmAgent` (alias: `Agent`):** The foundation for reasoning agents. Key configuration for agents like `TaskPlannerAgent`, `PRDAgent`, `ReportingAgent` will involve:
        * `name`: Unique identifier (e.g., `"TaskPlannerAgent"`).
        * `model`: Set to `"gemini-2.5"`.
        * `instruction`: Critically important. Must clearly define the agent's specific role, input expectations (e.g., "Read task folder path from `context.state['task_folder_path']`"), desired output/action, constraints, and precise instructions on using any assigned `tools`. Reference relevant state keys explicitly.
        * `tools`: List of `FunctionTool` instances providing necessary capabilities (e.g., file I/O).
        * `examples`: Consider adding few-shot examples (using `google.adk.examples.Example`) for agents with complex logic or specific output formats (like `TaskPlannerAgent` mapping state to `next_step`, or `ReportingAgent` generating proposals) to further guide the LLM.
        * (Ref: ADK Docs - LlmAgent, Defining Identity, Guiding Instructions, Examples).
    * **Workflow Agents:**
        * **`LoopAgent`:** Used for `SleepyDev_RootAgent`. It will contain `sub_agents=[BacklogReaderAgent, SingleTaskOrchestrator]`. Termination relies on `BacklogReaderAgent` setting `actions.escalate=True` or hitting `max_iterations`. (Ref: ADK Docs - Workflow Agents, Loop agents).
        * **`SequentialAgent`:** Could be used internally by `SingleTaskOrchestrator` if its routing logic is implemented via a sequence of checks/delegations rather than a single LLM call. (Ref: ADK Docs - Workflow Agents, Sequential Agents).
* **Tools (`BaseTool`, `FunctionTool`):** Provide specific capabilities.
    * **Custom `FunctionTool`s:** Essential for File System operations (read/write/list/mkdir/modify `backlog.md`) and `subprocess` execution (for `aider`, formatters).
    * **Definition:** Must follow ADK best practices: descriptive names, type-hinted parameters (JSON serializable, no defaults), detailed docstrings (explaining purpose, parameters, *return dict structure*, including `status` and `result`/`error_message` keys), and returning a `dict`.
    * **Context Access:** Tool functions requiring access to session state or actions (like `BacklogReaderAgent` needing `escalate`) must include `tool_context: ToolContext` in their signature. ADK automatically injects the context.
    * (Ref: ADK Docs - Tools, Function Tools, Defining Effective Tool Functions, Tool Context).
* **Session Management (`Session`, `State`):** Central to passing data between agents within a run cycle.
    * **`InMemorySessionService`:** Sufficient for MVP, instantiated and passed to the `Runner`. Note that state is ephemeral.
    * **`State`:** Accessed via `context.state`. Used for:
        * `BacklogReaderAgent` -> `SingleTaskOrchestrator`: `state['current_task_description']`.
        * `SingleTaskOrchestrator` -> `ExecutionAgent`: `state['task_folder_path']`, potentially specific instructions.
        * `TaskPlannerAgent` -> `SingleTaskOrchestrator`: `state['next_step']`.
        * `RootCauseInvestigatorAgent` -> `RootCauseDocumenterAgent` / `FixPlanningAgent`: `state['root_cause_findings']`.
        * Loop control: `BacklogReaderAgent` setting `state['backlog_empty']` (or directly using `escalate`). State prefixes (`temp:`) can be used for intermediate data within the orchestrator's flow if needed.
    * (Ref: ADK Docs - Session Management, State, State Prefixes).
* **Context Objects (`InvocationContext`, `CallbackContext`, `ToolContext`):** Provide access to runtime information.
    * **`ToolContext`:** Will be used extensively within custom `FunctionTool` implementations to access `state` (read/write), `agent_name`, `invocation_id`, and most importantly `actions` (for `BacklogReaderAgent` to set `escalate=True`).
    * **`CallbackContext`:** Will be used if implementing lifecycle callbacks (e.g., for logging) to access `state`, `agent_name`, `invocation_id`, `user_content`.
    * (Ref: ADK Docs - Context, Tool Context, CallbackContext).
* **Events & Actions (`Event`, `EventActions`):** The framework uses these internally. Understanding `EventActions` is key for loop termination (`actions.escalate`) and potentially controlling summarization (`actions.skip_summarization` in `CodeExecutionAgent`'s tool callback if `aider`'s raw output is preferred). State modifications via `context.state['key'] = value` are automatically tracked in `actions.state_delta`. (Ref: ADK Docs - Event, EventActions).
* **Runner (`Runner`):** The main execution engine. Will be instantiated with `agent=SleepyDev_RootAgent`, `app_name="SleepyDevTeam"`, and `session_service=InMemorySessionService()`. The core application logic will invoke `runner.run_async(...)`. (Ref: ADK Docs - Core Concepts, Runner).

## 3. Guiding AI Coding Agent Implementation (e.g., Roo Code)

Given Roo Code's large context window, provide detailed information to minimize ADK-specific hallucinations:

* **Prioritize Spec over General Knowledge:** Instruct Roo Code to rely *primarily* on the provided PRD and this Technical Specification document, especially Section 6 (Detailed ADK Components), rather than its general training data about ADK, which might be outdated or incomplete.
* **Provide ADK Definitions:** When asking Roo Code to implement an agent or tool, *include the detailed class/method/property definitions* from Section 6 for the relevant ADK components (`LlmAgent`, `LoopAgent`, `FunctionTool`, `ToolContext`, `State`, `EventActions`, etc.) directly within the prompt context.
* **Use Exact ADK Terminology:** Consistently use the precise ADK terminology found in the documentation and this spec within your prompts.
* **Implement Agent by Agent:** Request implementation for one agent (e.g., `BacklogReaderAgent`) or one `FunctionTool` at a time. Provide the specific requirements for that component. *Example Prompt Structure:*
    1.  "**Goal:** Implement the `BacklogReaderAgent` for Sleepy Dev Team."
    2.  "**Relevant ADK Components:** \[Paste definitions for `LlmAgent`/`BaseAgent`, `FunctionTool`, `ToolContext`, `State`, `EventActions` from Section 6]"
    3.  "**Requirements (from PRD FR-002 & Tech Spec):** \[Detail the logic: read `backlog.md`, check if empty, set `actions.escalate=True` via `tool_context` if empty, otherwise get first line, put in `state['current_task_description']`, rewrite `backlog.md`, use File I/O tools]"
    4.  "**Tool Definition:** Implement this logic within one or more Python functions suitable for use as ADK `FunctionTool`s. Remember tools must return dictionaries, ideally with a `status` key."
* **Specify Tool Implementation Details:** Explicitly remind Roo Code about `FunctionTool` requirements: Python function, type hints, detailed docstring, dictionary return, `tool_context` parameter if state/actions access is needed.
* **Reference Architecture & State:** Explain the context: "The `BacklogReaderAgent` runs inside the `RootAgent` (`LoopAgent`). It reads the backlog and puts the task description into `tool_context.state['current_task_description']` for the *next* agent in the loop, `SingleTaskOrchestrator`, to consume."
* **Use ADK Examples:** Include minimal, correct ADK code snippets (e.g., from ADK Quickstart) demonstrating agent instantiation or tool usage if needed to clarify patterns.
* **Iterate and Correct:** Review generated code for correct ADK usage (e.g., Did it correctly use `tool_context.actions.escalate`? Did the tool return a dict?). Provide specific feedback for refinement.

## 4. Potential Callback Usage Patterns (MVP & Beyond)

* **Logging (Highly Recommended for MVP):** Implement `before_agent_callback`, `after_agent_callback`, `before_tool_callback`, `after_tool_callback` on key agents (`SingleTaskOrchestrator`, `TaskPlannerAgent`, Execution Agents) to log entry/exit points, tool arguments/results, and relevant state values (`current_task_description`, `next_step`). This is crucial for debugging the flow. (Ref: ADK Callbacks - Logging Pattern).
* **State Validation (Potential):** `before_` callbacks could check if required state keys exist before an agent/tool proceeds (e.g., `SingleTaskOrchestrator` checking if `current_task_description` was actually set).
* **Controlling Summarization (Potential):** `after_tool_callback` for `CodeExecutionAgent` could set `tool_context.actions.skip_summarization = True` if `aider`'s raw output is needed by `ReportingAgent`. (Ref: ADK Callbacks - Tool-Specific Actions).

## 5. Key Implementation Patterns (Summary)

* **Root Loop Control:** `SleepyDev_RootAgent` (`LoopAgent`) drives the process, terminated by `BacklogReaderAgent` setting `actions.escalate = True`.
* **Backlog File Modification:** `BacklogReaderAgent` reads the top line of `backlog.md` and physically rewrites the file without that line. Requires File Write tool.
* **State-Driven Routing:** `SingleTaskOrchestrator` uses `state['next_step']` (from `TaskPlannerAgent`) to invoke the correct `ExecutionAgent`.
* **Tool Abstraction:** `CodeExecutionAgent`/`FormattingAgent` use `FunctionTool`s wrapping `subprocess`. Other agents use `FunctionTool`s for File I/O.
* **LLM API Key Cycling:** Required for handling `gemini-2.5` rate limits.

## 6. Execution Environment

* **Containerization:** Docker and Docker Compose. `Dockerfile` needs Python, ADK, `aider-chat`, `discord.py`, formatters.
* **Execution:** `start-dev.bat`, `stop-dev.bat` scripts.
* **Configuration:** `.env` file for API keys, paths.

## 7. Detailed ADK Components & Classes Reference

*(This section details the specific properties and methods for key ADK classes, based on the provided documentation snippets)*

* **`google.adk.agents.BaseAgent`**: Base class for all agents.
    * **Properties:** `after_agent_callback`: Optional[Callable], `before_agent_callback`: Optional[Callable], `description`: str, `name`: str (required), `parent_agent`: Optional[BaseAgent], `sub_agents`: list[BaseAgent], `root_agent`: BaseAgent.
    * **Methods:** `find_agent(name: str)`: Optional[BaseAgent], `find_sub_agent(name: str)`: Optional[BaseAgent], `async run_async(parent_context: InvocationContext)`: AsyncGenerator[Event, None], `async run_live(parent_context: InvocationContext)`: AsyncGenerator[Event, None]. (Protected: `_run_async_impl`, `_run_live_impl`).

* **`google.adk.agents.LlmAgent`** (alias: `Agent`): LLM-based Agent.
    * **Properties (Adds to BaseAgent):** `after_model_callback`: Optional[Callable], `after_tool_callback`: Optional[Callable], `before_model_callback`: Optional[Callable], `before_tool_callback`: Optional[Callable], `code_executor`: Optional[BaseCodeExecutor], `disallow_transfer_to_parent`: bool, `disallow_transfer_to_peers`: bool, `examples`: Optional[ExamplesUnion], `generate_content_config`: Optional[types.GenerateContentConfig], `global_instruction`: Union[str, InstructionProvider], `include_contents`: Literal['default','none'], `input_schema`: Optional[type[BaseModel]], `instruction`: Union[str, InstructionProvider], `model`: Union[str, BaseLlm] (required, e.g., `"gemini-2.5"`), `output_key`: Optional[str], `output_schema`: Optional[type[BaseModel]], `planner`: Optional[BasePlanner], `tools`: list[ToolUnion], `canonical_model`: BaseLlm, `canonical_tools`: list[BaseTool].
    * **Methods (Adds to BaseAgent):** `canonical_global_instruction(ctx)`: str, `canonical_instruction(ctx)`: str.

* **`google.adk.agents.LoopAgent`**: Workflow agent that runs sub-agents in a loop.
    * **Properties (Adds to BaseAgent):** `max_iterations`: Optional[int].

* **`google.adk.agents.SequentialAgent`**: Workflow agent that runs sub-agents sequentially.
    * **(No specific properties beyond BaseAgent listed in provided docs).**

* **`google.adk.tools.BaseTool`**: Base class for all tools.
    * **Properties:** `name`: str, `description`: str, `is_long_running`: bool (default False).
    * **Methods:** `async process_llm_request(tool_context, llm_request)`: None, `async run_async(args, tool_context)`: Any (Abstract).

* **`google.adk.tools.FunctionTool`**: Wraps a Python function as a tool.
    * **Properties:** `func`: Callable.
    * **Methods:** `async run_async(args, tool_context)`: Any (Executes wrapped function).

* **`google.adk.tools.ToolContext`**: Context for tool invocation. Inherits `CallbackContext`.
    * **Properties (Adds to CallbackContext):** `invocation_context`: InvocationContext, `function_call_id`: Optional[str], `event_actions`: EventActions, `actions`: EventActions (property alias).
    * **Methods (Adds to CallbackContext):** `get_auth_response(auth_config)`: AuthCredential, `list_artifacts()`: list[str], `request_credential(auth_config)`: None, `search_memory(query)`: SearchMemoryResponse.

* **`google.adk.agents.callback_context.CallbackContext`**: Context for agent/model callbacks. Inherits `ReadonlyContext`.
    * **Properties (Adds to ReadonlyContext):** `state`: State (Mutable), `user_content`: Optional[Content].
    * **Methods:** `load_artifact(filename, version=None)`: Optional[Part], `save_artifact(filename, artifact)`: int.

* **`google.adk.sessions.Session`**: Represents user-agent interactions.
    * **Properties:** `id`: str, `app_name`: str, `user_id`: str, `state`: dict[str, Any], `events`: list[Event], `last_update_time`: float.

* **`google.adk.sessions.State`**: Manages state dictionary with pending delta.
    * **Properties:** `value`: dict, `delta`: dict.
    * **Methods:** `get(key, default=None)`: Any, `has_delta()`: bool, `to_dict()`: dict[str, Any], `update(delta)`.
    * **Constants:** `APP_PREFIX`, `TEMP_PREFIX`, `USER_PREFIX`.

* **`google.adk.sessions.BaseSessionService`**: Base class for session services.
    * **Methods (Abstract):** `create_session(...)`, `delete_session(...)`, `get_session(...)`, `list_events(...)`, `list_sessions(...)`.
    * **Methods (Concrete):** `append_event(session, event)`, `close_session(session)`.

* **`google.adk.sessions.InMemorySessionService`**: In-memory session service (MVP). Implements `BaseSessionService`.

* **`google.adk.runners.Runner`**: Manages agent execution.
    * **Properties:** `app_name`: str, `agent`: BaseAgent, `artifact_service`: Optional[BaseArtifactService], `session_service`: BaseSessionService, `memory_service`: Optional[BaseMemoryService].
    * **Methods:** `run(...)`: Generator[Event, None, None], `async run_async(...)`: AsyncGenerator[Event, None], `async run_live(...)`: AsyncGenerator[Event, None], `close_session(session)`.

* **`google.adk.events.Event`**: Represents an event in a conversation.
    * **Properties:** `invocation_id`: str, `author`: str, `actions`: EventActions, `content`: Optional[Content], `id`: str, `timestamp`: float, `is_final_response`: bool, `branch`: Optional[str], `long_running_tool_ids`: Optional[set[str]].
    * **Methods:** `get_function_calls()`: list[FunctionCall], `get_function_responses()`: list[FunctionResponse], `is_final_response()`: bool, `has_trailing_code_exeuction_result()`: bool, `static new_id()`.

* **`google.adk.events.EventActions`**: Actions attached to an event.
    * **Properties:** `artifact_delta`: dict[str, int], `escalate`: Optional[bool], `requested_auth_configs`: dict[str, AuthConfig], `skip_summarization`: Optional[bool], `state_delta`: dict[str, object], `transfer_to_agent`: Optional[str].

This detailed document should provide substantial context and specific guidance for the AI coding agent tasked with implementing the Sleepy Dev Team project using Google ADK.