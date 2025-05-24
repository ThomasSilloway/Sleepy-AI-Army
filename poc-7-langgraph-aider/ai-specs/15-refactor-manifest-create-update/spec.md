## Problem

`manifest_update.py` currently uses the `re` (regular expression) module to modify the `goal-manifest.md` file. This approach is inherently **fragile**. Since the manifest originates from a Jinja2 template, any minor changes to the template's structure, whitespace, or formatting can break the `re` patterns, leading to update failures or corrupted manifest files. This makes the system difficult to maintain and unreliable.

## Chosen Solution: Full Rerender from State

We will implement a **"Full Rerender from State"** strategy.
**Core Idea:** The `goal-manifest.md` file will be treated as a **build artifact**, not a source file. The **single source of truth** for its content will be a structured Pydantic model (`ManifestData`) stored within the `WorkflowState`.
**Process:**
1.  `manifest_create_node` will initialize this `ManifestData` model and render the *first* version of `goal-manifest.md`.
2.  `manifest_update_node` will retrieve the `ManifestData` model from the state, *modify its data fields* based on workflow events, and then *completely rerender* the `goal-manifest.md` using the Jinja2 template and the updated data.

This approach ensures the manifest always reflects the current state and matches the template structure, leveraging Jinja2's strength and eliminating fragile `re` logic.

## Related files


## High-Level Implementation Plan (SPR)

* **`DEFINE:Pydantic:ManifestData`**
    * **Location:** `src/pydantic_models/core_schemas.py`
    * **Purpose:** Structured data holder for `goal-manifest.md`.
    * **Fields:**
        * `goal_title: str`
        * `task_description_for_manifest: str`
        * `last_updated_timestamp: str`
        * `overall_status: str`
        * `current_focus: str`
        * `artifacts: List[Artifact]`
        * `ai_questions_list: List[str]`
        * `human_responses_content: str`

* **`DEFINE:Pydantic:Artifact`**
    * **Location:** `src/pydantic_models/core_schemas.py` (nested or separate)
    * **Purpose:** Represents one artifact entry.
    * **Fields:**
        * `status: str` (e.g., `"[in-progress]"`, `"[Complete]"`)
        * `path: str`

* **`MODIFY:State:WorkflowState`**
    * **Location:** `src/state.py`
    * **Action:** Add `manifest_data: Optional[ManifestData]` field.

* **`MODIFY:Template:goal-manifest.md.j2`**
    * **Location:** (Requires existing/new template file)
    * **Action:** Ensure template renders *only* from `ManifestData` context.
    * **Details:**
        * Use `{{ manifest_data.field }}` syntax.
        * Implement `{% for artifact in manifest_data.artifacts %}` loop.
        * Implement `{% for question in manifest_data.ai_questions_list %}` loop.
        * Use `{% if manifest_data.ai_questions_list %}` ... `{% else %}` NONE `{% endif %}` logic.

* **`MODIFY:Node:manifest_create_node`**
    * **Location:** `src/nodes/manifest_create.py`
    * **Action:**
        * Instantiate `ManifestData`.
        * Populate `ManifestData` from LLM + defaults.
        * Store `ManifestData` -> `state['manifest_data']`.
        * Call `WriteFileFromTemplateService` with `manifest_data.model_dump()`.

* **`REWRITE:Node:manifest_update_node`**
    * **Location:** `src/nodes/manifest_update.py`
    * **Action:**
        * **`DELETE`**: All `re` logic.
        * **`Workspace`**: `manifest_data` from `state`.
        * **`UPDATE`**: `manifest_data` fields (status, timestamp, artifacts, ai_questions) based on `state['error_message']` / previous results.
        * **`STORE`**: Updated `manifest_data` back to `state`.
        * **`CALL`**: `WriteFileFromTemplateService` with updated `manifest_data.model_dump()` to **overwrite** `goal-manifest.md`.
        * **`MAINTAIN`**: `ChangelogService` integration.