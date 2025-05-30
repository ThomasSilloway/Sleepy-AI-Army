# Create New project folder

Create the army-general folder and the files that it requires. 

## Helpful Docs

Below is the vision statement for the entire project, but we are just working on a small part of it.
```
## 1. Introduction / Vision

This document outlines the requirements for the Minimum Viable Product (MVP) of "Sleepy Dev Team," an AI-assisted development orchestrator. The vision is to create a system that leverages AI (specifically Google Gemini models and tools like `aider`) to make incremental progress on software development tasks outlined in a backlog, primarily during times when the user is away from the computer (e.g., overnight, during breaks). Instead of attempting end-to-end task completion, the system focuses on advancing multiple tasks by one logical step per run cycle, allowing the user to review progress and guide the overall direction. This project refactors concepts and potentially code from the earlier Godot-AI-Developer project into a more generic, scalable tool.

## 2. Goals & Objectives

* **Goal:** Automate the incremental advancement of development tasks defined in a simple backlog file.
* **Goal:** Leverage AI to perform various development sub-tasks (Q&A generation, documentation, planning, coding via `aider`, analysis) autonomously based on task state.
* **Goal:** Provide a mechanism for user review and control over the automated process via a proposal system.
* **Objective:** Implement systems capable of performing MVP tasks: Q&A, Brainstorming, PRD writing, Planning, Root Cause Analysis, Fix Planning, Polish Planning, Code Execution (via `aider`), Formatting, and Learnings Documentation.
* **Objective:** Integrate with `aider` for code generation/modification tasks, using `gemini-2.5` as the backend LLM.
* **Objective:** Implement a Discord bot interface for manual triggering.
* **Objective:** Ensure the system runs reliably in a local Docker environment.
* **Objective:** Refactor the Discord bot communication from the Godot-AI-Developer project for more direct command/response interaction.

## 3. Target Audience / User Personas

* **Primary User:** Individual developers (initially the project author) looking to leverage AFK time for automated assistance on their coding projects.
```

## Current project status
Each component below was directly taken from a proof of concept, so the code is very messy. We wanted to bring the project to a useful state as fast as possible though, so this is sufficient for now. Subsequent updates will clean up the code and make it more maintainable.

Army Man - Capable of making a small tweak to a file based on a prompt on a single file. The file must contain the relative path to the file from the root of the git repository.,
Secretary - Converts the backlog into new ai-goals folders and records the folder names for the General that should be operated on,

TODO:

General - Initiates the Secretary, upon completion, reads the folder names to operate on and starts a new Army Man for each folder. It should use the batch files in the main directory as a template for how to run the secretary and the army man.

Right now both the Secretary and the Army Man projects have an AppConfig that defines the root git path of the project they are meant to work on. 

We need to allow these to be overridden via commandline, so the General can run these with commandline parameters to specify which folders each of them should operate on.  For the Army man there are additional params it may require.

The general should have its own appconfig. Use the Secretary's app config as a template for how to implement the Generals. 

## Project Structure

The file structure should be
```
army-general
 - ai-docs/planning/
    - 01_vision-statement.md
    - 02_feature-list.md
    - 03_prd.md
    - 04_tech-architecture-brainstorming.md
    - 05_tech-architecture.md
 - src/
    - main.py
    - config.py
 - config.yml
```

# Implementation Process

Follow each step below one by one and in the exact order that they are presented.

## Vision Statement 
- Create a vision statement from the brainstorming notes above.
## Feature List 
- Create a feature list - what are the list of features we want to build
## PRD Creation

 PRD will operate within defined levels of detail:
* **Level 1: Requirements (This Prompt's Focus):** Defines the 'What' & 'Why'. Focuses on user needs, goals, **user interactions, externally observable system behaviors/outcomes, User Journeys/Flows**, high-level features/user stories, essential NFRs impacting the user/business, key constraints, and essential data inputs/outputs from an external perspective. **Output: PRD.**
* **Level 2: High-Level Design/Architecture:** Defines the 'How'. Key components, component interactions, technology choices, APIs. *(Out of scope for this prompt)*.
* **Level 3: Detailed Design/Implementation:** Specific algorithms, data structures, class designs, code. *(Out of scope for this prompt)*.

Your focus in this entire interaction and the final PRD is **strictly Level 1: Requirements.**
**Crucially, Functional Requirements defined in the PRD must describe the system's Level 1 externally observable behavior:**
* Focus on **User Interactions:** What actions does the user take? What inputs do they provide?
* Focus on **System Responses/Outcomes:** What are the high-level, expected results or state changes visible to the user or interacting systems?
* Structure these around **User Journeys or Key Process Flows** where applicable.
**You should NOT:**
* Delve into Level 2 or Level 3 details inthe PRD.
* Detail internal algorithms, specific component logic, database schemas, specific tool choices, or file structure specifics *within the main Functional Requirements section* of the PRD. If such details arise during creation and represent firm constraints, note them briefly under a `Technical Constraints` or `Technical Considerations` section, but do not elaborate on the implementation.
* [Other standard exclusions: Make business decisions, Generate code, Guarantee success]


## Architecture Brainstorming
Generate 2 different tech architecture ideas to implement this PRD. Then create another 3rd idea that uses a radically different approach. Think across multiple domains and dimensions.

For each of these ideas, list the pros and cons and then make a recommendation at the end of which we should go for.
 
## Architecture Planning 
Use the prompt below to plan out the final architecture. These sections will go in `05_tech-architecture.md`

```
# AI Agent Seed Prompt: Technical Design Finalizer & Scaffolder (Extended Process)

## 1. Role and Goal

**You are an AI Technical Design Finalizer & Scaffolder.**

Your primary objective is to synthesize various project planning inputs (which will be provided) into a detailed **Technical Architecture Document (TAD)** for a new project, tentatively titled: `[Project/Feature Name - User to specify]`.

## 2. Persona and Mindset

Throughout this engagement, you are to maintain a **meticulous, detail-oriented, and pragmatic mindset.** Your focus is on:
* Accurately interpreting all provided inputs (requirements, high-level design decisions, best practices).
* Translating these inputs into a concrete, actionable technical blueprint (the TAD).
* Ensuring the generated TAD is comprehensive, clear, and directly addresses the project's needs.

## 4. Process / Stages

We will employ an iterative refinement process within each stage.

### Stage 1: Generate Technical Architecture Document (TAD)

**A. Initial Interaction & Document Generation:**

2.  **Synthesize & Design:**
    * Thoroughly analyze all provided inputs.
    * Refine component responsibilities and interactions.
    * Define key data structures, formats, or schemas.
    * Confirm or specify technology choices (languages, frameworks, libraries, services).
    * Detail how Non-Functional Requirements (NFRs) from the PRD will be addressed.
    * Identify and list any final technical risks or dependencies.
    * Crucially, define a clear, logical, and human-readable **Folder and File Structure** for the project codebase.
3.  **Generate Technical Architecture Document (TAD):**
    * Create a detailed Markdown document titled "Technical Architecture: `[Project/Feature Name - from user]`".
    * This document **MUST** include, at a minimum, the following sections (provide section by section or in groups as requested by me):
        1.  **Overview:** Brief summary of the project, chosen architecture, and key goals. (Include document version and date).
        2.  **Component Breakdown:** Description of major architectural components, their responsibilities, and key interactions.
        3.  **Technology Stack:** List of chosen languages, frameworks, libraries, tools, and services, including versions if critical.
        4.  **Data Models / Structures:** Definition of important data formats, schemas, or key data objects (e.g., `AppConfig`, `WorkflowState`, input/output file formats, key API request/response structures if applicable).
        5.  **NFR Fulfillment:** Detailed explanation of how each key NFR (e.g., performance, security, scalability, maintainability, observability) identified in the PRD is addressed by the proposed design.
        6.  **Key Interaction Flows:** Detailed step-by-step descriptions of critical processes or user stories, showing how components interact. Include primary success paths and key error/exception handling paths.
        7.  **Error Handling Strategy:** High-level approach to error detection, logging, reporting, and recovery (if any) within the system.
        8.  **Proposed Folder and File Structure:** A clear visual representation (e.g., using an ASCII tree format) of the intended project layout, including key files within folders, and a "Key Points" section explaining the rationale behind the structure.
        9.  **Risks & Dependencies:** Identification of final technical risks, assumptions, and external dependencies.

**B. Iterative Refinement & Review Process (for TAD Sections):**

* **Critique & Revision (Simulated Professional Environment):**
    1.  **(Internal Thinking Step - Architect Persona):** Upon receiving feedback or when moving to a new section, first mentally adopt the persona of an **expert, best-in-field, brilliant software architect** aiming for the highest quality. Generate an initial or revised version of the requested section(s) incorporating all available information and feedback.
    2.  **(Internal Thinking Step - CTO Persona Review):** Next, mentally adopt the persona of a **distinguished, perfectionist CTO** with extensive experience. Critically review the architect's version. This review should be comprehensive, noting what went well and providing a detailed, constructive, (even nitpicky) list of improvements needed to achieve "A+" or "industry-leading" quality. Maintain a professional and concise tone.
    3.  **(Output Step - Architect Persona incorporating CTO Feedback):** Resume the **expert software architect** persona. State the original "grade" the CTO gave the previous version (e.g., "Overall Grade for Previous Submission: B+"). Then, taking into account all the CTO's feedback from your internal simulation, generate and output *only* the refined, "A+" version of the requested TAD section(s). Do not output the critique details unless explicitly asked.
```

## Coding
Break down the Architecture Plan into logical parts to help build the project and work on one part at a time. Ex2 - Build out the simplest version of the project that allows the project to be run.  Then start building out each feature / component there as necessary.