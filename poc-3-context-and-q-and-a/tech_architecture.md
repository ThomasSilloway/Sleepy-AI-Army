## Technical Architecture: Sleepy Dev Team - PoC 3 (Confirmed)

This document outlines the proposed file structure for the Sleepy Dev Team PoC 3 project, aligned with ADK best practices and referencing the structure observed in the travel-concierge sample project.

### File Structure

The file structure follows the guidelines specified in the ADK Best Practices documentation to ensure modularity, clarity, and consistency.

```
/src/sleepy-dev-team/         # Project root folder (using dashes)
├── README.md                   # Project README (Optional, but recommended)
├── requirements.txt            # Python dependencies (Existing)
├── .env                      Environment variables (API keys, config - Needs Creation)
│
└── sleepy_ai_army/             # Main Python package (using underscores)

    ├── __init__.py             # Exports root_agent from agent.py (Existing, content needs update)
    ├── agent.py                # Defines the root_agent (TaskPlannerAgent - Needs Creation/Update)
    ├── prompt.py               # Contains prompts for the root_agent (Needs Creation)
    │
    ├── shared_libraries/       # Directory for reusable code/constants (Needs Creation)
    │   ├── __init__.py         # Makes 'shared_libraries' a package (Needs Creation)
    │   ├── constants.py        # Defines constants (e.g., file names, status strings - Needs Creation)
    │   └── types.py            # Defines Pydantic types if needed (Optional - Needs Creation if used)
    │
    ├── shared_tools/           # Directory for reusable tools (Existing)
    │   ├── __init__.py         # Exports tool functions (Existing, needs update)
    │   ├── file_system.py      # File system tools (Existing, Needs Update for Read/Append/List)
    │
    └── sub_agents/             # Directory for specialized sub-agents (Existing)
        ├── __init__.py         # Makes 'sub_agents' a package (Existing)
        │
        ├── context_research/   # Folder for ContextResearchAgent (Needs Creation)
        │   ├── __init__.py     # Exports the agent (Needs Creation)
        │   ├── agent.py        # Definition of ContextResearchAgent (Needs Creation)
        │   └── prompt.py       # Prompts for ContextResearchAgent (Needs Creation)
        │
        ├── questions_and_answers/ # Folder for QnAAgent (Descriptive name)
        │   ├── __init__.py     # Exports the agent (Needs Creation)
        │   ├── agent.py        # Definition of QnAAgent (Needs Creation)
        │   └── prompt.py       # Prompts for QnAAgent (Needs Creation)
        │
        └── changelog/          # Folder for ChangelogAgent (Needs Creation)
            ├── __init__.py     # Exports the agent (Needs Creation)
            ├── agent.py        # Definition of ChangelogAgent (Needs Creation)
            └── prompt.py       # Prompts for ChangelogAgent (Needs Creation)
```

### Notes on Existing Files and Required Changes

Based on the provided `src/sleepy-ai-army/` code, the PRD requirements, and the updated ADK Best Practices:

#### Existing Files:

* `sleepy_ai_army/__init__.py`: Standard package initializer. No modifications needed 
* `sleepy_ai_army/sub_agents/__init__.py`: Exists, ready for sub-agent modules.
* `sleepy_ai_army/shared_tools/__init__.py`: Exists, exports tools. Needs update for new tools.
* `sleepy_ai_army/shared_tools/file_system.py`: Exists, contains `create_directory`, `write_file`.
* `requirements.txt`: Exists, lists `google-adk`, `python-dotenv`. Seems appropriate.

#### Required Changes/Additions:

* **Root Agent Definition**: Create `sleepy_ai_army/agent.py` to define the `TaskPlannerAgent` (as `root_agent`).
* **Root Agent Prompt**: Create `sleepy_ai_army/prompt.py` for the `TaskPlannerAgent` instructions.
* **Sub-Agent Modules**: Create the directories and the standard files (`__init__.py`, `agent.py`, `prompt.py`) within `sleepy_ai_army/sub_agents/` for:

  * `context_research`
  * `questions_and_answers`
  * `changelog`
  * The `changelog/agent.py` will define the `ChangelogAgent` intended to be wrapped by `AgentTool`.
* **Tools Update**: Update `shared_tools/file_system.py` to implement `ReadFile`, `AppendFile`, and `ListDirectory`. Update `shared_tools/__init__.py` to export these new functions.
* **Shared Libraries**: Create the `sleepy_ai_army/shared_libraries/` directory and its contents (`__init__.py`, `constants.py`, potentially `types.py`) for shared constants and types.
* **Configuration**: Create `sleepy_ai_army/.env` for API keys.
* **Project Root**: The project should reside within a root folder named with dashes (e.g., `sleepy-dev-team/`).
* **Tests Directory**: Create an empty `/tests/` directory at the project root (`/src/sleepy-dev-team/tests/`).
