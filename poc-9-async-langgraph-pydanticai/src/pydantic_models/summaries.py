from pydantic import BaseModel, Field

class TextSummary(BaseModel):
    """
    Pydantic model to structure the output of a text summarization task.
    """
    summary: str = Field(description="The concise summary of the input text.")

    # You could add more fields here if the summarization task becomes more complex,
    # for example, keywords, confidence score, etc.

if __name__ == '__main__':
    # Example usage and validation
    summary_data_valid = {"summary": "This is a test summary."}
    summary_obj = TextSummary(**summary_data_valid)
    print(f"Valid summary object: {summary_obj.model_dump_json(indent=2)}")

    summary_data_invalid_type = {"summary": 123} # Invalid type for summary
    try:
        TextSummary(**summary_data_invalid_type)
    except ValueError as e:
        print(f"Validation error for invalid type: {e}")

    summary_data_missing_field = {} # Missing 'summary' field
    try:
        TextSummary(**summary_data_missing_field)
    except ValueError as e:
        print(f"Validation error for missing field: {e}")
