[Skip to content](https://google.github.io/adk-docs/tools/#tools)

# Tools [¶](https://google.github.io/adk-docs/tools/\#tools "Permanent link")

## What is a Tool? [¶](https://google.github.io/adk-docs/tools/\#what-is-a-tool "Permanent link")

In the context of ADK, a Tool represents a specific
capability provided to an AI agent, enabling it to perform actions and interact
with the world beyond its core text generation and reasoning abilities. What
distinguishes capable agents from basic language models is often their effective
use of tools.

Technically, a tool is typically a modular code component— **like a Python**
**function**, a class method, or even another specialized agent—designed to
execute a distinct, predefined task. These tasks often involve interacting with
external systems or data.

![Agent tool call](https://google.github.io/adk-docs/assets/agent-tool-call.png)

### Key Characteristics [¶](https://google.github.io/adk-docs/tools/\#key-characteristics "Permanent link")

**Action-Oriented:** Tools perform specific actions, such as:

- Querying databases
- Making API requests (e.g., fetching weather data, booking systems)
- Searching the web
- Executing code snippets
- Retrieving information from documents (RAG)
- Interacting with other software or services

**Extends Agent capabilities:** They empower agents to access real-time information, affect external systems, and overcome the knowledge limitations inherent in their training data.

**Execute predefined logic:** Crucially, tools execute specific, developer-defined logic. They do not possess their own independent reasoning capabilities like the agent's core Large Language Model (LLM). The LLM reasons about which tool to use, when, and with what inputs, but the tool itself just executes its designated function.

## How Agents Use Tools [¶](https://google.github.io/adk-docs/tools/\#how-agents-use-tools "Permanent link")

Agents leverage tools dynamically through mechanisms often involving function calling. The process generally follows these steps:

1. **Reasoning:** The agent's LLM analyzes its system instruction, conversation history, and user request.
2. **Selection:** Based on the analysis, the LLM decides on which tool, if any, to execute, based on the tools available to the agent and the docstrings that describes each tool.
3. **Invocation:** The LLM generates the required arguments (inputs) for the selected tool and triggers its execution.
4. **Observation:** The agent receives the output (result) returned by the tool.
5. **Finalization:** The agent incorporates the tool's output into its ongoing reasoning process to formulate the next response, decide the subsequent step, or determine if the goal has been achieved.

Think of the tools as a specialized toolkit that the agent's intelligent core (the LLM) can access and utilize as needed to accomplish complex tasks.

## Tool Types in ADK [¶](https://google.github.io/adk-docs/tools/\#tool-types-in-adk "Permanent link")

ADK offers flexibility by supporting several types of tools:

1. **[Function Tools](https://google.github.io/adk-docs/tools/function-tools/):** Tools created by you, tailored to your specific application's needs.
   - **[Functions/Methods](https://google.github.io/adk-docs/tools/function-tools/#1-function-tool):** Define standard synchronous functions or methods in your code (e.g., Python def).
   - **[Agents-as-Tools](https://google.github.io/adk-docs/tools/function-tools/#3-agent-as-a-tool):** Use another, potentially specialized, agent as a tool for a parent agent.
   - **[Long Running Function Tools](https://google.github.io/adk-docs/tools/function-tools/#2-long-running-function-tool):** Support for tools that perform asynchronous operations or take significant time to complete.
2. **[Built-in Tools](https://google.github.io/adk-docs/tools/built-in-tools/):** Ready-to-use tools provided by the framework for common tasks.
    Examples: Google Search, Code Execution, Retrieval-Augmented Generation (RAG).
3. **[Third-Party Tools](https://google.github.io/adk-docs/tools/third-party-tools/):** Integrate tools seamlessly from popular external libraries.
    Examples: LangChain Tools, CrewAI Tools.

Navigate to the respective documentation pages linked above for detailed information and examples for each tool type.

## Referencing Tool in Agent’s Instructions [¶](https://google.github.io/adk-docs/tools/\#referencing-tool-in-agents-instructions "Permanent link")

Within an agent's instructions, you can directly reference a tool by using its **function name.** If the tool's **function name** and **docstring** are sufficiently descriptive, your instructions can primarily focus on **when the Large Language Model (LLM) should utilize the tool**. This promotes clarity and helps the model understand the intended use of each tool.

It is **crucial to clearly instruct the agent on how to handle different return values** that a tool might produce. For example, if a tool returns an error message, your instructions should specify whether the agent should retry the operation, give up on the task, or request additional information from the user.

Furthermore, ADK supports the sequential use of tools, where the output of one tool can serve as the input for another. When implementing such workflows, it's important to **describe the intended sequence of tool usage** within the agent's instructions to guide the model through the necessary steps.

### Example [¶](https://google.github.io/adk-docs/tools/\#example "Permanent link")

The following example showcases how an agent can use tools by **referencing their function names in its instructions**. It also demonstrates how to guide the agent to **handle different return values from tools**, such as success or error messages, and how to orchestrate the **sequential use of multiple tools** to accomplish a task.

```md-code__content
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

APP_NAME="weather_sentiment_agent"
USER_ID="user1234"
SESSION_ID="1234"
MODEL_ID="gemini-2.0-flash"

# Tool 1
def get_weather_report(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Returns:
        dict: A dictionary containing the weather information with a 'status' key ('success' or 'error') and a 'report' key with the weather details if successful, or an 'error_message' if an error occurred.
    """
    if city.lower() == "london":
        return {"status": "success", "report": "The current weather in London is cloudy with a temperature of 18 degrees Celsius and a chance of rain."}
    elif city.lower() == "paris":
        return {"status": "success", "report": "The weather in Paris is sunny with a temperature of 25 degrees Celsius."}
    else:
        return {"status": "error", "error_message": f"Weather information for '{city}' is not available."}

weather_tool = FunctionTool(func=get_weather_report)

# Tool 2
def analyze_sentiment(text: str) -> dict:
    """Analyzes the sentiment of the given text.

    Returns:
        dict: A dictionary with 'sentiment' ('positive', 'negative', or 'neutral') and a 'confidence' score.
    """
    if "good" in text.lower() or "sunny" in text.lower():
        return {"sentiment": "positive", "confidence": 0.8}
    elif "rain" in text.lower() or "bad" in text.lower():
        return {"sentiment": "negative", "confidence": 0.7}
    else:
        return {"sentiment": "neutral", "confidence": 0.6}

sentiment_tool = FunctionTool(func=analyze_sentiment)

# Agent
weather_sentiment_agent = Agent(
    model=MODEL_ID,
    name='weather_sentiment_agent',
    instruction="""You are a helpful assistant that provides weather information and analyzes the sentiment of user feedback.
**If the user asks about the weather in a specific city, use the 'get_weather_report' tool to retrieve the weather details.**
**If the 'get_weather_report' tool returns a 'success' status, provide the weather report to the user.**
**If the 'get_weather_report' tool returns an 'error' status, inform the user that the weather information for the specified city is not available and ask if they have another city in mind.**
**After providing a weather report, if the user gives feedback on the weather (e.g., 'That's good' or 'I don't like rain'), use the 'analyze_sentiment' tool to understand their sentiment.** Then, briefly acknowledge their sentiment.
You can handle these tasks sequentially if needed.""",
    tools=[weather_tool, sentiment_tool]
)

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=weather_sentiment_agent, app_name=APP_NAME, session_service=session_service)

# Agent Interaction
def call_agent(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

call_agent("weather in london?")

```

## Tool Context [¶](https://google.github.io/adk-docs/tools/\#tool-context "Permanent link")

For more advanced scenarios, ADK allows you to access additional contextual information within your tool function by including the special parameter `tool_context: ToolContext`. By including this in the function signature, ADK will **automatically** provide an **instance of the ToolContext** class when your tool is called during agent execution.

The **ToolContext** provides access to several key pieces of information and control levers:

- `state: State`: Read and modify the current session's state. Changes made here are tracked and persisted.

- `actions: EventActions`: Influence the agent's subsequent actions after the tool runs (e.g., skip summarization, transfer to another agent).

- `function_call_id: str`: The unique identifier assigned by the framework to this specific invocation of the tool. Useful for tracking and correlating with authentication responses. This can also be helpful when multiple tools are called within a single model response.

- `function_call_event_id: str`: This attribute provides the unique identifier of the **event** that triggered the current tool call. This can be useful for tracking and logging purposes.

- `auth_response: Any`: Contains the authentication response/credentials if an authentication flow was completed before this tool call.

- Access to Services: Methods to interact with configured services like Artifacts and Memory.


### **State Management** [¶](https://google.github.io/adk-docs/tools/\#state-management "Permanent link")

The `tool_context.state` attribute provides direct read and write access to the state associated with the current session. It behaves like a dictionary but ensures that any modifications are tracked as deltas and persisted by the session service. This enables tools to maintain and share information across different interactions and agent steps.

- **Reading State**: Use standard dictionary access ( `tool_context.state['my_key']`) or the `.get()` method ( `tool_context.state.get('my_key', default_value)`).

- **Writing State**: Assign values directly ( `tool_context.state['new_key'] = 'new_value'`). These changes are recorded in the state\_delta of the resulting event.

- **State Prefixes**: Remember the standard state prefixes:
  - `app:*`: Shared across all users of the application.

  - `user:*`: Specific to the current user across all their sessions.

  - (No prefix): Specific to the current session.

  - `temp:*`: Temporary, not persisted across invocations (useful for passing data within a single run call but generally less useful inside a tool context which operates between LLM calls).

```md-code__content
from google.adk.tools import ToolContext, FunctionTool

def update_user_preference(preference: str, value: str, tool_context: ToolContext):
    """Updates a user-specific preference."""
    user_prefs_key = "user:preferences"
    # Get current preferences or initialize if none exist
    preferences = tool_context.state.get(user_prefs_key, {})
    preferences[preference] = value
    # Write the updated dictionary back to the state
    tool_context.state[user_prefs_key] = preferences
    print(f"Tool: Updated user preference '{preference}' to '{value}'")
    return {"status": "success", "updated_preference": preference}

pref_tool = FunctionTool(func=update_user_preference)

# In an Agent:
# my_agent = Agent(..., tools=[pref_tool])

# When the LLM calls update_user_preference(preference='theme', value='dark', ...):
# The tool_context.state will be updated, and the change will be part of the
# resulting tool response event's actions.state_delta.

```

### **Controlling Agent Flow** [¶](https://google.github.io/adk-docs/tools/\#controlling-agent-flow "Permanent link")

The `tool_context.actions` attribute holds an **EventActions** object. Modifying attributes on this object allows your tool to influence what the agent or framework does after the tool finishes execution.

- **`skip_summarization: bool`**: (Default: False) If set to True, instructs the ADK to bypass the LLM call that typically summarizes the tool's output. This is useful if your tool's return value is already a user-ready message.

- **`transfer_to_agent: str`**: Set this to the name of another agent. The framework will halt the current agent's execution and **transfer control of the conversation to the specified agent**. This allows tools to dynamically hand off tasks to more specialized agents.

- **`escalate: bool`**: (Default: False) Setting this to True signals that the current agent cannot handle the request and should pass control up to its parent agent (if in a hierarchy). In a LoopAgent, setting **escalate=True** in a sub-agent's tool will terminate the loop.


#### Example [¶](https://google.github.io/adk-docs/tools/\#example_1 "Permanent link")

```md-code__content
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types

APP_NAME="customer_support_agent"
USER_ID="user1234"
SESSION_ID="1234"

def check_and_transfer(query: str, tool_context: ToolContext) -> str:
    """Checks if the query requires escalation and transfers to another agent if needed."""
    if "urgent" in query.lower():
        print("Tool: Detected urgency, transferring to the support agent.")
        tool_context.actions.transfer_to_agent = "support_agent"
        return "Transferring to the support agent..."
    else:
        return f"Processed query: '{query}'. No further action needed."

escalation_tool = FunctionTool(func=check_and_transfer)

main_agent = Agent(
    model='gemini-2.0-flash',
    name='main_agent',
    instruction="""You are the first point of contact for customer support of an analytics tool. Answer general queries. If the user indicates urgency, use the 'check_and_transfer' tool.""",
    tools=[check_and_transfer]
)

support_agent = Agent(
    model='gemini-2.0-flash',
    name='support_agent',
    instruction="""You are the dedicated support agent. Mentioned you are a support handler and please help the user with their urgent issue."""
)

main_agent.sub_agents = [support_agent]

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=main_agent, app_name=APP_NAME, session_service=session_service)

# Agent Interaction
def call_agent(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

call_agent("this is urgent, i cant login")

```

##### Explanation [¶](https://google.github.io/adk-docs/tools/\#explanation "Permanent link")

- We define two agents: `main_agent` and `support_agent`. The `main_agent` is designed to be the initial point of contact.
- The `check_and_transfer` tool, when called by `main_agent`, examines the user's query.
- If the query contains the word "urgent", the tool accesses the `tool_context`, specifically **`tool_context.actions`**, and sets the transfer\_to\_agent attribute to `support_agent`.
- This action signals to the framework to **transfer the control of the conversation to the agent named `support_agent`**.
- When the `main_agent` processes the urgent query, the `check_and_transfer` tool triggers the transfer. The subsequent response would ideally come from the `support_agent`.
- For a normal query without urgency, the tool simply processes it without triggering a transfer.

This example illustrates how a tool, through EventActions in its ToolContext, can dynamically influence the flow of the conversation by transferring control to another specialized agent.

### **Authentication** [¶](https://google.github.io/adk-docs/tools/\#authentication "Permanent link")

ToolContext provides mechanisms for tools interacting with authenticated APIs. If your tool needs to handle authentication, you might use the following:

- **`auth_response`**: Contains credentials (e.g., a token) if authentication was already handled by the framework before your tool was called (common with RestApiTool and OpenAPI security schemes).

- **`request_credential(auth_config: dict)`**: Call this method if your tool determines authentication is needed but credentials aren't available. This signals the framework to start an authentication flow based on the provided auth\_config.

- **`get_auth_response()`**: Call this in a subsequent invocation (after request\_credential was successfully handled) to retrieve the credentials the user provided.


For detailed explanations of authentication flows, configuration, and examples, please refer to the dedicated Tool Authentication documentation page.

### **Context-Aware Data Access Methods** [¶](https://google.github.io/adk-docs/tools/\#context-aware-data-access-methods "Permanent link")

These methods provide convenient ways for your tool to interact with persistent data associated with the session or user, managed by configured services.

- **`list_artifacts()`**: Returns a list of filenames (or keys) for all artifacts currently stored for the session via the artifact\_service. Artifacts are typically files (images, documents, etc.) uploaded by the user or generated by tools/agents.

- **`load_artifact(filename: str)`**: Retrieves a specific artifact by its filename from the **artifact\_service**. You can optionally specify a version; if omitted, the latest version is returned. Returns a `google.genai.types.Part` object containing the artifact data and mime type, or None if not found.

- **`save_artifact(filename: str, artifact: types.Part)`**: Saves a new version of an artifact to the artifact\_service. Returns the new version number (starting from 0).

- **`search_memory(query: str)`**: Queries the user's long-term memory using the configured `memory_service`. This is useful for retrieving relevant information from past interactions or stored knowledge. The structure of the **SearchMemoryResponse** depends on the specific memory service implementation but typically contains relevant text snippets or conversation excerpts.


#### Example [¶](https://google.github.io/adk-docs/tools/\#example_2 "Permanent link")

```md-code__content
from google.adk.tools import ToolContext, FunctionTool
from google.genai import types

def process_document(document_name: str, analysis_query: str, tool_context: ToolContext) -> dict:
    """Analyzes a document using context from memory."""

    # 1. Load the artifact
    print(f"Tool: Attempting to load artifact: {document_name}")
    document_part = tool_context.load_artifact(document_name)

    if not document_part:
        return {"status": "error", "message": f"Document '{document_name}' not found."}

    document_text = document_part.text # Assuming it's text for simplicity
    print(f"Tool: Loaded document '{document_name}' ({len(document_text)} chars).")

    # 2. Search memory for related context
    print(f"Tool: Searching memory for context related to: '{analysis_query}'")
    memory_response = tool_context.search_memory(f"Context for analyzing document about {analysis_query}")
    memory_context = "\n".join([m.events[0].content.parts[0].text for m in memory_response.memories if m.events and m.events[0].content]) # Simplified extraction
    print(f"Tool: Found memory context: {memory_context[:100]}...")

    # 3. Perform analysis (placeholder)
    analysis_result = f"Analysis of '{document_name}' regarding '{analysis_query}' using memory context: [Placeholder Analysis Result]"
    print("Tool: Performed analysis.")

    # 4. Save the analysis result as a new artifact
    analysis_part = types.Part.from_text(text=analysis_result)
    new_artifact_name = f"analysis_{document_name}"
    version = tool_context.save_artifact(new_artifact_name, analysis_part)
    print(f"Tool: Saved analysis result as '{new_artifact_name}' version {version}.")

    return {"status": "success", "analysis_artifact": new_artifact_name, "version": version}

doc_analysis_tool = FunctionTool(func=process_document)

# In an Agent:
# Assume artifact 'report.txt' was previously saved.
# Assume memory service is configured and has relevant past data.
# my_agent = Agent(..., tools=[doc_analysis_tool], artifact_service=..., memory_service=...)

```

By leveraging the **ToolContext**, developers can create more sophisticated and context-aware custom tools that seamlessly integrate with ADK's architecture and enhance the overall capabilities of their agents.

## Defining Effective Tool Functions [¶](https://google.github.io/adk-docs/tools/\#defining-effective-tool-functions "Permanent link")

When using a standard Python function as an ADK Tool, how you define it significantly impacts the agent's ability to use it correctly. The agent's Large Language Model (LLM) relies heavily on the function's **name**, **parameters (arguments)**, **type hints**, and **docstring** to understand its purpose and generate the correct call.

Here are key guidelines for defining effective tool functions:

- **Function Name:**
  - Use descriptive, verb-noun based names that clearly indicate the action (e.g., `get_weather`, `search_documents`, `schedule_meeting`).
  - Avoid generic names like `run`, `process`, `handle_data`, or overly ambiguous names like `do_stuff`. Even with a good description, a name like `do_stuff` might confuse the model about when to use the tool versus, for example, `cancel_flight`.
  - The LLM uses the function name as a primary identifier during tool selection.
- **Parameters (Arguments):**
  - Your function can have any number of parameters.
  - Use clear and descriptive names (e.g., `city` instead of `c`, `search_query` instead of `q`).
  - **Provide type hints** for all parameters (e.g., `city: str`, `user_id: int`, `items: list[str]`). This is essential for ADK to generate the correct schema for the LLM.
  - Ensure all parameter types are **JSON serializable**. Standard Python types like `str`, `int`, `float`, `bool`, `list`, `dict`, and their combinations are generally safe. Avoid complex custom class instances as direct parameters unless they have a clear JSON representation.
  - **Do not set default values** for parameters. E.g., `def my_func(param1: str = "default")`. Default values are not reliably supported or used by the underlying models during function call generation. All necessary information should be derived by the LLM from the context or explicitly requested if missing.
- **Return Type:**
  - The function's return value **must be a dictionary ( `dict`)**.
  - If your function returns a non-dictionary type (e.g., a string, number, list), the ADK framework will automatically wrap it into a dictionary like `{'result': your_original_return_value}` before passing the result back to the model.
  - Design the dictionary keys and values to be **descriptive and easily understood _by the LLM_**. Remember, the model reads this output to decide its next step.
  - Include meaningful keys. For example, instead of returning just an error code like `500`, return `{'status': 'error', 'error_message': 'Database connection failed'}`.
  - It's a **highly recommended practice** to include a `status` key (e.g., `'success'`, `'error'`, `'pending'`, `'ambiguous'`) to clearly indicate the outcome of the tool execution for the model.
- **Docstring:**


  - **This is critical.** The docstring is the primary source of descriptive information for the LLM.
  - **Clearly state what the tool _does_.** Be specific about its purpose and limitations.
  - **Explain _when_ the tool should be used.** Provide context or example scenarios to guide the LLM's decision-making.
  - **Describe _each parameter_ clearly.** Explain what information the LLM needs to provide for that argument.
  - Describe the **structure and meaning of the expected `dict` return value**, especially the different `status` values and associated data keys.

**Example of a good definition:**

```md-code__content
def lookup_order_status(order_id: str) -> dict:
  """Fetches the current status of a customer's order using its ID.

  Use this tool ONLY when a user explicitly asks for the status of
  a specific order and provides the order ID. Do not use it for
  general inquiries.

  Args:
      order_id: The unique identifier of the order to look up.

  Returns:
      A dictionary containing the order status.
      Possible statuses: 'shipped', 'processing', 'pending', 'error'.
      Example success: {'status': 'shipped', 'tracking_number': '1Z9...'}
      Example error: {'status': 'error', 'error_message': 'Order ID not found.'}
  """
  # ... function implementation to fetch status ...
  if status := fetch_status_from_backend(order_id):
       return {"status": status.state, "tracking_number": status.tracking} # Example structure
  else:
       return {"status": "error", "error_message": f"Order ID {order_id} not found."}

```

- **Simplicity and Focus:**
  - **Keep Tools Focused:** Each tool should ideally perform one well-defined task.
  - **Fewer Parameters are Better:** Models generally handle tools with fewer, clearly defined parameters more reliably than those with many optional or complex ones.
  - **Use Simple Data Types:** Prefer basic types ( `str`, `int`, `bool`, `float`, `List[str]`, etc.) over complex custom classes or deeply nested structures as parameters when possible.
  - **Decompose Complex Tasks:** Break down functions that perform multiple distinct logical steps into smaller, more focused tools. For instance, instead of a single `update_user_profile(profile: ProfileObject)` tool, consider separate tools like `update_user_name(name: str)`, `update_user_address(address: str)`, `update_user_preferences(preferences: list[str])`, etc. This makes it easier for the LLM to select and use the correct capability.

By adhering to these guidelines, you provide the LLM with the clarity and structure it needs to effectively utilize your custom function tools, leading to more capable and reliable agent behavior.

Back to top