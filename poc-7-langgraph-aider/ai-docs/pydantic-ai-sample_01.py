from pydantic_ai.direct import model_request_sync
from pydantic_ai.messages import ModelRequest

# Make a synchronous request to the model
model_response = model_request_sync(
    'anthropic:claude-3-5-haiku-latest',
    [ModelRequest.user_text_prompt('What is the capital of France?')]
)

print(model_response.parts[0].content)
#> Paris
print(model_response.usage)
"""
Usage(requests=1, request_tokens=56, response_tokens=1, total_tokens=57, details=None)
"""