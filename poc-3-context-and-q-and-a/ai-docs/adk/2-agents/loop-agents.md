[Skip to content](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/#loop-agents)

# Loop agents [¶](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/\#loop-agents "Permanent link")

## The `LoopAgent` [¶](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/\#the-loopagent "Permanent link")

The `LoopAgent` is a workflow agent that executes its sub-agents in a loop (i.e. iteratively). It **_repeatedly runs_ a sequence of agents** for a specified number of iterations or until a termination condition is met.

Use the `LoopAgent` when your workflow involves repetition or iterative refinement, such as like revising code.

### Example [¶](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/\#example "Permanent link")

- You want to build an agent that can generate images of food, but sometimes when you want to generate a specific number of items (e.g. 5 bananas), it generates a different number of those items in the image (e.g. an image of 7 bananas). You have two tools: `generate_image`, `count_food_items`. Because you want to keep generating images until it either correctly generates the specified number of items, or after a certain number of iterations, you should build your agent using a `LoopAgent`.

As with other [workflow agents](https://google.github.io/adk-docs/agents/workflow-agents/), the `LoopAgent` is not powered by an LLM, and is thus deterministic in how it executes. That being said, workflow agents are only concerned only with their execution (i.e. in a loop), and not their internal logic; the tools or sub-agents of a workflow agent may or may not utilize LLMs.

### How it Works [¶](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/\#how-it-works "Permanent link")

When the `LoopAgent`'s `run_async()` method is called, it performs the following actions:

1. **Sub-Agent Execution:** It iterates through the `sub_agents` list _in order_. For _each_ sub-agent, it calls the agent's `run_async()` method.
2. **Termination Check:**

_Crucially_, the `LoopAgent` itself does _not_ inherently decide when to stop looping. You _must_ implement a termination mechanism to prevent infinite loops. Common strategies include:
   - **`max_iterations`**: Set a maximum number of iterations in the `LoopAgent`. **The loop will terminate after that many iterations**.
   - **Escalation from sub-agent**: Design one or more sub-agents to evaluate a condition (e.g., "Is the document quality good enough?", "Has a consensus been reached?"). If the condition is met, the sub-agent can signal termination (e.g., by raising a custom event, setting a flag in a shared context, or returning a specific value).

![Loop Agent](https://google.github.io/adk-docs/assets/loop-agent.png)

### Full Example: Iterative Document Improvement [¶](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/\#full-example-iterative-document-improvement "Permanent link")

Imagine a scenario where you want to iteratively improve a document:

- **Writer Agent:** An `LlmAgent` that generates or refines a draft on a topic.
- **Critic Agent:** An `LlmAgent` that critiques the draft, identifying areas for improvement.



```md-code__content
LoopAgent(sub_agents=[WriterAgent, CriticAgent], max_iterations=5)

```


In this setup, the `LoopAgent` would manage the iterative process. The `CriticAgent` could be **designed to return a "STOP" signal when the document reaches a satisfactory quality level**, preventing further iterations. Alternatively, the `max_iterations` parameter could be used to limit the process to a fixed number of cycles, or external logic could be implemented to make stop decisions. The **loop would run at most five times**, ensuring the iterative refinement doesn't continue indefinitely.

Full Code

```md-code__content
from google.adk.agents.loop_agent import LoopAgent
from google.adk.agents.llm_agent import LlmAgent
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

# --- Constants ---
APP_NAME = "doc_writing_app"
USER_ID = "dev_user_01"
SESSION_ID = "session_01"
GEMINI_MODEL = "gemini-2.0-flash"

# --- State Keys ---
STATE_INITIAL_TOPIC = "quantum physics"
STATE_CURRENT_DOC = "current_document"
STATE_CRITICISM = "criticism"

writer_agent = LlmAgent(
    name="WriterAgent",
    model=GEMINI_MODEL,
    instruction=f"""
    You are a Creative Writer AI.
    Check the session state for '{STATE_CURRENT_DOC}'.
    If '{STATE_CURRENT_DOC}' does NOT exist or is empty, write a very short (1-2 sentence) story or document based on the topic in state key '{STATE_INITIAL_TOPIC}'.
    If '{STATE_CURRENT_DOC}' *already exists* and '{STATE_CRITICISM}', refine '{STATE_CURRENT_DOC}' according to the comments in '{STATE_CRITICISM}'."
    Output *only* the story or the exact pass-through message.
    """,
    description="Writes the initial document draft.",
    output_key=STATE_CURRENT_DOC # Saves output to state
)

# Critic Agent (LlmAgent)
critic_agent = LlmAgent(
    name="CriticAgent",
    model=GEMINI_MODEL,
    instruction=f"""
    You are a Constructive Critic AI.
    Review the document provided in the session state key '{STATE_CURRENT_DOC}'.
    Provide 1-2 brief suggestions for improvement (e.g., "Make it more exciting", "Add more detail").
    Output *only* the critique.
    """,
    description="Reviews the current document draft.",
    output_key=STATE_CRITICISM # Saves critique to state
)

# Create the LoopAgent
loop_agent = LoopAgent(
    name="LoopAgent", sub_agents=[writer_agent, critic_agent], max_iterations=2
)

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=loop_agent, app_name=APP_NAME, session_service=session_service)

# Agent Interaction
def call_agent(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

call_agent("execute")

```

Back to top