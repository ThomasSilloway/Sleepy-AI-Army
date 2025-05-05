## Approach 1 notes
Approach 1 - seems like TaskParsingAgent would need to happen before the gitsetup agent. bc the setup agent would need to figure out the slug for the branch from the task description


- Also i'd want to write to the changelog during each step. so i'm thinking maybe there'd be a changelog agent that each of those agents you outlined can use as an AgentTool


- It seems like maybe FileLocatorAgent and GitSetupAgent could happen in parallel inserting a parallel agent in there? Maybe to help with race conditions, we wouldn't have a single changelog file, but we'd have a changelog folder and each a gent would be responsible for writing to specific files that maybe have the timestamp and their agent name or something. Then the final reporting agent can combine all of those into a single file.


- Would definitely want to use on LLMAgents, not BaseAgents for flexibiliity in prototyping phase. 

## Other notes
either approach 1 or approach three would work best. But for approach 3, I wouldn't want to use the sequential agent as a agent tool because it does reduce observability.


So I do have a question about how sequential agents work. What happens if one of the agents that gets called in the sequence has an error? How does the flow change or does it crash or does it go on to the next one anyway or does it cancel the execution and return an error? Like how does that work from a detailed technical standpoint? If you can't find the information in the technical context that I gave you, please perform a search for grounding. Actually do a grounding search either way 

## Discussion

We don't really know from the documentation, so we'll create PoC #6 to investigate this.

I think my idea approach would be something like approach 3, but instead of the sequential agent being an AgentTool that the root agent calls, it would instead be a sub agent and then at the end of the sequential agent running, it would return control to the root agent with a summary of the execution, so it can provide a short report on what happened.

## Next steps 

- create PoC 6 to see if something like that is possible using the callbacks to prevent the next items in the sequence from running except the final summarization agent would still run no matter what and return back to the root agent