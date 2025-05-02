# twitch-interactive-app

## High Level Overview
 We just implemented a new feature. We found a bug in the implementation.

 Follow the steps below, starting with the first one and then choose the next task based off of the instructions.

## Bug Description

- 

## Docs

Related Files: 

PRD: @/ai-specs/05-01_01_initial_implementation/generated/prd.md

Change Notes: @/ai-specs/05-01_01_initial_implementation/generated/change_notes.md

Best Practices: @/ai-docs/best_practices.md 

Project Tech Design: @/project-tech-design.md

## Feature info

implement the prd

 
## Project Details

This second Proof-of-Concept (PoC2) for the "Sleepy Dev Team" project focuses on validating the task intake and initial setup workflow using the Google Agent Development Kit (ADK). Launched via adk web, a root SingleTaskOrchestrator agent receives user chat input and determines if it describes a new task or references an existing one based on the input's format. If the input refers to an existing task, the orchestrator simply notifies the user; otherwise, it delegates the new task description to the TaskSetupAgent sub-agent. The TaskSetupAgent then uses an LLM to infer a task type prefix (like Bug_ or Feature_), calculates the next sequence number for that type by scanning existing folders, generates a concise slug, and automatically creates the standardized task folder structure (/ai-tasks/Prefix_NN_slug/) with initial files. Successful completion demonstrates the system's ability to correctly route incoming task requests and automate the creation of organized workspaces for new development items. 

## Generated Folder Path

Full path to generated folder: ai-specs/05-01_01_initial_implementation

## Boomerang mode sub task creation

  - You are in boomerange mode, you can read files, but you cannot write to them. You can create sub tasks to edit files.
  
  - When creating subtasks with boomerang mode, make sure to include enough context including the filepaths to any files to be modified, filepaths to design docs, etc

  - Each filepath should be prepending with the (at symbol) followed by (forward slash) symbol followed by the full path relative to the workspace root.  
  
  - IMPORTANT: Do not use backticks around file paths.

  - When creating subtasks use the format below

  - When creating the `Tasks` section from the template, keep each task very discreet, it should only be at most 3 lines per task. 
    - Always have the first word be a verb and ALL CAPS like: CREATE, IMPLEMENT, READ, REVIEW, UPDATE, etc
    - Always create a task for updating the common errors doc
```
# Overview

{{Overview}}

## Docs

{{Docs}}

## Feature info

implement the prd

 
## Project Details

This second Proof-of-Concept (PoC2) for the "Sleepy Dev Team" project focuses on validating the task intake and initial setup workflow using the Google Agent Development Kit (ADK). Launched via adk web, a root SingleTaskOrchestrator agent receives user chat input and determines if it describes a new task or references an existing one based on the input's format. If the input refers to an existing task, the orchestrator simply notifies the user; otherwise, it delegates the new task description to the TaskSetupAgent sub-agent. The TaskSetupAgent then uses an LLM to infer a task type prefix (like Bug_ or Feature_), calculates the next sequence number for that type by scanning existing folders, generates a concise slug, and automatically creates the standardized task folder structure (/ai-tasks/Prefix_NN_slug/) with initial files. Successful completion demonstrates the system's ability to correctly route incoming task requests and automate the creation of organized workspaces for new development items. 

## Generated Folder Path

Full path to generated folder: ai-specs/05-01_01_initial_implementation

## Tasks

### Task 1
 - <insert instructions>

### Task 2
 - <insert instructions>

### Task 3
 - <insert instructions>

```



## Tasks
Perform the following tasks in order:

### Create bug report
```
Record your notes about the bug in a new file inside ai-specs/05-01_01_initial_implementation/generated/bugs/
- Located the ai-specs/05-01_01_initial_implementation/generated/bugs folder in the same directory as the prd file
- Find the highest bug number folder in the ai-specs/05-01_01_initial_implementation/generated/bugs folder
- Naming convention: Bug_<number + 1>_<Bug_Description>
- Note the bug description in the folder name should be 5 words or less
- Example: Bug_01_Signal_Connection_API_Incompatibility
- CREATE the new folder with that name in ai-specs/05-01_01_initial_implementation/generated/bugs/
- Then write the bug description into a new file inside the folder called `bug_description.md`
- Do not write any possible solutions in the bug report, just details about the bug
```

### Bug report review
```
- ASK ME to review the bug report before doing anything else
```

### Figure out next steps
```
 - ASK me which of the following steps below we should continue with (root cause analysis, Architecture Analysis, add logging, write bug fix plan, fix the bug immediately)
```

### Root Cause Analysis
```
- INVESTIGATE related code files to figure out the root cause
- WRITE root_cause_analysis.md with the details of root cause.  If unsure, write 3 options of what the root cause might be
  - Note: Use same directory as the `bug_description.md`
  - Note: Use only pseudo code if its even necessary, do not write full code blocks
- ASK me to review the new document and provide feedback
```

### Architecture Analysis
```
  - IDENTIFY related code files
  - WRITE architecture_analysis.md with details about how the related files and functionality work together, what issues this architecture might have related to the bug, root cause analysis, proposed solutions
   - Note: Use same directory as the `bug_description.md`
   - Note: Use only pseudo code if its even necessary, do not write full code blocks
  - ASK me to review the new document and provide feedback
```

### Add more logging
```
 - ASK me any questions about the bug or code files you might have before proceeding
 - ANALYZE the code files to try to find the root cause
 - ADD Logging to help observability of any issues - logs should be output to the DebugConsole in the app
 - ASK me to run the app again and gather the logs 
 ```

### Write Fix Bug Plan
```
- INVESTIGATE related code files to figure out the root cause
- WRITE bug_fix_plan.md with the details of root cause.  If unsure, write 3 options of what the root cause might be
  - Note: Use same directory as the `bug_description.md`
  - Note: Use only pseudo code if its even necessary, do not write full code blocks
- ASK me to review the new document and provide feedback
```

### Fix the bug
```
- IMPLEMENT the bug fix
- ASK me to run the app again and check functionality
- REPEAT steps above as necessary
```

 ### Complete
 ```
 - WRITE bug_fix_learnings.md with the details of what worked, what didn't work from this process. Use same directory as the `bug_description.md`
 ```

### Update change_notes.md file
- IMPORTANT: Always preserve existing content and append new changes. Convey this very clearly to any sub task along with all of the important notes below
- First READ the current content of ai-specs/05-01_01_initial_implementation/generated/change_notes.md to determine the next version number
- Add a new section with:
  - Version title (increment from last version, e.g., if last was v03, use v04)
    - A brief description of the changes made already made, IMPORTANT: not planned changes
    - Details of what was already implemented/fixed
    - IMPORTANT:
      - ONLY append new changes, DO NOT modify or delete existing content
      - ONLY include changes that have ALREADY been implemented, not future plans
      - Each new version should be added at the bottom of the file
      - Keep the same format as previous versions
      - When creating subtask for boomerang mode - only include the text that needs to change, don't include the entire change notes in the subtask prompt
