from pydantic import BaseModel, Field


class SanitizedGoalInfo(BaseModel):
    '''
    Pydantic model to structure the output from the LLM
    when generating a sanitized folder name for a goal.
    '''
    folder_name: str = Field(
        ...,
        description="A filesystem-friendly folder name derived from the task title or description. "
                    "It should be lowercase, with spaces replaced by hyphens, "
                    "and special characters removed or replaced appropriately. "
                    "Example: 'implement-user-login-feature'."
    )
