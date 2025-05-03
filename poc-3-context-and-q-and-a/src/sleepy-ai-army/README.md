# Running Sleepy Dev Team PoC 3 with ADK Web UI

This guide explains how to set up and run the Sleepy Dev Team PoC 3 project using the interactive ADK Web UI (`adk web`).

## Prerequisites

1.  **Python:** Ensure you have Python 3.9 or higher installed.
2.  **Google ADK:** The `google-adk` library must be installed.
3.  **Project Code:** You need the complete source code for the `sleepy-dev-team` project, structured according to the Technical Architecture document.
4.  **API Key:** You need a valid Gemini API key (from Google AI Studio or configured via Vertex AI ADC).
5.  **Terminal/Command Prompt:** Access to a terminal or command prompt to run commands.

## Setup Instructions

1.  **Navigate to Project Root:**
    Open your terminal or command prompt and change the directory to the root of the project, which should be the `/src/sleepy-dev-team/` folder.

    ```bash
    cd /path/to/your/src/sleepy-dev-team/
    ```

2.  **Create/Activate Virtual Environment (Recommended):**
    It's highly recommended to use a virtual environment to manage dependencies.

    ```bash
    # Create the environment (only needs to be done once)
    python -m venv .venv

    # Activate the environment (do this every time you open a new terminal for this project)
    # macOS / Linux:
    source .venv/bin/activate
    # Windows CMD:
    # .venv\Scripts\activate.bat
    # Windows PowerShell:
    # .venv\Scripts\Activate.ps1
    ```

3.  **Install Dependencies:**
    Install the required Python packages listed in `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Key:**
    * Locate the `.env` file inside the `sleepy_ai_army` package directory (`sleepy_ai_army/.env`). If it doesn't exist, create it.
    * Add your Gemini API key to the `.env` file. It should look similar to this (replace `YOUR_API_KEY_HERE` with your actual key):

        ```dotenv
        # For Google AI Studio API Key
        GOOGLE_API_KEY=YOUR_API_KEY_HERE
        GOOGLE_GENAI_USE_VERTEXAI=FALSE

        # --- OR ---

        # For Vertex AI (using Application Default Credentials)
        # Ensure you have run `gcloud auth application-default login`
        # GOOGLE_CLOUD_PROJECT=your-gcp-project-id
        # GOOGLE_CLOUD_LOCATION=us-central1 # Or your region
        # GOOGLE_GENAI_USE_VERTEXAI=TRUE
        ```
    * Ensure only one set of configurations (either AI Studio or Vertex AI) is active (not commented out).

## Running the Agent with `adk web`

1.  **Ensure Correct Directory:** Make absolutely sure your terminal is currently in the `/src/sleepy-dev-team/` directory (the *parent* directory of the `sleepy_ai_army` package).
2.  **Launch the Web UI:** Run the following command:

    ```bash
    adk web
    ```

3.  **Access the UI:** The terminal will output messages indicating the server has started, usually including a URL like `http://127.0.0.1:8000` or `http://localhost:8000`. Open this URL in your web browser.

## Interacting via the Web UI

1.  **Select Agent:** In the top-left corner of the ADK Web UI, find the dropdown menu listing available agent packages. Select **`sleepy_ai_army`**.
2.  **Start Interaction:** The chat interface on the right is now connected to your `sleepy_ai_army` agent system (specifically, the `root_agent` defined in `sleepy_ai_army/agent.py`).
