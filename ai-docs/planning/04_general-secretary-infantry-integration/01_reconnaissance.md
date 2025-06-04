# Reconnaissance Report: army-general & army-secretary with army-infantry Integration

**Battlefield Captain AI:** Jules
**Date:** 2025-06-04

## 1. Initial Objective Analysis

The core objective is to update the `army-general` and `army-secretary` components to utilize the new `army-infantry` component, ceasing use of the `army-man-small-tweak` component.

Key requirements for `army-general` include:
*   Verifying Git branch consistency (against a predefined expected branch) each time it runs an Infantry mission, halting execution if there's a mismatch.
*   Integrating and using a new asyncio-compatible `git-service.py` (originating from `army-infantry`) to replace its existing Git service functionalities, especially for branch checking and potentially for its final commit actions.

## 2. Simulated Reconnaissance & Intelligence Gaps

This section details the investigation undertaken to understand the existing systems and the new `army-infantry` component.

### Initial Intelligence Gaps & Investigation Strategy:

*   **Understanding Current Operations:** How do `army-general` and `army-secretary` currently function and interact with `army-man-small-tweak`?
    *   *Findings:* `army-general` (`army-general/src/main.py`) orchestrates operations. It first calls `army-secretary` (which prepares a list of mission folders in an output file). Then, for each folder, `army-general` calls `army-man-small-tweak` via a subprocess. `army-secretary` itself does not call `army-man-small-tweak`.
*   **`army-infantry` Details:** What is its API, how is it invoked, and how does it handle mission parameters?
    *   *Findings:* Documentation (`ai-docs/planning/01_infantry-full/`) and code (`army-infantry/src/main.py`, `army-infantry/src/app_config.py`) reveal `army-infantry` is run via CLI (`uv run src/main.py`). It expects `--root_git_path` and a relative `--mission_folder_path` as arguments. It's designed to be asynchronous.
*   **`git-service.py` Integration:** What is the nature of the new `git-service.py` from `army-infantry`, and how does it differ from `army-general`'s existing one?
    *   *Findings:* `army-infantry/src/services/git_service.py` is asynchronous (`asyncio`) and includes a `get_current_branch()` method. `army-general/src/services/git_service.py` is synchronous and lacks this method. The new service is intended to replace the old one in `army-general`.
*   **Codebase Locations:**
    *   `army-general`: `army-general/`
    *   `army-secretary`: `army-secretary/`
    *   `army-infantry`: `army-infantry/`
    *   `army-man-small-tweak`: `army-man-small-tweak/`
    *   Existing `git-service.py` in `army-general`: `army-general/src/services/git_service.py`
    *   New `git-service.py` in `army-infantry`: `army-infantry/src/services/git_service.py`

### Referenced Planning Documents:

*   `ai-docs/planning/01_infantry-full/01_vision-statement.md`: Confirmed `army-infantry` replaces `army-man-small-tweak` and handles Git operations.
*   `ai-docs/planning/01_infantry-full/03_tech-design-considerations.md`: Detailed `army-infantry`'s async nature, CLI parameter needs (for mission folder and root path), and `AppConfig` usage.
*   `ai-docs/planning/01_infantry-full/04_feature-list.md`: Re-iterated CLI config and mission processing features.

## 3. Formulate Clarifying Questions for the Commander-in-Chief

The following questions were initially formulated. Most were answered through codebase and document review.

1.  *File paths for `army-general`, `army-secretary`, `army-man-small-tweak`?*
    *   Answered via `ls`.
2.  *Primary function of `army-secretary` and its interaction differences from `army-general`?*
    *   Answered via `army-secretary/src/main.py`. It prepares inputs (folder lists) for `army-general`. It does not directly execute `army-man-small-tweak` or `army-infantry`.
3.  *Regarding Git branch check in `army-general`: How is the expected branch determined? How to halt execution?*
    *   Partially answered: `army-infantry`'s `GitService` can fetch the current branch. The "expected branch" will likely be a new configuration in `army-general`. Halting would involve logging and exiting/returning early. *Commander's final input on the source of the "expected branch name" (e.g., config file) would be beneficial for actual implementation.*
4.  *API for `army-infantry` to be used by `army-general` / `army-secretary`?*
    *   Answered: `army-general` will invoke `army-infantry` as a subprocess using CLI arguments (`--root_git_path`, `--mission_folder_path`). `army-secretary` does not directly use it.
5.  *Is `army-infantry`'s `git-service.py` a complete replacement for `army-general`'s?*
    *   Answered: Yes, it appears to be a functional superset and is async, aligning with the objective.
6.  *Specific error handling from `army-infantry` for `army-general`?*
    *   To be determined during implementation. `army-general` will primarily react to the success/failure exit code of the `army-infantry` subprocess.
7.  *Status of `army-infantry/src/nodes/mission_reporting/node.py` and impact?*
    *   Assumed complete enough for `army-infantry` to be functional for this integration, as the objective focuses on the invocation and branch checking part from `army-general`.
8.  *Location of `army-infantry` component?*
    *   Answered via `ls`: `army-infantry/`.
9.  *Is `git-service.py` already in `army-general` or needs copying?*
    *   Answered: `army-general` has an old one. The new one from `army-infantry` needs to be copied over to replace it.

## 4. Draft a Preliminary Battlefield Plan Outline (Original Broader Scope)

This was the initial high-level plan drafted before the Commander-in-Chief clarified the mission to be documentation-only. It's included here for historical context as per the original multi-point request format.

**Phase 1: Reconnaissance & Deeper Analysis (Information Gathering)**
1.  Locate Core Components
2.  Analyze `army-man-small-tweak` Usage
3.  Understand `army-infantry` Interface
4.  Clarify `git-service.py` Details

**Phase 2: `army-general` Refactoring**
1.  Integrate `git-service.py` (from `army-infantry`)
2.  Implement Git Branch Check
3.  Replace `army-man-small-tweak` with `army-infantry` calls
4.  Testing for `army-general`

**Phase 3: `army-secretary` Refactoring**
1.  (Initially considered, but analysis shows `army-secretary` does not directly call these components, so likely no direct refactoring needed for this specific objective part).
2.  Testing for `army-secretary` (if any changes were made).

**Phase 4: Documentation & Finalization**
1.  Create This Reconnaissance Document
2.  Update General Documentation
3.  Code Review & Refinement
4.  Submission

```
