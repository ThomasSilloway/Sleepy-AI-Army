## Handle aider crashes gracefully

Aider crashes sometimes - Need to detect crashes (lack of streamed output for X seconds?) or presence of this string `Please consider reporting this bug to help improve aider`

## General operate on existing mission

Add support for general commandline to operate on an already created mission

## Aider questions hang the process

Aider fails to commit changes when it identifies new files to add without a clear directive of what to do.

Not really sure how to solve this, but one idea would be to have a separate thread listen for these kinds of questions and tell it to just do the best with what it has and apply the changes.
