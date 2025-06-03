Make sure during each step you adhere to the coding conventions in `ai-docs\CONVENTIONS.md`

You are an expert software architect. You have a couple of jobs:

1. Explain how the current code works related to the problem outlined below.
2. Brainstorm 2-3 solutions to the problem below. After that, brainstorm 2 radically different approaches.
3. Write this brainstorming to a temporary file that's appropriately named in ai-docs/planning/<insert-next-number>_<insert-appropriate-folder-name>/brainstorming.md   ex folder name: `01_task-name` - Make sure to look at the list of folders we already have to figure out the next number to use for this folder name.
  IMPORTANT - Do not brainstorm any tests, tests are not needed for this project

When those are completed, assume the role of a critical CTO for the company and critique the brainstorming options. You have a couple different jobs:

1. List out the pros and cons and give each one a grade from A-F (A is excellent, F is fail just like in school).
2. Make a recommendation of which approach is best.
3. Generate a final solution that uses that final version, with changes to mitigate the pros and turn the plan from whatever grade it was into an A+ grade. If it makes sense, integrate elements from other solutions that were proposed that seem valuable. Write the entire critique to ai-docs/planning/<insert-appropriate-folder-name>/critique.md
4. Generate a spec for an ai coding agent containing the follow sections - Problem, Solution, High Level Implementation Plan. Use Sparse Priming Representation for this spec. Write this spec to a temporary file that's appropriately named ai-docs/planning/<insert-appropriate-folder-name>/spec.md
  IMPORTANT - Do not include testing in your critique, tests are not needed for this project

When the spec is completed, assume the role of a software engineer that has a single job:
1. Implement the changes described in the new spec file

When the spec is implemented, assume the role of the CTO again and do the following:
1. Follow the same CTO process to critique the code.
2. Add your critique to a file called `ai-docs/planning/<insert-appropriate-folder-name>/critique-code.md`

When the code critique is completed, assume the role of a software engineer again that has a single job:
1. Implement the changes suggested by the CTO.

Here's the problem we are trying to solve:

```
Status:

We just added the file scaffolding for the army-infantry folder. We also built out the scaffolding for graph builder and graph state.

Problem:

`army-infantry\src\nodes\initialize_mission\node.py` was just updated with a TODO that needs to be implemented.

The llm prompt service will need to be added to the config in main.py, while you're at it, add the remaining services as well. they can be found in the services folder.

Look at how `army-secretary\src\services\backlog_processor.py` builds the prompt for `_sanitize_title_with_llm` as an example of how to build the prompt.

Refer to the following planning files for more context:
- `ai-docs\planning\01_infantry-full\01_vision-statement.md`
- `ai-docs\planning\01_infantry-full\03_tech-design-considerations.md`
- `ai-docs\planning\01_infantry-full\04_feature-list.md`

You should be working on these files:
- `army-infantry\src\nodes\initialize-mission\node.py`
- the main file in that folder
```