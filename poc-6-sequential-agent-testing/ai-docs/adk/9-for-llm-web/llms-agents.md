[Skip to content](https://google.github.io/adk-docs/agents/llm-agents/#llm-agent)

# LLM Agent [¶](https://google.github.io/adk-docs/agents/llm-agents/\#llm-agent "Permanent link")

The `LlmAgent` (often aliased simply as `Agent`) is a core component in ADK, acting as the "thinking" part of your application. It leverages the power of a Large Language Model (LLM) for reasoning, understanding natural language, making decisions, generating responses, and interacting with tools.

Unlike deterministic [Workflow Agents](https://google.github.io/adk-docs/agents/workflow-agents/) that follow predefined execution paths, `LlmAgent` behavior is non-deterministic. It uses the LLM to interpret instructions and context, deciding dynamically how to proceed, which tools to use (if any), or whether to transfer control to another agent.

Building an effective `LlmAgent` involves defining its identity, clearly guiding its behavior through instructions, and equipping it with the necessary tools and capabilities.

## Defining the Agent's Identity and Purpose [¶](https://google.github.io/adk-docs/agents/llm-agents/\#defining-the-agents-identity-and-purpose "Permanent link")

First, you need to establish what the agent _is_ and what it's _for_.

- **`name` (Required):** Every agent needs a unique string identifier. This `name` is crucial for internal operations, especially in multi-agent systems where agents need to refer to or delegate tasks to each other. Choose a descriptive name that reflects the agent's function (e.g., `customer_support_router`, `billing_inquiry_agent`). Avoid reserved names like `user`.

- **`description` (Optional, Recommended for Multi-Agent):** Provide a concise summary of the agent's capabilities. This description is primarily used by _other_ LLM agents to determine if they should route a task to this agent. Make it specific enough to differentiate it from peers (e.g., "Handles inquiries about current billing statements," not just "Billing agent").

- **`model` (Required):** Specify the underlying LLM that will power this agent's reasoning. This is a string identifier like `"gemini-2.0-flash"`. The choice of model impacts the agent's capabilities, cost, and performance. See the [Models](https://google.github.io/adk-docs/agents/models/) page for available options and considerations.


```md-code__content
# Example: Defining the basic identity
capital_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="capital_agent",
    description="Answers user questions about the capital city of a given country."
    # instruction and tools will be added next
)

```

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

## Advanced Configuration & Control [¶](https://google.github.io/adk-docs/agents/llm-agents/\#advanced-configuration-control "Permanent link")

Beyond the core parameters, `LlmAgent` offers several options for finer control:

### Fine-Tuning LLM Generation ( `generate_content_config`) [¶](https://google.github.io/adk-docs/agents/llm-agents/\#fine-tuning-llm-generation-generate_content_config "Permanent link")

You can adjust how the underlying LLM generates responses using `generate_content_config`.

- **`generate_content_config` (Optional):** Pass an instance of `google.genai.types.GenerateContentConfig` to control parameters like `temperature` (randomness), `max_output_tokens` (response length), `top_p`, `top_k`, and safety settings.



```md-code__content
from google.genai import types

agent = LlmAgent(
      # ... other params
      generate_content_config=types.GenerateContentConfig(
          temperature=0.2, # More deterministic output
          max_output_tokens=250
      )
)

```


### Structuring Data ( `input_schema`, `output_schema`, `output_key`) [¶](https://google.github.io/adk-docs/agents/llm-agents/\#structuring-data-input_schema-output_schema-output_key "Permanent link")

For scenarios requiring structured data exchange, you can use Pydantic models.

- **`input_schema` (Optional):** Define a Pydantic `BaseModel` class representing the expected input structure. If set, the user message content passed to this agent _must_ be a JSON string conforming to this schema. Your instructions should guide the user or preceding agent accordingly.

- **`output_schema` (Optional):** Define a Pydantic `BaseModel` class representing the desired output structure. If set, the agent's final response _must_ be a JSON string conforming to this schema.
  - **Constraint:** Using `output_schema` enables controlled generation within the LLM but **disables the agent's ability to use tools or transfer control to other agents**. Your instructions must guide the LLM to produce JSON matching the schema directly.
- **`output_key` (Optional):** Provide a string key. If set, the text content of the agent's _final_ response will be automatically saved to the session's state dictionary under this key (e.g., `session.state[output_key] = agent_response_text`). This is useful for passing results between agents or steps in a workflow.


```md-code__content
from pydantic import BaseModel, Field

class CapitalOutput(BaseModel):
    capital: str = Field(description="The capital of the country.")

structured_capital_agent = LlmAgent(
    # ... name, model, description
    instruction="""You are a Capital Information Agent. Given a country, respond ONLY with a JSON object containing the capital. Format: {"capital": "capital_name"}""",
    output_schema=CapitalOutput, # Enforce JSON output
    output_key="found_capital"  # Store result in state['found_capital']
    # Cannot use tools=[get_capital_city] effectively here
)

```

### Managing Context ( `include_contents`) [¶](https://google.github.io/adk-docs/agents/llm-agents/\#managing-context-include_contents "Permanent link")

Control whether the agent receives the prior conversation history.

- **`include_contents` (Optional, Default: `'default'`):** Determines if the `contents` (history) are sent to the LLM.


  - `'default'`: The agent receives the relevant conversation history.
  - `'none'`: The agent receives no prior `contents`. It operates based solely on its current instruction and any input provided in the _current_ turn (useful for stateless tasks or enforcing specific contexts).

```md-code__content
stateless_agent = LlmAgent(
    # ... other params
    include_contents='none'
)

```

### Planning & Code Execution [¶](https://google.github.io/adk-docs/agents/llm-agents/\#planning-code-execution "Permanent link")

For more complex reasoning involving multiple steps or executing code:

- **`planner` (Optional):** Assign a `BasePlanner` instance to enable multi-step reasoning and planning before execution. (See [Multi-Agents](https://google.github.io/adk-docs/agents/multi-agents/) patterns).
- **`code_executor` (Optional):** Provide a `BaseCodeExecutor` instance to allow the agent to execute code blocks (e.g., Python) found in the LLM's response. ( [See Tools/Built-in tools](https://google.github.io/adk-docs/tools/built-in-tools/)).

## Putting It Together: Example [¶](https://google.github.io/adk-docs/agents/llm-agents/\#putting-it-together-example "Permanent link")

Code

Here's the complete basic `capital_agent`:

```md-code__content
# Full example code for the basic capital agent
# --- Full example code demonstrating LlmAgent with Tools vs. Output Schema ---
import json # Needed for pretty printing dicts

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field

# --- 1. Define Constants ---
APP_NAME = "agent_comparison_app"
USER_ID = "test_user_456"
SESSION_ID_TOOL_AGENT = "session_tool_agent_xyz"
SESSION_ID_SCHEMA_AGENT = "session_schema_agent_xyz"
MODEL_NAME = "gemini-2.0-flash"

# --- 2. Define Schemas ---

# Input schema used by both agents
class CountryInput(BaseModel):
    country: str = Field(description="The country to get information about.")

# Output schema ONLY for the second agent
class CapitalInfoOutput(BaseModel):
    capital: str = Field(description="The capital city of the country.")
    # Note: Population is illustrative; the LLM will infer or estimate this
    # as it cannot use tools when output_schema is set.
    population_estimate: str = Field(description="An estimated population of the capital city.")

# --- 3. Define the Tool (Only for the first agent) ---
def get_capital_city(country: str) -> str:
    """Retrieves the capital city of a given country."""
    print(f"\n-- Tool Call: get_capital_city(country='{country}') --")
    country_capitals = {
        "united states": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "japan": "Tokyo",
    }
    result = country_capitals.get(country.lower(), f"Sorry, I couldn't find the capital for {country}.")
    print(f"-- Tool Result: '{result}' --")
    return result

# --- 4. Configure Agents ---

# Agent 1: Uses a tool and output_key
capital_agent_with_tool = LlmAgent(
    model=MODEL_NAME,
    name="capital_agent_tool",
    description="Retrieves the capital city using a specific tool.",
    instruction="""You are a helpful agent that provides the capital city of a country using a tool.
The user will provide the country name in a JSON format like {"country": "country_name"}.
1. Extract the country name.
2. Use the `get_capital_city` tool to find the capital.
3. Respond clearly to the user, stating the capital city found by the tool.
""",
    tools=[get_capital_city],
    input_schema=CountryInput,
    output_key="capital_tool_result", # Store final text response
)

# Agent 2: Uses output_schema (NO tools possible)
structured_info_agent_schema = LlmAgent(
    model=MODEL_NAME,
    name="structured_info_agent_schema",
    description="Provides capital and estimated population in a specific JSON format.",
    instruction=f"""You are an agent that provides country information.
The user will provide the country name in a JSON format like {{"country": "country_name"}}.
Respond ONLY with a JSON object matching this exact schema:
{json.dumps(CapitalInfoOutput.model_json_schema(), indent=2)}
Use your knowledge to determine the capital and estimate the population. Do not use any tools.
""",
    # *** NO tools parameter here - using output_schema prevents tool use ***
    input_schema=CountryInput,
    output_schema=CapitalInfoOutput, # Enforce JSON output structure
    output_key="structured_info_result", # Store final JSON response
)

# --- 5. Set up Session Management and Runners ---
session_service = InMemorySessionService()

# Create separate sessions for clarity, though not strictly necessary if context is managed
session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_TOOL_AGENT)
session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_SCHEMA_AGENT)

# Create a runner for EACH agent
capital_runner = Runner(
    agent=capital_agent_with_tool,
    app_name=APP_NAME,
    session_service=session_service
)
structured_runner = Runner(
    agent=structured_info_agent_schema,
    app_name=APP_NAME,
    session_service=session_service
)

# --- 6. Define Agent Interaction Logic ---
async def call_agent_and_print(
    runner_instance: Runner,
    agent_instance: LlmAgent,
    session_id: str,
    query_json: str
):
    """Sends a query to the specified agent/runner and prints results."""
    print(f"\n>>> Calling Agent: '{agent_instance.name}' | Query: {query_json}")

    user_content = types.Content(role='user', parts=[types.Part(text=query_json)])

    final_response_content = "No final response received."
    async for event in runner_instance.run_async(user_id=USER_ID, session_id=session_id, new_message=user_content):
        # print(f"Event: {event.type}, Author: {event.author}") # Uncomment for detailed logging
        if event.is_final_response() and event.content and event.content.parts:
            # For output_schema, the content is the JSON string itself
            final_response_content = event.content.parts[0].text

    print(f"<<< Agent '{agent_instance.name}' Response: {final_response_content}")

    current_session = session_service.get_session(app_name=APP_NAME,
                                                  user_id=USER_ID,
                                                  session_id=session_id)
    stored_output = current_session.state.get(agent_instance.output_key)

    # Pretty print if the stored output looks like JSON (likely from output_schema)
    print(f"--- Session State ['{agent_instance.output_key}']: ", end="")
    try:
        # Attempt to parse and pretty print if it's JSON
        parsed_output = json.loads(stored_output)
        print(json.dumps(parsed_output, indent=2))
    except (json.JSONDecodeError, TypeError):
         # Otherwise, print as string
        print(stored_output)
    print("-" * 30)

# --- 7. Run Interactions ---
async def main():
    print("--- Testing Agent with Tool ---")
    await call_agent_and_print(capital_runner, capital_agent_with_tool, SESSION_ID_TOOL_AGENT, '{"country": "France"}')
    await call_agent_and_print(capital_runner, capital_agent_with_tool, SESSION_ID_TOOL_AGENT, '{"country": "Canada"}')

    print("\n\n--- Testing Agent with Output Schema (No Tool Use) ---")
    await call_agent_and_print(structured_runner, structured_info_agent_schema, SESSION_ID_SCHEMA_AGENT, '{"country": "France"}')
    await call_agent_and_print(structured_runner, structured_info_agent_schema, SESSION_ID_SCHEMA_AGENT, '{"country": "Japan"}')

if __name__ == "__main__":
    await main()

```

_(This example demonstrates the core concepts. More complex agents might incorporate schemas, context control, planning, etc.)_

## Related Concepts (Deferred Topics) [¶](https://google.github.io/adk-docs/agents/llm-agents/\#related-concepts-deferred-topics "Permanent link")

While this page covers the core configuration of `LlmAgent`, several related concepts provide more advanced control and are detailed elsewhere:

- **Callbacks:** Intercepting execution points (before/after model calls, before/after tool calls) using `before_model_callback`, `after_model_callback`, etc. See [Callbacks](https://google.github.io/adk-docs/callbacks/types-of-callbacks/).
- **Multi-Agent Control:** Advanced strategies for agent interaction, including planning ( `planner`), controlling agent transfer ( `disallow_transfer_to_parent`, `disallow_transfer_to_peers`), and system-wide instructions ( `global_instruction`). See [Multi-Agents](https://google.github.io/adk-docs/agents/multi-agents/).

Back to top