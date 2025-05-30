import pytest
import os
import re
import logging # Added import
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.backlog_processor import BacklogProcessor
from src.services.llm_prompt_service import LlmPromptService
from src.config import AppConfig
from src.models.goal_models import SanitizedGoalInfo

# Base path for pyfakefs, simulating the project root
PROJECT_ROOT_FS = '/app'
DEFAULT_OUTPUT_DIR_FS = os.path.join(PROJECT_ROOT_FS, 'ai_goals_output')
DEFAULT_BACKLOG_PATH_FS = os.path.join(PROJECT_ROOT_FS, 'TEST_BACKLOG.md')


@pytest.fixture
def mock_app_config_for_processor(fs): # fs fixture from pyfakefs
    """Provides a mock AppConfig suitable for BacklogProcessor tests."""
    # Create fake directories and files needed by AppConfig validation
    # AppConfig expects goal_git_path to be a dir and backlog_file_path to be a file.
    # For these tests, we'll use paths within the fake FS.
    
    fake_git_repo_path = os.path.join(PROJECT_ROOT_FS, "fake_repo")
    fs.create_dir(fake_git_repo_path)
    
    # Ensure the config.yaml path calculation within AppConfig resolves correctly.
    # AppConfig's __init__ calculates base_dir for config.yaml.
    # We need to make sure that when AppConfig is instantiated, it finds a mock config.yaml
    # or that its attributes are directly set.

    mock_config = MagicMock(spec=AppConfig)
    mock_config.gemini_api_key = "fake_processor_api_key" # Needed by LLM service if not mocked out
    mock_config.goal_git_path = fake_git_repo_path
    mock_config.backlog_file_name = "TEST_BACKLOG.md" # Will be joined with goal_git_path
    mock_config.ai_goals_directory_name = "ai_goals_output" # Will be joined with goal_git_path
    
    # Derived properties
    mock_config.backlog_file_path = os.path.join(mock_config.goal_git_path, mock_config.backlog_file_name)
    mock_config.goals_output_directory = os.path.join(mock_config.goal_git_path, mock_config.ai_goals_directory_name)

    # For default_llm_model_name (Aspect 3 of spec)
    # Assuming AppConfig is updated to have this attribute
    mock_config.default_llm_model_name = "gemini-test-model"

    # Do not create the backlog file here; let individual tests create it if needed.
    # This allows tests to define specific content or test missing file scenarios.
    # fs.create_file(mock_config.backlog_file_path, contents="Initial backlog content for AppConfig validation.")
    
    return mock_config


@pytest.fixture
def mock_llm_service():
    """Provides a mock LlmPromptService."""
    mock_service = MagicMock(spec=LlmPromptService)
    # Configure common mock behaviors here if needed, or in specific tests
    mock_service.get_structured_output = AsyncMock()
    return mock_service


@pytest.fixture
def backlog_processor(mock_llm_service, mock_app_config_for_processor, fs):
    """Fixture to create a BacklogProcessor instance with mocked dependencies."""
    # output_dir for BacklogProcessor will be derived from mock_app_config_for_processor.goals_output_directory
    # Ensure this directory exists in the fake filesystem if BacklogProcessor expects to write to it.
    # BacklogProcessor's __init__ creates output_dir if it doesn't exist.
    processor_output_dir = mock_app_config_for_processor.goals_output_directory
    
    return BacklogProcessor(
        llm_service=mock_llm_service,
        output_dir=processor_output_dir, # This path will be used by processor
        app_config=mock_app_config_for_processor
    )


# --- Tests for parse_task_from_section ---
def test_parse_task_from_section_valid(backlog_processor):
    section = "## Task Title\nThis is the description.\nMore description."
    title, description = backlog_processor.parse_task_from_section(section)
    assert title == "Task Title"
    assert description == "This is the description.\nMore description."

def test_parse_task_from_section_no_description(backlog_processor):
    section = "## Task Title Only"
    title, description = backlog_processor.parse_task_from_section(section)
    assert title == "Task Title Only"
    assert description == ""

def test_parse_task_from_section_no_title_marker(backlog_processor):
    section = "Not a task title\nDescription."
    assert backlog_processor.parse_task_from_section(section) is None

def test_parse_task_from_section_empty(backlog_processor):
    assert backlog_processor.parse_task_from_section("") is None
    assert backlog_processor.parse_task_from_section("  \n  ") is None


# --- Tests for sanitize_title_with_llm ---
@pytest.mark.asyncio
async def test_sanitize_title_with_llm_success(backlog_processor, mock_llm_service):
    mock_llm_service.get_structured_output.return_value = SanitizedGoalInfo(folder_name="llm-generated-folder-name")
    
    folder_name = await backlog_processor.sanitize_title_with_llm("Task description", "Task Title")
    
    assert folder_name == "llm-generated-folder-name"
    mock_llm_service.get_structured_output.assert_called_once()
    call_args = mock_llm_service.get_structured_output.call_args
        passed_type = call_args[1]['output_pydantic_model_type']
        assert passed_type.__name__ == SanitizedGoalInfo.__name__
        assert passed_type.__module__ == SanitizedGoalInfo.__module__


@pytest.mark.asyncio
async def test_sanitize_title_with_llm_failure_fallback(backlog_processor, mock_llm_service):
    mock_llm_service.get_structured_output.return_value = None # Simulate LLM failure
    
    task_title = "My Complex: Task Title!"
    folder_name = await backlog_processor.sanitize_title_with_llm("Description", task_title)
    
    assert "my-complex-task-title" in folder_name # Basic sanitization part
    assert re.search(r"_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{3}", folder_name), \
        f"Timestamp pattern not found in '{folder_name}'"


@pytest.mark.asyncio
async def test_sanitize_title_with_llm_empty_title_fallback(backlog_processor, mock_llm_service):
    mock_llm_service.get_structured_output.return_value = None
    
    folder_name = await backlog_processor.sanitize_title_with_llm("Description for untitled task", "")
    
    assert "untitled-task" in folder_name
    assert re.search(r"_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{3}", folder_name), \
        f"Timestamp pattern not found in '{folder_name}'"


# --- Tests for process_backlog_file ---
@pytest.mark.asyncio
async def test_process_backlog_file_success(backlog_processor, mock_llm_service, mock_app_config_for_processor, fs):
    backlog_content = """
## Task One
Description for task one.

## Task Two: Special Chars
Description with 'special' characters.
    """
    # Use the backlog_file_path from the mock_app_config_for_processor for consistency
    test_backlog_filepath = mock_app_config_for_processor.backlog_file_path
    fs.create_file(test_backlog_filepath, contents=backlog_content)

    # Mock LLM responses for each task
    mock_llm_service.get_structured_output.side_effect = [
        SanitizedGoalInfo(folder_name="task-one-folder"),
        SanitizedGoalInfo(folder_name="task-two-special-chars-folder")
    ]
    
    processor_output_dir = mock_app_config_for_processor.goals_output_directory

    await backlog_processor.process_backlog_file(test_backlog_filepath)

    # Verify folder and file creation
    assert fs.exists(processor_output_dir)
    
    task_one_folder = os.path.join(processor_output_dir, "task-one-folder")
    assert fs.exists(task_one_folder)
    assert fs.exists(os.path.join(task_one_folder, "task-description.md"))
    with open(os.path.join(task_one_folder, "task-description.md"), 'r') as f:
        assert f.read() == "Description for task one."

    task_two_folder = os.path.join(processor_output_dir, "task-two-special-chars-folder")
    assert fs.exists(task_two_folder)
    assert fs.exists(os.path.join(task_two_folder, "task-description.md"))
    with open(os.path.join(task_two_folder, "task-description.md"), 'r') as f:
        assert f.read() == "Description with 'special' characters."
    
    assert mock_llm_service.get_structured_output.call_count == 2


@pytest.mark.asyncio
async def test_process_backlog_file_not_found(backlog_processor, mock_app_config_for_processor, caplog, fs):
    # Ensure the configured backlog file does not exist in the fake FS
    non_existent_backlog_path = mock_app_config_for_processor.backlog_file_path
    if fs.exists(non_existent_backlog_path):
        fs.remove_object(non_existent_backlog_path)

    with caplog.at_level(logging.ERROR): # BacklogProcessor logs this as ERROR
        await backlog_processor.process_backlog_file(non_existent_backlog_path)
    
    assert f"Backlog file not found: {non_existent_backlog_path}" in caplog.text
    # Verify no output directory was created if it didn't exist
    # BacklogProcessor's __init__ creates self.output_dir.
    # This test focuses on process_backlog_file's behavior given a missing file.
    # So, we check that no task folders were made inside the pre-existing output_dir.
    assert len(fs.listdir(backlog_processor.output_dir)) == 0


@pytest.mark.asyncio
async def test_process_backlog_file_empty_or_no_tasks(backlog_processor, mock_llm_service, mock_app_config_for_processor, fs, caplog):
    test_backlog_filepath = mock_app_config_for_processor.backlog_file_path
    fs.create_file(test_backlog_filepath, contents="Just some text, no tasks.")
    
    with caplog.at_level(logging.INFO): # BacklogProcessor logs this as INFO
        await backlog_processor.process_backlog_file(test_backlog_filepath)
    
    mock_llm_service.get_structured_output.assert_not_called()
    assert "No tasks were processed" in caplog.text
    assert len(fs.listdir(backlog_processor.output_dir)) == 0


@pytest.mark.asyncio
async def test_process_backlog_file_llm_fails_for_a_task(backlog_processor, mock_llm_service, mock_app_config_for_processor, fs):
    backlog_content = "## Task With LLM Fail\nDescription."
    test_backlog_filepath = mock_app_config_for_processor.backlog_file_path
    fs.create_file(test_backlog_filepath, contents=backlog_content)

    mock_llm_service.get_structured_output.return_value = None # LLM fails

    await backlog_processor.process_backlog_file(test_backlog_filepath)
    
    # Check that a fallback folder was created
    # List contents of output_dir, expect one folder with timestamp pattern
    created_folders = fs.listdir(backlog_processor.output_dir)
    assert len(created_folders) == 1
    fallback_folder_name = created_folders[0]
    assert "task-with-llm-fail" in fallback_folder_name # basic sanitization part
    assert re.search(r"_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{3}", fallback_folder_name)
    
    task_folder_path = os.path.join(backlog_processor.output_dir, fallback_folder_name)
    assert fs.exists(os.path.join(task_folder_path, "task-description.md"))


@pytest.mark.asyncio
async def test_process_backlog_malformed_section_skip(backlog_processor, mock_llm_service, mock_app_config_for_processor, fs, caplog):
    backlog_content = """
Not a task section.
## Valid Task
Description for valid task.
    """
    test_backlog_filepath = mock_app_config_for_processor.backlog_file_path
    fs.create_file(test_backlog_filepath, contents=backlog_content)
    
    mock_llm_service.get_structured_output.return_value = SanitizedGoalInfo(folder_name="valid-task-folder")

    with caplog.at_level(logging.DEBUG): # BacklogProcessor logs this as DEBUG
        await backlog_processor.process_backlog_file(test_backlog_filepath)

    # Check for specific DEBUG log. Or set to INFO if the "Skipping" log is more important.
    # The "Skipping section not starting with '## '" is logged at DEBUG level.
    # If we want to assert this, caplog needs to be at DEBUG.
    # If we only care about higher level logs like "No tasks processed" or "Successfully processed",
    # then INFO is fine. Let's assume the DEBUG log is what we want to check here.
    assert "Skipping section not starting with '## '" in caplog.text
    # Also check that the valid task was processed
    assert fs.exists(os.path.join(backlog_processor.output_dir, "valid-task-folder"))
    assert mock_llm_service.get_structured_output.call_count == 1 # Only called for the valid task


@pytest.mark.asyncio
async def test_backlog_processor_creates_output_dir_if_not_exists(mock_llm_service, mock_app_config_for_processor, fs):
    """
    Tests that BacklogProcessor's __init__ creates the output directory
    if it doesn't exist.
    """
    output_dir_path = mock_app_config_for_processor.goals_output_directory
    # Ensure the directory does not exist initially
    if fs.exists(output_dir_path):
        fs.rmdir(output_dir_path) # rmdir for empty dir, or use fs.remove_object for recursive
    
    assert not fs.exists(output_dir_path)
    
    # Instantiate the processor
    BacklogProcessor(
        llm_service=mock_llm_service,
        output_dir=output_dir_path,
        app_config=mock_app_config_for_processor
    )
    
    assert fs.exists(output_dir_path)
    assert fs.isdir(output_dir_path)

# TODO from spec: "In process_backlog_file, if parse_task_from_section returns None
# (due to malformed section), collect these instances (e.g., line number or first 50 chars of section)
# in a list. After processing, if this list is not empty, log a summary of parsing issues."
# This requires modifying BacklogProcessor. For now, the test `test_process_backlog_malformed_section_skip`
# checks that malformed sections are skipped and logged individually. A summary log would be an enhancement.
