# PoC 6 - Project Scaffolding Script (`scaffold_project.py`)

## Purpose

This Python script automatically generates the initial directory structure and placeholder files for the "PoC 6: Sequential Agent Failure Handling" project, as defined in the Technical Architecture Document (v1.4). It saves you from manually creating each folder and file.

## Prerequisites

* **Python 3:** Ensure you have Python 3 installed on your system.

## Usage

1.  **Save the Script:** Save the Python code provided in the previous step as `scaffold_project.py` in a convenient location on your computer (e.g., your development workspace directory).
2.  **Open Terminal:** Open a terminal or command prompt.
3.  **Navigate:** Change directory (`cd`) to the location where you saved `scaffold_project.py`.
4.  **Run the Script:** Execute the script using Python:
    ```bash
    python scaffold_project.py
    ```

## Expected Outcome

* The script will print messages to the console indicating which directories and files it is creating.
* A new directory named `poc6-sequential-failure` will be created in the same location where you ran the script.
* Inside `poc6-sequential-failure`, you will find the complete folder structure and initial files (`.py`, `.env.example`, `requirements.txt`, `README.md`, etc.) as defined in the architecture document.
    * Some files will contain basic placeholder content or imports.
    * Files intended for more complex code (`agent.py`, `callbacks.py`, `tools.py`) will contain `# TODO:` comments indicating where implementation is needed.

## Next Steps After Running the Script

1.  **Navigate into Project:**
    ```bash
    cd poc6-sequential-failure
    ```
2.  **Create Virtual Environment:** It's highly recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment:**
    * Copy `.env.example` to `.env`.
    * Edit `.env` and add your actual Google API Key (`GOOGLE_API_KEY`). **Remember to keep your `.env` file secret and do not commit it to version control.**
5.  **Implement Code:** Open the project in your code editor and start implementing the agent logic, tool logic, and callback functions within the generated files, looking for `# TODO:` comments.
6.  **Run the Agent:** Once implemented, you can typically run the ADK agent using the web interface:
    ```bash
    adk web
    ```
    (Ensure you are in the `poc6-sequential-failure` directory with your virtual environment activated).