
from pydantic import BaseModel, Field


class ManifestConfigLLM(BaseModel):
    """
    Pydantic model for structured data extracted by LLM for goal manifest generation.
    """
    goal_title: str = Field(description="A concise title for the goal, summarized from the task description.")
    task_description: str = Field(description="The full original task description to be included in the manifest.")
    small_tweak_file_path: str = Field(description="The target file path for the task, relative to the git repository root.")


class Artifact(BaseModel):
    """
    Represents one artifact entry in the goal manifest.
    """
    status: str = Field(description="Status of the artifact, e.g., '[in-progress]', '[Complete]', '[Error]'.")
    path: str = Field(description="Path to the artifact file.")


class ManifestData(BaseModel):
    """
    Structured data holder for the content of goal-manifest.md.
    This model is the single source of truth for rendering the manifest.
    """
    goal_title: str
    task_description_for_manifest: str
    last_updated_timestamp: str
    overall_status: str
    current_focus: str
    artifacts: list[Artifact]
    ai_questions_list: list[str]
    human_responses_content: str
