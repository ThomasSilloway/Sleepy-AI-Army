import unittest
from unittest.mock import patch, MagicMock, mock_open
import subprocess

from src.services.aider_service import AiderService, AiderExecutionResult
from src.config import AppConfig

class TestAiderService(unittest.TestCase):

    def setUp(self):
        self.mock_app_config = MagicMock(spec=AppConfig)
        # Set any specific attributes on mock_app_config if AiderService uses them directly
        # e.g., self.mock_app_config.aider_command = "aider"
        self.aider_service = AiderService(app_config=self.mock_app_config)

    @patch('subprocess.Popen')
    def test_execute_successful(self, mock_popen):
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout.readline.side_effect = ["output line 1", "output line 2", ""]
        mock_process.stderr.readline.side_effect = ["", ""] # No error
        mock_process.wait.return_value = 0 # Simulate exit code from process.wait()
        mock_popen.return_value = mock_process

        command_args = ["--version"]
        result = self.aider_service.execute(command_args=command_args)

        expected_stdout = "output line 1\noutput line 2"
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, expected_stdout)
        self.assertEqual(result.stderr, "")
        mock_popen.assert_called_once()
        # Check that the command includes --yes-always
        called_command = mock_popen.call_args[0][0]
        self.assertIn("--yes-always", called_command)


    @patch('subprocess.Popen')
    def test_execute_aider_error(self, mock_popen):
        mock_process = MagicMock()
        mock_process.returncode = 1 # Aider exits with an error
        mock_process.stdout.readline.side_effect = ["some output", ""]
        mock_process.stderr.readline.side_effect = ["error line 1", "error line 2", ""]
        mock_process.wait.return_value = 1
        mock_popen.return_value = mock_process

        command_args = ["--unknown-arg"]
        result = self.aider_service.execute(command_args=command_args)

        expected_stdout = "some output"
        expected_stderr = "error line 1\nerror line 2"
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.stdout, expected_stdout)
        self.assertEqual(result.stderr, expected_stderr)

    @patch('subprocess.Popen')
    def test_execute_file_not_found(self, mock_popen):
        mock_popen.side_effect = FileNotFoundError("aider command not found")

        command_args = ["--version"]
        result = self.aider_service.execute(command_args=command_args)

        self.assertEqual(result.exit_code, -1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Error: 'aider' command not found", result.stderr)

    @patch('subprocess.Popen')
    def test_execute_general_popen_exception(self, mock_popen):
        mock_popen.side_effect = OSError("Some OS error") # Example of another Popen exception

        command_args = ["--version"]
        result = self.aider_service.execute(command_args=command_args)

        self.assertEqual(result.exit_code, -1)
        self.assertEqual(result.stdout, "")
        self.assertIn("An unexpected error occurred while executing aider: Some OS error", result.stderr)

    @patch('subprocess.Popen')
    def test_execute_with_files_to_add(self, mock_popen):
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout.readline.side_effect = ["output", ""]
        mock_process.stderr.readline.side_effect = ["", ""]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        command_args = ["--message", "Test commit"]
        files_to_add = ["file1.py", "path/to/file2.txt"]
        
        self.aider_service.execute(command_args=command_args, files_to_add=files_to_add)

        mock_popen.assert_called_once()
        called_command = mock_popen.call_args[0][0]
        
        # Expected command structure: ["aider", "file1.py", "path/to/file2.txt", "--message", "Test commit", "--yes-always"]
        expected_initial_part = ["aider"] + files_to_add
        self.assertTrue(called_command[:len(expected_initial_part)] == expected_initial_part)
        self.assertIn("--message", called_command)
        self.assertIn("Test commit", called_command)
        self.assertIn("--yes-always", called_command)


if __name__ == '__main__':
    unittest.main()
