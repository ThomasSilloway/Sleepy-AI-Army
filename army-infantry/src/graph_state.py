from typing import Optional, List, Dict, Any, TypedDict
from pydantic import BaseModel, Field
import datetime

class StructuredError(BaseModel):
    node_name: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str # ISO format timestamp

class MissionContext(BaseModel):
    # Core Identifiers (populated once at workflow start from AppConfig/CLI)
    mission_id: str
    mission_folder_path: str 
    project_git_root: str
    
    # Loaded from mission-spec.md
    mission_spec_content: Optional[str] = None 
    
    # Fields directly mapping to mission-report.md sections
    mission_title: Optional[str] = None
    final_status: Optional[str] = None # SUCCESS, FAILURE, BLOCKED
    execution_summary: Optional[str] = None
    files_modified_created: List[str] = Field(default_factory=list)
    git_summary: List[str] = Field(default_factory=list) # list of "hash - message"
    total_cost_usd: float = 0.0
    report_timestamp: Optional[str] = None # Timestamp for the report generation

    # Operational data & structured errors
    mission_errors: List[StructuredError] = Field(default_factory=list)
    
    class Config:
        frozen: bool = True

class WorkflowState(TypedDict):
    mission_context: MissionContext 
    current_step_name: Optional[str] # Name of the current/last executed node
    critical_error_message: Optional[str] # For immediate routing/critical failure
