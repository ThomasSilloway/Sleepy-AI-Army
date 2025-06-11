## Refactor aider_service

Refactor aider_service into its own aider folder with prompts.py file that can have the aider prompts.

## Git branch name check

Git_branch node: Check if branch name exists already, if it does add some kind of hash after to make it unique

## Handle aider crashes gracefully

Aider crashes sometimes - Need to detect crashes (lack of streamed output for X seconds?) or presence of this string `Please consider reporting this bug to help improve aider`

## Update formatting in Mission Report - Execution Summary

Right now we get: 

```
Added comments to functions in `projects\isometric_2d_prototype\isometric_2d_prototype\ai_components\shoot_component.gd`
Removed comment for `_ready()` in `projects\isometric_2d_prototype\isometric_2d_prototype\ai_components\shoot_component.gd`
```

It would be better if it was just the file name, not the whole relative path like this:

```
Added comments to functions in `shoot_component.gd`
Removed comment for `_ready()` in `shoot_component.gd`
```

We already have the full paths in the Files Modified and Files Created sections, so we can just show the filename in the Execution Summary

## Aider error not reported in the mission report

### Logs - Detailed

logs\detailed.log

### Logs - Overview

======== Logging initialized. Date: 2025-06-11 =========


[18:53:05.097] (overview) Invoking graph execution...
[18:53:05.099] (overview) Executing initialize_mission_node
[18:53:06.360] (overview) 
        Mission initialized:
            - Title: 'Add concise comments to functions in character_controller_ai.gd'
            - Branch to be created: 'docs/add-comments-character-controller'
            - Original branch: 'feature/basic-ai'
            - Editable files:  
                   -projects\isometric_2d_prototype\isometric_2d_prototype\character_controller\character_controller_ai.gd
            - Mission spec: 'Add concise comments to functions in `projects\isometric_2d_prototype\isometric_2d_prototype\character_controller\character_controller_ai.gd`. Only one line per comment & each comment should be no longer than 80 characters.
'
    
[18:53:06.361] (overview) Executing git_branch_node
[18:53:06.389] (overview) Checked out branch: docs/add-comments-character-controller
[18:53:06.390] (overview) Executing code_modification_node
[18:53:31.353] (error) Aider ERROR: The LLM did not conform to the edit format.
[18:53:31.353] (error) Aider ERROR: SearchReplaceNoExactMatch: This SEARCH block failed to exactly match lines
in
projects\isometric_2d_prototype\isometric_2d_prototype\character_controller\cha
racter_controller_ai.gd
<<<<<<< SEARCH
func _on_action_completed() -> void: # Ends the AI turn.
=======
func _on_action_completed() -> void: # Called when an action is completed.
>>>>>>> REPLACE
[18:53:31.353] (error) Error in code_modification_node: Aider reported 2 errors during its execution.
Traceback (most recent call last):
  File "C:\GithubRepos\Sleepy-AI-Army\army-infantry\src\nodes\code_modification\node.py", line 27, in code_modification_node
    state = await _code_modification(state, config)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\GithubRepos\Sleepy-AI-Army\army-infantry\src\nodes\code_modification\node.py", line 51, in _code_modification
    _update_mission_context_from_aider_summary(mission_context, aider_summary, state)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\GithubRepos\Sleepy-AI-Army\army-infantry\src\nodes\code_modification\node.py", line 123, in _update_mission_context_from_aider_summary
    raise RuntimeError(f"Aider reported {len(aider_summary.errors_reported)} errors during its execution.")
RuntimeError: Aider reported 2 errors during its execution.
[18:53:31.355] (overview) Executing git_checkout_original_branch_node
[18:53:31.406] (overview) Checked out original branch: feature/basic-ai
[18:53:31.407] (overview) Executing mission_reporting_node
[18:53:31.411] (overview)   - Final Step Name: mission_reporting_node
