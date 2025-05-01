# Python Best Practices (Concise for LLM)

This list provides core Python best practices, suitable for priming an LLM agent.

*   **PEP 8 Compliance:** Adhere to the standard style guide (indentation, naming, line length). Consistency is key.
*   **Naming Conventions:**
    *   `snake_case` for variables, functions, methods, modules.
    *   `CapWords` (CamelCase) for classes.
    *   `UPPERCASE_WITH_UNDERSCORES` for constants.
    *   Use meaningful, descriptive names.
*   **Readability & Simplicity:**
    *   Write clear, straightforward code.
    *   Prefer explicit over implicit logic.
    *   Keep functions/methods short and focused on a single task.
    *   Avoid overly complex expressions or nesting.
*   **Comments & Docstrings:**
    *   Use `#` comments to explain *why* something is done, not *what* the code does (the code itself explains the *what*).
    *   Use `"""Docstrings"""` for all public modules, classes, functions, and methods to describe their purpose, arguments, and return values.
    *   Keep comments and docstrings up-to-date with code changes.
*   **Modularity:**
    *   Organize code into functions and classes.
    *   Group related functionality into modules.
*   **Error Handling:**
    *   Use `try...except` blocks to handle potential errors gracefully.
    *   Be specific about the exceptions you catch.
*   **API/Function Signatures:** Pay close attention to the required arguments (positional vs. keyword) and types specified in function/method signatures, especially when using external libraries or frameworks. Use linters and type hints to help catch mismatches.
*   **Data Structures:**
    *   Choose appropriate data structures for the task (e.g., use `sets` or `dictionaries` for fast membership testing or lookups instead of `lists` where applicable).
*   **Imports:**
    *   Import modules at the top of the file.
    *   Import standard library modules first, then third-party, then local application modules.
    *   Use explicit imports (`import module` or `from module import specific_item`).
    *   Avoid wildcard imports (`from module import *`).
*   **Idiomatic Python:**
    *   Leverage Python's built-in functions and features (e.g., list comprehensions, `enumerate`, context managers (`with` statement)).

# Google Agent Development Kit (ADK) for Vertex AI: Best Practices

This document outlines best practices for developing AI agents using Google's Python-based Agent Development Kit (ADK) on Vertex AI.

**0.0. General**
- When samples are given as references, stay as close to that sample as possible, don't invent new code. The samples are correct, you likely have old data that you are working with.

**0. Folder and File structure**
```
/src/agent-name   # use only dashes  # `adk web` command should be executed here
├── README.md
├── requirements.txt
├── agent_name/  # use only underscores
        agent.py
        __init__.py  # MUST import root_agent from agent.py
        prompt.py
│   ├── shared_libraries/ # constants.py, types.py, etc
│   ├── tools/ # shared tools that multiple agents might use
│   └── sub_agents/
│       ├── sub_agent_1/
│           ├── agent.py
│           ├── prompt.py
│           ├── tools.py
│       ├── sub_agent_2/
│           ├── agent.py
│           ├── prompt.py
│           ├── tools.py
│       ├── etc
├── tests/ # Always empty
```

**1. Agent and Tool Definition:**

*   **Clear Descriptions:** Write clear, concise, and accurate `description` fields for agents and docstrings for tools. The LLM relies heavily on these to understand capabilities, route tasks (especially in multi-agent setups), and determine when/how to use tools.
*   **Specific Naming:** Use unique and descriptive `name` parameters for agents.
*   **Tool Docstrings:** Ensure tool function docstrings clearly explain:
    *   What the tool does.
    *   When it should be used.
    *   Required arguments (including types).
    *   What information it returns.
*   **Prompt Simplicity:** Keep agent `instruction` prompts focused and unambiguous, especially when the primary goal is to reliably call a specific tool. Complex prompts mixing freeform generation and tool use can lead to unpredictable behavior.
*   **Schema Definition:** Use shared schemas (e.g., via Pydantic) for structured input/output, promoting consistency and enabling validation (especially when using REST interfaces like FastAPI).
*   **Model** Use `gemini-2.0-flash` by default
*   **Agent definitions** - Should always be formatted like the following, do not use special classes
```
from travel_concierge.sub_agents.booking.agent import booking_agent

root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    description="A Travel Conceirge using the services of multiple sub-agents",
    instruction=prompt.ROOT_AGENT_INSTR,
    sub_agents=[
        inspiration_agent,
        planning_agent,
        booking_agent,
        pre_trip_agent,
        in_trip_agent,
        post_trip_agent,
    ],
    before_agent_callback=_load_precreated_itinerary,
)
```
 - Do not use Custom agents unless specifically requested
*   **Sub-agent definitions** - Should always be formatted like the following, do not use special classes
```
itinerary_agent = Agent(
    model="gemini-2.0-flash",
    name="itinerary_agent",
    description="Create and persist a structured JSON representation of the itinerary",
    instruction=prompt.ITINERARY_AGENT_INSTR,
)
```
*   **Main.py** - Don't include a main.py and don't include a __main__ definition in any files

**2. Asynchronous Operations & Integration:**

*   **Use `async`:** Leverage Python's `asyncio` for agent interactions (`runner.run_async`) and tool executions, especially when dealing with I/O-bound operations like LLM calls or external API requests. This prevents blocking and improves efficiency.
*   **Event Handling:** Process the `Events` yielded by `runner.run_async` to understand the agent's execution steps (tool calls, intermediate thoughts, final response). Use `event.is_final_response()` to identify the concluding output.
*   **Correct `asyncio` Usage:** Understand the nuances of `asyncio` primitives. Use `await` for native coroutines (like ADK methods or other async library functions). Use `asyncio.to_thread` *only* to run blocking I/O operations in a separate thread without blocking the event loop.
*   **Choosing Concurrency Primitives:** Select `asyncio` functions like `gather`, `wait`, or `wait_for` carefully based on how you need to coordinate concurrent tasks (e.g., wait for all to finish vs. wait for the first to complete, especially relevant in network communication scenarios).
*   **Stateful Connection Handling:** When integrating agents via network connections (e.g., WebSockets), implement robust state management in your connection handlers to control message flow according to the expected interaction pattern (e.g., ensuring only one reply is sent per agent turn, handling disconnections gracefully).

**3. Multi-Agent Systems:**

*   **Modularity:** Design specialized agents for specific tasks and compose them hierarchically.
*   **Clear Roles:** Define distinct roles and capabilities via agent descriptions to enable effective LLM-driven delegation and routing between agents.
*   **Orchestration:** Use a central `host_agent` or specific workflow agents (`Sequential`, `Parallel`, `Loop`) to manage interactions and task flow between sub-agents.
*   **Inter-Agent Communication:** Standardize communication protocols if building custom agent interactions (e.g., using REST APIs with shared schemas, like the Agent-to-Agent (A2A) protocol pattern).

**4. State Management:**

*   **Session Services:** Utilize session services (like `InMemorySessionService` or custom implementations) to manage conversational state and memory across interactions for a given user/session ID.
*   **State-Aware Tools (Standard):** Design tools to accept a `ToolContext` parameter. Access session state via `tool_context.state` to read data set by previous agents/steps (e.g., using `output_key`). This is the recommended approach.
*   **SequentialAgent Implicit Input Mapping (Alternative):** Be aware that when using `SequentialAgent`, if a tool step doesn't specify an `input_key`, the agent might implicitly pass the *direct output* of the preceding step as an argument to the tool's function, *if* the function signature has a parameter matching the type of that output (e.g., a function expecting `Dict` receiving the `Dict` output of the previous step). While this can work, relying on `ToolContext` is generally more explicit and robust.

**5. Development and Testing:**

*   **Virtual Environments:** Use Python virtual environments (`venv`) to manage project dependencies and isolate them from other projects.
*   **Local Testing:** Utilize the ADK's capabilities for local development, testing, and debugging (CLI, Web UI). Inspect events and state step-by-step.
*   **Credentials:** Use Application Default Credentials (ADC) (`gcloud auth application-default login`) for authenticating to Google Cloud services during local development.
*   **Iterative Testing:** Test agent interactions incrementally. Start simple and gradually add complexity (tools, sub-agents, state).

**6. Evaluation:**

*   **Systematic Evaluation:** Use ADK's built-in evaluation tools (`AgentEvaluator.evaluate()`) to systematically assess agent performance against predefined test cases (e.g., `test.json`).
*   **Evaluate Trajectory & Response:** Assess both the quality of the final response and the correctness of the step-by-step execution path (tool usage, intermediate reasoning).

**7. Deployment:**

*   **Containerization:** Package your agent application for deployment (e.g., using containers).
*   **API Server:** Expose your agent via a server (like FastAPI, potentially using helper functions like `create_app(agent)` from examples) for integration with other services or UIs.

**8. Artifact Creation:**

*   **Reliable Artifact Parts:** When creating `google.genai.types.Part` objects for artifacts, prefer using the constructor with `inline_data`: `types.Part(inline_data=types.Blob(data=..., mime_type=...))`. While documentation might mention a `types.Part.from_data(...)` convenience method, it may not be available in all library versions and can lead to `AttributeError`. Using the constructor directly is more robust.
