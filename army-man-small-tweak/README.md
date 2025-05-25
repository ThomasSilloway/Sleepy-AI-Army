# army-man-small-tweak

Proof-of-Concept for LangGraph Orchestration (PoC7).

## Setup

1. Ensure Python 3.9+ is installed.
2. Install `uv` (if you haven't already):
   ```bash
   pip install uv
   ```
   Or, for a global installation, you might prefer `pipx install uv`.
3. **Dependencies & Environment**: This project uses `uv` and `pyproject.toml` to manage dependencies. When you run commands like `uv run`, `uv` will automatically create a virtual environment (usually `.venv` in the project root) and install the dependencies listed in `pyproject.toml` if they are not already present or if `uv.lock` is not found.
4. **Locking Dependencies (Recommended)**: To ensure reproducible builds, after any changes to dependencies in `pyproject.toml`, generate or update the lock file:
   ```bash
   uv lock
   ```
   This creates/updates `uv.lock`, which `uv` will use to install exact versions of dependencies.

## Running

To execute the main application script:
```bash
cd army-man-small-tweak
uv run .\src\main.py
```
This command tells `uv` to run the specified Python script within the managed environment, ensuring all dependencies from `pyproject.toml` (and `uv.lock` if present) are available.
