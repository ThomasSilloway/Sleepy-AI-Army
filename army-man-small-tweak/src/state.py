"""TypedDict definition for the workflow's dynamic state."""
from typing import Optional, TypedDict

from src.pydantic_models.core_schemas import ManifestData


class WorkflowState(TypedDict):
    current_step_name: Optional[str]

    goal_folder_path: Optional[str]  
    workspace_folder_path: Optional[str]  

    # These are all absolute paths
    task_description_path: Optional[str]
    task_description_content: Optional[str]

    manifest_template_path: Optional[str]

    manifest_output_path: Optional[str]
    changelog_output_path: Optional[str]

    last_event_summary: Optional[str]
    aider_last_exit_code: Optional[int]
    error_message: Optional[str]

    is_manifest_generated: bool
    is_changelog_entry_added: bool

    # Fields for "Small Tweak" execution
    is_code_change_committed: bool
    last_change_commit_hash: Optional[str]
    last_change_commit_summary: Optional[str]
    # Add other state fields as they become necessary

    small_tweak_file_path: Optional[str]  # Path to the file to be tweaked

    # Data for goal-manifest.md, managed by manifest_create and manifest_update nodes
    manifest_data: Optional[ManifestData]
