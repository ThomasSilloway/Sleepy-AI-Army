from typing import Optional, TypedDict

from pydantic import BaseModel, Field


class MissionContext(BaseModel):
    # Loaded from mission-spec.md
    mission_spec_content: Optional[str] = None 

    # Fields directly mapping to mission-report.md sections
    mission_title: Optional[str] = None
    original_branch_name: Optional[str] = None
    generated_branch_name: Optional[str] = None
    status: Optional[str] = None # IN_PROGRESS, SUCCESS, FAILURE, BLOCKED
    aider_changes_made: list[str] = Field(default_factory=list)
    aider_questions_asked: list[str] = Field(default_factory=list)
    files_modified: list[str] = Field(default_factory=list)
    files_created: list[str] = Field(default_factory=list)
    git_summary: list[str] = Field(default_factory=list) # list of "hash - message"
    total_cost_usd: float = 0.0
    report_timestamp: Optional[str] = None # Timestamp for the report generation
    aider_editable_files: list[str] = Field(default_factory=list)

    # Operational data & structured errors
    mission_errors: list[str] = Field(default_factory=list)

class WorkflowState(TypedDict):
    mission_context: MissionContext 
    current_step_name: Optional[str] # Name of the current/last executed node
    critical_error_message: Optional[str] # For immediate routing/critical failure
