# Sleepy Dev Team - Core Loop PoC

Proof-of-Concept demonstrating a basic ADK agent loop reading tasks from a backlog file using the Google Agent Development Kit (ADK).

## Setup

1.  **Clone the repository (if applicable) or ensure you are in the project root directory.**
2.  **Create a Python virtual environment:**
    ```bash
    python -m venv venv
    ```
3.  **Activate the environment:**
    *   Linux/macOS: `source venv/bin/activate`
    *   Windows (Command Prompt/PowerShell): `.\venv\Scripts\activate`
4.  **Install requirements:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Create the backlog directory and file:**
    *   The application expects a file at `ai-tasks/backlog.md` relative to the project root.
    *   If it doesn't exist, the `main.py` script will create a sample one on first run.
    *   You can manually create/edit `ai-tasks/backlog.md` with tasks (one per line, Markdown list format):
        ```markdown
        * Task 1: First item.
        * Task 2: Second item.
        * Task 3: Another task.
        ```
6.  **(Optional) Create a `.env` file:**
    *   Based on `.example.env` if you need to configure API keys (e.g., `GEMINI_API_KEY`) for specific models. Not strictly required if using free-tier models or models without API key requirements.

## Execution

You can run the PoC using the ADK web interface or the provided main script. Ensure your virtual environment is activated.

*   **Using ADK Web:**
    1.  Navigate to the `src/` directory in your terminal: `cd src`
    2.  Run the ADK web server: `adk web`
    3.  Open the provided URL in your browser.
    4.  Start a new session. The agent should automatically start processing the backlog.

*   **Using Main Script:**
    1.  Ensure you are in the **project root directory** (the directory containing `src/`, `ai-tasks/`, `requirements.txt`).
    2.  Run the script as a module:
        ```bash
        python -m src.sleepy_dev_poc.main
        ```
    3.  Observe the console output for agent messages and backlog processing steps. The `ai-tasks/backlog.md` file will be modified as tasks are processed.

## Project Structure

```
/ (project root)
├── .env                   # Optional: Store API Keys, etc.
├── .example.env           # Example environment variables
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── ai-tasks/              # Directory for backlog file
│   └── backlog.md         # The input backlog file
└── src/                   # Source code directory
    └── sleepy_dev_poc/    # Main Python package for the agent
        ├── __init__.py    # Makes 'sleepy_dev_poc' a package, imports root_agent
        ├── agent.py       # Defines the root LoopAgent
        ├── main.py        # Script to configure/run ADK Runner directly
        ├── shared_libraries/
        │   ├── __init__.py
        │   └── constants.py # Defines paths, agent names, model, etc.
        ├── sub_agents/
        │   ├── __init__.py
        │   └── backlog_reader/
        │       ├── __init__.py
        │       ├── agent.py     # Defines BacklogReaderAgent (LlmAgent)
        │       ├── prompt.py    # Defines the instruction prompt
        │       └── tools.py     # Defines the 'process_backlog_file' FunctionTool
        └── tools/             # Optional: General reusable tools (currently empty)
            └── __init__.py