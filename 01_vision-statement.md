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
* **Objective:** Handle Gemini API rate limits via key cycling.
* **Objective:** Refactor the Discord bot communication from the Godot-AI-Developer project for more direct command/response interaction.

## 3. Target Audience / User Personas

* **Primary User:** Individual developers (initially the project author) looking to leverage AFK time for automated assistance on their coding projects.