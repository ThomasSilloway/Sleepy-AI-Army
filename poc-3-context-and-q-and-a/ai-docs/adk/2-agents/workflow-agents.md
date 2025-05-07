[Skip to content](https://google.github.io/adk-docs/agents/workflow-agents/#workflow-agents)

# Workflow Agents [¶](https://google.github.io/adk-docs/agents/workflow-agents/\#workflow-agents "Permanent link")

This section introduces " _workflow agents_" \- **specialized agents that control the execution flow of its sub-agents**.

Workflow agents are specialized components in ADK designed purely for **orchestrating the execution flow of sub-agents**. Their primary role is to manage _how_ and _when_ other agents run, defining the control flow of a process.

Unlike [LLM Agents](https://google.github.io/adk-docs/agents/llm-agents/), which use Large Language Models for dynamic reasoning and decision-making, Workflow Agents operate based on **predefined logic**. They determine the execution sequence according to their type (e.g., sequential, parallel, loop) without consulting an LLM for the orchestration itself. This results in **deterministic and predictable execution patterns**.

ADK provides three core workflow agent types, each implementing a distinct execution pattern:

- **Sequential Agents**


* * *


Executes sub-agents one after another, in **sequence**.

[Learn more](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)

- **Loop Agents**


* * *


**Repeatedly** executes its sub-agents until a specific termination condition is met.

[Learn more](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/)

- **Parallel Agents**


* * *


Executes multiple sub-agents in **parallel**.

[Learn more](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/)


## Why Use Workflow Agents? [¶](https://google.github.io/adk-docs/agents/workflow-agents/\#why-use-workflow-agents "Permanent link")

Workflow agents are essential when you need explicit control over how a series of tasks or agents are executed. They provide:

- **Predictability:** The flow of execution is guaranteed based on the agent type and configuration.
- **Reliability:** Ensures tasks run in the required order or pattern consistently.
- **Structure:** Allows you to build complex processes by composing agents within clear control structures.

While the workflow agent manages the control flow deterministically, the sub-agents it orchestrates can themselves be any type of agent, including intelligent `LlmAgent` instances. This allows you to combine structured process control with flexible, LLM-powered task execution.

Back to top