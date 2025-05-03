## High Level Overview
 We just implemented a new feature. There's a few things to tweak to add some polish

  Follow each Task at the bottom of this prompt one by one, make sure not to skip any steps.

## Polish

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

### Create polish plans
```
Record your notes about each polish item in a new file inside {{ generated_folder }}/generated/polish/
- Find the highest number folder in the {{ generated_folder }}/generated
- Naming convention: Polish_<number + 1>_<Polish_Description>
- Note the Polish description in the folder name should be 5 words or less
- Example: Polish_01_Improve_Timestamp_Formatting
- CREATE the new folder with that name in {{ generated_folder }}/generated/polish/
- Then write the polish description into a new file inside the folder called `polish_description.md`
- Write 3 possible solutions for how to implement this small change to the feature
- ASK ME to review the polish reports before doing anything else
```

### Implement the changes for each polish item one by one
```
- IMPLEMENT the polish_description.md plan with the accepted solution
- ASK me to run the app again and check functionality
```

{{ task_change_notes }}
