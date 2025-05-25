import pytest
from pydantic import ValidationError

from src.models.goal_models import SanitizedGoalInfo


def test_sanitized_goal_info_valid():
    """
    Tests successful creation of SanitizedGoalInfo with valid data.
    """
    folder_name = "test-folder-name"
    info = SanitizedGoalInfo(folder_name=folder_name)
    assert info.folder_name == folder_name


def test_sanitized_goal_info_missing_field():
    """
    Tests that SanitizedGoalInfo raises ValidationError if 'folder_name' is missing.
    """
    with pytest.raises(ValidationError) as excinfo:
        SanitizedGoalInfo() # type: ignore 
        # Using type: ignore because Pydantic expects folder_name, 
        # and we are intentionally omitting it to test validation.
    
    # Check that the error message contains information about the missing field
    assert "folder_name" in str(excinfo.value).lower()
    assert "field required" in str(excinfo.value).lower()


def test_sanitized_goal_info_field_description():
    """
    Checks if the description for folder_name is present.
    Pydantic v2 stores schema in model_json_schema().
    """
    schema = SanitizedGoalInfo.model_json_schema()
    assert "folder_name" in schema["properties"]
    assert "description" in schema["properties"]["folder_name"]
    assert "filesystem-friendly folder name" in schema["properties"]["folder_name"]["description"]

# Add more tests if other validation rules (e.g., regex for folder_name) are added to the model.
# For now, it's a simple string field.
