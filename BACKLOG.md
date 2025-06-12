## Env variable check

Do checking for environment variables in the general for all of the projects to make sure everything is set up properly.

Files to modify:

`army-general\src\main.py` - Update to check for the existance of `.env` in `army-infantry`, and `army-secretary` and fail with a nice error message if they are not found.

Put this functionality in a new function.

Use the code in `_run_infantry_mission()` as an example of how to get the full path to the infantry directory
