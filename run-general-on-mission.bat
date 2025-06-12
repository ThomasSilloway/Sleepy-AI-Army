@echo off
title Run Army General on a Specific Mission

echo.
echo This script will run the Army General on a specific, existing mission folder.
echo You need to provide the full path to the mission folder.
echo.
echo Example: C:\dev\your-project\missions\mission_20240521_123456
echo.

set /p MISSION_FOLDER_PATH="Enter the full path to the mission folder: "

if not defined MISSION_FOLDER_PATH (
    echo.
    echo No mission folder path provided. Aborting.
    pause
    exit /b 1
)

if not exist "%MISSION_FOLDER_PATH%" (
    echo.
    echo The provided path does not exist: "%MISSION_FOLDER_PATH%"
    echo Please check the path and try again.
    pause
    exit /b 1
)

echo.
echo Running Army General for mission: %MISSION_FOLDER_PATH%
echo.

REM This assumes the batch file is run from the project root directory,
REM which contains the 'army-general' folder.
cd army-general
uv run src/main.py --mission_folder_path "%MISSION_FOLDER_PATH%"
cd ..

echo.
echo Army General has finished. Press any key to exit.
pause
