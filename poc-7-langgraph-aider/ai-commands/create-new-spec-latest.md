# AI Command: Generate New Specification File (`spec.md`)

## 1. Task Overview
Your primary task is to generate a new `spec.md` file. This file will outline the next set of development tasks for the project.  
- IMPORTANT: Generate only the new `spec.md` do not move into implementation unless specifically asked.

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
/read-only poc-7-langgraph-aider\src\config.py
/read-only poc-7-langgraph-aider\src\utils\logging_setup.py
/read-only poc-7-langgraph-aider\src\nodes\initialization.py

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

Implement the action step below from an analysis of what the Poc7 is currently missing.

```
Comprehensive File-Based Logging System:

    Requirement: The "Logging System" (Section 2.6 of 05_2-tech_architecture-flow.md) is specified to provide "timestamped ([HH:MM:SS.mmm] format) logging to console, overview.log, and detailed.log." NFR-PoC7-003 also requires visibility into high-level and detailed logs.
    Current Status:
        Console logging is active via src/utils/logging_setup.py.
        The initialize_workflow_node resolves paths for overview_log_file_path and detailed_log_file_path and stores them in the WorkflowState.
        However, src/utils/logging_setup.py currently only sets up a StreamHandler for console output. It does not yet implement FileHandlers to write to overview.log and detailed.log.
        The initialize_workflow_node.py includes a TODO: Enhance setup_logging to use resolved log file paths from state, indicating this is a known pending item.
    Action: Update src/utils/logging_setup.py to configure FileHandlers for both overview.log and detailed.log, potentially using different logging levels for each. These handlers should use the file paths passed from the WorkflowState or AppConfig.
```
