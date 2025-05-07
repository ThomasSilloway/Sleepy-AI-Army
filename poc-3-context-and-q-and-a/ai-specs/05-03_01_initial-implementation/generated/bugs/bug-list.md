## QnA agent read 3 files 2x

- QnA agent read the files twice in a row instead of doing it just a single time. It read 3 files, then said `Okay, I will start the Q&A process for the task "Bug_01_players-pathing-destroyed-walls".

First, I need to read the context, status, and any existing Q&A.
`  Then read the same 3 files again.  Need to make it so it only reads the files once per file

## Changelog agent

The text sent to the changelog agent was correct, but the changelog agent made up its own text instead of using the one from the function call to it.

## Context agent

The list directories part of the context agent only listed top level directories and didn't do it recursively based off of folders it fiinds interesting - probably a prompting issue.

## Session state usage

we probably are utilizing the session state enough or at all. 

Not exactly sure how that's supposed to work, but I'm curious if the q&a or context agents are reading the status file at all. If they are, we can prevent that by putting the current task status into the session. Then the other agents can use that

Should probably do the same thing with the file paths so we have less places to update later on when we want to remove it from the constants.py