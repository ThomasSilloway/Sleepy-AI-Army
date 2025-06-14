"""Main application entry point for the PoC7 Orchestrator."""
import argparse
import logging
import traceback

import nest_asyncio
from dotenv import load_dotenv

from src.config import AppConfig
from src.graph_builder import build_graph
from src.services import (
    AiderService,
    ChangelogService,
    GitService,
    LlmPromptService,  # Added import
    WriteFileFromTemplateService,
)
from src.state import WorkflowState
from src.utils.logging_setup import setup_logging

# Load the .env file
load_dotenv()

# Apply nest_asyncio *before* any async operations can start
# Required for our hacky way of using asyncio.run() in different places just for pydantic ai
nest_asyncio.apply() # <-- Apply the patch

def main():
    print("PoC7 LangGraph Orchestrator Starting...")
    logger = logging.getLogger(__name__) # Define logger early for initialization errors

    try:
        # Set up argument parsing
        parser = argparse.ArgumentParser(description="PoC7 LangGraph Orchestrator")
        parser.add_argument("--root_git_path", type=str, help="Override the goal_git_path from the config YAML.")
        parser.add_argument("--goal_path", type=str, help="Override the goal_root_path from the config YAML.")
        args = parser.parse_args()

        # Load configuration using the AppConfig class method
        app_config = AppConfig.load_from_yaml(root_git_path=args.root_git_path, goal_path=args.goal_path)

        setup_logging(app_config=app_config)
        # You can now use app_config throughout your application
        logger.overview(f"Workspace root: {app_config.workspace_root_path}")
        logger.overview(f"Goal root: {app_config.goal_root_path}")

        # Instantiate Services
        changelog_service = ChangelogService(app_config=app_config)
        repo_path = app_config.goal_git_path        
        git_service = GitService(repo_path=repo_path)
        write_file_service = WriteFileFromTemplateService()
        llm_prompt_service = LlmPromptService(app_config=app_config)
        aider_service = AiderService(app_config=app_config, llm_prompt_service=llm_prompt_service)
        logger.debug("Services instantiated.")

    except Exception as e:
        # Use the logger if setup_logging has been called, otherwise print
        if logger.handlers:
            logger.critical(f"Failed to initialize application due to configuration error: {e}")
            logger.critical(f"Callstack:\n{traceback.format_exc()}")
        else:
            print(f"CRITICAL: Failed to initialize application due to configuration error: {e}")
            print(f"Callstack:\n{traceback.format_exc()}")
        return  # Exit if configuration fails

    # Define LangGraph graph
    graph_builder = build_graph()
    logger.debug("Graph builder created.")

    # Compile graph
    app_graph = graph_builder.compile()
    logger.debug("Graph compiled.")

    # Prepare initial WorkflowState

    # TODO: Do this initialization inside of the state.py class instead and change this to update the last event summary
    initial_state: WorkflowState = {
        "current_step_name": None,
        "goal_folder_path": None,
        "workspace_folder_path": None,
        "task_description_path": None,
        "task_description_content": None,
        "manifest_template_path": None,
        "changelog_template_path": None,
        "manifest_output_path": None,
        "changelog_output_path": None,
        "last_event_summary": "Workflow initiated.",
        "aider_last_exit_code": None,
        "error_message": None,
        "is_manifest_generated": False,
        "is_changelog_entry_added": False,
    }

    # Prepare RunnableConfig
    runnable_config = {
        "configurable": {
            "app_config": app_config,
            "aider_service": aider_service,
            "changelog_service": changelog_service,
            "git_service": git_service,
            "write_file_service": write_file_service,
            "llm_prompt_service": llm_prompt_service, # Add LlmPromptService to config
        }
    }
    logger.debug("RunnableConfig prepared.")

    # Invoke graph execution
    logger.overview("Invoking graph execution...")
    final_state = app_graph.invoke(initial_state, config=runnable_config)

    # logger.info(f"Final workflow state: {final_state}")
    # Output only the current_step_name, last_event_summary, error_message, is_manifest_generated, and is_changelog_entry_added each on separate lines with helpful indentation and labels
    logger.overview("PoC7 LangGraph Orchestrator finished.")
    logger.overview(f"  - Current Step Name: {final_state.get('current_step_name', 'N/A')}")
    logger.overview(f"  - Last Event Summary: {final_state.get('last_event_summary', 'N/A')}")
    logger.overview(f"  - Error Message: {final_state.get('error_message', 'N/A')}")
    logger.overview(f"  - Is Manifest Generated: {final_state.get('is_manifest_generated', 'N/A')}")
    logger.overview(f"  - Is Changelog Entry Added: {final_state.get('is_changelog_entry_added', 'N/A')}")

if __name__ == "__main__":
    main()
