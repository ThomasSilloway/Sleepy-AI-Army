## Refactor aider_service

Refactor aider_service into its own aider folder with prompts.py file that can have the aider prompts.

## Git branch name check

Git_branch node: Check if branch name exists already, if it does add some kind of hash after to make it unique

## Handle aider crashes gracefully

Aider crashes sometimes - Need to detect crashes (lack of streamed output for X seconds?) or presence of this string `Please consider reporting this bug to help improve aider`

## Update formatting in Mission Report - Execution Summary

### File Names

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

### New lines

Right now all the lines are squished together in the markdown preview, need to add `- ` before each line so it becomes a bullet list
