import asyncio
import logging
import os
import traceback # New import
from typing import TypedDict # Required for WorkflowState if it remains a TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from .config import AppConfig
from .services.llm_prompt_service import LLMPromptService
from .pydantic_models.summaries import TextSummary
from .state import WorkflowState


def setup_logging(app_config: AppConfig): # Pass AppConfig
    """Configures basic logging for the application."""
    numeric_level = getattr(logging, app_config.log_level.upper(), logging.INFO)
    
    handlers = [logging.StreamHandler()] # Always log to console
    if app_config.log_to_file:
        # Ensure the log directory exists if LOG_FILE_PATH includes a directory
        log_file_dir = os.path.dirname(app_config.log_file_path)
        if log_file_dir and not os.path.exists(log_file_dir):
            os.makedirs(log_file_dir, exist_ok=True)
        handlers.append(logging.FileHandler(app_config.log_file_path))
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=handlers
    )

async def start_node(state: WorkflowState, config) -> WorkflowState: # Add config
    """Initializes the workflow with input text from AppConfig."""
    app_config_from_config: AppConfig = config['configurable']['app_config'] # Get app_config
    logging.info("Executing start_node")
    state['input_text'] = app_config_from_config.poc9_input_text # Use text from config
    state['generated_summary'] = None
    state['error_message'] = None
    state['error_details'] = None # Initialize new field
    return state

async def main():
    """Main asynchronous function to set up and run the LangGraph application."""
    load_dotenv() # Load environment variables from .env for AppConfig

    try:
        app_config = AppConfig()
    except ValueError as e:
        # AppConfig raises ValueError if GEMINI_API_KEY is missing
        # Logging might not be set up yet if AppConfig fails early, so print as well.
        print(f"CRITICAL: Failed to initialize AppConfig: {e}")
        logging.critical(f"Failed to initialize AppConfig: {e}")
        return # Exit if config fails

    setup_logging(app_config) # Call with app_config
    logging.info("Starting PoC-9: Async LangGraph with Pydantic-AI")

    llm_service = LLMPromptService(app_config=app_config)

    # Define the graph structure using WorkflowState
    workflow = StateGraph(WorkflowState)

    workflow.add_node("start", start_node)

    # Node to perform summarization, configured with services
    async def summarization_node_with_config(state: WorkflowState, config) -> WorkflowState:
        """Summarizes input text using LLM service passed via config."""
        logging.info("Executing summarization_node_with_config")
        llm_service_from_config: LLMPromptService = config['configurable']['llm_service']
        app_config_from_config: AppConfig = config['configurable']['app_config']
        try:
            if not state['input_text']:
                raise ValueError("Input text is missing for summarization.")
            
            messages = [
                {"role": "system", "content": "You are an expert summarizer. Please provide a concise summary of the following text."},
                {"role": "user", "content": state['input_text']}
            ]
            
            summary_model: TextSummary | None = await llm_service_from_config.get_structured_output(
                messages=messages,
                output_pydantic_model_type=TextSummary,
                llm_model_name=app_config_from_config.gemini_summarizer_model_name
            )
            
            if summary_model:
                state['generated_summary'] = summary_model.summary
                logging.info(f"Summary generated: {state['generated_summary']}")
            else:
                state['error_message'] = "Failed to generate summary (LLM returned None)."
                logging.error(state['error_message'])
        except Exception as e:
            logging.error(f"Error in summarization_node_with_config: {e}", exc_info=True) # exc_info=True logs traceback
            state['error_message'] = str(e)
            state['error_details'] = traceback.format_exc() # Store traceback
        return state

    workflow.add_node("summarize", summarization_node_with_config)

    # Define graph flow: start -> summarize -> END
    workflow.set_entry_point("start")
    workflow.add_edge("start", "summarize")
    workflow.add_edge("summarize", END)

    # Compile the graph into a runnable application
    app = workflow.compile()

    # Initial state for graph invocation (input_text is set by start_node)
    initial_state: WorkflowState = {
        "input_text": "", 
        "generated_summary": None,
        "error_message": None,
        "error_details": None # Initialize new field
    }
    
    # Configuration for passing services to nodes
    runnable_config = {
        "configurable": {
            "llm_service": llm_service,
            "app_config": app_config,
        }
    }

    # Asynchronously invoke the graph
    logging.info("Invoking graph execution...")
    final_state = await app.ainvoke(initial_state, config=runnable_config)

    logging.info("Graph execution finished.")
    if final_state.get('error_message'):
        logging.error(f"Workflow completed with error: {final_state['error_message']}")
        if final_state.get('error_details'):
            logging.debug(f"Error details:\n{final_state['error_details']}")
    else:
        logging.info(f"Workflow completed successfully. Final summary: {final_state.get('generated_summary', 'N/A')}")

if __name__ == "__main__":
    # Early check for GEMINI_API_KEY from .env before attempting to run the async app.
    # AppConfig will perform a more thorough check, but this provides an immediate user-facing error.
    load_dotenv() 
    if not os.getenv("GEMINI_API_KEY"):
        print("CRITICAL: GEMINI_API_KEY environment variable not set. Please define it in your .env file.")
    else:
        asyncio.run(main())
