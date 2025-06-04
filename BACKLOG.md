## General double check git branch before Infantry

General should be updated to double check the git branch is the same every time it runs the Infantry.  If it's not, then need to halt execution.

## Aider service error handling with branches

When the aider node has an error, it needs to goto -> check out original branch node then to the error node or the error node needs to checkout the original branch if it was already checked out, maybe that's a better idea

## Check files for aider

After parsing out the files for aider to work on, if those files don't exist yet, it should fail. Would need to handle the case where it's meant to be a new file that's getting added tho

## Refactor aider_service

Refactor aider_service into its own aider folder with prompts.py file that can have the aider prompts.