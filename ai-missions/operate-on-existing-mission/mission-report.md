# Mission Report

Add commandline support to run infantry on existing mission

## Status

SUCCESS

## Execution Summary

 - Added argument parsing logic to `main.py`
 - Modified `main.py` to handle `--mission_folder_path` argument
 - Modified `main.py` to conditionally run `_run_secretary`
 - Created `run-general-on-mission.bat`
 - `run-general-on-mission.bat` prompts user for mission folder
 - `run-general-on-mission.bat` executes `main.py` with the provided path

## Files Modified

- `army-general\src\main.py`
- `run-general-on-mission.bat`

## Files Created

No files created.

## Git Branch

feature/add-commandline-mission-support

## Git Commits

- da14d9c Aider: Feature: Add script to run general on mission
- 12ce008 Aider: Feature: Run general on specific mission folder via arg

## LLM Usage Cost

Total Cost: $0.05

## Errors and Issues

No errors reported.

## Last Update
2025-06-12 14:48:28