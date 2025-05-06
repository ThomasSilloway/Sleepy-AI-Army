## Conditional Skipping via `before_agent_callback`

### a. Conceptual Overview
This approach directly implements the Sequential Pipeline Pattern using ADK's `SequentialAgent`. The conditional skipping logic required before `Agent B` and `Agent C` executes is implemented within `before_agent_callback` functions attached to those *respective agents*. These callbacks inspect the *shared session state* (`context.state`) for the outcome of the preceding agent. If a failure is detected, the callback returns a `types.Content` object (as documented in ADK callback examples), which prevents the main logic/instruction of that agent (B or C) from executing. `Agent D` has no such callback and simply runs its course.

### b. Key Conceptual Components & Interactions
* **`RootAgent`:** Invokes the `ErrorTestSequence`. Logs completion after it finishes.
* **`ErrorTestSequence` (`SequentialAgent`):** Contains `sub_agents = [AgentA, AgentB, AgentC, AgentD]`.
* **`AgentA` (`LlmAgent`):** Executes its task, calls the `FailingTool` (configured to return a structured error), and saves the outcome (e.g., `{"status": "error", ...}`) to `context.state['agent_a_outcome']`. Outputs its execution message.
* **`AgentB` (`LlmAgent`):**
    * **`before_agent_callback`:** `check_outcome_and_skip_callback`. This function reads `context.state['agent_a_outcome']`. If status is `"error"`, it logs the skip attempt and returns `types.Content(parts=[Part(text="Agent B skipped due to Agent A failure.")])`. Otherwise, it returns `None`.
    * **`instruction`:** `"Output 'Agent B running primary task'."` (This only runs if the callback returns `None`). Saves its outcome (e.g., `'skipped'` or `'completed'`) to `context.state['agent_b_outcome']`.
* **`AgentC` (`LlmAgent`):**
    * **`before_agent_callback`:** `check_outcome_and_skip_callback`. Similar logic, but checks `context.state['agent_b_outcome']`. Returns `Content` if B's outcome was `'skipped'` or `'error'`.
    * **`instruction`:** `"Output 'Agent C running primary task'."` (Only runs if callback returns `None`). Saves outcome to `context.state['agent_c_outcome']`.
* **`AgentD` (`LlmAgent`):**
    * No conditional callback.
    * **`instruction`:** `"Output 'Agent D running primary task'. Read outcomes from context.state['agent_a_outcome'], context.state['agent_b_outcome'], context.state['agent_c_outcome']. Generate and output a summary string reflecting the execution flow."`
* **`FailingTool` (`FunctionTool`):** As described in PRD/previous discussion - returns a structured error dictionary, e.g., `{"status": "error", "message": "..."}`.
* **Interaction:** `SequentialAgent` executes A, B, C, D. Callbacks on B and C intercept execution based on state set by the preceding agent. Agent D always runs its instruction. State (`context.state`) is the primary communication mechanism.

### c. Core Interface & Data Ideas
* **Interfaces:** Agent instructions reference state keys. Callbacks access state via `CallbackContext`. Tool provides structured error return.
* **Data Handling:** Session state (`context.state`) holds outcome flags/structures (e.g., `agent_a_outcome`, `agent_b_outcome`). Agent D aggregates these for its summary.

### d. Relevant Technology Categories / ADK Primitives
* **`ADK`:** `SequentialAgent`, `LlmAgent`, `FunctionTool`, `State`, `CallbackContext`, `before_agent_callback`, `types.Content`, `types.Part`.

### e. Initial Risk Assessment
* **Callback Implementation Detail:** Correctly implementing the callback logic to check state and return `types.Content` vs. `None` is *crucial*.
* **State Key Management:** Requires consistent naming and checking of state keys (e.g., `agent_a_outcome`, `agent_b_outcome`). Errors in setting/reading state break the conditional logic.
* **Clarity of "Skipped" State:** Need to ensure the state clearly reflects when an agent was skipped via callback versus completing successfully.

### f. Pros & Cons Analysis
* **Pros:**
    * *Uses Standard Feature:* Leverages the documented `ADK` callback mechanism and `types.Content` return for flow control.
    * *Explicit Control Point:* The skipping logic is cleanly separated into the callback functions.
    * *Agent Simplicity:* The main instruction for agents B and C remains focused on their primary task, assuming they are allowed to run.
    * *Guaranteed Finalizer:* Agent D runs unconditionally as it lacks the skipping callback.
* **Cons:**
    * *Callback Complexity:* Requires writing separate Python callback functions outside the agent instructions.
    * *Indirect Flow Control:* Control flow modification happens via the callback return mechanism, which might feel slightly less direct than inline logic.