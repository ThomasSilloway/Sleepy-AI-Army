# Overview

  Let's plan out a new feature. I've included detailed info below.

  Follow each task below one by one, make sure not to skip any steps.

## Feature Overview

implement the prd


## Relevant files

- (Add your docs here)


- Project Tech Design: @/project-tech-design.md
- Best Practices: @/ai-docs/best_practices.md 

## Project Details

This second Proof-of-Concept (PoC2) for the "Sleepy Dev Team" project focuses on validating the task intake and initial setup workflow using the Google Agent Development Kit (ADK). Launched via adk web, a root SingleTaskOrchestrator agent receives user chat input and determines if it describes a new task or references an existing one based on the input's format. If the input refers to an existing task, the orchestrator simply notifies the user; otherwise, it delegates the new task description to the TaskSetupAgent sub-agent. The TaskSetupAgent then uses an LLM to infer a task type prefix (like Bug_ or Feature_), calculates the next sequence number for that type by scanning existing folders, generates a concise slug, and automatically creates the standardized task folder structure (/ai-tasks/Prefix_NN_slug/) with initial files. Successful completion demonstrates the system's ability to correctly route incoming task requests and automate the creation of organized workspaces for new development items. 

## Generated Folder Path

Full path to generated folder: ai-specs/05-01_01_initial_implementation 

## IMPORTANT
 - DO NOT EDIT ANY CODE UNTIL I CONFIRM ITS OKAY

## Tasks

### Clarify Requirements & Assumptions
```
- GUIDE me through a structured Q&A process to clarify requirements and finalize assumptions for implementing the feature described in the `Feature Overview`.
- BEGIN by ANALYZING all provided context
- TELL me your initial `Assumptions` based on your context. 
  - IMPORTANT: Incorporate obvious details from your context directly into assumptions; do not ask questions about them.
- ASK me the initial `Clarifying Questions` you identify as necessary to resolve ambiguities or gather missing critical details for planning.
  - IMPORTANT: State clearly that you will WAIT for my answers before proceeding. WAIT for my response. Do not continue until I reply.
- CONTINUE the detailed questioning iteratively based on my answers. 
- ASK necessary follow-up questions if my responses are unclear or introduce new points requiring clarification. 
  - IMPORTANT: WAIT for my response after each round of questions before proceeding.
- REPEAT this Q&A cycle until you are confident you fully understand the requirements and all critical ambiguities necessary for architectural planning have been resolved.
- Once confident, SIGNAL your readiness by TELLING me the complete `Final Assumptions` list, summarizing our entire understanding based on the initial context and all Q&A.
  - IMPORTANT: AWAIT my explicit confirmation that these `Final Assumptions` are accurate and complete before concluding this task. Do not suggest moving to the next task until I confirm.
```

### Architecture Brainstorming
```
- CREATE a brainstorm doc called ai-specs/05-01_01_initial_implementation\generated\architecture_brainstorm.md 
 - IMPORTANT: Use the `Final Assumptions` established in the previous task as the basis for brainstorming.
- THINK about 3 different potential ways to implement the feature based on the context and finalized assumptions.
- UPDATE the created document (`architecture_brainstorm.md`) by adding a short summary of each of the 3 approaches, including potential pros and cons for each.
   -IMPORTANT: Do not output any of the contents of the brainstorm document to the chat, only write to the specified file path.
```

### Human in the loop
```
- ASK me to review the doc
```

### Create PRD
```
- CREATE a PRD in ai-specs/05-01_01_initial_implementation/generated/prd.md using the excepted method using the `Generated Folder Path` above
```

### Human in the loop
```
 - ASK for feedback doc
```

### Create tech architecture doc
```
- RE-REVIEW the best practices doc and use for the following steps
- CREATE a tech architecture doc in ai-specs/05-01_01_initial_implementation/generated/tech_architecture.md and include the following sections:
  - File structure
```

### Human in the loop
```
 - ASK for feedback doc
```
