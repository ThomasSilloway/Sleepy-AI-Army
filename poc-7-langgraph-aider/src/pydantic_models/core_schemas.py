from pydantic import BaseModel, Field


class ManifestConfigLLM(BaseModel):
    """
    Pydantic model for structured data extracted by LLM for goal manifest generation.
    """
    goal_title: str = Field(description="A concise title for the goal, summarized from the task description.")
    task_description: str = Field(description="The full original task description to be included in the manifest.")
    small_tweak_file_path: str = Field(description="The target file path for the task, relative to the git repository root.")
