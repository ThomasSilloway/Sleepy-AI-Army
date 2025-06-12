**Project:** army-infantry
**Title:** Update Aider Summary to Capture Questions

**Description:**
The current `AiderRunSummary` does not explicitly capture if `aider` stopped to ask a question instead of committing changes. This mission updates the Pydantic model and the corresponding LLM prompt to extract and store any questions `aider` asked during its run. This makes the `Aider Summary` in the final report more informative.

**Files to Modify:**
- `army-infantry/src/models/aider_summary.py`
- `army-infantry/src/services/aider_service/prompts.py`

**Implementation Details:**
1.  **Model Update:**
    - In `army-infantry/src/models/aider_summary.py`, add a new field to the `AiderRunSummary` model:
      ```python
      questions_asked: Optional[list[str]] = Field(
          default_factory=list,
          description="A list of any specific questions that aider asked the user before stopping."
      )
      ```

2.  **Prompt Update:**
    - In `army-infantry/src/services/aider_service/prompts.py`, modify the system prompt in the `get_system_prompt()` function.
    - Add instructions for the LLM to specifically look for questions asked by `aider` in the `stdout` and populate the new `questions_asked` field in the JSON output.
    - An example instruction to add would be:
      "## Questions Asked
      If the `aider` output contains any questions posed to the user, extract these questions verbatim and place them in the `questions_asked` list. If there are no questions, this should be an empty list."
