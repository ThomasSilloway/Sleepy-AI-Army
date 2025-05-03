[Skip to content](https://google.github.io/adk-docs/tools/function-tools/#function-tools)

# Function tools [¶](https://google.github.io/adk-docs/tools/function-tools/\#function-tools "Permanent link")

## What are function tools? [¶](https://google.github.io/adk-docs/tools/function-tools/\#what-are-function-tools "Permanent link")

When out-of-the-box tools don't fully meet specific requirements, developers can create custom function tools. This allows for **tailored functionality**, such as connecting to proprietary databases or implementing unique algorithms.

_For example,_ a function tool, "myfinancetool", might be a function that calculates a specific financial metric. ADK also supports long running functions, so if that calculation takes a while, the agent can continue working on other tasks.

ADK offers several ways to create functions tools, each suited to different levels of complexity and control:

1. Function Tool
2. Long Running Function Tool
3. Agents-as-a-Tool

## 1\. Function Tool [¶](https://google.github.io/adk-docs/tools/function-tools/\#1-function-tool "Permanent link")

Transforming a function into a tool is a straightforward way to integrate custom logic into your agents. This approach offers flexibility and quick integration.

### Parameters [¶](https://google.github.io/adk-docs/tools/function-tools/\#parameters "Permanent link")

Define your function parameters using standard **JSON-serializable types** (e.g., string, integer, list, dictionary). It's important to avoid setting default values for parameters, as the language model (LLM) does not currently support interpreting them.

### Return Type [¶](https://google.github.io/adk-docs/tools/function-tools/\#return-type "Permanent link")

The preferred return type for a Python Function Tool is a **dictionary**. This allows you to structure the response with key-value pairs, providing context and clarity to the LLM. If your function returns a type other than a dictionary, the framework automatically wraps it into a dictionary with a single key named **"result"**.

Strive to make your return values as descriptive as possible. _For example,_ instead of returning a numeric error code, return a dictionary with an "error\_message" key containing a human-readable explanation. **Remember that the LLM**, not a piece of code, needs to understand the result. As a best practice, include a "status" key in your return dictionary to indicate the overall outcome (e.g., "success", "error", "pending"), providing the LLM with a clear signal about the operation's state.

### Docstring [¶](https://google.github.io/adk-docs/tools/function-tools/\#docstring "Permanent link")

The docstring of your function serves as the tool's description and is sent to the LLM. Therefore, a well-written and comprehensive docstring is crucial for the LLM to understand how to use the tool effectively. Clearly explain the purpose of the function, the meaning of its parameters, and the expected return values.

Example

This tool is a python function which obtains the Stock price of a given Stock ticker/ symbol.

Note: You need to `pip install yfinance` library before using this tool.

```md-code__content
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

import yfinance as yf

APP_NAME = "stock_app"
USER_ID = "1234"
SESSION_ID = "session1234"

def get_stock_price(symbol: str):
    """
    Retrieves the current stock price for a given symbol.

    Args:
        symbol (str): The stock symbol (e.g., "AAPL", "GOOG").

    Returns:
        float: The current stock price, or None if an error occurs.
    """
    try:
        stock = yf.Ticker(symbol)
        historical_data = stock.history(period="1d")
        if not historical_data.empty:
            current_price = historical_data['Close'].iloc[-1]
            return current_price
        else:
            return None
    except Exception as e:
        print(f"Error retrieving stock price for {symbol}: {e}")
        return None

stock_price_agent = Agent(
    model='gemini-2.0-flash',
    name='stock_agent',
    instruction= 'You are an agent who retrieves stock prices. If a ticker symbol is provided, fetch the current price. If only a company name is given, first perform a Google search to find the correct ticker symbol before retrieving the stock price. If the provided ticker symbol is invalid or data cannot be retrieved, inform the user that the stock price could not be found.',
    description='This agent specializes in retrieving real-time stock prices. Given a stock ticker symbol (e.g., AAPL, GOOG, MSFT) or the stock name, use the tools and reliable data sources to provide the most up-to-date price.',
    tools=[get_stock_price],
)

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=stock_price_agent, app_name=APP_NAME, session_service=session_service)

# Agent Interaction
def call_agent(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

call_agent("stock price of GOOG")

```

The return value from this tool will be wrapped into a dictionary.

```md-code__content
{"result": "$123"}

```

### Best Practices [¶](https://google.github.io/adk-docs/tools/function-tools/\#best-practices "Permanent link")

While you have considerable flexibility in defining your function, remember that simplicity enhances usability for the LLM. Consider these guidelines:

- **Fewer Parameters are Better:** Minimize the number of parameters to reduce complexity.
- **Simple Data Types:** Favor primitive data types like `str` and `int` over custom classes whenever possible.
- **Meaningful Names:** The function's name and parameter names significantly influence how the LLM interprets and utilizes the tool. Choose names that clearly reflect the function's purpose and the meaning of its inputs. Avoid generic names like `do_stuff()`.

## 2\. Long Running Function Tool [¶](https://google.github.io/adk-docs/tools/function-tools/\#2-long-running-function-tool "Permanent link")

Designed for tasks that require a significant amount of processing time without blocking the agent's execution. This tool is a subclass of `FunctionTool`.

When using a `LongRunningFunctionTool`, your Python function can initiate the long-running operation and optionally return an **intermediate result** to keep the model and user informed about the progress. The agent can then continue with other tasks. An example is the human-in-the-loop scenario where the agent needs human approval before proceeding with a task.

### How it Works [¶](https://google.github.io/adk-docs/tools/function-tools/\#how-it-works "Permanent link")

You wrap a Python _generator_ function (a function using `yield`) with `LongRunningFunctionTool`.

1. **Initiation:** When the LLM calls the tool, your generator function starts executing.

2. **Intermediate Updates ( `yield`):** Your function should yield intermediate Python objects (typically dictionaries) periodically to report progress. The ADK framework takes each yielded value and sends it back to the LLM packaged within a `FunctionResponse`. This allows the LLM to inform the user (e.g., status, percentage complete, messages).

3. **Completion ( `return`):** When the task is finished, the generator function uses `return` to provide the final Python object result.

4. **Framework Handling:** The ADK framework manages the execution. It sends each yielded value back as an intermediate `FunctionResponse`. When the generator completes, the framework sends the returned value as the content of the final `FunctionResponse`, signaling the end of the long-running operation to the LLM.


### Creating the Tool [¶](https://google.github.io/adk-docs/tools/function-tools/\#creating-the-tool "Permanent link")

Define your generator function and wrap it using the `LongRunningFunctionTool` class:

```md-code__content
from google.adk.tools import LongRunningFunctionTool

# Define your generator function (see example below)
def my_long_task_generator(*args, **kwargs):
    # ... setup ...
    yield {"status": "pending", "message": "Starting task..."} # Framework sends this as FunctionResponse
    # ... perform work incrementally ...
    yield {"status": "pending", "progress": 50}               # Framework sends this as FunctionResponse
    # ... finish work ...
    return {"status": "completed", "result": "Final outcome"} # Framework sends this as final FunctionResponse

# Wrap the function
my_tool = LongRunningFunctionTool(func=my_long_task_generator)

```

### Intermediate Updates [¶](https://google.github.io/adk-docs/tools/function-tools/\#intermediate-updates "Permanent link")

Yielding structured Python objects (like dictionaries) is crucial for providing meaningful updates. Include keys like:

- status: e.g., "pending", "running", "waiting\_for\_input"

- progress: e.g., percentage, steps completed

- message: Descriptive text for the user/LLM

- estimated\_completion\_time: If calculable


Each value you yield is packaged into a FunctionResponse by the framework and sent to the LLM.

### Final Result [¶](https://google.github.io/adk-docs/tools/function-tools/\#final-result "Permanent link")

The Python object your generator function returns is considered the final result of the tool execution. The framework packages this value (even if it's None) into the content of the final `FunctionResponse` sent back to the LLM, indicating the tool execution is complete.

Example: File Processing Simulation

```md-code__content
import time
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.tools import LongRunningFunctionTool
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 1. Define the generator function
def process_large_file(file_path: str) -> dict:
    """
    Simulates processing a large file, yielding progress updates.

    Args:
      file_path: Path to the file being processed.

    Returns:
      A final status dictionary.
    """
    total_steps = 5

    # This dict will be sent in the first FunctionResponse
    yield {"status": "pending", "message": f"Starting processing for {file_path}..."}

    for i in range(total_steps):
        time.sleep(1)  # Simulate work for one step
        progress = (i + 1) / total_steps
        # Each yielded dict is sent in a subsequent FunctionResponse
        yield {
            "status": "pending",
            "progress": f"{int(progress * 100)}%",
            "estimated_completion_time": f"~{total_steps - (i + 1)} seconds remaining"
        }

    # This returned dict will be sent in the final FunctionResponse
    return {"status": "completed", "result": f"Successfully processed file: {file_path}"}

# 2. Wrap the function with LongRunningFunctionTool
long_running_tool = LongRunningFunctionTool(func=process_large_file)

# 3. Use the tool in an Agent
file_processor_agent = Agent(
    # Use a model compatible with function calling
    model="gemini-2.0-flash",
    name='file_processor_agent',
    instruction="""You are an agent that processes large files. When the user provides a file path, use the 'process_large_file' tool. Keep the user informed about the progress based on the tool's updates (which arrive as function responses). Only provide the final result when the tool indicates completion in its final function response.""",
    tools=[long_running_tool]
)

APP_NAME = "file_processor"
USER_ID = "1234"
SESSION_ID = "session1234"

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=file_processor_agent, app_name=APP_NAME, session_service=session_service)

# Agent Interaction
def call_agent(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

call_agent("Replace with a path to your file...")

```

#### Key aspects of this example [¶](https://google.github.io/adk-docs/tools/function-tools/\#key-aspects-of-this-example "Permanent link")

- **process\_large\_file**: This generator simulates a lengthy operation, yielding intermediate status/progress dictionaries.

- **`LongRunningFunctionTool`**: Wraps the generator; the framework handles sending yielded updates and the final return value as sequential FunctionResponses.

- **Agent instruction**: Directs the LLM to use the tool and understand the incoming FunctionResponse stream (progress vs. completion) for user updates.

- **Final return**: The function returns the final result dictionary, which is sent in the concluding FunctionResponse to indicate completion.


## 3\. Agent-as-a-Tool [¶](https://google.github.io/adk-docs/tools/function-tools/\#3-agent-as-a-tool "Permanent link")

This powerful feature allows you to leverage the capabilities of other agents within your system by calling them as tools. The Agent-as-a-Tool enables you to invoke another agent to perform a specific task, effectively **delegating responsibility**. This is conceptually similar to creating a Python function that calls another agent and uses the agent's response as the function's return value.

### Key difference from sub-agents [¶](https://google.github.io/adk-docs/tools/function-tools/\#key-difference-from-sub-agents "Permanent link")

It's important to distinguish an Agent-as-a-Tool from a Sub-Agent.

- **Agent-as-a-Tool:** When Agent A calls Agent B as a tool (using Agent-as-a-Tool), Agent B's answer is **passed back** to Agent A, which then summarizes the answer and generates a response to the user. Agent A retains control and continues to handle future user input.

- **Sub-agent:** When Agent A calls Agent B as a sub-agent, the responsibility of answering the user is completely **transferred to Agent B**. Agent A is effectively out of the loop. All subsequent user input will be answered by Agent B.


### Usage [¶](https://google.github.io/adk-docs/tools/function-tools/\#usage "Permanent link")

To use an agent as a tool, wrap the agent with the AgentTool class.

```md-code__content
tools=[AgentTool(agent=agent_b)]

```

### Customization [¶](https://google.github.io/adk-docs/tools/function-tools/\#customization "Permanent link")

The `AgentTool` class provides the following attributes for customizing its behavior:

- **skip\_summarization: bool:** If set to True, the framework will **bypass the LLM-based summarization** of the tool agent's response. This can be useful when the tool's response is already well-formatted and requires no further processing.

Example

```md-code__content
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

APP_NAME="summary_agent"
USER_ID="user1234"
SESSION_ID="1234"

summary_agent = Agent(
    model="gemini-2.0-flash",
    name="summary_agent",
    instruction="""You are an expert summarizer. Please read the following text and provide a concise summary.""",
    description="Agent to summarize text",
)

root_agent = Agent(
    model='gemini-2.0-flash',
    name='root_agent',
    instruction="""You are a helpful assistant. When the user provides a text, use the 'summarize' tool to generate a summary. Always forward the user's message exactly as received to the 'summarize' tool, without modifying or summarizing it yourself. Present the response from the tool to the user.""",
    tools=[AgentTool(agent=summary_agent)]
)

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

# Agent Interaction
def call_agent(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

long_text = """Quantum computing represents a fundamentally different approach to computation,
leveraging the bizarre principles of quantum mechanics to process information. Unlike classical computers
that rely on bits representing either 0 or 1, quantum computers use qubits which can exist in a state of superposition - effectively
being 0, 1, or a combination of both simultaneously. Furthermore, qubits can become entangled,
meaning their fates are intertwined regardless of distance, allowing for complex correlations. This parallelism and
interconnectedness grant quantum computers the potential to solve specific types of incredibly complex problems - such
as drug discovery, materials science, complex system optimization, and breaking certain types of cryptography - far
faster than even the most powerful classical supercomputers could ever achieve, although the technology is still largely in its developmental stages."""

call_agent(long_text)

```

### How it works [¶](https://google.github.io/adk-docs/tools/function-tools/\#how-it-works_1 "Permanent link")

1. When the `main_agent` receives the long text, its instruction tells it to use the 'summarize' tool for long texts.
2. The framework recognizes 'summarize' as an `AgentTool` that wraps the `summary_agent`.
3. Behind the scenes, the `main_agent` will call the `summary_agent` with the long text as input.
4. The `summary_agent` will process the text according to its instruction and generate a summary.
5. **The response from the `summary_agent` is then passed back to the `main_agent`.**
6. The `main_agent` can then take the summary and formulate its final response to the user (e.g., "Here's a summary of the text: ...")

Back to top
