# Overview

  Some work on this new feature has already begun, let's document the progress thus far into /ai-docs/changelog/<number>-app-updates.md

  You are in Architect mode, you can directly write and modify .md files.

  Follow each Task at the bottom of this prompt one by one, make sure not to skip any steps.

## Feature Overview

implement the prd



## Docs

PRD: @/ai-specs/05-01_01_initial_implementation/generated/prd.md

Change Notes: @/ai-specs/05-01_01_initial_implementation/generated/change_notes.md

Project Tech Design: @/project-tech-design.md

Project Summary: @/project-summary.md

## Project Details

This second Proof-of-Concept (PoC2) for the "Sleepy Dev Team" project focuses on validating the task intake and initial setup workflow using the Google Agent Development Kit (ADK). Launched via adk web, a root SingleTaskOrchestrator agent receives user chat input and determines if it describes a new task or references an existing one based on the input's format. If the input refers to an existing task, the orchestrator simply notifies the user; otherwise, it delegates the new task description to the TaskSetupAgent sub-agent. The TaskSetupAgent then uses an LLM to infer a task type prefix (like Bug_ or Feature_), calculates the next sequence number for that type by scanning existing folders, generates a concise slug, and automatically creates the standardized task folder structure (/ai-tasks/Prefix_NN_slug/) with initial files. Successful completion demonstrates the system's ability to correctly route incoming task requests and automate the creation of organized workspaces for new development items. 

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
### Analyze Implementation Refinements for Best Practices
- PREMISE - Each diff represents a necessary correction or refinement addressing issues or limitations in the preceding code implementation.
- LOCATE - The `ai-specs/05-01_01_initial_implementation/generated/git_changes` directory within the current feature's spec folder.
- ITERATE - Through all `NN_<hash>.diff` files chronologically based on their numeric prefix.
- ANALYZE - Each commit message and diff to understand the implementation's evolution:
    - SUMMARIZE The specific code modifications introduced by the diff.
    - INFER The underlying reason, issue, or limitation in the *previous* code state that necessitated this change.
    - IDENTIFY The corrective pattern, technique, or programming principle applied in the solution.
- GENERATE - A feature-specific report named ai-specs/05-01_01_initial_implementation/generated/refinement_analysis.md
 This report should detail, for each commit:
    - The inferred reason for the change (original issue/limitation).
    - The corrective pattern or principle applied.
- SYNTHESIZE - Generalizable lessons, recurring patterns, and actionable principles by reviewing the complete `refinement_analysis.md`.
- UPDATE - The central ai-docs/best_practices.md document by intelligently integrating the synthesized findings.
    - IMPORTANT: Ensure new additions are non-redundant with existing content.
    - IMPORTANT: Maintain or improve the document's clear and logical organization.
```
