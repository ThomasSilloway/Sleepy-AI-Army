# poc-8-backlog-to-goals/src/models/goal_models.py
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
    # We can add more fields here later if the LLM is asked to extract more info,
    # for example, a short summary of the goal, or keywords.
    # For now, folder_name is the primary requirement.

# Example usage (not for execution here):
# if __name__ == '__main__':
#     example_data_valid = {"folder_name": "my-new-task-folder"}
#     goal_info_valid = SanitizedGoalInfo(**example_data_valid)
#     print(f"Valid data parsed: {goal_info_valid}")

#     example_data_invalid = {"directory_name": "another-folder"} # Wrong field name
#     try:
#         goal_info_invalid = SanitizedGoalInfo(**example_data_invalid)
#     except ValueError as e:
#         print(f"Invalid data failed parsing as expected: {e}")

#     example_data_missing = {} # Missing required field
#     try:
#         goal_info_missing = SanitizedGoalInfo(**example_data_missing)
#     except ValueError as e:
#         print(f"Missing data failed parsing as expected: {e}")
