## High Level Overview
 We just implemented a new feature. There's a few things to tweak to add some polish

  Follow each Task at the bottom of this prompt one by one, make sure not to skip any steps.

## Polish

- 

## Docs

Related Files: 

PRD: @/ai-specs/05-01_02_initial_implementation/generated/prd.md

Change Notes: @/ai-specs/05-01_02_initial_implementation/generated/change_notes.md

Best Practices: @/ai-docs/best_practices.md 

Project Tech Design: @/project-tech-design.md

## Feature info

Implement the prd

 
## Project Details

This project is a Proof-of-Concept (PoC) designed to validate the core agent looping and file interaction mechanisms for the larger "Sleepy Dev Team" initiative using the Google Agent Development Kit (ADK). It implements a minimal ADK application featuring a LoopAgent that iteratively invokes a BacklogReaderAgent. The BacklogReaderAgent utilizes ADK tools to read task descriptions one by one from a designated /ai-tasks/backlog.md file, report the task content, and then physically remove the processed line from the file. Execution relies on the standard adk web command within a local Python virtual environment, with progress observed via console output. Successful completion will demonstrate the fundamental ADK patterns for sequential task processing from a file and tool-based file system interaction, confirming feasibility for the main project. 

## Generated Folder Path

Full path to generated folder: ai-specs/05-01_02_initial_implementation

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

Implement the prd

 
## Project Details

This project is a Proof-of-Concept (PoC) designed to validate the core agent looping and file interaction mechanisms for the larger "Sleepy Dev Team" initiative using the Google Agent Development Kit (ADK). It implements a minimal ADK application featuring a LoopAgent that iteratively invokes a BacklogReaderAgent. The BacklogReaderAgent utilizes ADK tools to read task descriptions one by one from a designated /ai-tasks/backlog.md file, report the task content, and then physically remove the processed line from the file. Execution relies on the standard adk web command within a local Python virtual environment, with progress observed via console output. Successful completion will demonstrate the fundamental ADK patterns for sequential task processing from a file and tool-based file system interaction, confirming feasibility for the main project. 

## Generated Folder Path

Full path to generated folder: ai-specs/05-01_02_initial_implementation

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

### Ask me questions
```
- ASK me questions about each polish item to make sure you understand the requirements
```

### Implement the changes for each polish item one by one
```
- IMPLEMENT the change
```

### Review
```
- ASK me to run the app again and check functionality
```

### Update change_notes.md file
- IMPORTANT: Always preserve existing content and append new changes. Convey this very clearly to any sub task along with all of the important notes below
- First READ the current content of ai-specs/05-01_02_initial_implementation/generated/change_notes.md to determine the next version number
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
