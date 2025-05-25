## 8. Proposed Folder and File Structure

This section outlines the proposed folder and file structure *within the `src` directory* for the "PoC7 - Goal Manifest Generation - Pydantic AI / Jinja" project. It reflects the existing codebase structure and incorporates the new Pydantic model directory.

```plaintext
src/
├── __init__.py                         # Makes 'src' a Python package
├── ai-specs/
│   └── goal-manifest-creation-spec.md  # LLM directive for manifest generation
├── config.py                           # Contains AppConfig Pydantic model
├── graph_builder.py                    # LangGraph StateGraph definition
├── main.py                             # Main application entry point
├── nodes/
│   ├── __init__.py                     # Makes 'nodes' a Python package
│   ├── finalization_nodes.py
│   ├── generate_manifest_node.py       # Node being refactored
│   ├── initialization.py
│   ├── small_tweak_execution.py
│   └── validation.py
├── pydantic_models/                    # Directory for Pydantic data models
│   ├── __init__.py                     # Makes 'pydantic_models' a Python package
│   └── core_schemas.py                 # E.g., Contains ManifestConfigLLM, other shared Pydantic models
├── services/
│   ├── __init__.py                     # Makes 'services' a Python package
│   ├── aider_service.py
│   ├── changelog_service.py
│   ├── git_service.py
│   ├── llm_prompt_service.py           # NEW: Service for LLM interaction
│   └── write_file_from_template_service.py # NEW: Service for Jinja2 rendering
├── state.py                            # Defines WorkflowState TypedDict
├── templates/
│   ├── __init__.py                     # Optional: Makes 'templates' a discoverable package
│   ├── goal-manifest.j2                # Jinja2 template for goal-manifest.md
│   └── changelog.j2                    # Jinja2 template for changelog.md entries
└── utils/
    ├── __init__.py                     # Makes 'utils' a Python package
    └── logging_setup.py
```

**Key Points & Rationale (focusing on `src/` contents and `pydantic_models/` directory):**

  * **`src/` Directory Structure:** The overall structure of `src/` with its sub-packages (`ai-specs/`, `nodes/`, `pydantic_models/`, `services/`, `templates/`, `utils/`) is designed for modularity and clarity.
  * **`pydantic_models/` (Sub-package):**
      * This sub-package is designated to house Pydantic models that define data structures used across the application. This includes schemas for LLM inputs/outputs like the new `ManifestConfigLLM` (which will reside in `core_schemas.py` or a similar file within this package).
      * **Rationale:** Centralizing Pydantic model definitions in `src/pydantic_models/` enhances organization, discoverability, and reusability of these schemas. It promotes a clear separation of data structure definitions from operational logic.
  * **`templates/` Directory within `src/`:** This sub-package houses Jinja2 template files. `config.yml` entries for template filenames (e.g., `manifest_template_filename`) will need to include the `src/templates/` prefix (e.g., `src/templates/goal-manifest.j2`) assuming `AppConfig.workspace_root_path` (defined in `config.yml`) points to the project root directory (the parent of `src/`).
