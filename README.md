# Sleepy AI Army

## The AI Agent Coding Problem

Picture this: you're deep in development on your passion project – maybe a game in Godot. You're excitedly building a new weapon system, pouring all your focus into it.

But that nagging feeling persists... your backlog. It's full of other important tasks:
* A navigation bug where characters awkwardly walk *around* holes in walls instead of pathfinding through them.
* Another issue where players and enemies can phase right through each other!

While you're focused on the weapons, those crucial navigation fixes just sit there, gathering dust. It's the classic developer dilemma: you can only truly focus on one complex task at a time.

Wouldn't it be amazing if *something* could chip away at those other tasks while you focus, or even while you sleep? Maybe figure out *why* navigation is broken, draft a plan, or even attempt a fix?

**This is the core problem Sleepy AI Army solves:** It tackles the frustration of a growing backlog by enabling incremental progress on multiple fronts, even when your attention is elsewhere.

## Vision & Purpose

Sleepy AI Army is your **AI-powered assistant crew**, designed to help you make steady, incremental progress on your software projects during your downtime.

**How it helps:**
* You add tasks to a simple list (your backlog).
* When you're away – sleeping, at the gym, spending time with family – the "Sleepy AI Army" activates.
* It looks at your list and starts working on **multiple tasks** in parallel.
* Crucially, it only takes **one small, logical step** on each task before pausing work *on that specific task* for the current cycle.

Think of it as a team diligently chipping away at your to-do list while you're occupied, ensuring slow but steady progress across your entire project.

<center>
  <img src="army.png" alt="AI Army icon">
</center>

## What Sleepy AI Army Doesn't Do

Let's be clear about the boundaries:

* **Not an Instant App Generator:** You can't give it vague commands like "build me a social media site" and expect a finished product. It excels at working on *existing* projects with *specific* tasks.
* **Not a Developer Replacement:** It's an *assistant*. Your oversight, review, and strategic decisions are essential. The AI handles the "first draft" or the next logical step, but *you* steer the ship.
* **Not (Yet) a Project Manager:** Complex dependency tracking, resource allocation, and scheduling are outside the MVP scope.

## Problems Solved

Sleepy AI Army addresses common development headaches:

* **Stagnant Backlogs:** Keeps tasks moving forward, preventing them from sitting untouched for weeks or months.
* **AI Overreach & Risk:** Focuses AI efforts on small, manageable steps, combined with mandatory human review, preventing agents from making large, unintended changes.
* **Development Bottlenecks:** Enables parallel progress (bug analysis, feature planning, documentation) during your downtime, accelerating overall development.
* **Tedious First Steps:** Automates the initial grunt work of tackling a task – generating questions, drafting basic plans, analyzing code, etc.

## Key Features / Capabilities

The system uses a team of specialized AI agents, each skilled in different development steps:

* **Asking Questions:** Clarifying task requirements.
* **Brainstorming:** Generating different implementation ideas.
* **Documentation:** Writing initial drafts (requirements, technical plans).
* **Bug Analysis:** Investigating code to find root causes.
* **Planning:** Outlining steps for fixes or features.
* **Coding:** Writing or modifying code via tools like `aider` (using Gemini).
* **Formatting:** Applying code style rules (e.g., `black`, `prettier`).
* **Documenting Learnings:** Summarizing insights after tasks (especially bug fixes).

### Task Planning for Each Goal

A critical function is determining the *next logical step* for each task:
1.  When a backlog item becomes an active "goal" (e.g., `Bug_001_Fix_Navigation_Walls` in its folder within `ai-goals/`), the system analyzes its description and any related files.
2.  It identifies the single most appropriate *next action* (e.g., "Ask clarifying questions," "Analyze relevant code," "Draft a fix plan," "Implement the code fix").
3.  It maintains a list of planned and completed steps for that goal as it progresses.

## How It Works (High Level)

The workflow operates in cycles, prioritizing safety and human control:

1.  **Input:** You maintain a simple task list in `backlog.md`. These are high-level goals (e.g., "Fix navigation wall bug," "Add pause menu feature").
2.  **Goal Creation / Update Cycle:**
    * The system processes the `backlog.md`. For each task ready to be worked on:
        * If new, it creates a dedicated folder (e.g., `ai-goals/Bug_001_Fix_Navigation_Walls/`).
        * An AI analyzes the goal and determines the *single next action* needed.
        * It performs *only that one action* (e.g., writes questions, drafts a plan, attempts code change).
        * The result is saved in the goal's folder.
    * The system repeats this "one step per goal" process for *all* active goals it can work on in the current run cycle.
3.  **Pause & Aggregate:** Once the system has taken one step on every possible goal for that run, the automated process pauses.
4.  **Human Review:** When you return, you review the outputs for *all* the goals that were updated. You can:
    * Answer questions posed by the AI.
    * Modify generated plans or documents.
    * Review and approve/reject code changes.
    * Update the task list or backlog based on the progress.
5.  **Repeat Cycle:** Based on your review and feedback, the system is ready for the next run cycle (e.g., the next night) to pick up the *next* logical step for each goal.

## Limitations & Dependencies (MVP)

* **Task Dependencies Need Manual Management:** The system doesn't automatically know if Goal C needs Goal B to be done first.
    * *Example:* If adding a "level complete" screen (Goal C) relies on fixing a player movement bug (Goal B), *you* must ensure Goal B is finished before adding Goal C to the `backlog.md`. You control the sequence.
* **Single Step Execution & Human Review Required:** The AI performs only *one defined step per goal per run cycle* and then waits for batch review. It won't complete complex features end-to-end autonomously.
    * *Example:* The AI might write code for a feature based on a plan. It stops. You review it later with all other updates from that run. Only after your review can it proceed to the *next* step (like writing tests) in a *future* run cycle. Your review gates progress for *all* tasks.

## POC Status

- PoC 3, 4, and 5 are incomplete projects see their readme for more info
- PoC 1, 2, 6 Are fully implemented and intended to be run with `adk web`
