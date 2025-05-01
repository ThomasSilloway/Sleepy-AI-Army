# Overview

  We've just planned out a new feature and created a PRD. Let's work on implementing.

  Follow each Task at the bottom of this prompt one by one, make sure not to skip any steps. 

## Docs

Related Files: 

PRD: @/{{ prd_link }}

Change Notes: @/{{ change_notes }}

Best Practices: @/ai-docs/best_practices.md 

## Feature info

{{ feature_overview }}
 
## Project Details

{{ project_details }} 

## Generated Folder Path

Full path to generated folder: {{ generated_folder }}

## Boomerang mode sub task creation

{{ task_boomerang_mode }}

## Tasks

### Implement PRD
 - Implement the PRD, keeping in mind to limit files to 500 lines of code or less. For each feature/section in the PRD that makes sense, create a new subtask for boomerang mode. Implement using the technical architecture

{{ task_change_notes }}

### Double check your implementation
```
 - Make sure the PRD was implemented correctly
 - Append the notes of your review to change_notes.md
 - Ensure each file that was touched has an empty line at the end of the file
```
