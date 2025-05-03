### Create common mistakes doc
```
- CREATE common_coding_mistakes.md in {{ generated_folder }}/generated folder above if it doesn't exist
- PROMPT coding subtasks to update this file any time our coding agent makes a mistake which causes an error. 
   - Purpose: We'll use this doc to try to improve our best practices for the coding agent over time so it can make less errors.
  - Details to include: compile errors that it caused with its code, how it overcame them and how we could prevent that issue in the future with better documentation, prompts, etc.
- PROMPT coding subtasks to use the best practices docs above to improve the code quality and reduce errors in the future.
```
