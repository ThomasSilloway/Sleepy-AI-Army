[Skip to content](https://google.github.io/adk-docs/get-started/quickstart/#quickstart)

# Quickstart [¶](https://google.github.io/adk-docs/get-started/quickstart/\#quickstart "Permanent link")

This quickstart guides you through installing the Agent Development Kit (ADK),
setting up a basic agent with multiple tools, and running it locally either in the terminal or in the interactive, browser-based dev UI.

This quickstart assumes a local IDE (VS Code, PyCharm, etc.) with Python 3.9+
and terminal access. This method runs the application entirely on your machine
and is recommended for internal development.

## 1\. Set up Environment & Install ADK [¶](https://google.github.io/adk-docs/get-started/quickstart/\#venv-install "Permanent link")

Create & Activate Virtual Environment (Recommended):

```md-code__content
# Create
python -m venv .venv
# Activate (each new terminal)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1

```

Install ADK:

```md-code__content
pip install google-adk

```

## 2\. Create Agent Project [¶](https://google.github.io/adk-docs/get-started/quickstart/\#create-agent-project "Permanent link")

### Project structure [¶](https://google.github.io/adk-docs/get-started/quickstart/\#project-structure "Permanent link")

You will need to create the following project structure:

```md-code__content
parent_folder/
    multi_tool_agent/
        __init__.py
        agent.py
        .env

```

Create the folder `multi_tool_agent`:

```md-code__content
mkdir multi_tool_agent/

```

Note for Windows users

When using ADK on Windows for the next few steps, we recommend creating
Python files using File Explorer or an IDE because the following commands
( `mkdir`, `echo`) typically generate files with null bytes and/or incorrect
encoding.

### `__init__.py` [¶](https://google.github.io/adk-docs/get-started/quickstart/\#__init__py "Permanent link")

Now create an `__init__.py` file in the folder:

```md-code__content
echo "from . import agent" > multi_tool_agent/__init__.py

```

Your `__init__.py` should now look like this:

multi\_tool\_agent/\_\_init\_\_.py

```md-code__content
from . import agent

```

### `agent.py` [¶](https://google.github.io/adk-docs/get-started/quickstart/\#agentpy "Permanent link")

Create an `agent.py` file in the same folder:

```md-code__content
touch multi_tool_agent/agent.py

```

Copy and paste the following code into `agent.py`:

multi\_tool\_agent/agent.py

```md-code__content
import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (41 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}

root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time],
)

```

### `.env` [¶](https://google.github.io/adk-docs/get-started/quickstart/\#env "Permanent link")

Create a `.env` file in the same folder:

```md-code__content
touch multi_tool_agent/.env

```

More instructions about this file are described in the next section on [Set up the model](https://google.github.io/adk-docs/get-started/quickstart/#set-up-the-model).

![intro_components.png](https://google.github.io/adk-docs/assets/quickstart-flow-tool.png)

## 3\. Set up the model [¶](https://google.github.io/adk-docs/get-started/quickstart/\#set-up-the-model "Permanent link")

Your agent's ability to understand user requests and generate responses is
powered by a Large Language Model (LLM). Your agent needs to make secure calls
to this external LLM service, which requires authentication credentials. Without
valid authentication, the LLM service will deny the agent's requests, and the
agent will be unable to function.

[Gemini - Google AI Studio](https://google.github.io/adk-docs/get-started/quickstart/#gemini---google-ai-studio)[Gemini - Google Cloud Vertex AI](https://google.github.io/adk-docs/get-started/quickstart/#gemini---google-cloud-vertex-ai)

1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Open the **`.env`** file located inside ( `multi_tool_agent/`) and copy-paste the following code.

multi\_tool\_agent/.env

```md-code__content
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE

```

3. Replace `GOOGLE_API_KEY` with your actual `API KEY`.


1. You need an existing
    [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) account and a
    project.   - Set up a
         [Google Cloud project](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
   - Set up the
      [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
   - Authenticate to Google Cloud, from the terminal by running
      `gcloud auth login`.
   - [Enable the Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com).
2. Open the **`.env`** file located inside ( `multi_tool_agent/`). Copy-paste
    the following code and update the project ID and location.

multi\_tool\_agent/.env

```md-code__content
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=LOCATION

```


## 4\. Run Your Agent [¶](https://google.github.io/adk-docs/get-started/quickstart/\#run-your-agent "Permanent link")

Using the terminal, navigate to the parent directory of your agent project
(e.g. using `cd ..`):

```md-code__content
parent_folder/      <-- navigate to this directory
    multi_tool_agent/
        __init__.py
        agent.py
        .env

```

There are multiple ways to interact with your agent:

[Dev UI (adk web)](https://google.github.io/adk-docs/get-started/quickstart/#dev-ui-adk-web)[Terminal (adk run)](https://google.github.io/adk-docs/get-started/quickstart/#terminal-adk-run)[API Server (adk api\_server)](https://google.github.io/adk-docs/get-started/quickstart/#api-server-adk-api_server)

Run the following command to launch the **dev UI**.

```md-code__content
adk web

```

**Step 1:** Open the URL provided (usually `http://localhost:8000` or
`http://127.0.0.1:8000`) directly in your browser.

**Step 2.** In the top-left corner of the UI, you can select your agent in
the dropdown. Select "multi\_tool\_agent".

Troubleshooting

If you do not see "multi\_tool\_agent" in the dropdown menu, make sure you
are running `adk web` in the **parent folder** of your agent folder
(i.e. the parent folder of multi\_tool\_agent).

**Step 3.** Now you can chat with your agent using the textbox:

![adk-web-dev-ui-chat.png](https://google.github.io/adk-docs/assets/adk-web-dev-ui-chat.png)

**Step 4.** You can also inspect individual function calls, responses and
model responses by clicking on the actions:

![adk-web-dev-ui-function-call.png](https://google.github.io/adk-docs/assets/adk-web-dev-ui-function-call.png)

**Step 5.** You can also enable your microphone and talk to your agent:

Model support for voice/video streaming

In order to use voice/video streaming in ADK, you will need to use Gemini models that support the Live API. You can find the **model ID(s)** that supports the Gemini Live API in the documentation:

- [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
- [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

You can then replace the `model` string in `root_agent` in the `agent.py` file you created earlier ( [jump to section](https://google.github.io/adk-docs/get-started/quickstart/#agentpy)). Your code should look something like:

```md-code__content
root_agent = Agent(
    name="weather_time_agent",
    model="replace-me-with-model-id", #e.g. gemini-2.0-flash-live-001
    ...

```

![adk-web-dev-ui-audio.png](https://google.github.io/adk-docs/assets/adk-web-dev-ui-audio.png)

Run the following command, to chat with your Google Search agent.

```md-code__content
adk run multi_tool_agent

```

![adk-run.png](https://google.github.io/adk-docs/assets/adk-run.png)

To exit, use Cmd/Ctrl+C.

`adk api_server` enables you to create a local FastAPI server in a single
command, enabling you to test local cURL requests before you deploy your
agent.

![adk-api-server.png](https://google.github.io/adk-docs/assets/adk-api-server.png)

To learn how to use `adk api_server` for testing, refer to the
[documentation on testing](https://google.github.io/adk-docs/get-started/testing/).

### 📝 Example prompts to try [¶](https://google.github.io/adk-docs/get-started/quickstart/\#example-prompts-to-try "Permanent link")

- What is the weather in New York?
- What is the time in New York?
- What is the weather in Paris?
- What is the time in Paris?

## 🎉 Congratulations! [¶](https://google.github.io/adk-docs/get-started/quickstart/\#congratulations "Permanent link")

You've successfully created and interacted with your first agent using ADK!

* * *

## 🛣️ Next steps [¶](https://google.github.io/adk-docs/get-started/quickstart/\#next-steps "Permanent link")

- **Go to the tutorial**: Learn how to add memory, session, state to your agent:
[tutorial](https://google.github.io/adk-docs/get-started/tutorial/).
- **Delve into advanced configuration:** Explore the [setup](https://google.github.io/adk-docs/get-started/installation/)
section for deeper dives into project structure, configuration, and other
interfaces.
- **Understand Core Concepts:** Learn about
[agents concepts](https://google.github.io/adk-docs/agents/).

Back to top