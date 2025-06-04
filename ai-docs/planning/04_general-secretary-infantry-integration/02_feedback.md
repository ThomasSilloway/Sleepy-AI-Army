# Feedback on `army-infantry` Integration Plan

- Actually the General can repair the situation if the Army Infantry fails to return to the original branch.  It can just checkout the original branch itself.  So no need to halt execution.  Just log the error and then checkout the original branch. If there are any files unstaged though, it should commit those files with the message "AI General - Cleanup Infantry unstaged files".

- I've already updated army-general's git_service.py to the asyncio version, but it's usage has not been updated yet.

- Secretary does need to be updated actually bc it's still referencing old terminology like `goals` and `tasks` and should be updated to follow the naming conventions that both army infantry uses and the Readme specifies for the grand vision like `missions`, etc