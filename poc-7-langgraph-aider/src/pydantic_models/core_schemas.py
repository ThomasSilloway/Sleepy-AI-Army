from pydantic import BaseModel, Field

class ManifestConfigLLM(BaseModel):
    """
    Pydantic model for structured data extracted by LLM for goal manifest generation.
    """
    goal_title: str = Field(description="A concise title for the goal, summarized from the task description.")
    task_description_for_manifest: str = Field(description="The full original task description to be included in the manifest.")
    target_file_path_relative_to_git_root: str = Field(description="The target file path for the task, relative to the git repository root.")
