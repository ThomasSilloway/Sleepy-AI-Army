## Feature List

These describe *what* the `Infantry Agent` will do:

* Process structured `Mission` specifications from a designated input queue.
* Utilize LLMs (e.g., via Aider) for code generation and modification.
* Employ an internal Generate-Critique-Regenerate (GCR) cycle for code refinement.
* Manage dedicated Git branches and atomic commits for each `Mission`.
* Provide detailed execution logs, including LLM interactions and GCR steps.
* Report comprehensive status updates (e.g., success, failure, blocked) for each `Mission`.
* Generate concise changelog entry drafts upon `Mission` completion.
* Optionally draft Pull Requests against a specified base branch.

---
## Non-Functional Requirements

These describe *how* the `Infantry Agent` will perform its functions or constraints on its operation:

* Execute coding tasks strictly based on the provided `Mission` context ("sealed orders").
* Adhere to project-specific coding conventions and standards outlined in the `Mission`.
* Support configurable selection of LLM models for code generation.
* Implement clear error handling and reporting for unresolvable `Mission` issues.
* Operate autonomously without requiring human interaction during a `Mission` run.
