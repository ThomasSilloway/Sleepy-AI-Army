# poc-8-backlog-to-goals/tests/test_backlog_processor.py
import pytest
import asyncio
import os
import shutil
import logging
from unittest.mock import AsyncMock, patch, call

from src.services.backlog_processor import BacklogProcessor
from src.services.llm_prompt_service import LlmPromptService # For type hinting mock
from src.models.goal_models import SanitizedGoalInfo
from src.config import AppConfig

@pytest.fixture
def temp_output_dir():
    test_dir = os.path.join(os.path.dirname(__file__), "temp_test_output_goals")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    yield test_dir
    # shutil.rmtree(test_dir) # Keep for inspection if needed

@pytest.fixture
def mock_app_config():
    config = AsyncMock(spec=AppConfig)
    config.gemini_api_key = "fake_test_key"
    config.default_llm_model_name = "gemini-test-model"
    return config

@pytest.fixture
def mock_llm_service(mock_app_config):
    service = AsyncMock(spec=LlmPromptService)
    async def get_structured_output_side_effect(messages, output_pydantic_model_type, llm_model_name):
        user_message_content = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message_content = msg.get("content", "")
                break
        title_match = user_message_content.split("Task Title (if available): '")[1].split("'")[0] if "Task Title" in user_message_content else "unknown-task"
        sanitized = title_match.lower().replace(" ", "-").replace(":", "")
        if output_pydantic_model_type == SanitizedGoalInfo:
            return SanitizedGoalInfo(folder_name=f"mock-{sanitized}")
        return None
    service.get_structured_output = AsyncMock(side_effect=get_structured_output_side_effect)
    return service

@pytest.fixture
def backlog_processor(mock_llm_service, temp_output_dir, mock_app_config):
    processor = BacklogProcessor(
        llm_service=mock_llm_service,
        output_dir=temp_output_dir,
        app_config=mock_app_config
    )
    return processor

@pytest.mark.asyncio
async def test_process_backlog_file_creates_structure_and_content(backlog_processor, mock_llm_service, temp_output_dir):
    sample_backlog_content = """
## Task One: Design API
Description for task one.
This involves OpenAPI specs.

## Task Two: Implement Database
Description for task two.
Using PostgreSQL.

## Invalid Task Section
This section should be skipped as it doesn't start with '## '.
"""
    temp_backlog_path = os.path.join(temp_output_dir, "test_backlog.md")
    with open(temp_backlog_path, "w", encoding="utf-8") as f:
        f.write(sample_backlog_content)

    await backlog_processor.process_backlog_file(temp_backlog_path)

    assert mock_llm_service.get_structured_output.call_count == 2
    
    call_args_task_one = mock_llm_service.get_structured_output.call_args_list[0]
    messages_task_one = call_args_task_one[1]['messages']
    assert "Task One: Design API" in messages_task_one[1]['content']
    assert call_args_task_one[1]['output_pydantic_model_type'] == SanitizedGoalInfo

    call_args_task_two = mock_llm_service.get_structured_output.call_args_list[1]
    messages_task_two = call_args_task_two[1]['messages']
    assert "Task Two: Implement Database" in messages_task_two[1]['content']
    assert call_args_task_two[1]['output_pydantic_model_type'] == SanitizedGoalInfo

    expected_folder_name_task_one = "mock-task-one-design-api"
    expected_folder_name_task_two = "mock-task-two-implement-database"

    task_one_folder = os.path.join(temp_output_dir, expected_folder_name_task_one)
    task_two_folder = os.path.join(temp_output_dir, expected_folder_name_task_two)

    assert os.path.isdir(task_one_folder)
    assert os.path.isdir(task_two_folder)

    task_one_desc_file = os.path.join(task_one_folder, "task-description.md")
    task_two_desc_file = os.path.join(task_two_folder, "task-description.md")

    assert os.path.isfile(task_one_desc_file)
    assert os.path.isfile(task_two_desc_file)

    with open(task_one_desc_file, "r", encoding="utf-8") as f:
        content_one = f.read()
    assert content_one == "Description for task one.\nThis involves OpenAPI specs."

    with open(task_two_desc_file, "r", encoding="utf-8") as f:
        content_two = f.read()
    assert content_two == "Description for task two.\nUsing PostgreSQL."
    
    all_items_in_output = os.listdir(temp_output_dir)
    expected_items = {expected_folder_name_task_one, expected_folder_name_task_two, "test_backlog.md"}
    assert set(all_items_in_output) == expected_items
    
    os.remove(temp_backlog_path)
```
