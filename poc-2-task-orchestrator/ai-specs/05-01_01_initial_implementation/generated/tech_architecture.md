# Technical Architecture Document: Sleepy Dev Team - Task Intake & Setup PoC (PoC2)

**Version:** PoC-2.2-TechArch-v3
**Date:** 2025-05-01

## Objective

This document outlines the technical architecture and implementation plan for the Proof-of-Concept 2 (PoC2) of the Sleepy Dev Team project, based on the requirements specified in the PRD (Version: PoC-2.2). It uses the Google Agent Development Kit (ADK) and focuses on task intake using the SingleTaskOrchestrator (STO) and initial task setup using the TaskSetupAgent (TSA) with generalized, shared tools. This architecture document is intended to guide an AI coding agent, reflecting specific structural preferences.

## Core Requirements Summary (Based on PRD PoC-2.2)

### Root Agent (SingleTaskOrchestrator - STO)

* LlmAgent acting as the root.
* Receives user input via adk web.
* Uses prompt-guided LLM reasoning to determine new vs. existing task.
* Routes accordingly.
* Does **not** use generalized tools.

### Sub-Agent (TaskSetupAgent - TSA)

* LlmAgent invoked by STO for new tasks.
* Infers prefix and generates a slug.
* Calls generalized tools to:

  * Get next task number
  * Format as NNN
  * Create task directory `/ai-tasks/Prefix_NNN_slug/`
  * Create `changelog.md` and `task_description.md`

### Generalized Tools

* Defined in `shared_tools/`:

  * `get_next_task_number`: from `task_helpers.py`
  * `create_directory`, `write_file`: from `file_system.py`

### NNN Formatting

* TSA formats the number as a three-digit zero-padded string (e.g., `003`).

### LLM Reasoning

* STO: input classification
* TSA: prefix inference and slug generation

### Environment

* Executed via `adk web` in local Python `.venv`

## Target Project Structure (Revised)

```
POC-2-TASK-ORCHESTRATOR/           # Project Root
├── README.md                      # Project Info
├── ai-docs/                       # Docs
├── ai-specs/
│   └── 05-01_01_initial_implementation/
│       └── generated/
│           └── tech_architecture.md
├── ai-tasks/                      # Runtime task folders (must exist)
├── scripts/                       # Utilities (optional)
└── src/
    └── sleepy_dev_poc/
        ├── .env
        ├── .example.env
        ├── requirements.txt
        ├── __init__.py
        ├── agent.py
        ├── prompt.py
        ├── tools.py
        ├── shared_libraries/
        │   ├── __init__.py
        │   └── constants.py
        ├── shared_tools/
        │   ├── __init__.py
        │   ├── file_system.py
        │   └── task_helpers.py
        └── sub_agents/
            ├── __init__.py
            └── task_setup_agent/
                ├── __init__.py
                ├── agent.py
                ├── prompt.py
                └── tools.py
```

## File Implementation Details

### README.md

```markdown
# Sleepy Dev Team - Task Intake & Setup PoC (PoC2)

Demonstrates task intake and setup using ADK agents (STO, TSA)
and generalized tools.

## Setup
1. Create venv: `python -m venv .venv`
2. Activate: `source .venv/bin/activate` or `.\.venv\Scripts\activate`
3. Install reqs: `pip install -r src/sleepy_dev_poc/requirements.txt`
4. Create task dir: `mkdir ai-tasks`
5. (Optional) Create `.env` in `src/sleepy_dev_poc/`

## Execution
Run from the project root: `adk web`  
Interact via chat (e.g., "Fix the login bug", "/ai-tasks/Feature_001_add-widget")
```

### ai-tasks/

* Must be manually created before execution.
* Used by `get_next_task_number`.
* TSA writes new tasks here.

### src/sleepy\_dev\_poc/

#### .env

```dotenv
# GEMINI_API_KEY=YOUR_API_KEY_HERE
```

#### .example.env

```dotenv
# GEMINI_API_KEY=
```

#### requirements.txt

```plaintext
google-adk
python-dotenv
```

#### **init**.py

```python
from .agent import root_agent
print("Initializing sleepy_dev_poc package...")
```

#### agent.py (STO)

```python
from google.adk.agents import LlmAgent
from .shared_libraries import constants
from . import prompt as sto_prompt
from .sub_agents.task_setup_agent.agent import task_setup_agent

root_agent = LlmAgent(
    name=constants.ROOT_AGENT_NAME,
    model=constants.MODEL_NAME,
    instruction=sto_prompt.STO_PROMPT,
    sub_agents=[task_setup_agent],
    description="Routes user input to task setup or responds if task exists."
)
```

#### prompt.py (STO)

```python
from .shared_libraries import constants

STO_PROMPT = """
Analyze user input: Is it a new task description OR reference to existing task
(contains '/ai-tasks/' or 'Prefix_NNN_slug' format)?
Respond ONLY JSON: {"action": "exists", "detail": "Path/Name"} OR {"action": "new_task"}
Input: {{user_content}}
"""
```

#### tools.py (STO)

```python
# Placeholder for root-specific tools.
pass
```

### shared\_libraries/constants.py

```python
import os

ROOT_AGENT_NAME = "SingleTaskOrchestrator_PoC2"
TASK_SETUP_AGENT_NAME = "TaskSetupAgent_PoC2"
BASE_TASK_PATH = os.path.abspath("ai-tasks")
ALLOWED_PREFIXES = ["Bug_", "Polish_", "Feature_", "Refactor_"]
DEFAULT_PREFIX = "Task_"
MODEL_NAME = "gemini-1.5-flash"
NNN_PADDING = 3
```

### shared\_tools/**init**.py

```python
from .file_system import create_directory, write_file
from .task_helpers import get_next_task_number
```

### shared\_tools/file\_system.py

```python
from typing import Dict, Any
import os

def create_directory(path: str, create_parents: bool = True) -> Dict[str, Any]:
    # Implementation stub
    pass

def write_file(path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
    # Implementation stub
    pass
```

### shared\_tools/task\_helpers.py

```python
from typing import Dict, Any
import os, re
from ..shared_libraries import constants

def get_next_task_number(base_path: str, prefix: str) -> Dict[str, Any]:
    # Implementation stub
    pass
```

### sub\_agents/init.py:

**Python**

```python
# Package initialization for sub_agents
```

### sub\_agents/task\_setup\_agent/init.py:

**Python**

```python
# Package initialization for task_setup_agent sub-agent
```

### sub\_agents/task\_setup\_agent/agent.py (TSA):

**Summary:** Defines TaskSetupAgent (LlmAgent). Uses its prompt.py for LLM call (prefix/slug). Calls shared tools (get\_next\_task\_number, create\_directory, write\_file imported from ...shared\_tools). Formats number to NNN. Orchestrates directory/file creation. Handles errors. Needs shared tool functions wrapped as FunctionTool instances.

**Python**

```python
# Defines the TaskSetupAgent
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from ...shared_libraries import constants
from . import prompt as tsa_prompt
# Import shared tool functions directly
from ...shared_tools.file_system import create_directory, write_file
from ...shared_tools.task_helpers import get_next_task_number

# Create tool instances for this agent
get_next_task_number_tool = FunctionTool(func=get_next_task_number)
create_directory_tool = FunctionTool(func=create_directory)
write_file_tool = FunctionTool(func=write_file)

task_setup_agent = LlmAgent(
    name=constants.TASK_SETUP_AGENT_NAME,
    model=constants.MODEL_NAME,
    instruction=tsa_prompt.TASK_SETUP_AGENT_PROMPT,
    tools=[ # Tools it orchestrates
        get_next_task_number_tool,
        create_directory_tool,
        write_file_tool,
    ],
    description="Generates prefix/slug, gets next number, creates task folder/files.",
    # Logic via callbacks/run to: LLM -> tool -> format NNN -> tool -> tool -> tool
)
```

### sub\_agents/task\_setup\_agent/prompt.py (TSA):

**Summary:** Defines the prompt constant (TASK\_SETUP\_AGENT\_PROMPT) for TSA. Guides LLM to infer prefix, generate slug, return structured JSON.

**Python**

```python
# Prompt for the TaskSetupAgent
from ...shared_libraries import constants

TASK_SETUP_AGENT_PROMPT = f"""
Analyze task description. Infer prefix from {constants.ALLOWED_PREFIXES} (default: {constants.DEFAULT_PREFIX}). Generate short (<=5 words) hyphenated slug.
Output ONLY JSON: {{"prefix": "...", "slug": "..."}}
Task: {{user_content}}
"""
```

### sub\_agents/task\_setup\_agent/tools.py (TSA):

**Summary:** Placeholder for tools specific only to TSA. Since TSA primarily orchestrates calls to shared tools for PoC2, this file will likely remain empty or contain only comments/imports.

**Python**

```python
# Tools specifically defined for TaskSetupAgent.
# For PoC2, TSA primarily uses shared tools. This may remain empty.
pass
```

---

### Key ADK Concepts Used:

* LlmAgent
* FunctionTool
* Sub-Agent Hierarchy
* ToolContext (implicitly if tools need state/actions)
* Constants
* adk web

### Setup and Execution:

* Follow setup steps in `README.md` (venv, install reqs from `src/sleepy_dev_poc/requirements.txt`, create `ai-tasks/` in root).
* Run `adk web` from the project root (`POC-2-TASK-ORCHESTRATOR/`).
* Test with new task descriptions and existing task references via chat.
* Verify directory/file creation in `ai-tasks/`.
