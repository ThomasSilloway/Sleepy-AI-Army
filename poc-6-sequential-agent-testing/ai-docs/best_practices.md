# Python Best Practices (Concise for LLM)

This list provides core Python best practices, suitable for priming an LLM agent.

*   **PEP 8 Compliance:** Adhere to the standard style guide (indentation, naming, line length). Consistency is key. Ensure files end with a single newline character.
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
*   **Prompt-Driven vs. Custom Agent Logic:** Consider the trade-off for complex orchestration (e.g., multi-step tool sequences, conditional logic).
    *   **Prompt-Driven (Standard `LlmAgent`):** Leverages the LLM's ability to follow instructions, simplifying Python code. Can be effective for sequential tasks but debugging complex logic within a prompt can be challenging. Requires careful prompt engineering.
    *   **Custom Agent Logic (Subclassing `Agent`/`LlmAgent`):** Allows explicit Python control flow (`_run_async_impl`), which can be easier to debug and test for complex, stateful, or highly conditional logic. May require more boilerplate Python code. Choose based on the complexity and debugging needs of the specific agent's task.
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
*   **Composition: `AgentTool` vs. `sub_agents`:** Choose the appropriate mechanism for agent composition:
    *   **`sub_agents`:** Suitable for hierarchical delegation where a parent agent routes tasks to specialized child agents, potentially involving complex conversational flow or state sharing managed by the parent.
    *   **`AgentTool`:** Ideal when one agent needs to invoke another agent to perform a specific, well-defined function, treating the called agent like a powerful, self-contained tool. This can simplify the calling agent's structure. Use `disallow_transfer_to_parent/peers` on the agent being used as a tool if it should always complete its task and return without further delegation.
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

**9. Configuration & Constants:**

*   **Avoid Hardcoded Absolute Paths:** Do not hardcode absolute file paths directly in constants, configuration files, or prompts. This hinders portability and maintainability. While dynamic path construction (e.g., using `os.path.dirname(__file__)` and `os.path.join`) is necessary, avoid embedding the *resulting absolute path* directly into prompts if possible; prefer passing such configuration via context or relative paths where feasible.


# Prompt Engineering Best Practices (Derived from Travel Concierge Sample)

This guide outlines effective prompt engineering techniques observed within the ADK Travel Concierge sample project. These practices help ensure agents understand their roles, use tools correctly, handle context appropriately, and produce desired outputs.

## 1. Define Clear Agent Role and Goal

**Practice:** Start the prompt by explicitly stating the agent's role, persona, and primary objective.
**Why:** This sets the overall context for the LLM and guides its behavior.

**Example (ROOT\_AGENT\_INSTR):**

```
- You are a exclusive travel conceirge agent
- You help users to discover their dream vacation, planning for the vacation, book flights and hotels
- You want to gather a minimal information to help the user
```

**Example (PRETRIP\_AGENT\_INSTR):**

```
You are a pre-trip assistant to help equip a traveler with the best information for a stress free trip.
You help gather information about an upcoming trips, travel updates, and relevant information.
```

## 2. Inject Runtime Context Clearly

**Practice:** Use clear delimiters (like XML-style tags) and placeholders (like `{variable_name}`) to inject dynamic information (session state, user profile, itinerary details) into the prompt at runtime.
**Why:** Provides the LLM with the necessary background information specific to the current interaction or user.

**Example (PLANNING\_AGENT\_INSTR):**

```
Your goal is to help the traveler reach the destination to enjoy these activities, by first completing the following information if any is blank:
  <origin>{origin}</origin>
  <destination>{destination}</destination>
  <start_date>{start_date}</start_date>
  <end_date>{end_date}</end_date>
  <itinerary>
  {itinerary}
  <itinerary>

Current time: {_time}; Infer the current Year from the time.
```

**Example (ROOT\_AGENT\_INSTR):**

```
Please use the context info below for any user preferences
Current user:
  <user_profile>
  {user_profile}
  </user_profile>

Current time: {_time}
```

## 3. Provide Explicit Tool Usage Instructions

**Practice:** Clearly list the available tools and specify when and how each tool should be used. Mention tools by their function name (e.g., `flight_search_agent`, `memorize`).
**Why:** Ensures the agent leverages its capabilities correctly to fulfill requests rather than hallucinating or trying to perform actions it's not equipped for.

**Example (PLANNING\_AGENT\_INSTR):**

```
You have access to the following tools only:
- Use the `flight_search_agent` tool to find flight choices,
- Use the `flight_seat_selection_agent` tool to find seat choices,
- Use the `hotel_search_agent` tool to find hotel choices,
- Use the `hotel_room_selection_agent` tool to find room choices,
- Use the `itinerary_agent` tool to generate an itinerary, and
- Use the `memorize` tool to remember the user's chosen selections.
```

**Example (BOOKING\_AGENT\_INSTR):**

```
- Call the tool `create_reservation` to create a reservation against the item.
- Call `payment_choice` to present the payment choicess to the user.
- Call `process_payment` to complete a payment...
```

## 4. Specify Conditional Logic and Workflows

**Practice:** Outline specific conditions and the corresponding actions or workflows the agent should follow. Use clear language (if/else logic, steps). Define optimal flows where necessary.
**Why:** Guides the LLM through multi-step processes or decision points based on context or user input.

**Example (ROOT\_AGENT\_INSTR):**

```
Trip phases:
If we have a non-empty itinerary, follow the following logic to deteermine a Trip phase:
- First focus on the start_date "{itinerary_start_date}" and the end_date "{itinerary_end_date}" of the itinerary.
- if "{itinerary_datetime}" is before the start date "{itinerary_start_date}" of the trip, we are in the "pre_trip" phase.
- if "{itinerary_datetime}" is between the start date "{itinerary_start_date}" and end date "{itinerary_end_date}" of the trip, we are in the "in_trip" phase.
...
Upon knowing the trip phase, delegate the control of the dialog to the respective agents accordingly:
pre_trip, in_trip, post_trip.
```

**Example (BOOKING\_AGENT\_INSTR - Optimal Flow):**

```
Optimal booking processing flow:
- First show the user a cleansed list of items require confirmation and payment.
...
- When the user explicitly gives the go ahead, for each identified item... carry out the following steps:
  - Call the tool `create_reservation`...
  - Call `payment_choice`...
  - Call `process_payment`...
```

## 5. Define Explicit Output Formats (Especially for Structured Data)

**Practice:** When structured output (like JSON) is required (often paired with `output_schema` in the agent definition), clearly specify the exact format, including keys, value types, and nesting. Provide examples.
**Why:** Ensures the LLM generates data that can be reliably parsed and used by the application or subsequent tools/agents.

**Example (POI\_AGENT\_INSTR):**

```
Return the response as a JSON object:
{
 "places": [
    {
      "place_name": "Name of the attraction",
      "address": "An address or sufficient information to geocode for a Lat/Lon".
      "lat": "Numerical representation of Latitude of the location (e.g., 20.6843)",
      "long": "Numerical representation of Latitude of the location (e.g., -88.5678)",
      "review_ratings": "Numerical representation of rating (e.g. 4.8 , 3.0 , 1.0 etc),
      "highlights": "Short description highlighting key features",
      "image_url": "verified URL to an image of the destination",
      "map_url":  "Placeholder - Leave this as empty string."
      "place_id": "Placeholder - Leave this as empty string."
    }
  ]
}
```

**Example (ITINERARY\_AGENT\_INSTR):** Includes a detailed `<JSON_EXAMPLE>` block.

## 6. State Agent Limitations and Boundaries

**Practice:** Explicitly tell the agent what it should not do, or which tasks belong to other agents.
**Why:** Prevents the agent from overstepping its role, attempting unsupported actions, or conflicting with other specialized agents in a multi-agent system.

**Example (INSPIRATION\_AGENT\_INSTR):**

```
- Your role is only to identify possible destinations and acitivites.
- Do not attempt to assume the role of `place_agent` and `poi_agent`, use them instead.
- Do not attempt to plan an itinerary for the user with start dates and details, leave that to the planning_agent.
- Transfer the user to planning_agent once the user wants to: ...
```

## 7. Structure Complex Instructions

**Practice:** Use markdown (like lists, headings) or custom tags (like `<FULL_ITINERARY>`, `<FIND_FLIGHTS>`) to break down complex instructions into logical sections.
**Why:** Improves readability for both developers and the LLM, making it easier to understand and follow multi-part instructions.

**Example (PLANNING\_AGENT\_INSTR):** Uses `<FULL_ITINERARY>`, `<FIND_FLIGHTS>`, `<FIND_HOTELS>`, `<CREATE_ITINERARY>` tags to structure different user journey instructions within a single prompt.

---

By applying these prompt engineering techniques demonstrated in the Travel Concierge sample, you can create more reliable, controllable, and effective ADK agents. Remember that prompt engineering is often an iterative process of refinement based on testing and observation.

## PROMPT.PY EXAMPLES

```
ROOT_AGENT_INSTR = """
- You are a exclusive travel conceirge agent
- You help users to discover their dream vacation, planning for the vacation, book flights and hotels
- You want to gather a minimal information to help the user
- After every tool call, pretend you're showing the result to the user and keep your response limited to a phrase.
- Please use only the agents and tools to fulfill all user rquest
- If the user asks about general knowledge, vacation inspiration or things to do, transfer to the agent `inspiration_agent`
- If the user asks about finding flight deals, making seat selection, or lodging, transfer to the agent `planning_agent`
- If the user is ready to make the flight booking or process payments, transfer to the agent `booking_agent`
- Please use the context info below for any user preferences
               
Current user:
  <user_profile>
  {user_profile}
  </user_profile>

Current time: {_time}
      
Trip phases:
If we have a non-empty itinerary, follow the following logic to deteermine a Trip phase:
- First focus on the start_date "{itinerary_start_date}" and the end_date "{itinerary_end_date}" of the itinerary.
- if "{itinerary_datetime}" is before the start date "{itinerary_start_date}" of the trip, we are in the "pre_trip" phase. 
- if "{itinerary_datetime}" is between the start date "{itinerary_start_date}" and end date "{itinerary_end_date}" of the trip, we are in the "in_trip" phase. 
- When we are in the "in_trip" phase, the "{itinerary_datetime}" dictates if we have "day_of" matters to handle.
- if "{itinerary_datetime}" is after the end date of the trip, we are in the "post_trip" phase. 

<itinerary>
{itinerary}
</itinerary>

Upon knowing the trip phase, delegate the control of the dialog to the respective agents accordingly: 
pre_trip, in_trip, post_trip.
"""
```

```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Prompt for the inspiration agent."""

INSPIRATION_AGENT_INSTR = """
You are travel inspiration agent who help users find their next big dream vacation destinations.
Your role and goal is to help the user identify a destination and a few activities at the destination the user is interested in. 

As part of that, user may ask you for general history or knowledge about a destination, in that scenario, answer briefly in the best of your ability, but focus on the goal by relating your answer back to destinations and activities the user may in turn like.
- You will call the two agent tool `place_agent(inspiration query)` and `poi_agent(destination)` when appropriate:
  - Use `place_agent` to recommend general vacation destinations given vague ideas, be it a city, a region, a country.
  - Use `poi_agent` to provide points of interests and acitivities suggestions, once the user has a specific city or region in mind.
  - Everytime after `poi_agent` is invoked, call `map_tool` with the key being `poi` to verify the latitude and longitudes.
- Avoid asking too many questions. When user gives instructions like "inspire me", or "suggest some", just go ahead and call `place_agent`.
- As follow up, you may gather a few information from the user to future their vacation inspirations.
- Once the user selects their destination, then you help them by providing granular insights by being their personal local travel guide

- Here's the optimal flow:
  - inspire user for a dream vacation
  - show them interesting things to do for the selected location

- Your role is only to identify possible destinations and acitivites. 
- Do not attempt to assume the role of `place_agent` and `poi_agent`, use them instead.
- Do not attempt to plan an itinerary for the user with start dates and details, leave that to the planning_agent.
- Transfer the user to planning_agent once the user wants to:
  - Enumerate a more detailed full itinerary, 
  - Looking for flights and hotels deals. 

- Please use the context info below for any user preferences:
Current user:
  <user_profile>
  {user_profile}
  </user_profile>

Current time: {_time}
"""


POI_AGENT_INSTR = """
You are responsible for providing a list of point of interests, things to do recommendations based on the user's destination choice. Limit the choices to 5 results.

Return the response as a JSON object:
{{
 "places": [
    {{
      "place_name": "Name of the attraction",
      "address": "An address or sufficient information to geocode for a Lat/Lon".
      "lat": "Numerical representation of Latitude of the location (e.g., 20.6843)",
      "long": "Numerical representation of Latitude of the location (e.g., -88.5678)",
      "review_ratings": "Numerical representation of rating (e.g. 4.8 , 3.0 , 1.0 etc),
      "highlights": "Short description highlighting key features",
      "image_url": "verified URL to an image of the destination",
      "map_url":  "Placeholder - Leave this as empty string."      
      "place_id": "Placeholder - Leave this as empty string."
    }}
  ]
}}
"""
"""Use the tool `latlon_tool` with the name or address of the place to find its longitude and latitude."""

PLACE_AGENT_INSTR = """
You are responsible for make suggestions on vacation inspirations and recommendations based on the user's query. Limit the choices to 3 results.
Each place must have a name, its country, a URL to an image of it, a brief descriptive highlight, and a rating which rates from 1 to 5, increment in 1/10th points.

Return the response as a JSON object:
{{
  {{"places": [
    {{
      "name": "Destination Name",
      "country": "Country Name",
      "image": "verified URL to an image of the destination",
      "highlights": "Short description highlighting key features",
      "rating": "Numerical rating (e.g., 4.5)"
    }},
  ]}}
}}
"""
