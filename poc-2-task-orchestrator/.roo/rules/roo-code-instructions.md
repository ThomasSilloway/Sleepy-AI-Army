# Overview

- Framework - python - Google ADK

## Project Goals

- Create an ai-agent framework

## Implementation details
- Ensure there's a newline at the end of each file
- Assume any commands run in the terminal are run in a powershell terminal
- Don't delete existing debug logging, I want to keep it!

## Running commands
 - WHenever you want to run a command, format the command like you're using powershell. Commands are always run in powershell. Ex: Don't use && to combine commands, use ; instead

## Tool usage
 - When directed to make a web search, use the fetch tool. Only look for the top 3 search results and then only search one of those URLs for the in fo at a time to avoid getting rate limited.
