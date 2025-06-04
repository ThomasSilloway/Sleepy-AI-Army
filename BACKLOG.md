## General double check git branch before Infantry

General should be updated to double check the git branch is the same every time it runs the Infantry.  If it's not, then need to halt execution.

## Check files for aider

After parsing out the files for aider to work on, if those files don't exist yet, it should fail. Would need to handle the case where it's meant to be a new file that's getting added tho

## Refactor aider_service

Refactor aider_service into its own aider folder with prompts.py file that can have the aider prompts.

## Manifest commit git

Make sure after manifest is created that it's committed via git

## Git branch name check

Git_branch node: Check if branch name exists already, if it does add some kind of hash after to make it unique
