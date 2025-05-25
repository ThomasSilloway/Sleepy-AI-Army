# TODOs for PoC 8

Working directory: `poc-8-backlog-to-goals`

Implement a bunch of cleanup and a few small tweaks outlined below

## Paths

The backlog file path and goals output directory that are hardcoded in `main.py` should be moved to a config file similar to how it is done in `army-man-small-tweak`.

We need these properties
 - goal_git_path
 - backlog_file_name
 - ai_goals_directory_name

Then the backlog file path can be constructed as `os.path.join(goal_git_path, backlog_file_name)`
 and the goals output directory can be constructed as `os.path.join(goal_git_path, ai_goals_directory_name)`

The config file should handle loading from a yaml file the same way it is done in `army-man-small-tweak`.

A change from `army-man-small-tweak` is we want accessable properties for the combined backlog file path and goals output directory.

All of this functionality should be in the config file

## Logging

Add a log file called backlog-to-goals.log that logs to `poc-8-backlog-to-goals\logs` folder

## Remove unnecessary comments

There are a lot of comments in the code that are not needed. Remove them. Make any necessary comments more concise.

## Implement all TODOs

Implement all the TODOs in the `poc-8-backlog-to-goals` code and then remove the TODO comments.

## Cleanup logs

There are a few instances of print() being used immediately after logger.info() - this seems unnecessary.

## Confirm llm_prompt_service.py

Confirm `poc-8-backlog-to-goals\src\services\llm_prompt_service.py` is an exact copy of `army-man-small-tweak\src\services\llm_prompt_service.py`

## Don't implement tests

Don't implement tests for this PoC.

# Critique and improve the code

Assume the role of a critical CTO for the company and critique the for the working directory. You have a couple different jobs:

1. List out the good and bad of the working directory and give a grade from A-F (A is excellent, F is fail just like in school).
2. Make recommendations on how to improve the code to with changes to mitigate the bad while keeping the good and turn the code from whatever grade it was into an A+ grade.
4. Generate a spec for an ai coding agent containing the follow sections for each aspect of the changes - Problem, Solution, High Level Implementation Plan. Use Sparse Priming Representation for this spec. So there should be multiple Problem/Solution/High Level Implementation Plan sections, one for each aspect of the changes in this document. The spec should be put into the working directory in the directory `ai-docs\specs\XX-short-description` where `XX` is the next number in the sequence and `short-description` is a short description of the spec.

Then:

Assume the role of an expert software engineer and implement the changes from the spec.