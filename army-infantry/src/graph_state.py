from typing import Any, Optional, TypedDict

from pydantic import BaseModel, Field


class StructuredError(BaseModel):
    node_name: str
    message: str
    details: Optional[dict[str, Any]] = None
    timestamp: str # ISO format timestamp

class MissionContext(BaseModel):
    # Loaded from mission-spec.md
    mission_spec_content: Optional[str] = None 

    # Fields directly mapping to mission-report.md sections
    mission_title: Optional[str] = None
    status: Optional[str] = None # IN_PROGRESS, SUCCESS, FAILURE, BLOCKED
    execution_summary: Optional[str] = None
    files_modified_created: list[str] = Field(default_factory=list)
    git_summary: list[str] = Field(default_factory=list) # list of "hash - message"
    total_cost_usd: float = 0.0
    report_timestamp: Optional[str] = None # Timestamp for the report generation

    # Operational data & structured errors
    mission_errors: list[StructuredError] = Field(default_factory=list)

class WorkflowState(TypedDict):
    mission_context: MissionContext 
    current_step_name: Optional[str] # Name of the current/last executed node
    critical_error_message: Optional[str] # For immediate routing/critical failure
