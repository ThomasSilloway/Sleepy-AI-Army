[Skip to content](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/#parallel-agents)

# Parallel agents [¶](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/\#parallel-agents "Permanent link")

## The `ParallelAgent` [¶](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/\#the-parallelagent "Permanent link")

The `ParallelAgent` is a [workflow agent](https://google.github.io/adk-docs/agents/workflow-agents/) that executes its sub-agents _concurrently_. This dramatically speeds up workflows where tasks can be performed independently.

Use `ParallelAgent` when: For scenarios prioritizing speed and involving independent, resource-intensive tasks, a `ParallelAgent` facilitates efficient parallel execution. **When sub-agents operate without dependencies, their tasks can be performed concurrently**, significantly reducing overall processing time.

As with other [workflow agents](https://google.github.io/adk-docs/agents/workflow-agents/), the `ParallelAgent` is not powered by an LLM, and is thus deterministic in how it executes. That being said, workflow agents are only concerned only with their execution (i.e. in parallel), and not their internal logic; the tools or sub-agents of a workflow agent may or may not utilize LLMs.

### Example [¶](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/\#example "Permanent link")

This approach is particularly beneficial for operations like multi-source data retrieval or heavy computations, where parallelization yields substantial performance gains. Importantly, this strategy assumes no inherent need for shared state or direct information exchange between the concurrently executing agents.

### How it works [¶](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/\#how-it-works "Permanent link")

When the `ParallelAgent`'s `run_async()` method is called:

1. **Concurrent Execution:** It initiates the `run()` method of _each_ sub-agent present in the `sub_agents` list _concurrently_. This means all the agents start running at (approximately) the same time.
2. **Independent Branches:** Each sub-agent operates in its own execution branch. There is **_no_ automatic sharing of conversation history or state between these branches** during execution.
3. **Result Collection:** The `ParallelAgent` manages the parallel execution and, typically, provides a way to access the results from each sub-agent after they have completed (e.g., through a list of results or events). The order of results may not be deterministic.

### Independent Execution and State Management [¶](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/\#independent-execution-and-state-management "Permanent link")

It's _crucial_ to understand that sub-agents within a `ParallelAgent` run independently. If you _need_ communication or data sharing between these agents, you must implement it explicitly. Possible approaches include:

- **Shared `InvocationContext`:** You could pass a shared `InvocationContext` object to each sub-agent. This object could act as a shared data store. However, you'd need to manage concurrent access to this shared context carefully (e.g., using locks) to avoid race conditions.
- **External State Management:** Use an external database, message queue, or other mechanism to manage shared state and facilitate communication between agents.
- **Post-Processing:** Collect results from each branch, and then implement logic to coordinate data afterwards.

![Parallel Agent](https://google.github.io/adk-docs/assets/parallel-agent.png)

### Full Example: Parallel Web Research [¶](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/\#full-example-parallel-web-research "Permanent link")

Imagine researching multiple topics simultaneously:

1. **Researcher Agent 1:** An `LlmAgent` that researches "renewable energy sources."
2. **Researcher Agent 2:** An `LlmAgent` that researches "electric vehicle technology."
3. **Researcher Agent 3:** An `LlmAgent` that researches "carbon capture methods."



```md-code__content
ParallelAgent(sub_agents=[ResearcherAgent1, ResearcherAgent2, ResearcherAgent3])

```


These research tasks are independent. Using a `ParallelAgent` allows them to run concurrently, potentially reducing the total research time significantly compared to running them sequentially. The results from each agent would be collected separately after they finish.

Code

```md-code__content
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import google_search
from google.genai import types

APP_NAME = "parallel_research_app"
USER_ID = "research_user_01"
SESSION_ID = "parallel_research_session"
GEMINI_MODEL = "gemini-2.0-flash"

# --- Define Researcher Sub-Agents ---

# Researcher 1: Renewable Energy
researcher_agent_1 = LlmAgent(
    name="RenewableEnergyResearcher",
    model=GEMINI_MODEL,
    instruction="""You are an AI Research Assistant specializing in energy.
    Research the latest advancements in 'renewable energy sources'.
    Use the Google Search tool provided.
    Summarize your key findings concisely (1-2 sentences).
    Output *only* the summary.
    """,
    description="Researches renewable energy sources.",
    tools=[google_search], # Provide the search tool
    # Save the result to session state
    output_key="renewable_energy_result"
)

# Researcher 2: Electric Vehicles
researcher_agent_2 = LlmAgent(
    name="EVResearcher",
    model=GEMINI_MODEL,
    instruction="""You are an AI Research Assistant specializing in transportation.
    Research the latest developments in 'electric vehicle technology'.
    Use the Google Search tool provided.
    Summarize your key findings concisely (1-2 sentences).
    Output *only* the summary.
    """,
    description="Researches electric vehicle technology.",
    tools=[google_search], # Provide the search tool
    # Save the result to session state
    output_key="ev_technology_result"
)

# Researcher 3: Carbon Capture
researcher_agent_3 = LlmAgent(
    name="CarbonCaptureResearcher",
    model=GEMINI_MODEL,
    instruction="""You are an AI Research Assistant specializing in climate solutions.
    Research the current state of 'carbon capture methods'.
    Use the Google Search tool provided.
    Summarize your key findings concisely (1-2 sentences).
    Output *only* the summary.
    """,
    description="Researches carbon capture methods.",
    tools=[google_search], # Provide the search tool
    # Save the result to session state
    output_key="carbon_capture_result"
)

# --- Create the ParallelAgent ---
# This agent orchestrates the concurrent execution of the researchers.
parallel_research_agent = ParallelAgent(
    name="ParallelWebResearchAgent",
    sub_agents=[researcher_agent_1, researcher_agent_2, researcher_agent_3]
)

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=parallel_research_agent, app_name=APP_NAME, session_service=session_service)

# Agent Interaction
def call_agent(query):
    '''
    Helper function to call the agent with a query.
    '''
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

call_agent("research latest trends")

```

Back to top