```spr
Title: Enhanced Subprocess Output Logging in Army General
Version: 1.0
Date: 2025-05-31
Author: Jules (AI Agent)
Status: Proposed

## 1. Problem

((Goal))
The `army-general` application orchestrates `army-secretary` and `army-man-small-tweak` as subprocesses.
If these subprocesses encounter errors, especially before their own logging initializes or if their logging fails, their `stdout` and `stderr` output is not captured by `army-general`'s logging.
This makes diagnosing issues in the child processes difficult, as crucial error messages or operational output can be lost.

((Current System))
`army-general` uses `subprocess.run()` with `capture_output=True` to execute child processes.
It checks the `returncode` but does not currently log the captured `process.stdout` or `process.stderr` content.
Each application (`army-general`, `army-secretary`, `army-man-small-tweak`) has its own independent logging configuration.

((Key Challenge))
To provide a mechanism for `army-general` to optionally log the complete output of its child processes for improved diagnostics, without requiring modifications to the child processes themselves.

## 2. Solution

((Overview))
Modify `army-general` to optionally log the `stdout` and `stderr` streams from `army-secretary` and `army-man-small-tweak` subprocesses.
This feature will be controlled by new configuration flags, allowing users to enable it when detailed diagnostics are needed.

((Detailed Solution - A+ Approach from Critique))
1.  **Configuration Update (`army-general/config.yml` & `army-general/src/config.py`):**
    *   Introduce two new boolean configuration flags:
        *   `log_secretary_output` (default: `false`)
        *   `log_army_man_output` (default: `false`)
    *   Update `AppConfig` in `src/config.py` to load and store these new flags.
    *   Add comments in `config.yml` explaining these flags.

2.  **Subprocess Execution Modification (`army-general/src/main.py`):**
    *   In `_run_secretary()` and `_run_army_man()` functions:
        *   After `subprocess.run()` completes, check the corresponding new configuration flag (e.g., `app_config.log_secretary_output`).
        *   If the flag is `true`:
            *   Log a demarcation message (e.g., `logger.info("--- Start of output from Secretary ---")`).
            *   Decode `process.stdout` and `process.stderr` (if not empty) from bytes to string (using 'utf-8' or a consistent encoding).
            *   Iterate through each line of the decoded `stdout`:
                *   Log each line using `army-general`'s `logger.info()`, prefixed with a clear identifier (e.g., `"[SECRETARY STDOUT]: "`).
            *   Iterate through each line of the decoded `stderr`:
                *   Log each line using `army-general`'s `logger.warning()` (or `logger.error()` if subprocess `returncode != 0`), prefixed (e.g., `"[SECRETARY STDERR]: "`).
            *   If `stdout` or `stderr` is empty, log a specific message like `"[SECRETARY STDOUT]: (empty)"` or skip logging for that stream.
            *   Log an end demarcation message (e.g., `logger.info("--- End of output from Secretary ---")`).

((No Changes to Child Projects))
This solution explicitly requires no modifications to `army-secretary` or `army-man-small-tweak`.

## 3. High-Level Implementation Plan

1.  **Modify `army-general/src/config.py`:**
    *   Add `log_secretary_output: bool = False` and `log_army_man_output: bool = False` (or similar, depending on Pydantic/config library usage) to the `AppConfig` class.
    *   Ensure these are loaded from the YAML file.
2.  **Modify `army-general/config.yml`:**
    *   Add the new keys `log_secretary_output: false` and `log_army_man_output: false` with comments.
3.  **Modify `army-general/src/main.py`:**
    *   **In `_run_secretary()` function:**
        *   Retrieve `app_config.log_secretary_output`.
        *   If true, implement logging of `process.stdout` and `process.stderr` as described in "Detailed Solution", using `logger.info` for stdout and `logger.warning`/`logger.error` for stderr, with appropriate prefixes and demarcations.
    *   **In `_run_army_man()` function:**
        *   Retrieve `app_config.log_army_man_output`.
        *   If true, implement logging of `process.stdout` and `process.stderr` similarly, using prefixes like `[ARMY-MAN STDOUT/STDERR]`.
    *   Ensure consistent decoding of byte streams (`process.stdout.decode('utf-8', errors='replace')`).
    *   Handle potential `None` or empty `stdout`/`stderr` gracefully.

((Success Criteria))
*   When new config flags are `false`, `army-general`'s logging behavior is unchanged.
*   When a flag (e.g., `log_secretary_output`) is `true`:
    *   The `stdout` from the corresponding subprocess is logged line-by-line to `army-general`'s log outputs (console and file) at INFO level, clearly prefixed.
    *   The `stderr` from the corresponding subprocess is logged line-by-line at WARNING or ERROR level, clearly prefixed.
    *   Demarcation messages are present.
*   The changes are isolated to the `army-general` project.
```
