# TODOs for PoC 8

Working directory: `poc-8-backlog-to-goals`

Implement some cleanup and a few small tweaks outlined below. Perform each task one at a time and in the exact order below.

# Tasks

## Logging

Move the logging from `main.py` into its own class under `src\utils\logging_setup.py`

## Implement all TODOs

Implement all the TODOs in the `poc-8-backlog-to-goals` code and then remove the TODO comments.

# Critique and improve the code

Assume the role of a critical CTO for the company and critique the changes for the working directory. You have a couple different jobs:

1. List out the good and bad of the changes to the working directory and give a grade from A-F (A is excellent, F is fail just like in school). Don't grade based off of testing, its not needed for this PoC. Only critique the changes made, do not critique the original code.
2. Make recommendations on how to improve the code to with changes to mitigate the bad while keeping the good and turn the code from whatever grade it was into an A+ grade. Keep in mind that tests are not needed for this PoC.
3. Generate a spec for an ai coding agent containing the follow sections for each aspect of the changes - Problem, Solution, High Level Implementation Plan. Use Sparse Priming Representation for this spec. So there should be multiple Problem/Solution/High Level Implementation Plan sections, one for each aspect of the changes in this document. The spec should be put into the working directory in the directory `ai-docs\specs\XX-short-description` where `XX` is the next number in the sequence and `short-description` is a short description of the spec.

## Implement changes from new spec

Assume the role of an expert software engineer and implement the changes from the spec the CTO generated above.  Don't implement any tests even if the spec says you should.

## Don't implement tests

Don't implement tests, if there any any tests, remove them
