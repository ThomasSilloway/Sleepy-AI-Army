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