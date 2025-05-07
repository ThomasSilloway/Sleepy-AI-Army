# PoC 5: Aider Small Tweak Integration

ADK project for PoC 5: Aider Small Tweak Integration.

## Note - Incomplete project, stopped after initial implement due to re-considering how we should be approaching this solution.

Big session this morning, largely kicked off by thinking PoC 5's current agent approach might be better as a workflow. Key insight: now understanding prompt chains more deeply. Realizing they can effectively be workflows, especially since you can call tools/run code programmatically between the LLM prompt steps. This means a chain isn't just LLM->LLM, but LLM->Code/Tool->LLM->Code/Tool, which is very workflow-like. Plus, these chains can be looped for iterative processes. Definitely changes how I'm viewing implementation options.

https://docs.google.com/document/d/1UaQhYy1pGrnLpCV9y0bU0ozCUjnj0cS9GV68KHMYo5g
