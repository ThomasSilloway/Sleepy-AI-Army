```
army-infantry/
├── .env.example                 # Example environment variables (e.g., API keys for LLMs)
├── .gitignore                   # Standard git ignore file specifying intentionally untracked files
├── config.yml                   # Default static configuration for the agent (e.g., model names, paths)
├── pyproject.toml               # Project metadata, dependencies, and build system configuration (e.g., Poetry, PDM, Hatch)
├── README.md                    # Readme specific to the Infantry Agent, explaining its setup and usage
├── run-infantry.bat             # Batch script to run the Infantry Agent with default parameters
│
└── src/                         # Source code for the Infantry Agent
    ├── __init__.py              # Makes 'src' a Python package
    ├── main.py                  # Main entry point for the agent; parses CLI args, initializes and runs the graph
    ├── app_config.py            # Defines Pydantic models for loading and validating `config.yml`
    ├── graph_state.py           # Defines the GraphState structure (e.g., TypedDict or Pydantic model) for LangGraph
    ├── graph_builder.py         # Defines the LangGraph (nodes, edges, state transitions)
    │
    ├── nodes/                   # Contains all LangGraph nodes for the agent's workflow
    │   ├── __init__.py          # Makes 'nodes' a Python package
    │   │
    │   ├── initialize-mission/    # Node for reading mission-spec.md and extracting initial data
    │   │   ├── __init__.py        # Makes 'initialize-mission' a package, might re-export from node.py
    │   │   ├── node.py            # Contains the main async node function(s) for mission initialization
    │   │   └── prompts.py         # Prompts used by the LLM to extract structured data from mission-spec.md
    │   │
    │   ├── git-branch/            # Node for handling Git branch creation and management
    │   │   ├── __init__.py        # Makes 'git-branch' a package
    │   │   ├── node.py            # Main async node function(s) for Git branch operations
    │   │   └── prompts.py         # (Optional) Prompts if LLM is used for generating branch names
    │   │
    │   ├── code-modification/   # Node for orchestrating code changes using Aider
    │   │   ├── __init__.py        # Makes 'code-modification' a package
    │   │   ├── node.py            # Main async node function(s) to interact with AiderService
    │   │   └── prompts.py         # GCR-engineered prompts to guide Aider's code generation
    │   │
    │   ├── git-checkout-original-branch/ # Node for checking out the original Git branch
    │   │   ├── __init__.py        # Makes 'git-checkout-original-branch' a package
    │   │   └── node.py            # Main async node function(s) to checkout the pre-mission branch
    │   │
    │   └── mission-reporting/   # Node for generating the final mission-report.md
    │       ├── __init__.py        # Makes 'mission-reporting' a package
    │       ├── node.py            # Main async node function(s) for compiling and writing the report
    │       └── prompts.py         # (Optional) Prompts if LLM is used for generating report summaries
    │
    ├── services/                # Contains service classes encapsulating business logic and external interactions
    │   ├── __init__.py          # Makes 'services' a Python package
    │   ├── aider_service.py     # Service class for interacting with the Aider CLI tool
    │   ├── git_service.py       # Service class for performing Git operations (branch, checkout, commit list, etc.)
    │   ├── llm_service.py       # Service class for direct interactions with LLMs (e.g., Gemini via API) and parsing responses
    │   ├── file_service.py      # Service class for abstracting file system operations (read, write, check existence)
    │   └── report_service.py    # Service class for generating the mission report content using Jinja2 templates
    │
    └── templates/               # Directory for Jinja2 templates
        └── mission_report_template.md.j2 # Jinja2 template for the `mission-report.md`
```