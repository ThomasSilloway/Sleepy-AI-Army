import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import tempfile
import asyncio # Required for @patch('asyncio.run') to work correctly with return_value

from src.state import WorkflowState
from src.config import AppConfig
from src.services.aider_service import AiderService, AiderExecutionResult
from src.services.llm_prompt_service import LlmPromptService
from src.services.changelog_service import ChangelogService
from src.services.git_service import GitService # Though not directly used, it's part of config
from src.models.aider_summary import AiderRunSummary
from src.nodes.small_tweak_execution import execute_small_tweak_node, LLM_MODEL_FOR_SUMMARY

class TestExecuteSmallTweakNode(unittest.TestCase):

    def setUp(self):
        self.state = WorkflowState()
        
        # Create a temporary file for task_description_path
        self.temp_task_desc_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
        self.temp_task_desc_file.write("Test task description.")
        self.temp_task_desc_file.close()
        self.state['task_description_path'] = self.temp_task_desc_file.name

        self.mock_app_config = MagicMock(spec=AppConfig)
        self.mock_app_config.aider_code_model = "test-aider-model"
        # Add other AppConfig attributes if the node uses them directly

        self.mock_aider_service = MagicMock(spec=AiderService)
        self.mock_llm_prompt_service = MagicMock(spec=LlmPromptService)
        self.mock_changelog_service = MagicMock(spec=ChangelogService)
        self.mock_git_service = MagicMock(spec=GitService) # Not directly used by new logic but part of config

        self.config = {
            "configurable": {
                "app_config": self.mock_app_config,
                "aider_service": self.mock_aider_service,
                "llm_prompt_service": self.mock_llm_prompt_service,
                "changelog_service": self.mock_changelog_service,
                "git_service": self.mock_git_service,
            }
        }
        # Reset state fields that the node modifies
        self.state['aider_last_exit_code'] = None
        self.state['last_change_commit_hash'] = None
        self.state['last_change_commit_summary'] = None
        self.state['is_code_change_committed'] = False
        self.state['error_message'] = None
        self.state['last_event_summary'] = None
        self.state['aider_run_summary'] = None
        self.state['is_changelog_entry_added'] = None


    def tearDown(self):
        os.unlink(self.temp_task_desc_file.name)

    @patch('asyncio.run')
    def test_scenario1_aider_success_llm_success_with_commit(self, mock_asyncio_run):
        # Aider success
        mock_aider_result = AiderExecutionResult(exit_code=0, stdout="Aider ran fine.", stderr="")
        self.mock_aider_service.execute.return_value = mock_aider_result

        # LLM summary success with commit
        mock_llm_summary = AiderRunSummary(
            changes_made=["Added function X", "Modified file Y"],
            commit_hash="testcommithash123",
            files_modified=["file_a.py", "file_b.py"],
            files_created=[],
            errors_reported=[],
            raw_output_summary="Aider made changes and committed.",
            commit_message="feat: Implement X and Y"
        )
        mock_asyncio_run.return_value = mock_llm_summary
        self.mock_changelog_service.record_event_in_changelog.return_value = True


        updated_state = execute_small_tweak_node(self.state, self.config)

        self.assertEqual(updated_state['aider_last_exit_code'], 0)
        self.assertTrue(updated_state['is_code_change_committed'])
        self.assertEqual(updated_state['last_change_commit_hash'], "testcommithash123")
        self.assertEqual(updated_state['last_change_commit_summary'], "feat: Implement X and Y")
        self.assertIn("Small Tweak applied. Commit: testcommithash123", updated_state['last_event_summary'])
        self.assertIn("Added function X", updated_state['last_event_summary'])
        self.assertIsNone(updated_state['error_message'])
        self.assertIsNotNone(updated_state['aider_run_summary'])
        self.assertTrue(updated_state['is_changelog_entry_added'])
        self.mock_changelog_service.record_event_in_changelog.assert_called_once()
        # Check that llm_prompt_service.get_structured_output was called via asyncio.run
        self.assertEqual(mock_asyncio_run.call_args[0][0].__qualname__, 'LlmPromptService.get_structured_output')


    @patch('asyncio.run')
    def test_scenario2_aider_success_llm_success_no_commit(self, mock_asyncio_run):
        mock_aider_result = AiderExecutionResult(exit_code=0, stdout="Aider ran fine, no commit.", stderr="")
        self.mock_aider_service.execute.return_value = mock_aider_result

        mock_llm_summary = AiderRunSummary(
            changes_made=["Fixed a typo"],
            commit_hash=None, # No commit
            files_modified=["docs.md"],
            raw_output_summary="Aider fixed a typo, did not commit."
        )
        mock_asyncio_run.return_value = mock_llm_summary
        self.mock_changelog_service.record_event_in_changelog.return_value = True

        updated_state = execute_small_tweak_node(self.state, self.config)

        self.assertEqual(updated_state['aider_last_exit_code'], 0)
        self.assertFalse(updated_state['is_code_change_committed'])
        self.assertIsNone(updated_state['last_change_commit_hash'])
        self.assertEqual(updated_state['last_change_commit_summary'], "Commit message not extracted.") # Default when no commit_message
        self.assertIn("Small Tweak applied. Commit: N/A", updated_state['last_event_summary'])
        self.assertIn("Fixed a typo", updated_state['last_event_summary'])
        self.assertTrue(updated_state['is_changelog_entry_added'])
        self.mock_changelog_service.record_event_in_changelog.assert_called_once()

    @patch('asyncio.run')
    def test_scenario3_aider_success_llm_summary_failure(self, mock_asyncio_run):
        mock_aider_result = AiderExecutionResult(exit_code=0, stdout="Aider ran fine.", stderr="")
        self.mock_aider_service.execute.return_value = mock_aider_result

        mock_asyncio_run.return_value = None # LLM returns None

        updated_state = execute_small_tweak_node(self.state, self.config)

        self.assertEqual(updated_state['aider_last_exit_code'], 0)
        self.assertFalse(updated_state['is_code_change_committed'])
        self.assertIsNone(updated_state['last_change_commit_hash'])
        self.assertEqual(updated_state['last_change_commit_summary'], "Summary extraction failed.")
        self.assertIn("Aider ran successfully, but summary extraction failed.", updated_state['last_event_summary'])
        self.assertIsNone(updated_state['aider_run_summary'])
        self.assertFalse(updated_state['is_changelog_entry_added']) # Changelog skipped
        self.mock_changelog_service.record_event_in_changelog.assert_not_called()


    @patch('asyncio.run')
    def test_scenario4_aider_failure_non_zero_exit(self, mock_asyncio_run):
        mock_aider_result = AiderExecutionResult(exit_code=1, stdout="Something went wrong.", stderr="Aider error: Critical problem.")
        self.mock_aider_service.execute.return_value = mock_aider_result

        # LLM might still try to summarize the error
        mock_llm_summary = AiderRunSummary(
            errors_reported=["Critical problem."],
            raw_output_summary="Aider encountered a critical problem."
        )
        mock_asyncio_run.return_value = mock_llm_summary

        updated_state = execute_small_tweak_node(self.state, self.config)

        self.assertEqual(updated_state['aider_last_exit_code'], 1)
        self.assertFalse(updated_state['is_code_change_committed'])
        self.assertIsNotNone(updated_state['error_message'])
        self.assertIn("Failed to apply Small Tweak. Aider exit code: 1", updated_state['error_message'])
        self.assertIn("Critical problem.", updated_state['error_message'])
        self.assertIn("Aider exit code: 1", updated_state['last_event_summary'])
        self.assertFalse(updated_state['is_changelog_entry_added'])
        self.mock_changelog_service.record_event_in_changelog.assert_not_called()

    @patch('asyncio.run') # Still need to patch asyncio.run even if aider_service fails before LLM call
    def test_scenario5_aider_command_not_found(self, mock_asyncio_run):
        # Simulate AiderService returning a "file not found" result
        mock_aider_error_result = AiderExecutionResult(
            exit_code=-1, 
            stdout="", 
            stderr="Error: 'aider' command not found."
        )
        self.mock_aider_service.execute.return_value = mock_aider_error_result
        
        # LLM might be called with empty stdout/stderr, or might return a basic summary
        mock_llm_summary = AiderRunSummary(
            errors_reported=["Error: 'aider' command not found."],
            raw_output_summary="Aider command was not found."
        )
        mock_asyncio_run.return_value = mock_llm_summary


        updated_state = execute_small_tweak_node(self.state, self.config)

        self.assertEqual(updated_state['aider_last_exit_code'], -1)
        self.assertFalse(updated_state['is_code_change_committed'])
        self.assertIsNotNone(updated_state['error_message'])
        self.assertIn("Aider exit code: -1", updated_state['error_message'])
        # Check if the specific error from AiderExecutionResult.stderr got propagated
        # The node logic combines the exit code message with LLM summary or raw stderr.
        # Depending on what LLM returns, the message might vary.
        # Here, we assume LLM successfully reports the error from stderr.
        self.assertIn("Error: 'aider' command not found.", updated_state['error_message']) 
        self.assertIn("Aider exit code: -1", updated_state['last_event_summary'])
        self.assertFalse(updated_state['is_changelog_entry_added'])
        self.mock_changelog_service.record_event_in_changelog.assert_not_called()

    @patch('asyncio.run')
    def test_scenario6_llm_service_raises_exception(self, mock_asyncio_run):
        mock_aider_result = AiderExecutionResult(exit_code=0, stdout="Aider ran fine.", stderr="")
        self.mock_aider_service.execute.return_value = mock_aider_result

        mock_asyncio_run.side_effect = Exception("LLM API is down")

        updated_state = execute_small_tweak_node(self.state, self.config)

        self.assertEqual(updated_state['aider_last_exit_code'], 0) # Aider itself succeeded
        self.assertFalse(updated_state['is_code_change_committed']) # LLM failed, so we can't confirm commit
        self.assertIsNotNone(updated_state['error_message'])
        self.assertIn("Error during LLM summary extraction: Exception('LLM API is down')", updated_state['error_message'])
        self.assertIn("Aider execution completed, but summary extraction failed.", updated_state['last_event_summary'])
        self.assertIsNone(updated_state['aider_run_summary']) # LLM failed
        self.assertFalse(updated_state['is_changelog_entry_added']) # Changelog skipped
        self.mock_changelog_service.record_event_in_changelog.assert_not_called() # Or called with generic error

    def test_task_description_file_not_found(self):
        # Test case where task_description_path does not exist
        os.unlink(self.state['task_description_path']) # Delete the temp file

        updated_state = execute_small_tweak_node(self.state, self.config)

        self.assertFalse(updated_state['is_code_change_committed'])
        self.assertIsNotNone(updated_state['error_message'])
        self.assertTrue(updated_state['error_message'].startswith("[SmallTweakExecution] Task description file not found at:"))
        self.assertTrue(updated_state['last_event_summary'].startswith("Error: Task description file missing at"))
        self.mock_aider_service.execute.assert_not_called() # Aider should not be called
        self.mock_changelog_service.record_event_in_changelog.assert_not_called()

    def test_task_description_path_missing_in_state(self):
        # Test case where task_description_path is not in state
        del self.state['task_description_path']

        updated_state = execute_small_tweak_node(self.state, self.config)
        
        self.assertFalse(updated_state['is_code_change_committed'])
        self.assertIsNotNone(updated_state['error_message'])
        self.assertEqual(updated_state['error_message'], "[SmallTweakExecution] Critical information missing: task_description_path not found in state.")
        self.assertEqual(updated_state['last_event_summary'], "Error: Missing task_description_path for Small Tweak.")
        self.mock_aider_service.execute.assert_not_called()
        self.mock_changelog_service.record_event_in_changelog.assert_not_called()


if __name__ == '__main__':
    unittest.main()
