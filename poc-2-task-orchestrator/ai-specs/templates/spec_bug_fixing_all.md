# twitch-interactive-app

## High Level Overview
 We just implemented a new feature. We found a bug in the implementation.

 Follow the steps below, starting with the first one and then choose the next task based off of the instructions.

## Bug Description

- 

## Docs

Related Files: 

PRD: @/{{ prd_link }}

Change Notes: @/{{ change_notes }}

Best Practices: @/ai-docs/best_practices.md 

Project Tech Design: @/project-tech-design.md

## Feature info

{{ feature_overview }}
 
## Project Details

{{ project_details }} 

## Generated Folder Path

Full path to generated folder: {{ generated_folder }}

## Boomerang mode sub task creation

{{ task_boomerang_mode }}

## Tasks
Perform the following tasks in order:

### Create bug report
```
Record your notes about the bug in a new file inside {{ generated_folder }}/generated/bugs/
- Located the {{ generated_folder }}/generated/bugs folder in the same directory as the prd file
- Find the highest bug number folder in the {{ generated_folder }}/generated/bugs folder
- Naming convention: Bug_<number + 1>_<Bug_Description>
- Note the bug description in the folder name should be 5 words or less
- Example: Bug_01_Signal_Connection_API_Incompatibility
- CREATE the new folder with that name in {{ generated_folder }}/generated/bugs/
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

{{ task_change_notes }}
