```spr
Title: Refactor Subprocess Output Logging in Army General
Version: 1.0
Date: 2025-05-31
Author: Jules (AI Agent)
Status: Proposed

## 1. Problem

((Context))
The `army-general/src/main.py` file contains duplicated code within the `_run_secretary()` and `_run_army_man()` functions. This duplication pertains to the recently implemented feature for optionally logging `stdout` and `stderr` from these subprocesses.

((Duplicated Logic))
The duplicated sections include:
*   Checking the boolean flag (e.g., `app_config.log_secretary_output`).
*   Logging start and end demarcation messages.
*   Accessing/decoding `stdout` and `stderr` from either a `subprocess.CompletedProcess` object (for successful execution or when `check=False`) or a `subprocess.CalledProcessError` object.
*   Iterating over output lines and logging them with appropriate prefixes (e.g., `[SECRETARY STDOUT]`) and log levels.
*   Handling empty output streams.

((Impact))
Code duplication makes the software harder to maintain (changes need to be applied in multiple places), increases the risk of inconsistencies, and reduces readability.

## 2. Solution

((Overview))
Refactor the duplicated subprocess output logging logic into a single, reusable helper function within `army-general/src/main.py`. This function will be responsible for all aspects of formatting and logging the `stdout` and `stderr` content based on the provided parameters.

((Chosen Approach - A+ Solution from Critique))
A new private helper function `_log_subprocess_details` will be implemented.

**Function Signature:**
```python
def _log_subprocess_details(
    process_name: str,
    log_flag: bool,
    stdout_content: str | bytes,
    stderr_content: str | bytes,
    return_code: int  # Changed from return_code_for_stderr_level for clarity
) -> None:
```

*   `process_name` (str): The name of the subprocess (e.g., "Secretary", "Army Man") for use in log prefixes.
*   `log_flag` (bool): The configuration flag that determines if logging should occur (e.g., `app_config.log_secretary_output`).
*   `stdout_content` (str | bytes): The content of `stdout` from the subprocess. Can be string (if `text=True` on `CompletedProcess`) or bytes (from `CalledProcessError`).
*   `stderr_content` (str | bytes): The content of `stderr` from the subprocess. Can be string or bytes.
*   `return_code` (int): The actual return code of the subprocess. Used to determine the log level for `stderr`.

**Function Logic (`_log_subprocess_details`):**
1.  If `not log_flag`, return immediately.
2.  Log start demarcation: `logger.info(f"--- Start of output from {process_name} ---")`.
3.  Process and log `stdout_content`:
    *   Decode if `stdout_content` is bytes: `stdout_str = stdout_content.decode('utf-8', errors='replace') if isinstance(stdout_content, bytes) else stdout_content`.
    *   If `stdout_str` (and not empty after `strip()`):
        *   For each line in `stdout_str.splitlines()`: `logger.info(f"[{process_name.upper()} STDOUT]: {line}")`.
    *   Else: `logger.info(f"[{process_name.upper()} STDOUT]: (empty)")`.
4.  Process and log `stderr_content`:
    *   Decode if `stderr_content` is bytes: `stderr_str = stderr_content.decode('utf-8', errors='replace') if isinstance(stderr_content, bytes) else stderr_content`.
    *   If `stderr_str` (and not empty after `strip()`):
        *   Determine `log_level`: `logging.ERROR` if `return_code != 0`, else `logging.WARNING`.
        *   For each line in `stderr_str.splitlines()`: `logger.log(log_level, f"[{process_name.upper()} STDERR]: {line}")`.
    *   Else: `logger.info(f"[{process_name.upper()} STDERR]: (empty)")`.
5.  Log end demarcation: `logger.info(f"--- End of output from {process_name} ---")`.

## 3. High-Level Implementation Plan

1.  **Implement `_log_subprocess_details` function:**
    *   Add the function to `army-general/src/main.py` as defined above.
2.  **Refactor `_run_secretary()`:**
    *   Remove the duplicated logging logic.
    *   In the `try` block (after successful `subprocess.run` and if `check=True` is used, this means `returncode == 0`):
        *   Call `_log_subprocess_details("Secretary", app_config.log_secretary_output, process.stdout, process.stderr, process.returncode)`.
    *   In the `except subprocess.CalledProcessError as e:` block:
        *   Call `_log_subprocess_details("Secretary", app_config.log_secretary_output, e.stdout, e.stderr, e.returncode)`.
        *   The primary `logger.error(f"Run Secretary failed...")` message should be logged *before* this call.
3.  **Refactor `_run_army_man()`:**
    *   Apply the same refactoring pattern as in `_run_secretary()`, using "Army Man" as `process_name` and `app_config.log_army_man_output` for `log_flag`.
4.  **Verification:**
    *   Ensure that the `subprocess.run` calls consistently use `text=True` and `check=True` to align with the expectations of the refactored calling code (i.e., success path means `returncode == 0`, failures raise `CalledProcessError`).
    *   Confirm that the overall logging behavior (when flags are true or false) remains identical to the pre-refactoring version.

((Success Criteria))
*   Duplicated subprocess output logging logic in `_run_secretary` and `_run_army_man` is removed and replaced by calls to `_log_subprocess_details`.
*   The `_log_subprocess_details` function correctly logs `stdout` and `stderr` as per its definition.
*   The application's logging behavior for subprocess output remains functionally unchanged.
*   Code readability and maintainability in `army-general/src/main.py` are improved.
```
