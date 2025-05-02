# Sleepy Dev Team - Task Intake & Setup PoC (PoC2)

Demonstrates task intake and setup using ADK agents (STO, TSA)
and generalized tools.

## Setup
1. Create venv: `python -m venv .venv`
2. Activate: `source .venv/bin/activate` or `.\.venv\Scripts\activate`
3. Install reqs: `pip install -r src/sleepy_dev_poc/requirements.txt`
4. Create task dir: `mkdir ai-tasks` (Already done)
5. (Optional) Create `.env` in `src/sleepy_dev_poc/`

## Execution
Run from the project root: `adk web`  
Interact via chat (e.g., "Fix the login bug", "/ai-tasks/Feature_001_add-widget")