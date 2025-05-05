# Brainstormed Architecture Options: PoC 5 (Aider Small Tweak Integration)

This document presents three distinct high-level architectural approaches for implementing the "Aider Small Tweak Integration" PoC (PRD Version: `1.0-PoC5`), utilizing Google `ADK` and drawing specifically from the common multi-agent patterns described in the provided technical context.

## Approach 1: Sequential Pipeline Pattern

### a. Conceptual Overview
This approach directly models the entire workflow described in the PRD (FR-PoC5-001, FR-PoC5-002, FR-PoC5-003) as a single Sequential Pipeline Pattern. An `ADK` `SequentialAgent` manages the execution of specialized sub-agents, each responsible for one major step of the process (Git Setup -> Parse Task -> Locate File -> Execute Aider -> Log/Report). Communication and data handoff between steps occur primarily via *Shared Session State* (`context.state`).

### b. Key Conceptual Components & Interactions
* **`SmallTweakPipeline` (`SequentialAgent`):** The top-level agent orchestrating the fixed sequence.
* **Sub-Agents (likely `LlmAgent` or simple `BaseAgent` wrappers around tools):**
    * `GitSetupAgent`: Checks out main, creates the feature branch. Writes `branch_name`, `workspace_path`, `goal_path` to state. Uses a specific `GitTool`.
    * `TaskParsingAgent`: Reads `task_description.md` from `goal_path` (state), parses filename and change description. Writes `target_file_name`, `change_description` to state. Uses a `FileTool` (read).
    * `FileLocatorAgent`: Uses `workspace_path` and `target_file_name` (state) to find the full path. Writes `target_file_full_path` to state. Uses a `FileTool` (find/search).
    * `AiderExecutionAgent`: Formats and executes the `aider` command using `target_file_full_path` and `change_description` (state). Captures success/failure. Writes `aider_outcome` to state. Uses a specific, secured `AiderTool` (subprocess wrapper).
    * `LoggingReportingAgent`: Reads relevant state (`branch_name`, `aider_outcome`, etc.), appends to `changelog.md` in `goal_path` (state). Formats the final status message. Uses a `FileTool` (append/write) and handles final output.
* **Tools:**
    * `GitTool` (Specific): Handles Git commands (checkout, branch). Needs careful implementation for security.
    * `FileTool` (Generic): Handles read, find, append/write operations.
    * `AiderTool` (Specific): Securely wraps the `aider` subprocess execution. Critical to prevent arbitrary command execution.
* **Interaction:** `SequentialAgent` invokes sub-agents in order. Each agent reads necessary data from `context.state` and writes its results back to `context.state` for the next agent. Intermediate status reporting to `adk web` likely handled via logging callbacks or potentially specific tool calls within each agent.

### c. Core Interface & Data Ideas
* **Interfaces:** Agent-to-Tool interactions via `ADK` mechanism. Inter-agent communication via Session State.
* **Data Handling:** State keys (`branch_name`, `target_file_name`, `aider_outcome`, etc.) pass data. Files (`task_description.md`, `changelog.md`, target code file) handled by tools.

### d. Relevant Technology Categories / ADK Primitives
* **`ADK`:** `SequentialAgent`, `LlmAgent`, `FunctionTool`, `State`, `ToolContext`, Callbacks (for logging/status updates).
* **External:** `Git CLI`, `aider CLI`.

### e. Initial Risk Assessment
* **State Management Complexity:** Reliant on careful management of state keys; errors in one step's output state break subsequent steps.
* **Error Handling Propagation:** Requires robust error handling within each sub-agent to stop the sequence and report failures correctly via state or exceptions.
* **Limited Flexibility:** The fixed sequence is simple but less adaptable if different paths or conditional logic become necessary later.

### f. Pros & Cons Analysis
* **Pros:**
    * *Simplicity:* Directly maps the linear workflow of the PoC to a straightforward `ADK` pattern. Easy to understand the flow.
    * *Clear Step Separation:* Each agent has a well-defined responsibility within the sequence.
    * *Good Observability:* Intermediate progress reporting maps naturally to the completion of each sequential step.
* **Cons:**
    * *Rigid Flow:* Less flexible for potential future variations or conditional execution paths.
    * *Tight Coupling via State:* Sub-agents are tightly coupled through the specific keys expected in the session state.
    * *Error Handling Chain:* An error early on requires careful propagation to prevent later steps from executing incorrectly.

## Approach 2: Coordinator/Dispatcher Pattern (Simplified for PoC)

### a. Conceptual Overview
This approach uses a central Coordinator/Dispatcher Pattern. A main `CoordinatorAgent` (`LlmAgent`) drives the process. For this PoC with a single, linear workflow, the Coordinator might simply invoke a sequence of specialized Agents (likely implemented as `AgentTools` for clean invocation) one after another, similar to manually implementing a sequence. However, this structure offers more flexibility for future expansion where the Coordinator could route to different tools/agents based on task type.

### b. Key Conceptual Components & Interactions
* **`CoordinatorAgent` (`LlmAgent`):** The central agent triggered by `adk web`. Its prompt would outline the sequence of steps: call Git tool/agent, call Parsing tool/agent, etc. It manages the overall flow by invoking specialized `AgentTools`.
* **Specialized Agents (Implemented as `AgentTools`):**
    * `GitSetupAgentTool`: Performs Git setup. Takes workspace/goal paths, returns branch name.
    * `TaskParsingAgentTool`: Parses `task_description.md`. Takes goal path, returns file name and change description.
    * `FileLocatorAgentTool`: Locates the target file. Takes workspace and filename, returns full path.
    * `AiderExecutionAgentTool`: Executes `aider`. Takes full path and change description, returns success/failure outcome.
    * `LoggingReportingAgentTool`: Logs to `changelog.md` and formats final report. Takes relevant results (branch name, outcome, paths).
* **Generic Tools (Used within `AgentTools`):**
    * `FileSystemTool` (Generic): Used by `TaskParsingAgentTool`, `FileLocatorAgentTool`, `LoggingReportingAgentTool`.
    * `GitTool` (Specific): Used by `GitSetupAgentTool`.
    * `AiderTool` (Specific): Used by `AiderExecutionAgentTool`.
* **Interaction:** `Coordinator Agent` uses LLM reasoning (guided by its prompt) or simple coded logic to call the specialized `AgentTools` in the correct sequence. Data is passed *explicitly* as arguments to the `AgentTools` and returned as their results. Session state might be used less heavily for intermediate data compared to Approach 1, or used by the Coordinator to hold state between its own reasoning steps.

### c. Core Interface & Data Ideas
* **Interfaces:** Coordinator invokes `AgentTools`. `AgentTools` invoke underlying generic/specific `FunctionTools`.
* **Data Handling:** Data primarily passed via arguments and return values of `AgentTool` calls. `task_description.md` and `changelog.md` handled via `FileSystemTool` within relevant `AgentTools`.

### d. Relevant Technology Categories / ADK Primitives
* **`ADK`:** `LlmAgent`, `AgentTool`, `FunctionTool`, `State` (potentially less critical for step-to-step handoff), Callbacks.
* **External:** `Git CLI`, `aider CLI`.

### e. Initial Risk Assessment
* **Coordinator Prompt Complexity:** The Coordinator's prompt or internal logic needs to correctly sequence the `AgentTool` calls.
* **`AgentTool` Interface Design:** Requires defining clear input arguments and return structures for each `AgentTool`.
* **Overhead:** Slightly more structural overhead (defining agents specifically to be tools) compared to the pure `SequentialAgent` approach for this simple linear flow.

### f. Pros & Cons Analysis
* **Pros:**
    * *High Flexibility:* Structure is easily adaptable for future routing logic within the Coordinator if new task types emerge.
    * *Clear Service Encapsulation:* Each major step (Git, Parse, Execute, Log) is encapsulated as a callable `AgentTool` service.
    * *Decoupled Steps:* Agents (as Tools) are primarily coupled via their explicit interfaces (inputs/outputs) rather than implicitly via shared state keys.
* **Cons:**
    * *Slightly More Complex Setup:* Requires defining agents and then wrapping/invoking them as `AgentTools`.
    * *Potential for Centralized Complexity:* The Coordinator agent's logic/prompt could become complex if many steps are involved (though less likely for this PoC).
    * *Invocation Overhead:* Minor overhead associated with `AgentTool` invocation compared to direct state passing in a `SequentialAgent`.

## Approach 3: Hierarchical Task Decomposition (Simplified)

### a. Conceptual Overview
This applies a simplified Hierarchical Task Decomposition pattern. A top-level `RootAgent` (potentially just a simple `LlmAgent` or even a basic script invoking the runner) receives the trigger and delegates the entire "Perform Small Tweak" task to a single, comprehensive `SmallTweakExecutionAgent`. This execution agent, likely implemented itself using a `SequentialAgent` internally (similar to Approach 1), handles all the necessary sub-steps (Git, Parse, Locate, Execute, Log) within its own execution flow. The `RootAgent` simply invokes this comprehensive agent and reports the outcome.

### b. Key Conceptual Components & Interactions
* **`RootAgent` (or entry script):** Receives trigger, identifies `goal_path`. Invokes `SmallTweakExecutionAgent` (likely as an `AgentTool`). Receives final outcome and presents it. Very minimal logic.
* **`SmallTweakExecutionAgent` (Composite Agent, potentially an `AgentTool`):**
    * *Internal Structure:* Likely uses an internal `SequentialAgent` to manage its sub-steps.
    * *Sub-steps/Internal Agents:* Contains logic equivalent to the sub-agents described in Approach 1 (`GitSetup`, `TaskParsing`, `FileLocator`, `AiderExecution`, `LoggingReporting`). These could be internal methods, functions, or even nested `LlmAgents` within the sequence.
    * *Tools Used Internally:* Uses the specific `GitTool`, generic `FileTool`, and specific `AiderTool`.
* **Tools:** As defined in Approach 1/2, but invoked within the `SmallTweakExecutionAgent`.
* **Interaction:** `RootAgent` makes a single call to `SmallTweakExecutionAgent` (as `AgentTool`). All internal steps and state management happen within the `SmallTweakExecutionAgent`. It returns a final status (success/failure) and potentially key info (branch name) to the `RootAgent`. Intermediate status reporting to `adk web` would need to be surfaced from within the `SmallTweakExecutionAgent`'s execution (e.g., via logging callbacks passed down or specific tool calls).

### c. Core Interface & Data Ideas
* **Interfaces:** `RootAgent` invokes `SmallTweakExecutionAgent` via `AgentTool` interface. Internal components communicate via Session State within the `SmallTweakExecutionAgent`'s context.
* **Data Handling:** Most state is contained within the execution context of the `SmallTweakExecutionAgent`. File handling performed by tools invoked internally.

### d. Relevant Technology Categories / ADK Primitives
* **`ADK`:** `LlmAgent`, `AgentTool`, `SequentialAgent` (likely used internally), `FunctionTool`, `State`, Callbacks.
* **External:** `Git CLI`, `aider CLI`.

### e. Initial Risk Assessment
* **Monolithic Sub-Agent:** The `SmallTweakExecutionAgent` becomes quite large and responsible for many steps, potentially reducing modularity at the higher level.
* **Observability Challenge:** Surfacing intermediate progress updates from deep within the `SmallTweakExecutionAgent` back to the `adk web` interface might require more complex plumbing (e.g., passing callback functions or using a dedicated status-reporting tool).
* **Error Handling Complexity:** Errors deep within the sequence need to be caught and propagated correctly to result in a final failure status for the entire `SmallTweakExecutionAgent` tool call.

### f. Pros & Cons Analysis
* **Pros:**
    * *Simple Top-Level:* The `RootAgent` becomes extremely simple, just delegating the entire task.
    * *High Encapsulation:* The entire "Small Tweak" process is *self-contained* within a single logical (though internally complex) unit.
    * *Clear Task Boundary:* Clearly defines the boundary of the "Perform Small Tweak" capability.
* **Cons:**
    * *Reduced High-Level Modularity:* Less easy to reuse individual steps (like Git Setup) at the orchestrator level compared to Approach 2.
    * *Potential Observability Issues:* Displaying granular, real-time progress from internal steps might be harder.
    * *Internal Complexity:* Hides complexity inside the `SmallTweakExecutionAgent`, which might make debugging its internal flow more difficult.

These three approaches provide different ways to structure the `ADK` application using established patterns, offering trade-offs between simplicity, flexibility, encapsulation, and observability. The best choice depends on the anticipated future evolution of the system and the desired level of modularity.