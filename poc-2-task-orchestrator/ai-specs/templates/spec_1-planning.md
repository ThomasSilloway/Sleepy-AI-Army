# Overview

  Let's plan out a new feature. I've included detailed info below.

  Follow each task below one by one, make sure not to skip any steps.

## Feature Overview

{{ feature_overview }}

## Relevant files

- (Add your docs here)


- Project Tech Design: @/project-tech-design.md
- Best Practices: @/ai-docs/best_practices.md 

## Project Details

{{ project_details }} 

## Generated Folder Path

Full path to generated folder: {{ generated_folder }} 

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
- CREATE a brainstorm doc called {{ generated_folder }}\generated\architecture_brainstorm.md 
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
- CREATE a PRD in {{ generated_folder }}/generated/prd.md using the excepted method using the `Generated Folder Path` above
```

### Human in the loop
```
 - ASK for feedback doc
```

### Create tech architecture doc
```
- RE-REVIEW the best practices doc and use for the following steps
- CREATE a tech architecture doc in {{ generated_folder }}/generated/tech_architecture.md and include the following sections:
  - File structure
```

### Human in the loop
```
 - ASK for feedback doc
```
