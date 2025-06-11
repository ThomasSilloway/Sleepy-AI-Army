## Manifest commit git

Make sure after manifest is created that it's committed via git

## Refactor aider_service

Refactor aider_service into its own aider folder with prompts.py file that can have the aider prompts.

## Git branch name check

Git_branch node: Check if branch name exists already, if it does add some kind of hash after to make it unique

## Handle aider crashes gracefully

Aider crashes sometimes - Need to detect crashes (lack of streamed output for X seconds?) or presence of this string `Please consider reporting this bug to help improve aider`

## Fix bug with calling infantry from general

### Notes
- `update-comments-shoot_component` has an underscore - oh it's just using the value from the config, nopt from commandline.

- Also noticed this time it didn't create a branch for some reason

### Log
:15.887 - info - Constructed army-infantry run command: uv run src/main.py --root_git_path C:\GithubRepos\Project-Elder --mission_folder_path C:\GithubRepos\Project-Elder\ai-missions\update-comments-with-a-temp-word
08:15.887 - info - Executing army-infantry from directory: C:\GithubRepos\Sleepy-AI-Army\army-infantry
08:16.761 - info - --- Start of output from army-infantry ---
08:16.761 - info - [ARMY-INFANTRY STDOUT]: (empty)
08:16.761 - error - [ARMY-INFANTRY STDERR]: warning: `VIRTUAL_ENV=C:\GithubRepos\Sleepy-AI-Army\army-general\.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
08:16.761 - error - [ARMY-INFANTRY STDERR]: Traceback (most recent call last):
08:16.761 - error - [ARMY-INFANTRY STDERR]:   File "C:\GithubRepos\Sleepy-AI-Army\army-infantry\src\main.py", line 41, in <module>
08:16.762 - error - [ARMY-INFANTRY STDERR]:     app_config = AppConfig(command_line_git_path=args.root_git_path)
08:16.762 - error - [ARMY-INFANTRY STDERR]:   File "C:\GithubRepos\Sleepy-AI-Army\army-infantry\src\app_config.py", line 110, in __init__
08:16.762 - error - [ARMY-INFANTRY STDERR]:     self.validate()
08:16.762 - error - [ARMY-INFANTRY STDERR]:     ~~~~~~~~~~~~~^^
08:16.762 - error - [ARMY-INFANTRY STDERR]:   File "C:\GithubRepos\Sleepy-AI-Army\army-infantry\src\app_config.py", line 211, in validate
08:16.762 - error - [ARMY-INFANTRY STDERR]:     raise ValueError(f"mission_folder_path '{self.mission_folder_path_absolute}' is not a valid directory.")
08:16.762 - error - [ARMY-INFANTRY STDERR]: ValueError: mission_folder_path 'C:\GithubRepos\Project-Elder\ai-missions\update-comments-shoot_component' is not a valid directory.
08:16.762 - info - --- End of output from army-infantry ---
08:16.762 - error - army-infantry execution failed for mission C:\GithubRepos\Project-Elder\ai-missions\update-comments-with-a-temp-word with return code 1.
08:16.763 - warning - army-infantry failed to process mission: C:\GithubRepos\Project-Elder\ai-missions\update-comments-with-a-temp-word. Continuing with cleanup.
08:16.780 - info - Current branch: feature/basic-ai

