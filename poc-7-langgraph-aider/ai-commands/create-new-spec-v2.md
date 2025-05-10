# AI Command: Generate New Specification File (`spec.md`)

## 1. Task Overview
Your primary task is to generate a new `spec.md` file. This file will outline the next set of development tasks for the project

## 2. Output File Details
- **Location**: The new `spec.md` should be placed in a sibiling directory to the example `spec.md`
- **Subdirectory Naming**: Follow the pattern `XX-short-description` (e.g., `03-services-graph-setup`). Choose an appropriate `XX` number and description based on the tasks.
- **Filename**: `spec.md` 

## 3. Content for the Generated `spec.md`

### 3.2. Structure, Format, and Level of Detail **(CRITICAL)**
- **Template**: The generated `spec.md` **MUST** strictly adhere to the template, format, and **level of detail** exemplified by `spec.md` example
- **Guidance**:
    - Use clear "Objectives" and "Low-Level Tasks" sections.
    - Tasks should be actionable and broken down logically (e.g., by file to create/update).
    - **Avoid excessive detail**: Do not specify exact variable names (unless architecturally significant), precise logging messages, or overly granular implementation steps within the tasks. The level of detail in the reference `spec.md` example is the target.

### 3.3. Context Section in the Generated `spec.md`
The `Context` block within the `spec.md` you generate should include:
- `/add` commands for files to be created or modified by implementing *the new* spec. Based on the target functionality
- `/read-only` commands for relevant architectural documents and supporting code files

## Project Context

```
/read-only poc-7-langgraph-aider\ai-docs\planning\01_manifest-and-changelist\05_1_tech_architecture_overview.md      
/read-only poc-7-langgraph-aider\ai-docs\planning\01_manifest-and-changelist\05_2-tech_architecture-flow.md
/read-only poc-7-langgraph-aider\ai-docs\planning\01_manifest-and-changelist\05_3-tech_architecture-file-structure.md
/read-only poc-7-langgraph-aider\src\nodes\initialization.py
/read-only poc-7-langgraph-aider\src\main.py
/read-only poc-7-langgraph-aider\src\graph_builder.py
/read-only poc-7-langgraph-aider\src\state.py

/read-only poc-7-langgraph-aider\ai-commands\create-new-spec-v2.md
/read-only poc-7-langgraph-aider\ai-specs\03-services-graph-setup\spec.md
```  

## Important Best Practices to follow
```
/read-only poc-7-langgraph-aider\ai-docs\langgraph-best-practices.md
/read-only poc-7-langgraph-aider\ai-docs\langraph-sample.py
```

## Files that the spec should update

Use your best judgement

## Tasks to extrapolate in the new spec.md: 

Implement this workflow step from the technical architecture flow:

Input Validation (validate_inputs_node): Sets current_step_name. Verifies task_description.md and templates. Reads task content into WorkflowState.task_description_content. Updates WorkflowState.last_event_summary to "Input files validated successfully." Logs success or signals error.

Note: Use initialization.py node as a template for how to structure nodes, logs within nodes, comments, etc
