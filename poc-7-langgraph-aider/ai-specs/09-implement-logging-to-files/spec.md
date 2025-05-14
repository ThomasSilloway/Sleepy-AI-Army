# Features: Implement Comprehensive File-Based Logging System

> Given the Objective, implement every detail of every task, using the referenced architectural documents as the primary guide for implementation specifics.

## Objectives

- Enhance the application's logging system to support writing logs to `overview.log` and `detailed.log` files.
- Adhere to the specified timestamp format (`[HH:MM:SS.mmm]`) for log entries as per the technical architecture.
IMPORTANT: Some aspects of the current logging_setup.py may differ from the tech-architecture documents. Use the current implementation as the source of truth and build out changes from there.

## Context

```
/add poc-7-langgraph-aider\src\utils\logging_setup.py

/read-only poc-7-langgraph-aider\src\state.py
/read-only poc-7-langgraph-aider\src\config.py
/read-only poc-7-langgraph-aider\src\main.py
/read-only poc-7-langgraph-aider\ai-docs\planning\01_manifest-and-changelist\05_1_tech_architecture_overview.md      
/read-only poc-7-langgraph-aider\ai-docs\planning\01_manifest-and-changelist\05_2-tech_architecture-flow.md
/read-only poc-7-langgraph-aider\ai-docs\planning\01_manifest-and-changelist\05_3-tech_architecture-file-structure.md
/read-only poc-7-langgraph-aider\ai-specs\09-implement-logging-to-files\spec.md
```

## Low-Level Tasks

> Ordered from start to finish. Implement the described functionality, using standard Python features, error handling, and logging as appropriate.

### Task 1: Enhance `setup_logging` Function for File Logging
```

  - UPDATE `poc-7-langgraph-aider\src\utils\logging_setup.py`:
      - Fonfigure a `logging.FileHandler` to write to `overview_log_path`.
          - This handler should be configured with an appropriate logging level (e.g., `logging.INFO`).
          - Apply the `LowercaseLevelnameFormatter` (or a new formatter if different formatting is needed for files).
      - Configure a separate `logging.FileHandler` to write to this `detailed_log_path`.
          - This handler should be configured with a more verbose logging level (e.g., `logging.DEBUG`).
          - Apply the `LowercaseLevelnameFormatter` (or a new formatter).
      - Ensure the root logger is configured to add these file handlers.
      - Adjust the log formatter's `datefmt` and `fmt` string to align more closely with the `[HH:MM:SS.mmm]` timestamp requirement and overall log message structure (e.g., `fmt="[%(asctime)s.%(msecs)03d] (%(levelname)s) [%(name)s] %(message)s"` and `datefmt="%H:%M:%S"`).

```