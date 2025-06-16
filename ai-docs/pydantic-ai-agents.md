## Agent with retries

```
agent = Agent(model="gemini-1.5-flash", retries=3, result_type=CityInfo)
result = agent.run_sync("Where was the 2012 Olympics?")
```

## Agent with system prompt (instructions)

Note: Don't actually use system prompt variable in most cases, use instructions instead.

```
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4o',
    instructions='You are a helpful assistant that can answer questions and help with tasks.',  
)

result = agent.run_sync('What is the capital of France?')
print(result.output)
#> Paris
```

## Structured output Example 2

```
from pydantic import BaseModel

from pydantic_ai import Agent


class CityLocation(BaseModel):
    city: str
    country: str


agent = Agent('google-gla:gemini-1.5-flash', output_type=CityLocation)
result = agent.run_sync('Where were the olympics held in 2012?')
print(result.output)
#> city='London' country='United Kingdom'
print(result.usage())
#> Usage(requests=1, request_tokens=57, response_tokens=8, total_tokens=65)
```

## Getting printing debug info for messages and tracking all tokens

```
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')

result = agent.run_sync('Tell me a joke.')
print(result.output)
#> Did you hear about the toothpaste scandal? They called it Colgate.

# all messages from the run
print(result.all_messages())
"""
[
    ModelRequest(
        parts=[
            SystemPromptPart(
                content='Be a helpful assistant.',
                timestamp=datetime.datetime(...),
            ),
            UserPromptPart(
                content='Tell me a joke.',
                timestamp=datetime.datetime(...),
            ),
        ]
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='Did you hear about the toothpaste scandal? They called it Colgate.'
            )
        ],
        usage=Usage(requests=1, request_tokens=60, response_tokens=12, total_tokens=72),
        model_name='gpt-4o',
        timestamp=datetime.datetime(...),
    ),
]
"""
```

## Storing and loading messages to json

```
from pydantic_core import to_jsonable_python

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter  

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')

result1 = agent.run_sync('Tell me a joke.')
history_step_1 = result1.all_messages()
as_python_objects = to_jsonable_python(history_step_1)  
same_history_as_step_1 = ModelMessagesTypeAdapter.validate_python(as_python_objects)

result2 = agent.run_sync(  
    'Tell me a different joke.', message_history=same_history_as_step_1
)
```

## Storing and loading messages (to JSON)

While maintaining conversation state in memory is enough for many applications, often times you may want to store the messages history of an agent run on disk or in a database. This might be for evals, for sharing data between Python and JavaScript/TypeScript, or any number of other use cases.

The intended way to do this is using a `TypeAdapter`.

We export ModelMessagesTypeAdapter that can be used for this

## ModelMessagesTypeAdapter

```
ModelMessagesTypeAdapter = TypeAdapter(
    list[ModelMessage],
    config=ConfigDict(
        defer_build=True,
        ser_json_bytes="base64",
        val_json_bytes="base64",
    ),
)

-----

validate_python(
    object: Any,
    /,
    *,
    strict: bool | None = None,
    from_attributes: bool | None = None,
    context: dict[str, Any] | None = None,
    experimental_allow_partial: (
        bool | Literal["off", "on", "trailing-strings"]
    ) = False,
    by_alias: bool | None = None,
    by_name: bool | None = None,
) -> T
```