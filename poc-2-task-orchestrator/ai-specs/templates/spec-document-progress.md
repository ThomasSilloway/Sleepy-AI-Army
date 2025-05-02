# Overview

  Some work on this new feature has already begun, let's document the progress thus far into /ai-docs/changelog/<number>-app-updates.md

  You are in Architect mode, you can directly write and modify .md files.

  Follow each Task at the bottom of this prompt one by one, make sure not to skip any steps.

## Feature Overview

{{ feature_overview }}


## Docs

PRD: @/{{ prd_link }}

Change Notes: @/{{ change_notes }}

Project Tech Design: @/project-tech-design.md

Project Summary: @/project-summary.md

## Project Details

{{ project_details }} 

## IMPORTANT
 - DO NOT EDIT ANY CODE 

## Tasks

### Add changelog file
```
- FIND the last change log number in /ai-docs/changelog/
- CREATE /ai-docs/changelog/<next-number>-app-updates-<3 word description>.md
- ANALYZE the current project
- UPDATE app updates file with the latest updates we have implemented thus far in the PRD
```

### Update project summary
```
 - READ @/project-summary.md
   - Purpose: to help summarize the project to an LLM agent
 - CONSIDER changes from the latest feature that may need to be included
 - UPDATE project-summary.md by seamlessly integrating the existing summary with any of these new details into a nice summary for future LLMs to use as a reference for the entire project
   - IMPORTANT: do not reference old features, it should just be a summary of the current state of the project, no need to highlight recent features
   - IMPORTANT: Do not print out the changes to the chat log, directly edit the file
   - IMPORTANT: Do not put full sentences in bold
```

### Update tech design doc
```
- ANALYZE @/project-tech-design.md and see if any changes are necessary due to the new changes.
  - The purpose of this file is to help a coding architect LLM understand what files to change when it comes to bug fixing or making a new feature
- UPDATE the tech design doc with any changes
  - IMPORTANT: do not reference old features, it should just be a summary of the current state of the project, no need to highlight recent features
  - IMPORTANT: Do not print out the changes to the chat log, directly edit the file
  - IMPORTANT: Do not put full sentences in bold, if any are, remove them
```

### Analyze Git Commits for Best Practice
```
- LOCATE {{ generated_folder }}/generated/git_changes directory in the current feature's spec folder
- ITERATE through all `NN_<hash>.diff` files chronologically
- ANALYZE each commit message and diff to identify coding mistakes
- GENERATE the feature-specific {{ generated_folder }}/generated/coding_mistakes.md with findings
- UPDATE `ai-docs/best_practices.md` by extracting general patterns from the analysis and merging new patterns intelligently
  - IMPORTANT: Avoid duplication
  - IMPORTANT: Maintain clear organization
```
