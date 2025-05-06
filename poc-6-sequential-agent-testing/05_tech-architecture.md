# Technical Architecture: PoC 6 (ADK SequentialAgent Failure Handling Experiment)

**Version:** 1.4 (Generated 2025-05-05)

## 1. Overview

This document outlines the technical architecture for Proof-of-Concept 6 (PoC 6). The goal is to experimentally validate a mechanism using standard Google Agent Development Kit (ADK) features to achieve conditional skipping of intermediate steps within a `SequentialAgent` following a simulated failure, while ensuring guaranteed execution of a final step. The chosen architecture employs a `SequentialAgent` containing four sub-agents (A, B, C, D), with conditional skipping implemented using `before_agent_callback`. State persistence for outcomes of A, B, and C relies on agents outputting structured JSON strings captured via the `output_key` mechanism. Callbacks (from a shared module) read these JSON strings to control the flow. Agent D utilizes ADK's prompt state injection (`{}`) to access prior outcomes and provide a final plain text summary, implicitly returning control upon completion.

## 2. Component Breakdown (Refined Structure)

* **`RootAgent` (`LlmAgent` or `BaseAgent`)**

  * **Defined in:** `poc6_sequential_failure/agent.py`
  * **Responsibilities:** Invoke `ErrorTestSequence`, log completion.
  * **Interactions:** Starts `ErrorTestSequence`.

* **`ErrorTestSequence` (`SequentialAgent`)**

  * **Defined in:** `poc6_sequential_failure/agent.py`
  * **Responsibilities:** Execute Agents A, B, C, D sequentially in strict order.
  * **Interactions:** Contains Agents A, B, C, D. Returns control to `RootAgent` upon its own completion.

* **`AgentA` (`LlmAgent`)**

  * **Defined in:** `poc6_sequential_failure/sub_agents/agent_a/agent.py`
  * **Responsibilities:** Call `FailingTool`; return JSON string indicating `status`.
  * **Instruction:** `poc6_sequential_failure/sub_agents/agent_a/prompt.py`
  * **Configuration:** `output_key='agent_a_outcome'`
  * **Tool:** `FailingTool` from `agent_a.tools`

* **`AgentB` (`LlmAgent`)**

  * **Defined in:** `poc6_sequential_failure/sub_agents/agent_b/agent.py`
  * **Responsibilities:** Skip if failure in A; else run and return JSON `status: "success"`.
  * **Instruction:** `agent_b/prompt.py`
  * **Configuration:** `output_key='agent_b_outcome'`, `before_agent_callback=check_outcome_and_skip_callback`

* **`AgentC` (`LlmAgent`)**

  * **Defined in:** `poc6_sequential_failure/sub_agents/agent_c/agent.py`
  * **Responsibilities:** Skip if failure/skip in B; else run and return JSON `status: "success"`.
  * **Instruction:** `agent_c/prompt.py`
  * **Configuration:** `output_key='agent_c_outcome'`, `before_agent_callback=check_outcome_and_skip_callback`

* **`AgentD` (`LlmAgent`)**

  * **Defined in:** `poc6_sequential_failure/sub_agents/agent_d/agent.py`
  * **Responsibilities:**

    1. Access prior outcomes via `{agent_a_outcome}`, etc.
    2. Parse JSON and summarize.
    3. Output plain text summary.
  * **Instruction Example:**

    > Perform the following steps:
    >
    > 1. Review the outcomes of the previous steps: Agent A -> `{agent_a_outcome}`, B -> `{agent_b_outcome}`, C -> `{agent_c_outcome}`.
    > 2. Output only the summary sentence as plain text.
  * **Configuration:** No `output_key`

* **`FailingTool` (`FunctionTool`)**

  * **Defined in:** `agent_a/tools.py`
  * **Responsibilities:** Simulate failure, return `{"status": "error"}`

* **`check_outcome_and_skip_callback` (Function)**

  * **Defined in:** `callbacks/callbacks.py`
  * **Responsibilities:** Read prior agent state JSON; skip if failed/skipped

## 2.1. Note on Structured Output (`output_schema`)

* `output_schema` disables tools or control transfer in ADK.
* Agent A requires `FailingTool` → cannot use `output_schema`.
* To ensure consistency, none of the agents use `output_schema`.
* All agents output final results as JSON **strings** via `output_key`.

## 3. Technology Stack

* **Language:** Python
* **Framework:** Google Agent Development Kit (ADK)
* **Core ADK Components:**

  * `LlmAgent`, `SequentialAgent`, `FunctionTool`, `State`
  * `before_agent_callback`, `output_key`, `Runner`, `InMemorySessionService`
  * `google.genai.types` → `types.Content`, `types.Part`
* **LLM Model:** `gemini-2.0-flash`
* **Library:** `json` for parsing state

## 4. Data Models / Structures (Final)

* **Session State (`context.state`)**

  * `agent_a_outcome`: `'{"status": "failure", ...}'`
  * `agent_b_outcome`: `'{"status": "success"}` or `'skipped'`
  * `agent_c_outcome`: `'{"status": "success"}` or `'skipped'`

* **Prompt Injection (Agent D):** `{agent_a_outcome}`, etc.

* **Tool Return (FailingTool):** `{ "status": "error", "message": "Simulated failure" }`

* **Callback Return:** `None` or `types.Content(...)`

* **Standard Agent Output JSON:**

  ```json
  {
    "status": "success" | "failure",
    "message": "Optional description",
    "result": "Optional field"
  }
  ```

* **Skipped JSON (Callback):**

  ```json
  {
    "status": "skipped",
    "message": "Skipped due to prior step outcome."
  }
  ```

## 5. NFR Fulfillment

Uses only standard ADK components: `SequentialAgent`, `LlmAgent`, `FunctionTool`, `State`, `output_key`, `before_agent_callback`, and prompt injection.

## 6. Key Interaction Flows (Failure Scenario - Final)

* RootAgent starts ErrorTestSequence.
* ErrorTestSequence invokes AgentA.
* AgentA calls FailingTool, receives `{"status": "error", ...}` dictionary.
* AgentA formulates final text response: `{"status": "failure", "message": "Tool failed..."}`.
* Framework saves this JSON string to `context.state['agent_a_outcome']` via `output_key`.
* ErrorTestSequence attempts to invoke AgentB.
* AgentB's `before_agent_callback` runs.
* Callback reads JSON string from `context.state['agent_a_outcome']`, parses it, finds `status == "failure"`.
* Callback explicitly sets `context.state['agent_b_outcome'] = '{"status": "skipped", "message": "Skipped due to Agent A failure."}'`.
* Callback returns `types.Content(...)`, skipping AgentB.
* ErrorTestSequence attempts to invoke AgentC.
* AgentC's `before_agent_callback` runs.
* Callback reads JSON string from `context.state['agent_b_outcome']`, parses it, finds `status == "skipped"`.
* Callback explicitly sets `context.state['agent_c_outcome'] = '{"status": "skipped", "message": "Skipped due to Agent B outcome."}'`.
* Callback returns `types.Content(...)`, skipping AgentC.
* ErrorTestSequence invokes AgentD.
* ADK prepares Agent D's prompt, injecting the state values: `...Agent A -> {"status": "failure", ...}, Agent B -> {"status": "skipped", ...}, Agent C -> {"status": "skipped", ...}. Parse these...`
* AgentD executes, parsing the injected JSON strings within its prompt context.
* AgentD generates the plain text summary: "Agent A failed, B and C were skipped, D completed.".
* AgentD outputs this summary as its final response. It completes its turn successfully.
* ErrorTestSequence, having completed its last sub-agent (D), finishes execution.
* RootAgent receives control back and logs "Sequence complete".

## 7. Error Handling Strategy (Final)

* **Simulated Failure**: Via FailingTool.
* **Agent Interpretation & JSON Output (A, B, C)**: Agents responsible for outputting status as JSON strings.
* **State via output\_key (A, B, C)**: Framework captures JSON strings.
* **Conditional Skipping (Callback)**: Reads/parses JSON string from state. Explicitly writes "skipped" JSON string to state if skipping. Requires robust JSON handling.
* **State Injection (D)**: Agent D receives prior outcomes directly via `{}` prompt syntax.
* **Finalizer (D)**: Agent D parses injected outcomes and outputs a plain text summary. Natural completion returns control.

## 8. Proposed Folder and File Structure (Revised)

```
/poc6-sequential-failure       # Root folder where 'adk web' is run
├── .env                         # Local environment variables (API keys, etc.) - KEEP SECRET
├── .env.example                 # Example environment file for setup guidance
├── README.md                    # Project description
├── requirements.txt             # Python dependencies (google-adk, etc.)
└── poc6_sequential_failure/     # Main Python package
    ├── __init__.py              # Imports root_agent from agent.py
    ├── agent.py                 # Defines RootAgent and ErrorTestSequence (SequentialAgent)
    ├── prompt.py                # Root-level prompts or shared constants (if any)
    ├── callbacks/               # Shared callback functions
    │   ├── __init__.py          # Makes 'callbacks' a sub-package
    │   └── callbacks.py         # Defines check_outcome_and_skip_callback
    └── sub_agents/              # Sub-directory for individual agents
        ├── agent_a/
        │   ├── __init__.py      # Empty
        │   ├── agent.py         # Defines Agent A (LlmAgent)
        │   ├── prompt.py        # Instruction prompt for Agent A (to output JSON)
        │   └── tools.py         # Defines FailingTool and its FunctionTool instance
        ├── agent_b/
        │   ├── __init__.py      # Empty
        │   ├── agent.py         # Defines Agent B (LlmAgent), imports shared callback
        │   └── prompt.py        # Instruction prompt for Agent B (to output JSON)
        ├── agent_c/
        │   ├── __init__.py      # Empty
        │   ├── agent.py         # Defines Agent C (LlmAgent), imports shared callback
        │   └── prompt.py        # Instruction prompt for Agent C (to output JSON)
        └── agent_d/
            ├── __init__.py      # Empty
            ├── agent.py         # Defines Agent D (LlmAgent)
            └── prompt.py        # Instruction uses {state_key} injection
```

**Initial File Contents (Minimal - Examples reflecting new structure):**

```python
poc6_sequential_failure/__init__.py:
    from .agent import root_agent

poc6_sequential_failure/agent.py:
    # Imports (Agent, SequentialAgent), imports from .sub_agents.*, definition of error_test_sequence, root_agent.

poc6_sequential_failure/callbacks/__init__.py:
    # (Empty)

poc6_sequential_failure/callbacks/callbacks.py:
    # Imports (types, CallbackContext, json), define check_outcome_and_skip_callback(...).

poc6_sequential_failure/sub_agents/agent_a/__init__.py:
    # (Empty)

poc6_sequential_failure/sub_agents/agent_a/tools.py:
    # Imports (FunctionTool), define _failing_tool_impl() -> dict:, failing_tool = FunctionTool(func=...).

poc6_sequential_failure/sub_agents/agent_a/agent.py:
    # Imports (Agent, .tools, .prompt), define agent_a = Agent(..., tools=[tools.failing_tool], output_key='agent_a_outcome', instruction=prompt.AGENT_A_INSTR).

poc6_sequential_failure/sub_agents/agent_b/__init__.py:
    # (Empty)

poc6_sequential_failure/sub_agents/agent_b/agent.py:
    # Imports (Agent, ...callbacks.callbacks, .prompt), define agent_b = Agent(..., before_agent_callback=callbacks.check_outcome_and_skip_callback, output_key='agent_b_outcome', ...).
    # (Similar structure for agent C)

poc6_sequential_failure/sub_agents/agent_d/__init__.py:
    # (Empty)

poc6_sequential_failure/sub_agents/agent_d/agent.py:
    # Imports (Agent, .prompt), define agent_d = Agent(...).

.env.example:
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"

requirements.txt:
    google-adk
```

## 9. Risks & Dependencies

* **Callback Implementation**: Logic must correctly parse JSON strings (handling errors), check status, set skipped state (as a JSON string), and return correctly.
* **LLM JSON Compliance (A, B, C)**: Relies heavily on the LLM reliably adhering to instructions to output only valid JSON strings. Invalid JSON will break the flow.
* **Prompt State Injection (`{}`)**: Relies on the `{state_key}` injection mechanism working as described in the provided brainstorming summary context. If this mechanism behaves differently, Agent D's instruction/parsing may fail.
* **State Management**: Consistent naming of `output_keys` (A, B, C) and reliable state access are crucial.
* **Tool Error Structure**: Agent A's instruction relies on interpreting the dictionary returned by FailingTool.
* **ADK Framework**: Dependency on Google ADK behavior.
