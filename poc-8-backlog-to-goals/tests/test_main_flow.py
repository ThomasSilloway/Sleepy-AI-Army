import pytest
import os
import yaml
from unittest.mock import patch, AsyncMock

from src.main import run as main_run # Import the main entry point
from src.models.goal_models import SanitizedGoalInfo # For mocking LLM response

# Use a consistent project root for pyfakefs
PROJECT_ROOT_FS = '/app' 
CONFIG_YAML_NAME = 'config.yaml'
BACKLOG_MD_NAME = 'TEST_MAIN_FLOW_BACKLOG.md'
ENV_FILE_NAME = '.env' # Though its loading might be complex to fully simulate if not careful

@pytest.fixture
def setup_main_flow_fs(fs): # fs fixture from pyfakefs
    """Sets up the fake file system for a main flow test."""
    
    # --- Create config.yaml ---
    fake_git_repo_path = os.path.join(PROJECT_ROOT_FS, "test_repo_for_main")
    fs.create_dir(fake_git_repo_path)

    config_content = {
        "goal_git_path": fake_git_repo_path,
        "backlog_file_name": BACKLOG_MD_NAME,
        "ai_goals_directory_name": "main_flow_ai_goals",
        "default_llm_model_name": "gemini-1.5-flash-latest" # Assuming this field is added to AppConfig
    }
    # Place config.yaml at PROJECT_ROOT_FS/config.yaml
    # AppConfig calculates its path relative to src/config.py, assuming src/config.py is in PROJECT_ROOT_FS/src/
    fs.create_file(os.path.join(PROJECT_ROOT_FS, CONFIG_YAML_NAME), contents=yaml.dump(config_content))

    # --- Create backlog.md ---
    # This is placed at config_content["goal_git_path"] / config_content["backlog_file_name"]
    backlog_content = """
## Main Flow Task 1
Description for main flow task 1.

## Main Flow Task 2
Description for main flow task 2.
    """
    fs.create_file(os.path.join(fake_git_repo_path, BACKLOG_MD_NAME), contents=backlog_content)

    # --- Create .env file ---
    # AppConfig loads this from the project root.
    # The 'monkeypatch.setenv' is generally preferred for testing env vars.
    # This file is more for completeness of the setup if AppConfig insists on loading it.
    fs.create_file(os.path.join(PROJECT_ROOT_FS, ENV_FILE_NAME), contents="GEMINI_API_KEY=env_api_key_for_main_flow\n")
    
    return {
        "project_root": PROJECT_ROOT_FS,
        "config_file_path": os.path.join(PROJECT_ROOT_FS, CONFIG_YAML_NAME),
        "backlog_file_path": os.path.join(fake_git_repo_path, BACKLOG_MD_NAME),
        "expected_output_parent_dir": fake_git_repo_path, # where ai_goals_directory_name will be created
        "expected_ai_goals_dir_name": config_content["ai_goals_directory_name"]
    }


@pytest.mark.asyncio
@patch('src.config.load_dotenv') # Explicitly patch load_dotenv for this test
@patch('src.services.llm_prompt_service.LlmPromptService.get_structured_output', new_callable=AsyncMock)
@patch('src.config.os.path.abspath') # To control where AppConfig thinks it is
async def test_main_run_successful_flow(
    mock_load_dotenv_explicit, # Renamed to avoid clash with other mock names if any
    mock_config_abspath, 
    mock_llm_get_structured_output, 
    setup_main_flow_fs, 
    monkeypatch, 
    caplog
):
    """
    Tests the main.run() flow with mocked LLM and file system.
    Verifies that directories and files are created as expected.
    """
    # --- Mocking Setup ---
    # 1. AppConfig path calculation:
    # AppConfig's __init__ uses os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # to find config.yaml. __file__ for src/config.py is /app/src/config.py in this context.
    # So, base_dir for AppConfig should be /app.
    mock_config_abspath.return_value = os.path.join(PROJECT_ROOT_FS, 'src', 'config.py')

    # 2. Environment variable for GEMINI_API_KEY
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key_main_flow")
    # mock_load_dotenv_explicit (from decorator) handles preventing real load_dotenv


    # 3. LLM Service Mocking:
    # LlmPromptService.get_structured_output is already mocked by @patch
    mock_get_structured_output.side_effect = [
        SanitizedGoalInfo(folder_name="main-flow-task-1-folder"),
        SanitizedGoalInfo(folder_name="main-flow-task-2-folder")
    ]

    # --- Run the main function ---
    # The main.py script's run() function is imported as main_run
    await main_run()

    # --- Assertions ---
    # 1. Check logs for key messages (optional, but good for diagnostics)
    assert "Starting PoC 8: Backlog to Goals Processor" in caplog.text
    assert "AppConfig initialized." in caplog.text
    assert f"Using backlog file path: {setup_main_flow_fs['backlog_file_path']}" in caplog.text
    assert "LlmPromptService initialized." in caplog.text
    assert "BacklogProcessor initialized." in caplog.text
    assert "Successfully processed 2 tasks." in caplog.text # Assuming 2 tasks in backlog
    assert "PoC 8 processing finished." in caplog.text

    # 2. Verify directory and file creation in the fake file system
    expected_output_base = os.path.join(
        setup_main_flow_fs["expected_output_parent_dir"],
        setup_main_flow_fs["expected_ai_goals_dir_name"]
    )
    assert os.path.exists(expected_output_base) # fs.exists also works

    task1_folder = os.path.join(expected_output_base, "main-flow-task-1-folder")
    assert os.path.exists(task1_folder)
    assert os.path.exists(os.path.join(task1_folder, "task-description.md"))
    with open(os.path.join(task1_folder, "task-description.md"), 'r') as f:
        assert "Description for main flow task 1." in f.read()

    task2_folder = os.path.join(expected_output_base, "main-flow-task-2-folder")
    assert os.path.exists(task2_folder)
    assert os.path.exists(os.path.join(task2_folder, "task-description.md"))
    with open(os.path.join(task2_folder, "task-description.md"), 'r') as f:
        assert "Description for main flow task 2." in f.read()
        
    # Verify LLM calls
    assert mock_get_structured_output.call_count == 2

# TODO: Add more integration tests for error scenarios in main.run():
# - AppConfig validation fails (e.g., missing API key, invalid paths in config.yaml)
# - Backlog file specified in config.yaml not found by BacklogProcessor
# - LLM service consistently fails to generate names (all fallbacks)

@pytest.mark.asyncio
@patch('src.config.load_dotenv') # Explicitly patch load_dotenv
@patch('src.config.os.path.abspath')
async def test_main_run_appconfig_fail_missing_key(mock_load_dotenv_explicit, mock_config_abspath, setup_main_flow_fs, monkeypatch, caplog):
    # Simulate GEMINI_API_KEY missing
    mock_config_abspath.return_value = os.path.join(PROJECT_ROOT_FS, 'src', 'config.py')
    monkeypatch.delenv("GEMINI_API_KEY", raising=False) # Ensure it's not set
    # mock_load_dotenv_explicit (from decorator) handles preventing real load_dotenv

    await main_run()

    assert "GEMINI_API_KEY is not set" in caplog.text
    assert "PoC 8 processing finished." not in caplog.text # Should exit early


@pytest.mark.asyncio
@patch('src.services.llm_prompt_service.LlmPromptService.get_structured_output', new_callable=AsyncMock)
@patch('src.config.os.path.abspath')
async def test_main_run_backlog_file_not_found_in_fs(
    mock_abspath, 
    mock_get_structured_output, 
    setup_main_flow_fs, # This normally creates the backlog file
    fs, # pyfakefs fixture to manipulate files
    monkeypatch, 
    caplog
):
    mock_config_abspath.return_value = os.path.join(PROJECT_ROOT_FS, 'src', 'config.py')
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key_main_flow")
    # The conftest.py autouse fixture for load_dotenv should cover this.
    # If not, add @patch('src.config.load_dotenv') to this test as well.

    # Remove the backlog file that setup_main_flow_fs created
    backlog_path_to_remove = setup_main_flow_fs['backlog_file_path']
    if fs.exists(backlog_path_to_remove):
        fs.remove_object(backlog_path_to_remove)
    
    # AppConfig validation for backlog_file_path checks if it's a file.
    # This test will check if BacklogProcessor correctly handles the error
    # if the file is removed *after* AppConfig validation but *before* BacklogProcessor reads it.
    # However, AppConfig's current validate() checks os.path.isfile(self.backlog_file_path).
    # So, if fs is manipulated, AppConfig init itself should fail.

    # Let's adjust the test: AppConfig passes validation (file exists),
    # but then the file is removed before BacklogProcessor.process_backlog_file.
    # This requires a more sophisticated patch or ensuring AppConfig validates against one state
    # and BacklogProcessor runs against another.
    # For simplicity, let's test the scenario where AppConfig itself flags the missing file.
    # This means setup_main_flow_fs should NOT create the backlog file for this test.
    
    # Re-setup config.yaml without the backlog file being created by setup_main_flow_fs
    # This is tricky because the fixture is already run.
    # Alternative: Test the "Backlog file not found: {backlog_filepath}" log from BacklogProcessor
    # by ensuring AppConfig validation *passes* but the file is gone when BacklogProcessor runs.

    # The simplest way is to make AppConfig validation pass for the file's existence,
    # then have process_backlog_file fail.
    # This means we need to patch os.path.isfile for AppConfig's validation scope.
    
    with patch('src.config.os.path.isfile') as mock_config_isfile:
        mock_config_isfile.return_value = True # Fool AppConfig validation that backlog file exists

        await main_run() # main.run() will instantiate AppConfig, then BacklogProcessor

    # Now, BacklogProcessor.process_backlog_file should try to open the (actually missing) file.
    assert f"Backlog file not found: {backlog_path_to_remove}" in caplog.text
    mock_get_structured_output.assert_not_called() # Should not get to LLM calls
    assert "PoC 8 processing finished." in caplog.text # main.run might finish if error is handled in BacklogProcessor
                                                      # Current BacklogProcessor logs error and returns.
                                                      # So, main flow might complete.
                                                      
# The test `test_main_run_backlog_file_not_found_in_fs` highlights a dependency on when AppConfig
# validates the backlog file. If it's at init, then main.run() would fail earlier.
# The current AppConfig does validate this at init. So, if the file is missing,
# AppConfig raises ValueError, and main.run() logs this and exits.
# The log "Backlog file not found" from BacklogProcessor wouldn't be reached.
# So, the previous test needs rethinking based on AppConfig's strictness.

# Corrected test for AppConfig failing due to missing backlog file:
@pytest.mark.asyncio
@patch('src.config.load_dotenv') # Explicitly patch load_dotenv
@patch('src.config.os.path.abspath')
async def test_main_run_appconfig_fails_backlog_missing(
    mock_load_dotenv_explicit, # Injected by @patch
    mock_config_abspath, 
    setup_main_flow_fs, # This fixture normally creates the backlog file
    fs, # To remove the file
    monkeypatch, 
    caplog
):
    mock_config_abspath.return_value = os.path.join(PROJECT_ROOT_FS, 'src', 'config.py')
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key_main_flow")
    # mock_load_dotenv_explicit (from decorator) handles preventing real load_dotenv

    # Remove the backlog file that setup_main_flow_fs created, so AppConfig validation fails
    backlog_path_to_remove = setup_main_flow_fs['backlog_file_path']
    if fs.exists(backlog_path_to_remove):
        fs.remove_object(backlog_path_to_remove)

    await main_run()

    assert f"backlog_file_path '{backlog_path_to_remove}' (from config.yaml) does not exist or is not a file." in caplog.text
    assert "PoC 8 processing finished." not in caplog.text # Should exit early due to AppConfig error.
