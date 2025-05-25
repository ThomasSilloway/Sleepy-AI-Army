import unittest
from unittest.mock import MagicMock, patch
import tempfile
import os
from pathlib import Path
import re
from datetime import datetime

from src.state import WorkflowState
from src.nodes.manifest_update import manifest_update_node
# Assuming AppConfig and ChangelogService might be imported by the node or its dependencies,
# though not directly used in the provided snippet for manifest_update_node.
# from src.config import AppConfig 
# from src.services.changelog_service import ChangelogService

# Helper content as provided in the task
initial_manifest_content = """# Document character_controller_ai.gd
Document the `projects/isometric_2d_prototype/isometric_2d_prototype/character_controller/character_controller_ai.gd` file

Last Updated: 2025-05-23 02:35 PM

## Overall Status
New

## Current Focus
Document the `projects/isometric_2d_prototype/isometric_2d_prototype/character_controller/character_controller_ai.gd` file

## Artifacts
* [in-progress] projects/isometric_2d_prototype/isometric_2d_prototype/character_controller/character_controller_ai.gd

## AI Questions for User
NONE

## Human Responses
NONE
"""
small_tweak_file_path_for_test = "projects/isometric_2d_prototype/isometric_2d_prototype/character_controller/character_controller_ai.gd"

class TestManifestUpdateNode(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_path = Path(self.temp_dir.name)
        
        self.mock_app_config = MagicMock()
        # Mock ChangelogService
        self.mock_changelog_service = MagicMock()
        self.mock_changelog_service.record_event_in_changelog.return_value = True # Default to success

        self.config = {
            "configurable": {
                "app_config": self.mock_app_config,
                "changelog_service": self.mock_changelog_service,
            }
        }
        
        # Prepare a manifest file
        self.manifest_file_path = self.temp_dir_path / "goal-manifest.md"
        with open(self.manifest_file_path, "w", encoding="utf-8") as f:
            f.write(initial_manifest_content)

    def tearDown(self):
        self.temp_dir.cleanup()

    def read_manifest_file(self) -> str:
        with open(self.manifest_file_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_manifest_update_success_no_prior_error(self):
        initial_state = WorkflowState(
            task_description_content="Some task description",
            manifest_output_path=str(self.manifest_file_path),
            small_tweak_file_path=small_tweak_file_path_for_test,
            error_message=None, # No prior error
            current_step_name="Previous Step"
        )

        updated_state = manifest_update_node(initial_state, self.config)
        manifest_content = self.read_manifest_file()

        # Check manifest content
        self.assertIn("Overall Status: Complete", manifest_content)
        expected_artifact_line = f"* [Complete] {small_tweak_file_path_for_test}"
        self.assertTrue(
            any(expected_artifact_line in line for line in manifest_content.splitlines()),
            f"Expected artifact line '{expected_artifact_line}' not found or not correct."
        )
        self.assertIn("AI Questions for User:\nNONE", manifest_content)
        
        # Check timestamp (hard to check exact value, but check it changed from original)
        self.assertNotIn("Last Updated: 2025-05-23 02:35 PM", manifest_content)
        # Check that the new timestamp has the current year and a valid format
        current_year = str(datetime.now().year)
        self.assertTrue(re.search(rf"Last Updated: {current_year}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}} (?:AM|PM)", manifest_content))


        # Check state
        self.assertIsNone(updated_state.get("error_message"))
        self.assertEqual(updated_state.get("current_step_name"), "Update Manifest")
        self.assertIn("Goal Manifest updated and changelog entry added.", updated_state.get("last_event_summary", ""))

        # Check changelog service call
        self.mock_changelog_service.record_event_in_changelog.assert_called_once()
        call_args = self.mock_changelog_service.record_event_in_changelog.call_args[0]
        self.assertEqual(call_args[0], updated_state) # current_workflow_state
        self.assertEqual(call_args[1], "Goal Manifest Updated") # preceding_event_summary

    def test_manifest_update_with_prior_error(self):
        prior_error = "Tweak failed due to syntax error"
        initial_state = WorkflowState(
            task_description_content="Some task description",
            manifest_output_path=str(self.manifest_file_path),
            small_tweak_file_path=small_tweak_file_path_for_test,
            error_message=prior_error, # Prior error
            current_step_name="Execute Small Tweak"
        )

        updated_state = manifest_update_node(initial_state, self.config)
        manifest_content = self.read_manifest_file()

        # Check manifest content
        self.assertIn("Overall Status: Error in Execution", manifest_content)
        
        # The logic in manifest_update_node sets artifact to [in-progress] if there was a prior error.
        expected_artifact_line = f"* [in-progress] {small_tweak_file_path_for_test}"
        self.assertTrue(
            any(expected_artifact_line in line for line in manifest_content.splitlines()),
             f"Expected artifact line '{expected_artifact_line}' not found or not correct."
        )
        
        expected_ai_question = f"AI Questions for User:\nError occurred during the automated task, can you review it please?\n\nError details:\n{prior_error}"
        self.assertIn(expected_ai_question, manifest_content)
        
        self.assertNotIn("Last Updated: 2025-05-23 02:35 PM", manifest_content)
        current_year = str(datetime.now().year)
        self.assertTrue(re.search(rf"Last Updated: {current_year}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}} (?:AM|PM)", manifest_content))

        # Check state
        self.assertEqual(updated_state.get("error_message"), prior_error) # Original error should persist
        self.assertEqual(updated_state.get("current_step_name"), "Update Manifest")
        self.assertIn("Goal Manifest updated and changelog entry added.", updated_state.get("last_event_summary", ""))

        # Check changelog service call
        self.mock_changelog_service.record_event_in_changelog.assert_called_once()
        call_args = self.mock_changelog_service.record_event_in_changelog.call_args[0]
        self.assertEqual(call_args[0], updated_state)
        expected_changelog_summary = f"Goal Manifest Updated (with error in previous step: {prior_error.splitlines()[0]})"
        self.assertEqual(call_args[1], expected_changelog_summary)

    def test_manifest_update_file_not_found(self):
        non_existent_manifest_path = str(self.temp_dir_path / "non_existent_manifest.md")
        initial_state = WorkflowState(
            task_description_content="Some task description",
            manifest_output_path=non_existent_manifest_path, # Path to non-existent file
            small_tweak_file_path=small_tweak_file_path_for_test,
            error_message=None,
            current_step_name="Previous Step"
        )

        updated_state = manifest_update_node(initial_state, self.config)

        # Check state
        self.assertIsNotNone(updated_state.get("error_message"))
        self.assertIn(f"[ManifestUpdate] Manifest file not found at {non_existent_manifest_path}", updated_state.get("error_message", ""))
        self.assertEqual(updated_state.get("last_event_summary"), "Error: Manifest file not found for update.")
        self.assertEqual(updated_state.get("current_step_name"), "Update Manifest")


        # Check changelog service call - should not be called
        self.mock_changelog_service.record_event_in_changelog.assert_not_called()

    def test_manifest_update_changelog_fails_on_return_false(self):
        self.mock_changelog_service.record_event_in_changelog.return_value = False # Simulate changelog failure
        
        initial_state = WorkflowState(
            task_description_content="Some task description",
            manifest_output_path=str(self.manifest_file_path),
            small_tweak_file_path=small_tweak_file_path_for_test,
            error_message=None,
            current_step_name="Previous Step"
        )

        updated_state = manifest_update_node(initial_state, self.config)
        manifest_content = self.read_manifest_file()

        # Check manifest content (should be updated successfully)
        self.assertIn("Overall Status: Complete", manifest_content)
        expected_artifact_line = f"* [Complete] {small_tweak_file_path_for_test}"
        self.assertTrue(
            any(expected_artifact_line in line for line in manifest_content.splitlines()),
            f"Expected artifact line '{expected_artifact_line}' not found or not correct."
        )
        self.assertNotIn("Last Updated: 2025-05-23 02:35 PM", manifest_content)

        # Check state for changelog error
        self.assertIsNotNone(updated_state.get("error_message"))
        self.assertIn("[ManifestUpdate][ChangelogError] ChangelogService failed to record manifest update event.", updated_state.get("error_message", ""))
        self.assertEqual(updated_state.get("last_event_summary"), "Goal Manifest updated, but changelog recording failed.")
        self.assertEqual(updated_state.get("current_step_name"), "Update Manifest")


        # Check changelog service call
        self.mock_changelog_service.record_event_in_changelog.assert_called_once()

    def test_manifest_update_changelog_fails_on_exception(self):
        self.mock_changelog_service.record_event_in_changelog.side_effect = Exception("DB connection error") # Simulate changelog exception
        
        initial_state = WorkflowState(
            task_description_content="Some task description",
            manifest_output_path=str(self.manifest_file_path),
            small_tweak_file_path=small_tweak_file_path_for_test,
            error_message=None,
            current_step_name="Previous Step"
        )

        updated_state = manifest_update_node(initial_state, self.config)
        manifest_content = self.read_manifest_file()

        # Check manifest content (should be updated successfully)
        self.assertIn("Overall Status: Complete", manifest_content)
        expected_artifact_line = f"* [Complete] {small_tweak_file_path_for_test}"
        self.assertTrue(
            any(expected_artifact_line in line for line in manifest_content.splitlines()),
            f"Expected artifact line '{expected_artifact_line}' not found or not correct."
        )
        self.assertNotIn("Last Updated: 2025-05-23 02:35 PM", manifest_content)

        # Check state for changelog error
        self.assertIsNotNone(updated_state.get("error_message"))
        self.assertIn("[ManifestUpdate][ChangelogError] Exception during changelog service call for manifest update: DB connection error", updated_state.get("error_message", ""))
        self.assertEqual(updated_state.get("last_event_summary"), "Goal Manifest updated, but changelog recording failed with an exception.")
        self.assertEqual(updated_state.get("current_step_name"), "Update Manifest")

        # Check changelog service call
        self.mock_changelog_service.record_event_in_changelog.assert_called_once()

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


