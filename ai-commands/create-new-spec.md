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
- **Template**: The generated `spec.md` **MUST** strictly adhere to the template and format exemplified by `spec.md.example` example
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
/read-only ai-docs/CONVENTIONS.md

/read-only ai-commands\create-new-spec.md
/read-only ai-docs\spec.md.example
```  

## Files that the spec should update

Use your best judgement

## Tasks to extrapolate in the new spec.md: 

Implement these sections from the tech architecture workflow doc below. 

```
Update `manifest_generation.py` using the two new service classes to fulfill the architecture plan that will generate manifest files from the task-description file. This should replace the TODOs in that file
```