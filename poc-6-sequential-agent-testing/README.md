# POC-6-SEQUENTIAL-AGENT-TESTING

Demonstrates conditional skipping and failure handling within an ADK SequentialAgent.

## Purpose

This project is Proof-of-Concept 6 (PoC 6), designed as a technical experiment to validate and demonstrate control flow patterns within the Google Agent Development Kit (ADK). Specifically, it uses a `SequentialAgent` to show how intermediate steps (Agents B, C) can be conditionally skipped based on the failure of a preceding step (Agent A), while ensuring a final step (Agent D) always executes and summarizes the outcome.

## Setup

1.  **Clone/Setup Project:** Ensure you have the project files checked out or created (e.g., using the scaffolding script). The root directory is `POC-6-SEQUENTIAL-AGENT-TESTING`.
2.  **Create Virtual Environment:** From the project root directory (`POC-6-SEQUENTIAL-AGENT-TESTING`), create a virtual environment:
    ```bash
    python -m venv .venv
    ```
3.  **Activate Environment:**
    * Mac/Linux: `source .venv/bin/activate`
    * Windows: `.\.venv\Scripts\activate`
4.  **Install Requirements:** Install the necessary Python packages:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: `requirements.txt` is located in the project root)*
5.  **Configure Environment Variables:**
    * Copy the example environment file: `cp .env.example .env` (or copy manually)
    * Edit the `.env` file and replace the placeholder with your actual Google API Key:
        ```dotenv
        GOOGLE_API_KEY="YOUR_ACTUAL_GOOGLE_API_KEY"
        ```
    * **Keep your `.env` file secure and do not commit it to version control.**

## Execution

1.  **Navigate to Source Directory:** The `adk web` command needs to be run from the directory containing the main agent package so it can be discovered. Change to the correct directory:
    ```bash
    cd src/sequential-failure-test/
    ```
2.  **Run ADK Web UI:** Start the ADK development server:
    ```bash
    adk web
    ```
3.  **Interact:**
    * Open your web browser to the URL provided by the `adk web` command (usually `http://127.0.0.1:8080`).
    * Start a new chat session.
    * Send any message to trigger the `RootAgent`. This will initiate the `ErrorTestSequence`.
    * **Observe:** Use the ADK Web UI's "Events" and "State" tabs to observe the execution flow of Agents A, B, C, and D.
        * In the initial MVP setup (MVP Step 1), you should see all agents execute successfully, with Agent D providing a summary reflecting this success path.
        * In later steps, after implementing the failure tool and callback logic, you will trigger the failure scenario and observe Agents B and C being skipped.