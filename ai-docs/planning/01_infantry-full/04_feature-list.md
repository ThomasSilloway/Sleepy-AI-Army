## Sleepy AI Army v0.2: Infantry Agent - Functional Requirements

### 1. Mission Processing
* Reads and executes `Mission` objectives from a `mission-spec.md` file located in a configured mission folder.
* Halts and reports `BLOCKED` or `FAILED` status (with reasons) if a `Mission` cannot be confidently executed based on its specification.

### 2. Code & Content Generation
* Generates and/or modifies code within the target project using Aider, guided by a GCR (Generate-Critique-Regenerate) engineered prompt derived from `Mission` requirements.
* Applies project-specific coding conventions (if specified via a `CONVENTIONS.MD` file referenced in the `Mission` context) during Aider-based code generation.
* Generates structured text data (e.g., Git branch names, commit messages, sections for the `mission-report.md`) using direct LLM calls with Pydantic for response parsing.

### 3. Version Control
* Creates and manages a unique Git branch within the target project's repository for each `Mission`.
* Commits code changes atomically to the mission branch, using generated descriptive messages.
* Optionally drafts a Pull Request against a specified base branch for the completed mission branch.

### 4. Reporting & Logging
* Generates a `mission-report.md` file within the mission folder, detailing:
    * Mission objectives (from `mission-spec.md`)
    * Final status (`SUCCESS`, `FAILURE`, `BLOCKED`)
    * Execution summary
    * List of files modified or created
    * Git commit history (short hashes and messages)
    * Estimated LLM interaction cost
    * Error details, if any
* Generates `overview.log` and `detailed.log` files recording agent activities, Aider interactions, and direct LLM calls.

### 5. Configuration
* Receives operational parameters (including `project_git_root` and the relative `mission-folder` path) through configuration settings.
* Supports configurable selection of LLM models for Aider and for direct LLM calls (used with Pydantic).
