## Proposed

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

## Final

/read-only ai-docs/CONVENTIONS.md
/read-only ai-docs/planning/01_infantry-full/01_vision-statement.md
/read-only ai-docs/planning/01_infantry-full/02_objective-list.md
/read-only ai-docs/planning/01_infantry-full/03_tech-design-considerations.md
/read-only ai-docs/planning/01_infantry-full/04_feature-list.md
/read-only ai-docs/planning/01_infantry-full/05_file-structure.md
/read-only ai-docs/spec.md.example
/read-only army-infantry/.env.example
/read-only army-infantry/pyproject.toml
/read-only army-infantry/src/__init__.py
/read-only army-infantry/src/app_config.py
/read-only army-infantry/src/graph_builder.py
/read-only army-infantry/src/graph_state.py
/read-only army-infantry/src/main.py
/read-only army-infantry/src/models/__init__.py
/read-only army-infantry/src/models/aider_summary.py
/read-only army-infantry/src/nodes/__init__.py
/read-only army-infantry/src/nodes/code-modification/__init__.py
/read-only army-infantry/src/nodes/code-modification/node.py
/read-only army-infantry/src/nodes/code-modification/prompts.py
/read-only army-infantry/src/nodes/git-branch/__init__.py
/read-only army-infantry/src/nodes/git-branch/node.py
/read-only army-infantry/src/nodes/git-branch/prompts.py
/read-only army-infantry/src/nodes/git-checkout-original-branch/__init__.py
/read-only army-infantry/src/nodes/git-checkout-original-branch/node.py
/read-only army-infantry/src/nodes/initialize-mission/__init__.py
/read-only army-infantry/src/nodes/initialize-mission/node.py
/read-only army-infantry/src/nodes/initialize-mission/prompts.py
/read-only army-infantry/src/nodes/mission-reporting/__init__.py
/read-only army-infantry/src/nodes/mission-reporting/node.py
/read-only army-infantry/src/nodes/mission-reporting/prompts.py
/read-only army-infantry/src/services/__init__.py
/read-only army-infantry/src/services/aider_service.py
/read-only army-infantry/src/services/git_service.py
/read-only army-infantry/src/services/llm_prompt_service.py
/read-only army-infantry/src/services/write_file_from_template_service.py
/read-only army-infantry/src/templates/mission_report_template.md.j2
/read-only army-infantry/src/utils/__init__.py
/read-only army-infantry/src/utils/logging_setup.py