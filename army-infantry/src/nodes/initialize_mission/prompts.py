from .models import MissionData


def get_system_prompt() -> str:
    return f"""
    You are an expert assistant that generates mission titles from mission descriptions.

    Your goal is to extract specific pieces of information and structure them according to the provided JSON schema.
    The JSON schema to use for your response is:
    {MissionData.model_json_schema()}
    Ensure your output is a valid JSON object that conforms to this schema.
    Your task is to extract the mission title from the provided mission specification content. The title should be concise and human-readable.
"""

def get_user_prompt(mission_spec_content: str) -> str:
    return f"""
        Mission Description: '{mission_spec_content}'
    """
