# Features: Add root agent, sequential agent, and task parsing agent

> Given the Objective, implement every detail of every task.

## Objectives

### TODO FOR NEXT TIME: Tell it to leave in commented out aspects from specific files if we want them

- Add initial constants.py 

- Add initial implementation of the first 3 agents
 - RootAgent
 - SmallTweakSequence
 - TaskParsingAgent 
    - Note: Does not use CHangelogAgent yet (does not exist)

## Context

/add poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\agent.py

/add poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\constants\__init__.py
/add poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\constants\constants.py

/add poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\sub_agents\task_parsing\agent.py
/add poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\sub_agents\task_parsing\prompt.py
/add poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\sub_agents\task_parsing\__init__.py


/read-only ai-docs\sample-agent-tool-use.md

/read-only poc-5-aider-agent\ai-docs\03-prd.md
/read-only poc-5-aider-agent\ai-docs\06_tech-architecture.md

/read-only poc-5-aider-agent\src\sleepy-ai-poc5\sleepy_ai_agent\shared_tools\file_system.py

/read-only poc-6-sequential-agent-testing\src\sequential-failure-test\sequential_failure_test_agent\agent.py
/read-only poc-6-sequential-agent-testing\src\sequential-failure-test\sequential_failure_test_agent\prompt.py

## Low-Level Tasks
> Ordered from start to finish

### Implement constants.py
```
 - UPDATE constants.py with all constants needed to fulfill the tech-architecture.md
```

### Implement TaskParsingAgent
```
- UPDATE `sleepy_ai_agent\sub_agents\task_parsing\agent.py` with the TaskParsingAgent using `ai-docs\sample-agent-tool-use.md` as a template
- CREATE prompt.py with the prompt for the TaskParsingAgent using `ai-docs\sample-agent-tool-use.md` as a template
```

### Implement RootAgent
```
- UPDATE `sleepy_ai_agent\agent.py` with the RootAgent and SmallTweakSequence using `sequential_failure_test_agent\agent.py` as a template
- CREATE prompt.py with the prompt for the RootAgent using 	`sequential_failure_test_agent\prompt.py` as a template
```
