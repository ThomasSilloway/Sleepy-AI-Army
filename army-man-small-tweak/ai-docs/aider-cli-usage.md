**Aider CLI Options: Automation Focus (LLM Agent)**

**Core Execution & Task Specification**

* Single-shot command
    * CLI: `--message "<PROMPT>"` or `-m "<PROMPT>"`
    * Desc: Primary for automation. Sends prompt; Aider processes, applies changes, then exits. Non-interactive.
    * Usage: `aider [files_to_update] -m "Detailed instructions"`

* Apply pre-defined changes
    * CLI: `--apply <PATCH_FILE_PATH>`
    * Desc: Applies diff/plain-text patch. Combine with `--message` or use standalone.
    * Usage: `aider --apply my_feature.diff -m "Integrate patch."`

**File Handling**

* Specify files for update
    * Syntax: `aider <file1.py> [file2.js ...]`
    * Desc: List target files for edits directly after `aider` command, before other flags.

* Specify files for read-only context
    * CLI: `--read <context_file.md_or_url>`
    * Desc: Adds file/URL content as read-only context. Not edited by the main task.
    * Usage: `aider target.py --read standards.md -m "Update target.py per standards.md"`

**Model Configuration**

* Select main LLM
    * CLI: `--model <MODEL_ID>`
    * Desc: Specifies primary LLM (e.g., `gpt-4o`, `claude-3-5-sonnet`, `ollama/model-name`).
    * Env: `AIDER_MODEL`

* Set API key(s)
    * CLI: `--api-key <PROVIDER_NAME=YOUR_API_KEY>`
    * Desc: API key for LLM provider (e.g., `openai=sk-xxxx`). Multiple allowed.
    * Env: `AIDER_OPENAI_API_KEY`, `AIDER_ANTHROPIC_API_KEY` (and others per provider)

* Specify editor model (Architect mode)
    * CLI: `--editor-model <MODEL_ID>`
    * Desc: Model for edit generation step in Architect mode.

* Specify weak model (Auxiliary tasks)
    * CLI: `--weak-model <MODEL_ID>`
    * Desc: Often faster/cheaper model for commit messages, history summarization.

**Controlling Aider's Behavior for Automation**

* Edit format
    * CLI: `--edit-format <FORMAT_TYPE>`
    * Desc: How LLM specifies changes (e.g., `diff`, `udiff`, `whole`). `whole` can be simpler for script parsing.

* Auto-accept (Architect mode)
    * CLI: `--auto-accept-architect`
    * Desc: Auto-accepts architect model proposals. Useful for non-interactive scripts.

* Git commit behavior
    * CLI: `--no-auto-commits`
    * Desc: Disables Aider's automatic git commits. Lets the script manage version control.
    * CLI: `--no-dirty-commits`
    * Desc: Prevents Aider from committing pre-existing (dirty) changes in the repository.

* Automated testing & linting
    * CLI: `--auto-test` / `--no-auto-test`
    * Desc: Enable/disable auto-running tests after Aider makes changes.
    * CLI: `--test-cmd "<YOUR_TEST_COMMAND>"`
    * Desc: Specifies the shell command to execute for running tests.
    * CLI: `--auto-lint` / `--no-auto-lint`
    * Desc: Enable/disable auto-running a linter after Aider makes changes.
    * CLI: `--lint-cmd "<YOUR_LINT_COMMAND>"`
    * Desc: Specifies the shell command to execute for linting.

* Configuration file
    * CLI: `--config <FILE_PATH.YML>` or `-c <FILE_PATH.YML>`
    * Desc: Loads Aider options from a specified YAML configuration file. Recommended for standardizing settings in automation scripts.

**Key Automation Note for LLM:**
* The `--message` flag is fundamental for non-interactive CLI execution. Ensure prompts are comprehensive and self-contained. For highly complex, multi-step interactions or conditional logic, directly using Aider's Python library functions within your script might offer more control than chaining multiple CLI calls.
