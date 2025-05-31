# Brainstorming: Refactoring Subprocess Logging in `army-general`

## 1. Identified Duplication in `army-general/src/main.py`

The primary duplication exists in the `_run_secretary()` and `_run_army_man()` functions. It encompasses:

*   **Successful Process Output Logging:** The logic to log `process.stdout` and `process.stderr` when the respective `log_..._output` flag is true. This includes:
    *   Start/end demarcation log messages.
    *   Decoding (if needed, though current `subprocess.run` uses `text=True`).
    *   Line-by-line logging with dynamic prefixes (e.g., `[SECRETARY STDOUT]`, `[ARMY-MAN STDERR]`).
    *   Determining log level for `stderr` based on `process.returncode`.
    *   Handling of empty `stdout` or `stderr` streams.

*   **Failed Process Output Logging (`CalledProcessError`):** The logic within the `except subprocess.CalledProcessError as e:` block to log `e.stdout` (bytes) and `e.stderr` (bytes) if the `log_..._output` flag is true. This also includes:
    *   Start/end demarcation.
    *   Decoding from bytes.
    *   Line-by-line logging with dynamic prefixes.
    *   Handling of empty streams.

The key differences between the two calls (`_run_secretary` and `_run_army_man`) are:
*   The specific configuration flag being checked (`app_config.log_secretary_output` vs. `app_config.log_army_man_output`).
*   The prefix string used for logging (e.g., "SECRETARY" vs. "ARMY-MAN").
*   The main logger messages indicating success or failure of the specific subprocess.

## 2. Refactoring Solutions

### Solution A: Dedicated Helper Function for Logging Process Output

*   **Description:** Create a new function, e.g., `_log_subprocess_output(process_name: str, completed_process: subprocess.CompletedProcess | None, process_error: subprocess.CalledProcessError | None, log_flag: bool)`.
    *   `process_name`: A string like "Secretary" or "Army Man" to be used in log prefixes.
    *   `completed_process`: The `subprocess.CompletedProcess` object if the command ran (even if it failed with a non-zero exit code but didn't raise `CalledProcessError` because `check=False` was used, or if `check=True` and it succeeded).
    *   `process_error`: The `subprocess.CalledProcessError` object if `check=True` caused an exception. One of `completed_process` or `process_error` would typically be non-None.
    *   `log_flag`: The boolean flag indicating whether to perform logging (e.g., `app_config.log_secretary_output`).
*   **Logic within helper:**
    *   If `log_flag` is false, return immediately.
    *   Log start demarcation using `process_name`.
    *   If `process_error` is provided:
        *   Access `process_error.stdout` (bytes) and `process_error.stderr` (bytes). Decode them.
        *   Log lines with appropriate prefixes (e.g., `f"[{process_name.upper()} STDOUT ON ERROR]:"`) and levels (`INFO` for stdout, `ERROR` for stderr).
    *   Else if `completed_process` is provided:
        *   Access `completed_process.stdout` (string, as `text=True`) and `completed_process.stderr` (string).
        *   Log lines with appropriate prefixes (e.g., `f"[{process_name.upper()} STDOUT]:"`) and levels (`INFO` for stdout, `ERROR` if `returncode != 0` else `WARNING` for stderr).
    *   Handle empty streams for both cases.
    *   Log end demarcation.
*   **Usage:**
    ```python
    # In _run_secretary()
    try:
        process = subprocess.run(...) # check=True
        _log_subprocess_output("Secretary", process, None, app_config.log_secretary_output)
        # ... handle process.returncode ...
    except subprocess.CalledProcessError as e:
        _log_subprocess_output("Secretary", None, e, app_config.log_secretary_output)
        # ... handle error ...
    ```

### Solution B: Context Manager for Subprocess Execution and Logging

*   **Description:** Create a context manager class, e.g., `SubprocessRunnerAndLogger`.
    *   `__init__(self, process_name: str, command: list[str], cwd: str, log_flag: bool, app_config_val)`
    *   `__enter__(self)`: Runs the subprocess. Stores the result or exception. Returns `self`.
    *   `__exit__(self, exc_type, exc_val, exc_tb)`: Performs the detailed logging based on the stored result/exception and `log_flag`. Handles cleanup if any.
*   **Logic:** The logging logic from Solution A would be mostly within `__exit__`. The `subprocess.run` call would be in `__enter__` or `__init__`.
*   **Usage:**
    ```python
    # In _run_secretary()
    log_flag = app_config.log_secretary_output
    runner = SubprocessRunnerAndLogger("Secretary", command_to_run, secretary_directory, log_flag)
    with runner:
        if runner.exception:
            # Handle CalledProcessError specifics not handled by __exit__ logging
            logger.error(f"Run Secretary failed: {runner.exception}")
            return False
        elif runner.process_details.returncode != 0:
            # Handle non-zero exit code specifics not handled by __exit__ logging
            if not log_flag: # If detailed logs weren't printed by context manager
                 logger.error(f"Secretary returned non-zero exit code: {runner.process_details.returncode}. ...")
            return False
    logger.info("Secretary completed successfully.")
    return True
    ```
    This gets a bit more complex in how the calling code interacts with the success/failure and the captured output if needed outside of just logging.

### Solution C: Modifying `subprocess.run` Call to Include a Logging Callback

*   **Description:** This is more involved. It would mean wrapping `subprocess.run` or creating a new function that takes an optional callback for real-time (or near real-time if polling `process.stdout.readline()`) logging.
    *   The `subprocess.Popen` class would be needed to get access to stdout/stderr streams for real-time reading.
    *   The callback would be invoked for each line.
*   **Logic:** The helper function would manage `Popen`, read lines from `stdout`/`stderr` in a non-blocking way (or separate threads), and call the user-provided logging callback.
*   **Pros:**
    *   Could provide interleaved `stdout` and `stderr` in the order they are produced (if using threads and queues).
*   **Cons:**
    *   Significantly more complex than the current `subprocess.run` usage.
    *   Harder to manage `check=True` equivalent behavior.
    *   Demarcation and overall success/failure logging becomes trickier.
    *   Likely overkill for the current requirement of just dumping output after completion or on error.

This brainstorming focuses on centralizing the *post-mortem* logging logic. Solution A seems like the most straightforward and least disruptive way to refactor the existing duplicated blocks.
