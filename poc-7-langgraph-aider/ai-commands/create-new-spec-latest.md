# AI Command: Generate New Specification File (`spec.md`)

## 1. Task Overview
Your primary task is to generate a new `spec.md` file. This file will outline the next set of development tasks for the project

## 2. Output File Details
- **Location**: The new `spec.md` should be placed in a sibiling directory to the example `spec.md`
- **Subdirectory Naming**: Follow the pattern `XX-short-description` (e.g., `03-services-graph-setup`). Choose an appropriate `XX` number and description based on the tasks.
- **Filename**: `spec.md` 

## 3. Content for the Generated `spec.md`

### 3.2. Structure, Format, and Level of Detail **(CRITICAL)**
- **Template**: The generated `spec.md` **MUST** strictly adhere to the template and format exemplified by `spec.md` example
- **Template 2**: The generated `spec.md` tasks section **MUST** be higher level than the template. 
  - Good Example: ``` Update the graph_builder to point to the success node after `validate_inputs_node` is complete ```
  - Bad Examples specify specific code to write in files
- **Guidance**:
    - Use clear "Objectives" and "Low-Level Tasks" sections.
    - Tasks should be actionable and broken down logically (e.g., by file to create/update).
    - **Avoid excessive detail**: Do not specify exact variable names (unless architecturally significant), precise logging messages, or overly granular implementation steps within the tasks. 

### 3.3. Context Section in the Generated `spec.md`
The `Context` block within the `spec.md` you generate should include:
- `/add` commands for files to be created or modified by implementing *the new* spec. Based on the target functionality
- `/read-only` commands for relevant architectural documents and supporting code files

## Project Context

```
/read-only poc-7-langgraph-aider\ai-docs\planning\01_manifest-and-changelist\05_1_tech_architecture_overview.md      
/read-only poc-7-langgraph-aider\ai-docs\planning\01_manifest-and-changelist\05_2-tech_architecture-flow.md
/read-only poc-7-langgraph-aider\ai-docs\planning\01_manifest-and-changelist\05_3-tech_architecture-file-structure.md
/read-only poc-7-langgraph-aider\src\main.py
/read-only poc-7-langgraph-aider\src\state.py
/read-only poc-7-langgraph-aider\src\services\aider_service.py
/read-only poc-7-langgraph-aider\src\services\changelog_service.py
/read-only poc-7-langgraph-aider\tests\test_aider_service_command.py

/read-only poc-7-langgraph-aider\ai-commands\create-new-spec-latest.md
/read-only poc-7-langgraph-aider\ai-specs\06-implement-aider-service\spec.md
```  

## Important Best Practices to follow
```
/read-only poc-7-langgraph-aider\ai-docs\langgraph-best-practices.md
/read-only poc-7-langgraph-aider\ai-docs\langraph-sample.py
/read-only poc-7-langgraph-aider\ai-docs\aider-cli-usage.md

/read-only ai-docs/CONVENTIONS.md
```

## Files that the spec should update

Use your best judgement

## Tasks to extrapolate in the new spec.md: 

Implement this workflow step from the technical architecture flow:

```
#### **2.4. `ChangelogService` (Changelog Management Service) `changelog_service.py`**
* **Description:** A dedicated Python class responsible for orchestrating updates to the `changelog.md` file. It employs `aider` via the AiderService class to interpret contextual information derived from the current `WorkflowState` and a summary of the preceding event, thereby generating the specific content for the changelog entry. This approach leverages `aider`'s inferential capabilities but introduces a significant dependency on its consistent interpretation of broad context and the quality of internal prompt engineering.
* **Responsibilities:**
    * Provide a method to request a changelog update, e.g., `record_event_in_changelog(current_workflow_state: WorkflowState)`.
    * Internally, construct a highly sophisticated prompt for `aider` via AiderService. This prompt must effectively guide `aider` to:
        * Analyze relevant information from `current_workflow_state` (e.g., paths of recently created files like `generated_manifest_filepath`, status flags like `is_manifest_generated`, and the `last_event_summary`).
        * Interpret the `preceding_event_summary` to understand the nature and outcome of the event that needs to be logged.
        * Synthesize this information to generate an appropriate changelog entry title and descriptive bullet points that accurately reflect the event.
        * Adhere to the structural guidelines of `format-changelog.md`, including the generation or incorporation of a current timestamp (the service will manage timestamp generation and ensure its inclusion in the prompt or `aider`'s instruction).
    * Execute the AiderService's `execute` command to update `changelog.md` based off of the prompt provided.
    * Handle AiderService's output and exit status. The success and correctness of the generated changelog entry heavily rely on the quality and robustness of the internal prompt engineering used to guide `aider`, which is a key challenge for this service.
* **Key Interactions:**
    * Instantiated by the `Main Execution Script`.
    * Injected via `RunnableConfig` and invoked by `LangGraph Orchestrator` nodes (e.g., by `generate_manifest_node` after successful manifest creation, passing the current `WorkflowState` and an `event_summary`).
    * Uses the `Logging System`.
    * Interacts with `changelog.md` located at the path derived from `AppConfig.goal_root_path` and `AppConfig.changelog_output_filename`.
```
