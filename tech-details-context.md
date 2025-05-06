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


# Summary of ADK Concepts for Architecture Brainstorming

This summary captures key points about the Google Agent Development Kit (ADK) discussed during the brainstorming session, intended as input for architecting a new ADK project.

## 1. Referenced ADK Documentation & Key Learnings

* **Multi-Agent Systems:** Documentation on different approaches for multi-agent hierarchies was referenced and considered important to follow.
    * **URL:** `https://google.github.io/adk-docs/agents/multi-agents/`
* **LLM Agents & State/Artifacts:** Documentation explaining how to use session state and artifacts within prompts using `{}` syntax was noted. It also covered methods for storing data in the state (directly from model output, via tools, or callbacks).
    * **URL:** `https://google.github.io/adk-docs/agents/llm-agents/#guiding-the-agent-instructions-instruction`
* **Simplification:** Re-reading the docs led to the realization that ADK might allow for much simpler implementations than initially thought, particularly questioning the complexity of a previously built loop (poc1).

## 2. ADK Session Mechanics & State Management

* **Prompt Integration:** Session state and artifacts can be directly referenced in prompts using `{}`.
* **State Updates:** State can be updated through:
    * Direct output from an LLM agent.
    * Modifications made within a tool.
    * Changes implemented in callbacks.
* **Information Flow:** Data needed by later agents (e.g., file content for a Q&A agent) can be pre-loaded into the state by earlier agents (potentially using parallel agents for efficiency).

## 3. ADK Agent Architectures & Patterns Discussed

* **Adherence to Patterns:** Strong intention to stick to the multi-agent hierarchy patterns described in the ADK documentation. A summary of these patterns was deemed necessary for the technical architecture process.
* **Specific Agent Types Mentioned/Implied:**
    * `LoopAgent`: For iterative processing (e.g., handling backlog items, the root agent in the PRD).
    * `SequentialAgent`: For executing steps in order (e.g., Read Backlog -> Orchestrate Task).
    * `ParallelAgent`: For concurrent operations (e.g., multiple agents reading different files simultaneously).
    * `LlmAgent`: The core agent type for leveraging language models for tasks like planning or Q&A.
* **Hierarchical Examples:**
    * A sequential agent delegating to a parallel agent (for info gathering), which then passes control back for the next sequential step.
    * A loop agent containing sub-agents like "get next task" and a delegator agent that routes based on the task type.
    * The `SingleTaskOrchestrator` concept, which acts as a router/delegator based on the inferred next step for a task.
* **Project-Specific Instructions:** The idea that agent prompts and potentially architecture might need tailoring based on the specific project type (e.g., ADK builder vs. Godot game project).

## 4. Related ADK Examples & Tools

* **Demo Projects:**
    * `AashiDutt/Google-Agent-Development-Kit-Demo`: Noted for clean Streamlit integration.
    * `abhishekkumar35/google-adk-nocode`: Mentioned as a potentially useful visual/no-code interface for ADK, possibly helpful for visualization.
* **Articles/Tutorials:**
    * Bibek Poudel's Medium article: Highlighted for a good Streamlit+ADK example.

This information should provide a solid foundation for an AI brainstorming agent to understand the context, tools, and patterns considered important for building your ADK project.

## 3\. Common Multi-Agent Patterns using ADK Primitives [¶](https://google.github.io/adk-docs/agents/multi-agents/\#3-common-multi-agent-patterns-using-adk-primitives "Permanent link")

By combining ADK's composition primitives, you can implement various established patterns for multi-agent collaboration.

### Coordinator/Dispatcher Pattern [¶](https://google.github.io/adk-docs/agents/multi-agents/\#coordinatordispatcher-pattern "Permanent link")

- **Structure:** A central [`LlmAgent`](https://google.github.io/adk-docs/agents/llm-agents/) (Coordinator) manages several specialized `sub_agents`.
- **Goal:** Route incoming requests to the appropriate specialist agent.
- **ADK Primitives Used:**
  - **Hierarchy:** Coordinator has specialists listed in `sub_agents`.
  - **Interaction:** Primarily uses **LLM-Driven Delegation** (requires clear `description` s on sub-agents and appropriate `instruction` on Coordinator) or **Explicit Invocation ( `AgentTool`)** (Coordinator includes `AgentTool`-wrapped specialists in its `tools`).

```md-code__content
# Conceptual Code: Coordinator using LLM Transfer
from google.adk.agents import LlmAgent

billing_agent = LlmAgent(name="Billing", description="Handles billing inquiries.")
support_agent = LlmAgent(name="Support", description="Handles technical support requests.")

coordinator = LlmAgent(
    name="HelpDeskCoordinator",
    model="gemini-2.0-flash",
    instruction="Route user requests: Use Billing agent for payment issues, Support agent for technical problems.",
    description="Main help desk router.",
    # allow_transfer=True is often implicit with sub_agents in AutoFlow
    sub_agents=[billing_agent, support_agent]
)
# User asks "My payment failed" -> Coordinator's LLM should call transfer_to_agent(agent_name='Billing')
# User asks "I can't log in" -> Coordinator's LLM should call transfer_to_agent(agent_name='Support')

```

### Sequential Pipeline Pattern [¶](https://google.github.io/adk-docs/agents/multi-agents/\#sequential-pipeline-pattern "Permanent link")

- **Structure:** A [`SequentialAgent`](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/) contains `sub_agents` executed in a fixed order.
- **Goal:** Implement a multi-step process where the output of one step feeds into the next.
- **ADK Primitives Used:**
  - **Workflow:** `SequentialAgent` defines the order.
  - **Communication:** Primarily uses **Shared Session State**. Earlier agents write results (often via `output_key`), later agents read those results from `context.state`.

```md-code__content
# Conceptual Code: Sequential Data Pipeline
from google.adk.agents import SequentialAgent, LlmAgent

validator = LlmAgent(name="ValidateInput", instruction="Validate the input.", output_key="validation_status")
processor = LlmAgent(name="ProcessData", instruction="Process data if state key 'validation_status' is 'valid'.", output_key="result")
reporter = LlmAgent(name="ReportResult", instruction="Report the result from state key 'result'.")

data_pipeline = SequentialAgent(
    name="DataPipeline",
    sub_agents=[validator, processor, reporter]
)
# validator runs -> saves to state['validation_status']
# processor runs -> reads state['validation_status'], saves to state['result']
# reporter runs -> reads state['result']

```

### Parallel Fan-Out/Gather Pattern [¶](https://google.github.io/adk-docs/agents/multi-agents/\#parallel-fan-outgather-pattern "Permanent link")

- **Structure:** A [`ParallelAgent`](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/) runs multiple `sub_agents` concurrently, often followed by a later agent (in a `SequentialAgent`) that aggregates results.
- **Goal:** Execute independent tasks simultaneously to reduce latency, then combine their outputs.
- **ADK Primitives Used:**
  - **Workflow:** `ParallelAgent` for concurrent execution (Fan-Out). Often nested within a `SequentialAgent` to handle the subsequent aggregation step (Gather).
  - **Communication:** Sub-agents write results to distinct keys in **Shared Session State**. The subsequent "Gather" agent reads multiple state keys.

```md-code__content
# Conceptual Code: Parallel Information Gathering
from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent

fetch_api1 = LlmAgent(name="API1Fetcher", instruction="Fetch data from API 1.", output_key="api1_data")
fetch_api2 = LlmAgent(name="API2Fetcher", instruction="Fetch data from API 2.", output_key="api2_data")

gather_concurrently = ParallelAgent(
    name="ConcurrentFetch",
    sub_agents=[fetch_api1, fetch_api2]
)

synthesizer = LlmAgent(
    name="Synthesizer",
    instruction="Combine results from state keys 'api1_data' and 'api2_data'."
)

overall_workflow = SequentialAgent(
    name="FetchAndSynthesize",
    sub_agents=[gather_concurrently, synthesizer] # Run parallel fetch, then synthesize
)
# fetch_api1 and fetch_api2 run concurrently, saving to state.
# synthesizer runs afterwards, reading state['api1_data'] and state['api2_data'].

```

### Hierarchical Task Decomposition [¶](https://google.github.io/adk-docs/agents/multi-agents/\#hierarchical-task-decomposition "Permanent link")

- **Structure:** A multi-level tree of agents where higher-level agents break down complex goals and delegate sub-tasks to lower-level agents.
- **Goal:** Solve complex problems by recursively breaking them down into simpler, executable steps.
- **ADK Primitives Used:**
  - **Hierarchy:** Multi-level `parent_agent`/ `sub_agents` structure.
  - **Interaction:** Primarily **LLM-Driven Delegation** or **Explicit Invocation ( `AgentTool`)** used by parent agents to assign tasks to children. Results are returned up the hierarchy (via tool responses or state).

```md-code__content
# Conceptual Code: Hierarchical Research Task
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool

# Low-level tool-like agents
web_searcher = LlmAgent(name="WebSearch", description="Performs web searches for facts.")
summarizer = LlmAgent(name="Summarizer", description="Summarizes text.")

# Mid-level agent combining tools
research_assistant = LlmAgent(
    name="ResearchAssistant",
    model="gemini-2.0-flash",
    description="Finds and summarizes information on a topic.",
    tools=[agent_tool.AgentTool(agent=web_searcher), agent_tool.AgentTool(agent=summarizer)]
)

# High-level agent delegating research
report_writer = LlmAgent(
    name="ReportWriter",
    model="gemini-2.0-flash",
    instruction="Write a report on topic X. Use the ResearchAssistant to gather information.",
    tools=[agent_tool.AgentTool(agent=research_assistant)]
    # Alternatively, could use LLM Transfer if research_assistant is a sub_agent
)
# User interacts with ReportWriter.
# ReportWriter calls ResearchAssistant tool.
# ResearchAssistant calls WebSearch and Summarizer tools.
# Results flow back up.

```

### Review/Critique Pattern (Generator-Critic) [¶](https://google.github.io/adk-docs/agents/multi-agents/\#reviewcritique-pattern-generator-critic "Permanent link")

- **Structure:** Typically involves two agents within a [`SequentialAgent`](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/): a Generator and a Critic/Reviewer.
- **Goal:** Improve the quality or validity of generated output by having a dedicated agent review it.
- **ADK Primitives Used:**
  - **Workflow:** `SequentialAgent` ensures generation happens before review.
  - **Communication:** **Shared Session State** (Generator uses `output_key` to save output; Reviewer reads that state key). The Reviewer might save its feedback to another state key for subsequent steps.

```md-code__content
# Conceptual Code: Generator-Critic
from google.adk.agents import SequentialAgent, LlmAgent

generator = LlmAgent(
    name="DraftWriter",
    instruction="Write a short paragraph about subject X.",
    output_key="draft_text"
)

reviewer = LlmAgent(
    name="FactChecker",
    instruction="Review the text in state key 'draft_text' for factual accuracy. Output 'valid' or 'invalid' with reasons.",
    output_key="review_status"
)

# Optional: Further steps based on review_status

review_pipeline = SequentialAgent(
    name="WriteAndReview",
    sub_agents=[generator, reviewer]
)
# generator runs -> saves draft to state['draft_text']
# reviewer runs -> reads state['draft_text'], saves status to state['review_status']

```

### Iterative Refinement Pattern [¶](https://google.github.io/adk-docs/agents/multi-agents/\#iterative-refinement-pattern "Permanent link")

- **Structure:** Uses a [`LoopAgent`](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/) containing one or more agents that work on a task over multiple iterations.
- **Goal:** Progressively improve a result (e.g., code, text, plan) stored in the session state until a quality threshold is met or a maximum number of iterations is reached.
- **ADK Primitives Used:**
  - **Workflow:** `LoopAgent` manages the repetition.
  - **Communication:** **Shared Session State** is essential for agents to read the previous iteration's output and save the refined version.
  - **Termination:** The loop typically ends based on `max_iterations` or a dedicated checking agent setting `actions.escalate=True` when the result is satisfactory.

```md-code__content
# Conceptual Code: Iterative Code Refinement
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

# Agent to generate/refine code based on state['current_code'] and state['requirements']
code_refiner = LlmAgent(
    name="CodeRefiner",
    instruction="Read state['current_code'] (if exists) and state['requirements']. Generate/refine Python code to meet requirements. Save to state['current_code'].",
    output_key="current_code" # Overwrites previous code in state
)

# Agent to check if the code meets quality standards
quality_checker = LlmAgent(
    name="QualityChecker",
    instruction="Evaluate the code in state['current_code'] against state['requirements']. Output 'pass' or 'fail'.",
    output_key="quality_status"
)

# Custom agent to check the status and escalate if 'pass'
class CheckStatusAndEscalate(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("quality_status", "fail")
        should_stop = (status == "pass")
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))

refinement_loop = LoopAgent(
    name="CodeRefinementLoop",
    max_iterations=5,
    sub_agents=[code_refiner, quality_checker, CheckStatusAndEscalate(name="StopChecker")]
)
# Loop runs: Refiner -> Checker -> StopChecker
# State['current_code'] is updated each iteration.
# Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5 iterations.

```

### Human-in-the-Loop Pattern [¶](https://google.github.io/adk-docs/agents/multi-agents/\#human-in-the-loop-pattern "Permanent link")

- **Structure:** Integrates human intervention points within an agent workflow.
- **Goal:** Allow for human oversight, approval, correction, or tasks that AI cannot perform.
- **ADK Primitives Used (Conceptual):**
  - **Interaction:** Can be implemented using a custom **Tool** that pauses execution and sends a request to an external system (e.g., a UI, ticketing system) waiting for human input. The tool then returns the human's response to the agent.
  - **Workflow:** Could use **LLM-Driven Delegation** ( `transfer_to_agent`) targeting a conceptual "Human Agent" that triggers the external workflow, or use the custom tool within an `LlmAgent`.
  - **State/Callbacks:** State can hold task details for the human; callbacks can manage the interaction flow.
  - **Note:** ADK doesn't have a built-in "Human Agent" type, so this requires custom integration.

```md-code__content
# Conceptual Code: Using a Tool for Human Approval
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool

# --- Assume external_approval_tool exists ---
# This tool would:
# 1. Take details (e.g., request_id, amount, reason).
# 2. Send these details to a human review system (e.g., via API).
# 3. Poll or wait for the human response (approved/rejected).
# 4. Return the human's decision.
# async def external_approval_tool(amount: float, reason: str) -> str: ...
approval_tool = FunctionTool(func=external_approval_tool)

# Agent that prepares the request
prepare_request = LlmAgent(
    name="PrepareApproval",
    instruction="Prepare the approval request details based on user input. Store amount and reason in state.",
    # ... likely sets state['approval_amount'] and state['approval_reason'] ...
)

# Agent that calls the human approval tool
request_approval = LlmAgent(
    name="RequestHumanApproval",
    instruction="Use the external_approval_tool with amount from state['approval_amount'] and reason from state['approval_reason'].",
    tools=[approval_tool],
    output_key="human_decision"
)

# Agent that proceeds based on human decision
process_decision = LlmAgent(
    name="ProcessDecision",
    instruction="Check state key 'human_decision'. If 'approved', proceed. If 'rejected', inform user."
)

approval_workflow = SequentialAgent(
    name="HumanApprovalWorkflow",
    sub_agents=[prepare_request, request_approval, process_decision]
)

```

These patterns provide starting points for structuring your multi-agent systems. You can mix and match them as needed to create the most effective architecture for your specific application.

## Guiding the Agent: Instructions ( `instruction`) [¶](https://google.github.io/adk-docs/agents/llm-agents/\#guiding-the-agent-instructions-instruction "Permanent link")

The `instruction` parameter is arguably the most critical for shaping an `LlmAgent`'s behavior. It's a string (or a function returning a string) that tells the agent:

- Its core task or goal.
- Its personality or persona (e.g., "You are a helpful assistant," "You are a witty pirate").
- Constraints on its behavior (e.g., "Only answer questions about X," "Never reveal Y").
- How and when to use its `tools`. You should explain the purpose of each tool and the circumstances under which it should be called, supplementing any descriptions within the tool itself.
- The desired format for its output (e.g., "Respond in JSON," "Provide a bulleted list").

**Tips for Effective Instructions:**

- **Be Clear and Specific:** Avoid ambiguity. Clearly state the desired actions and outcomes.
- **Use Markdown:** Improve readability for complex instructions using headings, lists, etc.
- **Provide Examples (Few-Shot):** For complex tasks or specific output formats, include examples directly in the instruction.
- **Guide Tool Use:** Don't just list tools; explain _when_ and _why_ the agent should use them.

```md-code__content
# Example: Adding instructions
capital_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="capital_agent",
    description="Answers user questions about the capital city of a given country.",
    instruction="""You are an agent that provides the capital city of a country.
When a user asks for the capital of a country:
1. Identify the country name from the user's query.
2. Use the `get_capital_city` tool to find the capital.
3. Respond clearly to the user, stating the capital city.
Example Query: "What's the capital of France?"
Example Response: "The capital of France is Paris."
""",
    # tools will be added next
)

```

_(Note: For instructions that apply to_ all _agents in a system, consider using `global_instruction` on the root agent, detailed further in the [Multi-Agents](https://google.github.io/adk-docs/agents/multi-agents/) section.)_

## Equipping the Agent: Tools ( `tools`) [¶](https://google.github.io/adk-docs/agents/llm-agents/\#equipping-the-agent-tools-tools "Permanent link")

Tools give your `LlmAgent` capabilities beyond the LLM's built-in knowledge or reasoning. They allow the agent to interact with the outside world, perform calculations, fetch real-time data, or execute specific actions.

- **`tools` (Optional):** Provide a list of tools the agent can use. Each item in the list can be:
  - A Python function (automatically wrapped as a `FunctionTool`).
  - An instance of a class inheriting from `BaseTool`.
  - An instance of another agent ( `AgentTool`, enabling agent-to-agent delegation - see [Multi-Agents](https://google.github.io/adk-docs/agents/multi-agents/)).

The LLM uses the function/tool names, descriptions (from docstrings or the `description` field), and parameter schemas to decide which tool to call based on the conversation and its instructions.

```md-code__content
# Define a tool function
def get_capital_city(country: str) -> str:
  """Retrieves the capital city for a given country."""
  # Replace with actual logic (e.g., API call, database lookup)
  capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
  return capitals.get(country.lower(), f"Sorry, I don't know the capital of {country}.")

# Add the tool to the agent
capital_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="capital_agent",
    description="Answers user questions about the capital city of a given country.",
    instruction="""You are an agent that provides the capital city of a country... (previous instruction text)""",
    tools=[get_capital_city] # Provide the function directly
)

```

Learn more about Tools in the [Tools](https://google.github.io/adk-docs/tools/) section.