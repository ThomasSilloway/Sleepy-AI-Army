@echo off
REM Batch file to run the PoC-9 application using uv

echo Checking if uv is available...
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: uv command not found. Please ensure uv is installed and in your PATH.
    goto :eof
) else (
    echo uv found.
)

REM Set the current directory to the script's directory
cd /D "%~dp0"

echo Starting PoC-9 Async LangGraph with Pydantic-AI application...

REM Option 1: Run main.py directly assuming uv handles the src context or it's run from root.
REM This is often cleaner if `pyproject.toml` is set up for src layout,
REM or if main.py handles its internal paths well.
uv run python src/main.py

if %errorlevel% neq 0 (
    echo Application failed to start or exited with an error.
) else (
    echo Application finished.
)

echo.
REM pause
