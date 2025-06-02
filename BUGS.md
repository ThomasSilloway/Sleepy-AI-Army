# Changes needed

List of changes we want to make, but haven't put into the automated backlog or Jules yet.

- The commit messages for Army Man are hard to parse.
 - Better:  `AI Army Man - Start - <TaskName>` and `AI Army Man - Task <Success|Failed>`
- Try removing `ai-docs\CONVENTIONS.md` from the `aider.conf.yml` file.  Add force it added via the commandline
- Secretary needs to commit the removal of the new goals folder 


Readme updates
 - auto commits
 - new conf file

# Brainstorming

# BUGS

## Aider gets stuck when asking for files - Possible fix

### Log

```
Aider v0.82.2
Main model: gemini/gemini-2.5-pro-preview-03-25 with diff-fenced edit format
Weak model: gemini/gemini-2.5-flash-preview-04-17
Git repo: .git with 137 files
Repo-map: disabled
Added army-man-small-tweak\src\models\aider_summary.py to the chat.
Added ai-goals\record-total-cost\task-description.md to the chat (read-only).
```

```
This change adds `Ge` to the imports and uses `ge=0.0` in the `total_cost` field definition, along with updating the description to reflect this constraint. This makes the model more robust by ensuring the cost, if provided, is not negative.
Tokens: 3.3k sent, 2.0k received. Cost: $0.02 message, $0.02 session.

ai-docs\CONVENTIONS.md
You've added `ai-docs/CONVENTIONS.md`. Thank you.

Based on the conventions in `ai-docs/CONVENTIONS.md` (specifically, "`typing.List` is deprecated, use `list` instead"), I've noticed that `army-man-small-tweak/src/models/aider_summary.py` uses `typing.List`.

To apply this convention, I'll need to edit `army-man-small-tweak/src/models/aider_summary.py`.

Could you please add the latest version of `army-man-small-tweak/src/models/aider_summary.py` to the chat so I can propose the necessary changes?
Tokens: 5.5k sent, 128 received. Cost: $0.0082 message, $0.03 session.
```

### Notes

Even though it was tasked with updating the `aider_summary.py` it asked for the file to be added to the chat.

### Questions

- Why did it ask for that file to be added when it was already added and it was making changes?  Maybe the critique pattern is messing things up?
- Why did the CONVENTIONS.md get added after the run already started?  Maybe it doesn't work well with read files getting added to the chat via the config?
   - I think removing this for now might fix our issue