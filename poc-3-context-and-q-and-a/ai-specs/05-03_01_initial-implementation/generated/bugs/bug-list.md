## QnA agent read 3 files 2x

- QnA agent read the files twice in a row instead of doing it just a single time. It read 3 files, then said `Okay, I will start the Q&A process for the task "Bug_01_players-pathing-destroyed-walls".

First, I need to read the context, status, and any existing Q&A.
`  Then read the same 3 files again.  Need to make it so it only reads the files once per file

## Changelog agent

The text sent to the changelog agent was correct, but the changelog agent made up its own text instead of using the one from the function call to it.

## Context agent

The list directories part of the context agent only listed top level directories and didn't do it recursively based off of folders it fiinds interesting - probably a prompting issue.