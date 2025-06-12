## Git branch name check

Git_branch node: Check if branch name exists already, if it does add date and time to the end of the branch name to make it unique in the format MM-DD-HH-MM-SS

Files to update:
 - army-infantry\src\nodes\git_branch\node.py
 - army-infantry\src\services\git_service.py


## Handle aider crashes gracefully

Aider crashes sometimes - Need to detect crashes (lack of streamed output for X seconds?) or presence of this string `Please consider reporting this bug to help improve aider`

## Env variable check

Do checking for environment variables in the general for all of the projects to make sure everything is set up properly.

## General operate on existing mission

Add support for general commandline to operate on an already created mission
