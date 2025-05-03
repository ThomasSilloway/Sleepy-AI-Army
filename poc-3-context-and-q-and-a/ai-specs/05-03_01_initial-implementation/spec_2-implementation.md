# Overview

  We've just planned out a new feature and created a PRD. Let's work on implementing.

  Follow each Task at the bottom of this prompt one by one, make sure not to skip any steps. 

## Docs

Related Files: 

PRD: @/ai-specs/05-03_01_initial-implementation/generated/prd.md

Change Notes: @/ai-specs/05-03_01_initial-implementation/generated/change_notes.md

Best Practices: @/ai-docs/best_practices.md 

## Feature info

implement the prd

 
## Project Details

 

## Generated Folder Path

Full path to generated folder: ai-specs/05-03_01_initial-implementation

## Tasks

### Implement PRD
 - Implement the PRD, keeping in mind to limit files to 500 lines of code or less. For each feature/section in the PRD that makes sense, create a new subtask for boomerang mode. Implement using the technical architecture

### Update change_notes.md file
- IMPORTANT: Always preserve existing content and append new changes. Convey this very clearly to any sub task along with all of the important notes below
- First READ the current content of ai-specs/05-03_01_initial-implementation/generated/change_notes.md to determine the next version number
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

### Double check your implementation
```
 - Make sure the PRD was implemented correctly
 - Append the notes of your review to change_notes.md
 - Ensure each file that was touched has an empty line at the end of the file
```
