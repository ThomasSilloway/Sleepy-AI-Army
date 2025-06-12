Add support for general commandline to run the infantry on an already created mission

- Add commandline argument to army-general to specify a mission folder path
- Update army-general `army-general\src\main.py` to check for this argument and if present, run the infantry on that mission folder instead of reading the secretary output file
- Look at `army-secretary\src\main.py` for example of how to add commandline arguments
- Create new batch file called `run-general-on-mission.bat` based off of `run-general.bat` that prompts for the mission folder path and then includes it as a commandline param
