ContentsMenuExpandLight modeDark modeAuto light/dark, in light modeAuto light/dark, in dark mode[Skip to content](https://google.github.io/adk-docs/api-reference/google-adk.html#furo-main-content)

[Back to top](https://google.github.io/adk-docs/api-reference/google-adk.html#)

[View this page](https://google.github.io/adk-docs/api-reference/_sources/google-adk.rst.txt "View this page")

Toggle Light / Dark / Auto color theme

Toggle table of contents sidebar

# Submodules [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#submodules "Link to this heading")

# google.adk.agents module [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#module-google.adk.agents "Link to this heading")

google.adk.agents.Agent [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.Agent "Link to this definition")

alias of [`LlmAgent`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent "google.adk.agents.llm_agent.LlmAgent")

_pydanticmodel_ google.adk.agents.BaseAgent [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent "Link to this definition")

Bases: `BaseModel`

Base class for all agents in Agent Development Kit.

Fields:

- `after_agent_callback (Callable[[google.adk.agents.callback_context.CallbackContext], google.genai.types.Content | None] | None)`

- `before_agent_callback (Callable[[google.adk.agents.callback_context.CallbackContext], google.genai.types.Content | None] | None)`

- `description (str)`

- `name (str)`

- `parent_agent (google.adk.agents.base_agent.BaseAgent | None)`

- `sub_agents (list[google.adk.agents.base_agent.BaseAgent])`


Validators:

- `__validate_name` » `name`


_field_ after\_agent\_callback _:Optional\[AfterAgentCallback\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent.after_agent_callback "Link to this definition")

Callback signature that is invoked after the agent run.

Parameters:

**callback\_context** – MUST be named ‘callback\_context’ (enforced).

Returns:

The content to return to the user. When set, the agent run will skipped and
the provided content will be appended to event history as agent response.

_field_ before\_agent\_callback _:Optional\[BeforeAgentCallback\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent.before_agent_callback "Link to this definition")

Callback signature that is invoked before the agent run.

Parameters:

**callback\_context** – MUST be named ‘callback\_context’ (enforced).

Returns:

The content to return to the user. When set, the agent run will skipped and
the provided content will be returned to user.

_field_ description _:str_ _=''_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent.description "Link to this definition")

Description about the agent’s capability.

The model uses this to determine whether to delegate control to the agent.
One-line description is enough and preferred.

_field_ name _:str_ _\[Required\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent.name "Link to this definition")

The agent’s name.

Agent name must be a Python identifier and unique within the agent tree.
Agent name cannot be “user”, since it’s reserved for end-user’s input.

Validated by:

- `__validate_name`


_field_ parent\_agent _:Optional\[BaseAgent\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent.parent_agent "Link to this definition")

The parent agent of this agent.

Note that an agent can ONLY be added as sub-agent once.

If you want to add one agent twice as sub-agent, consider to create two agent
instances with identical config, but with different name and add them to the
agent tree.

_field_ sub\_agents _:list\[BaseAgent\]_ _\[Optional\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent.sub_agents "Link to this definition")

The sub-agents of this agent.

find\_agent( _name_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent.find_agent "Link to this definition")

Finds the agent with the given name in this agent and its descendants.

Return type:

`Optional`\[ [`BaseAgent`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent "google.adk.agents.base_agent.BaseAgent")\]

Parameters:

**name** – The name of the agent to find.

Returns:

The agent with the matching name, or None if no such agent is found.

find\_sub\_agent( _name_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent.find_sub_agent "Link to this definition")

Finds the agent with the given name in this agent’s descendants.

Return type:

`Optional`\[ [`BaseAgent`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent "google.adk.agents.base_agent.BaseAgent")\]

Parameters:

**name** – The name of the agent to find.

Returns:

The agent with the matching name, or None if no such agent is found.

model\_post\_init( _\_BaseAgent\_\_context_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent.model_post_init "Link to this definition")

Override this method to perform additional initialization after \_\_init\_\_ and model\_construct.
This is useful if you want to do some validation that requires the entire model to be initialized.

Return type:

`None`

_finalasync_ run\_async( _parent\_context_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent.run_async "Link to this definition")

Entry method to run an agent via text-based conversaction.

Return type:

`AsyncGenerator`\[ [`Event`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event "google.adk.events.event.Event"), `None`\]

Parameters:

**parent\_context** – InvocationContext, the invocation context of the parent
agent.

Yields:

_Event_ – the events generated by the agent.

_finalasync_ run\_live( _parent\_context_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent.run_live "Link to this definition")

Entry method to run an agent via video/audio-based conversaction.

Return type:

`AsyncGenerator`\[ [`Event`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event "google.adk.events.event.Event"), `None`\]

Parameters:

**parent\_context** – InvocationContext, the invocation context of the parent
agent.

Yields:

_Event_ – the events generated by the agent.

_property_ root\_agent _: [BaseAgent](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent "google.adk.agents.base_agent.BaseAgent")_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent.root_agent "Link to this definition")

Gets the root agent of this agent.

_pydanticmodel_ google.adk.agents.LlmAgent [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent "Link to this definition")

Bases: [`BaseAgent`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent "google.adk.agents.base_agent.BaseAgent")

LLM-based Agent.

Fields:

- `after_model_callback (Optional[AfterModelCallback])`

- `after_tool_callback (Optional[AfterToolCallback])`

- `before_model_callback (Optional[BeforeModelCallback])`

- `before_tool_callback (Optional[BeforeToolCallback])`

- `code_executor (Optional[BaseCodeExecutor])`

- `disallow_transfer_to_parent (bool)`

- `disallow_transfer_to_peers (bool)`

- `examples (Optional[ExamplesUnion])`

- `generate_content_config (Optional[types.GenerateContentConfig])`

- `global_instruction (Union[str, InstructionProvider])`

- `include_contents (Literal['default', 'none'])`

- `input_schema (Optional[type[BaseModel]])`

- `instruction (Union[str, InstructionProvider])`

- `model (Union[str, BaseLlm])`

- `output_key (Optional[str])`

- `output_schema (Optional[type[BaseModel]])`

- `planner (Optional[BasePlanner])`

- `tools (list[ToolUnion])`


Validators:

- `__model_validator_after` » `all fields`

- `__validate_generate_content_config` » `generate_content_config`


_field_ after\_model\_callback _:Optional\[AfterModelCallback\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.after_model_callback "Link to this definition")

Called after calling LLM.

Parameters:

- **callback\_context** – CallbackContext,

- **llm\_response** – LlmResponse, the actual model response.


Returns:

The content to return to the user. When present, the actual model response
will be ignored and the provided content will be returned to user.

Validated by:

- `__model_validator_after`


_field_ after\_tool\_callback _:Optional\[AfterToolCallback\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.after_tool_callback "Link to this definition")

Called after the tool is called.

Parameters:

- **tool** – The tool to be called.

- **args** – The arguments to the tool.

- **tool\_context** – ToolContext,

- **tool\_response** – The response from the tool.


Returns:

When present, the returned dict will be used as tool result.

Validated by:

- `__model_validator_after`


_field_ before\_model\_callback _:Optional\[BeforeModelCallback\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.before_model_callback "Link to this definition")

Called before calling the LLM.
:param callback\_context: CallbackContext,
:param llm\_request: LlmRequest, The raw model request. Callback can mutate the
:param request.:

Returns:

The content to return to the user. When present, the model call will be
skipped and the provided content will be returned to user.

Validated by:

- `__model_validator_after`


_field_ before\_tool\_callback _:Optional\[BeforeToolCallback\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.before_tool_callback "Link to this definition")

Called before the tool is called.

Parameters:

- **tool** – The tool to be called.

- **args** – The arguments to the tool.

- **tool\_context** – ToolContext,


Returns:

The tool response. When present, the returned tool response will be used and
the framework will skip calling the actual tool.

Validated by:

- `__model_validator_after`


_field_ code\_executor _:Optional\[BaseCodeExecutor\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.code_executor "Link to this definition")

Allow agent to execute code blocks from model responses using the provided
CodeExecutor.

Check out available code executions in google.adk.code\_executor package.

NOTE: to use model’s built-in code executor, don’t set this field, add
google.adk.tools.built\_in\_code\_execution to tools instead.

Validated by:

- `__model_validator_after`


_field_ disallow\_transfer\_to\_parent _:bool_ _=False_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.disallow_transfer_to_parent "Link to this definition")

Disallows LLM-controlled transferring to the parent agent.

Validated by:

- `__model_validator_after`


_field_ disallow\_transfer\_to\_peers _:bool_ _=False_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.disallow_transfer_to_peers "Link to this definition")

Disallows LLM-controlled transferring to the peer agents.

Validated by:

- `__model_validator_after`


_field_ examples _:Optional\[ExamplesUnion\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.examples "Link to this definition")Validated by:

- `__model_validator_after`


_field_ generate\_content\_config _:Optional\[types.GenerateContentConfig\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.generate_content_config "Link to this definition")

The additional content generation configurations.

NOTE: not all fields are usable, e.g. tools must be configured via tools,
thinking\_config must be configured via planner in LlmAgent.

For example: use this config to adjust model temperature, configure safety
settings, etc.

Validated by:

- `__model_validator_after`

- `__validate_generate_content_config`


_field_ global\_instruction _:Union\[str,InstructionProvider\]_ _=''_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.global_instruction "Link to this definition")

Instructions for all the agents in the entire agent tree.

global\_instruction ONLY takes effect in root agent.

For example: use global\_instruction to make all agents have a stable identity
or personality.

Validated by:

- `__model_validator_after`


_field_ include\_contents _:Literal\['default','none'\]_ _='default'_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.include_contents "Link to this definition")

Whether to include contents in the model request.

When set to ‘none’, the model request will not include any contents, such as
user messages, tool results, etc.

Validated by:

- `__model_validator_after`


_field_ input\_schema _:Optional\[type\[BaseModel\]\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.input_schema "Link to this definition")

The input schema when agent is used as a tool.

Validated by:

- `__model_validator_after`


_field_ instruction _:Union\[str,InstructionProvider\]_ _=''_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.instruction "Link to this definition")

Instructions for the LLM model, guiding the agent’s behavior.

Validated by:

- `__model_validator_after`


_field_ model _:Union\[str,BaseLlm\]_ _=''_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.model "Link to this definition")

The model to use for the agent.

When not set, the agent will inherit the model from its ancestor.

Validated by:

- `__model_validator_after`


_field_ output\_key _:Optional\[str\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.output_key "Link to this definition")

The key in session state to store the output of the agent.

Typically use cases:
\- Extracts agent reply for later use, such as in tools, callbacks, etc.
\- Connects agents to coordinate with each other.

Validated by:

- `__model_validator_after`


_field_ output\_schema _:Optional\[type\[BaseModel\]\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.output_schema "Link to this definition")

The output schema when agent replies.

NOTE: when this is set, agent can ONLY reply and CANNOT use any tools, such as
function tools, RAGs, agent transfer, etc.

Validated by:

- `__model_validator_after`


_field_ planner _:Optional\[BasePlanner\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.planner "Link to this definition")

Instructs the agent to make a plan and execute it step by step.

NOTE: to use model’s built-in thinking features, set the thinking\_config
field in google.adk.planners.built\_in\_planner.

Validated by:

- `__model_validator_after`


_field_ tools _:list\[ToolUnion\]_ _\[Optional\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.tools "Link to this definition")

Tools available to this agent.

Validated by:

- `__model_validator_after`


canonical\_global\_instruction( _ctx_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.canonical_global_instruction "Link to this definition")

The resolved self.instruction field to construct global instruction.

This method is only for use by Agent Development Kit.

Return type:

`str`

canonical\_instruction( _ctx_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.canonical_instruction "Link to this definition")

The resolved self.instruction field to construct instruction for this agent.

This method is only for use by Agent Development Kit.

Return type:

`str`

_property_ canonical\_model _: [BaseLlm](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.BaseLlm "google.adk.models.base_llm.BaseLlm")_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.canonical_model "Link to this definition")

The resolved self.model field as BaseLlm.

This method is only for use by Agent Development Kit.

_property_ canonical\_tools _:list\[ [BaseTool](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.BaseTool "google.adk.tools.base_tool.BaseTool")\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LlmAgent.canonical_tools "Link to this definition")

The resolved self.tools field as a list of BaseTool.

This method is only for use by Agent Development Kit.

_pydanticmodel_ google.adk.agents.LoopAgent [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LoopAgent "Link to this definition")

Bases: [`BaseAgent`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent "google.adk.agents.base_agent.BaseAgent")

A shell agent that run its sub-agents in a loop.

When sub-agent generates an event with escalate or max\_iterations are
reached, the loop agent will stop.



Fields:

- `max_iterations (Optional[int])`


Validators:

_field_ max\_iterations _:Optional\[int\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.LoopAgent.max_iterations "Link to this definition")

The maximum number of iterations to run the loop agent.

If not set, the loop agent will run indefinitely until a sub-agent
escalates.

_pydanticmodel_ google.adk.agents.ParallelAgent [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.ParallelAgent "Link to this definition")

Bases: [`BaseAgent`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent "google.adk.agents.base_agent.BaseAgent")

A shell agent that run its sub-agents in parallel in isolated manner.

This approach is beneficial for scenarios requiring multiple perspectives or
attempts on a single task, such as:

- Running different algorithms simultaneously.

- Generating multiple responses for review by a subsequent evaluation agent.




Fields:

Validators:

_pydanticmodel_ google.adk.agents.SequentialAgent [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.SequentialAgent "Link to this definition")

Bases: [`BaseAgent`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent "google.adk.agents.base_agent.BaseAgent")

A shell agent that run its sub-agents in sequence.

Show JSON schema



Fields:

Validators:

# google.adk.artifacts module [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#module-google.adk.artifacts "Link to this heading")

_class_ google.adk.artifacts.BaseArtifactService [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.BaseArtifactService "Link to this definition")

Bases: `ABC`

Abstract base class for artifact services.

_abstract_ delete\_artifact( _\*_, _app\_name_, _user\_id_, _session\_id_, _filename_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.BaseArtifactService.delete_artifact "Link to this definition")

Deletes an artifact.

Return type:

`None`

Parameters:

- **app\_name** – The name of the application.

- **user\_id** – The ID of the user.

- **session\_id** – The ID of the session.

- **filename** – The name of the artifact file.


_abstract_ list\_artifact\_keys( _\*_, _app\_name_, _user\_id_, _session\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.BaseArtifactService.list_artifact_keys "Link to this definition")

Lists all the artifact filenames within a session.

Return type:

`list`\[ `str`\]

Parameters:

- **app\_name** – The name of the application.

- **user\_id** – The ID of the user.

- **session\_id** – The ID of the session.


Returns:

A list of all artifact filenames within a session.

_abstract_ list\_versions( _\*_, _app\_name_, _user\_id_, _session\_id_, _filename_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.BaseArtifactService.list_versions "Link to this definition")

Lists all versions of an artifact.

Return type:

`list`\[ `int`\]

Parameters:

- **app\_name** – The name of the application.

- **user\_id** – The ID of the user.

- **session\_id** – The ID of the session.

- **filename** – The name of the artifact file.


Returns:

A list of all available versions of the artifact.

_abstract_ load\_artifact( _\*_, _app\_name_, _user\_id_, _session\_id_, _filename_, _version=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.BaseArtifactService.load_artifact "Link to this definition")

Gets an artifact from the artifact service storage.

The artifact is a file identified by the app name, user ID, session ID, and
filename.

Return type:

`Optional`\[ `Part`\]

Parameters:

- **app\_name** – The app name.

- **user\_id** – The user ID.

- **session\_id** – The session ID.

- **filename** – The filename of the artifact.

- **version** – The version of the artifact. If None, the latest version will be
returned.


Returns:

The artifact or None if not found.

_abstract_ save\_artifact( _\*_, _app\_name_, _user\_id_, _session\_id_, _filename_, _artifact_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.BaseArtifactService.save_artifact "Link to this definition")

Saves an artifact to the artifact service storage.

The artifact is a file identified by the app name, user ID, session ID, and
filename. After saving the artifact, a revision ID is returned to identify
the artifact version.

Return type:

`int`

Parameters:

- **app\_name** – The app name.

- **user\_id** – The user ID.

- **session\_id** – The session ID.

- **filename** – The filename of the artifact.

- **artifact** – The artifact to save.


Returns:

The revision ID. The first version of the artifact has a revision ID of 0.
This is incremented by 1 after each successful save.

_class_ google.adk.artifacts.GcsArtifactService( _bucket\_name_, _\*\*kwargs_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.GcsArtifactService "Link to this definition")

Bases: [`BaseArtifactService`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.BaseArtifactService "google.adk.artifacts.base_artifact_service.BaseArtifactService")

An artifact service implementation using Google Cloud Storage (GCS).

Initializes the GcsArtifactService.

Parameters:

- **bucket\_name** – The name of the bucket to use.

- **\*\*kwargs** – Keyword arguments to pass to the Google Cloud Storage client.


delete\_artifact( _\*_, _app\_name_, _user\_id_, _session\_id_, _filename_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.GcsArtifactService.delete_artifact "Link to this definition")

Deletes an artifact.

Return type:

`None`

Parameters:

- **app\_name** – The name of the application.

- **user\_id** – The ID of the user.

- **session\_id** – The ID of the session.

- **filename** – The name of the artifact file.


list\_artifact\_keys( _\*_, _app\_name_, _user\_id_, _session\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.GcsArtifactService.list_artifact_keys "Link to this definition")

Lists all the artifact filenames within a session.

Return type:

`list`\[ `str`\]

Parameters:

- **app\_name** – The name of the application.

- **user\_id** – The ID of the user.

- **session\_id** – The ID of the session.


Returns:

A list of all artifact filenames within a session.

list\_versions( _\*_, _app\_name_, _user\_id_, _session\_id_, _filename_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.GcsArtifactService.list_versions "Link to this definition")

Lists all versions of an artifact.

Return type:

`list`\[ `int`\]

Parameters:

- **app\_name** – The name of the application.

- **user\_id** – The ID of the user.

- **session\_id** – The ID of the session.

- **filename** – The name of the artifact file.


Returns:

A list of all available versions of the artifact.

load\_artifact( _\*_, _app\_name_, _user\_id_, _session\_id_, _filename_, _version=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.GcsArtifactService.load_artifact "Link to this definition")

Gets an artifact from the artifact service storage.

The artifact is a file identified by the app name, user ID, session ID, and
filename.

Return type:

`Optional`\[ `Part`\]

Parameters:

- **app\_name** – The app name.

- **user\_id** – The user ID.

- **session\_id** – The session ID.

- **filename** – The filename of the artifact.

- **version** – The version of the artifact. If None, the latest version will be
returned.


Returns:

The artifact or None if not found.

save\_artifact( _\*_, _app\_name_, _user\_id_, _session\_id_, _filename_, _artifact_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.GcsArtifactService.save_artifact "Link to this definition")

Saves an artifact to the artifact service storage.

The artifact is a file identified by the app name, user ID, session ID, and
filename. After saving the artifact, a revision ID is returned to identify
the artifact version.

Return type:

`int`

Parameters:

- **app\_name** – The app name.

- **user\_id** – The user ID.

- **session\_id** – The session ID.

- **filename** – The filename of the artifact.

- **artifact** – The artifact to save.


Returns:

The revision ID. The first version of the artifact has a revision ID of 0.
This is incremented by 1 after each successful save.

_pydanticmodel_ google.adk.artifacts.InMemoryArtifactService [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.InMemoryArtifactService "Link to this definition")

Bases: [`BaseArtifactService`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.BaseArtifactService "google.adk.artifacts.base_artifact_service.BaseArtifactService"), `BaseModel`

An in-memory implementation of the artifact service.

Show JSON schema

Fields:

- `artifacts (dict[str, list[google.genai.types.Part]])`


_field_ artifacts _: `dict`\[ `str`, `list`\[ `Part`\]\]_ _\[Optional\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.InMemoryArtifactService.artifacts "Link to this definition")delete\_artifact( _\*_, _app\_name_, _user\_id_, _session\_id_, _filename_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.InMemoryArtifactService.delete_artifact "Link to this definition")

Deletes an artifact.

Return type:

`None`

Parameters:

- **app\_name** – The name of the application.

- **user\_id** – The ID of the user.

- **session\_id** – The ID of the session.

- **filename** – The name of the artifact file.


list\_artifact\_keys( _\*_, _app\_name_, _user\_id_, _session\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.InMemoryArtifactService.list_artifact_keys "Link to this definition")

Lists all the artifact filenames within a session.

Return type:

`list`\[ `str`\]

Parameters:

- **app\_name** – The name of the application.

- **user\_id** – The ID of the user.

- **session\_id** – The ID of the session.


Returns:

A list of all artifact filenames within a session.

list\_versions( _\*_, _app\_name_, _user\_id_, _session\_id_, _filename_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.InMemoryArtifactService.list_versions "Link to this definition")

Lists all versions of an artifact.

Return type:

`list`\[ `int`\]

Parameters:

- **app\_name** – The name of the application.

- **user\_id** – The ID of the user.

- **session\_id** – The ID of the session.

- **filename** – The name of the artifact file.


Returns:

A list of all available versions of the artifact.

load\_artifact( _\*_, _app\_name_, _user\_id_, _session\_id_, _filename_, _version=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.InMemoryArtifactService.load_artifact "Link to this definition")

Gets an artifact from the artifact service storage.

The artifact is a file identified by the app name, user ID, session ID, and
filename.

Return type:

`Optional`\[ `Part`\]

Parameters:

- **app\_name** – The app name.

- **user\_id** – The user ID.

- **session\_id** – The session ID.

- **filename** – The filename of the artifact.

- **version** – The version of the artifact. If None, the latest version will be
returned.


Returns:

The artifact or None if not found.

save\_artifact( _\*_, _app\_name_, _user\_id_, _session\_id_, _filename_, _artifact_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.InMemoryArtifactService.save_artifact "Link to this definition")

Saves an artifact to the artifact service storage.

The artifact is a file identified by the app name, user ID, session ID, and
filename. After saving the artifact, a revision ID is returned to identify
the artifact version.

Return type:

`int`

Parameters:

- **app\_name** – The app name.

- **user\_id** – The user ID.

- **session\_id** – The session ID.

- **filename** – The filename of the artifact.

- **artifact** – The artifact to save.


Returns:

The revision ID. The first version of the artifact has a revision ID of 0.
This is incremented by 1 after each successful save.

# google.adk.code\_executors module [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#module-google.adk.code_executors "Link to this heading")

_pydanticmodel_ google.adk.code\_executors.BaseCodeExecutor [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.BaseCodeExecutor "Link to this definition")

Bases: `BaseModel`

Abstract base class for all code executors.

The code executor allows the agent to execute code blocks from model responses
and incorporate the execution results into the final response.

optimize\_data\_file [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.BaseCodeExecutor.optimize_data_file "Link to this definition")

If true, extract and process data files from the model
request and attach them to the code executor. Supported data file
MimeTypes are \[text/csv\]. Default to False.

stateful [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.BaseCodeExecutor.stateful "Link to this definition")

Whether the code executor is stateful. Default to False.

error\_retry\_attempts [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.BaseCodeExecutor.error_retry_attempts "Link to this definition")

The number of attempts to retry on consecutive code
execution errors. Default to 2.

code\_block\_delimiters [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.BaseCodeExecutor.code_block_delimiters "Link to this definition")

The list of the enclosing delimiters to identify the
code blocks.

execution\_result\_delimiters [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.BaseCodeExecutor.execution_result_delimiters "Link to this definition")

The delimiters to format the code execution
result.



Fields:

- `code_block_delimiters (List[tuple[str, str]])`

- `error_retry_attempts (int)`

- `execution_result_delimiters (tuple[str, str])`

- `optimize_data_file (bool)`

- `stateful (bool)`


_field_ code\_block\_delimiters _: `List`\[ `tuple`\[ `str`, `str`\]\]_ _=\[('\`\`\`tool\_code\\n','\\n\`\`\`'),('\`\`\`python\\n','\\n\`\`\`')\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id0 "Link to this definition")

> The list of the enclosing delimiters to identify the code blocks.
> For example, the delimiter (’ [\`\`](https://google.github.io/adk-docs/api-reference/google-adk.html#id1) [\`](https://google.github.io/adk-docs/api-reference/google-adk.html#id3) python

‘, ‘
[\`\`](https://google.github.io/adk-docs/api-reference/google-adk.html#id5) [\`](https://google.github.io/adk-docs/api-reference/google-adk.html#id7)’) can be

> used to identify code blocks with the following format:
>
> `` `python
> print("hello")
> ` ``

_field_ error\_retry\_attempts _: `int`_ _=2_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id9 "Link to this definition")

The number of attempts to retry on consecutive code execution errors. Default to 2.

_field_ execution\_result\_delimiters _: `tuple`\[ `str`, `str`\]_ _=('\`\`\`tool\_output\\n','\\n\`\`\`')_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id10 "Link to this definition")

The delimiters to format the code execution result.

_field_ optimize\_data\_file _: `bool`_ _=False_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id11 "Link to this definition")

If true, extract and process data files from the model request
and attach them to the code executor.
Supported data file MimeTypes are \[text/csv\].

Default to False.

_field_ stateful _: `bool`_ _=False_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id12 "Link to this definition")

Whether the code executor is stateful. Default to False.

_abstract_ execute\_code( _invocation\_context_, _code\_execution\_input_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.BaseCodeExecutor.execute_code "Link to this definition")

Executes code and return the code execution result.

Return type:

`CodeExecutionResult`

Parameters:

- **invocation\_context** – The invocation context of the code execution.

- **code\_execution\_input** – The code execution input.


Returns:

The code execution result.

_class_ google.adk.code\_executors.CodeExecutorContext( _session\_state_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext "Link to this definition")

Bases: `object`

The persistent context used to configure the code executor.

Initializes the code executor context.

Parameters:

**session\_state** – The session state to get the code executor context from.

add\_input\_files( _input\_files_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext.add_input_files "Link to this definition")

Adds the input files to the code executor context.

Parameters:

**input\_files** – The input files to add to the code executor context.

add\_processed\_file\_names( _file\_names_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext.add_processed_file_names "Link to this definition")

Adds the processed file name to the session state.

Parameters:

**file\_names** – The processed file names to add to the session state.

clear\_input\_files() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext.clear_input_files "Link to this definition")

Removes the input files and processed file names to the code executor context.

get\_error\_count( _invocation\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext.get_error_count "Link to this definition")

Gets the error count from the session state.

Return type:

`int`

Parameters:

**invocation\_id** – The invocation ID to get the error count for.

Returns:

The error count for the given invocation ID.

get\_execution\_id() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext.get_execution_id "Link to this definition")

Gets the session ID for the code executor.

Return type:

`Optional`\[ `str`\]

Returns:

The session ID for the code executor context.

get\_input\_files() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext.get_input_files "Link to this definition")

Gets the code executor input file names from the session state.

Return type:

`list`\[ `File`\]

Returns:

A list of input files in the code executor context.

get\_processed\_file\_names() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext.get_processed_file_names "Link to this definition")

Gets the processed file names from the session state.

Return type:

`list`\[ `str`\]

Returns:

A list of processed file names in the code executor context.

get\_state\_delta() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext.get_state_delta "Link to this definition")

Gets the state delta to update in the persistent session state.

Return type:

`dict`\[ `str`, `Any`\]

Returns:

The state delta to update in the persistent session state.

increment\_error\_count( _invocation\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext.increment_error_count "Link to this definition")

Increments the error count from the session state.

Parameters:

**invocation\_id** – The invocation ID to increment the error count for.

reset\_error\_count( _invocation\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext.reset_error_count "Link to this definition")

Resets the error count from the session state.

Parameters:

**invocation\_id** – The invocation ID to reset the error count for.

set\_execution\_id( _session\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext.set_execution_id "Link to this definition")

Sets the session ID for the code executor.

Parameters:

**session\_id** – The session ID for the code executor.

update\_code\_execution\_result( _invocation\_id_, _code_, _result\_stdout_, _result\_stderr_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.CodeExecutorContext.update_code_execution_result "Link to this definition")

Updates the code execution result.

Parameters:

- **invocation\_id** – The invocation ID to update the code execution result for.

- **code** – The code to execute.

- **result\_stdout** – The standard output of the code execution.

- **result\_stderr** – The standard error of the code execution.


_pydanticmodel_ google.adk.code\_executors.ContainerCodeExecutor [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.ContainerCodeExecutor "Link to this definition")

Bases: [`BaseCodeExecutor`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.BaseCodeExecutor "google.adk.code_executors.base_code_executor.BaseCodeExecutor")

A code executor that uses a custom container to execute code.

base\_url [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.ContainerCodeExecutor.base_url "Link to this definition")

Optional. The base url of the user hosted Docker client.

image [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.ContainerCodeExecutor.image "Link to this definition")

The tag of the predefined image or custom image to run on the
container. Either docker\_path or image must be set.

docker\_path [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.ContainerCodeExecutor.docker_path "Link to this definition")

The path to the directory containing the Dockerfile. If set,
build the image from the dockerfile path instead of using the predefined
image. Either docker\_path or image must be set.

Initializes the ContainerCodeExecutor.

Parameters:

- **base\_url** – Optional. The base url of the user hosted Docker client.

- **image** – The tag of the predefined image or custom image to run on the
container. Either docker\_path or image must be set.

- **docker\_path** – The path to the directory containing the Dockerfile. If set,
build the image from the dockerfile path instead of using the predefined
image. Either docker\_path or image must be set.

- **\*\*data** – The data to initialize the ContainerCodeExecutor.


Show JSON schema

````
{
   "title": "ContainerCodeExecutor",
   "description": "A code executor that uses a custom container to execute code.\n\nAttributes:\n  base_url: Optional. The base url of the user hosted Docker client.\n  image: The tag of the predefined image or custom image to run on the\n    container. Either docker_path or image must be set.\n  docker_path: The path to the directory containing the Dockerfile. If set,\n    build the image from the dockerfile path instead of using the predefined\n    image. Either docker_path or image must be set.",
   "type": "object",
   "properties": {
      "optimize_data_file": {
         "default": false,
         "title": "Optimize Data File",
         "type": "boolean"
      },
      "stateful": {
         "default": false,
         "title": "Stateful",
         "type": "boolean"
      },
      "error_retry_attempts": {
         "default": 2,
         "title": "Error Retry Attempts",
         "type": "integer"
      },
      "code_block_delimiters": {
         "default": [\
            [\
               "```tool_code\n",\
               "\n```"\
            ],\
            [\
               "```python\n",\
               "\n```"\
            ]\
         ],
         "items": {
            "maxItems": 2,
            "minItems": 2,
            "prefixItems": [\
               {\
                  "type": "string"\
               },\
               {\
                  "type": "string"\
               }\
            ],
            "type": "array"
         },
         "title": "Code Block Delimiters",
         "type": "array"
      },
      "execution_result_delimiters": {
         "default": [\
            "```tool_output\n",\
            "\n```"\
         ],
         "maxItems": 2,
         "minItems": 2,
         "prefixItems": [\
            {\
               "type": "string"\
            },\
            {\
               "type": "string"\
            }\
         ],
         "title": "Execution Result Delimiters",
         "type": "array"
      },
      "base_url": {
         "anyOf": [\
            {\
               "type": "string"\
            },\
            {\
               "type": "null"\
            }\
         ],
         "default": null,
         "title": "Base Url"
      },
      "image": {
         "default": null,
         "title": "Image",
         "type": "string"
      },
      "docker_path": {
         "default": null,
         "title": "Docker Path",
         "type": "string"
      }
   }
}

````

Fields:

- `base_url (str | None)`

- `docker_path (str)`

- `image (str)`

- `optimize_data_file (bool)`

- `stateful (bool)`


_field_ base\_url _: `Optional`\[ `str`\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id13 "Link to this definition")

Optional. The base url of the user hosted Docker client.

_field_ docker\_path _: `str`_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id14 "Link to this definition")

The path to the directory containing the Dockerfile.
If set, build the image from the dockerfile path instead of using the
predefined image. Either docker\_path or image must be set.

_field_ image _: `str`_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id15 "Link to this definition")

The tag of the predefined image or custom image to run on the container.
Either docker\_path or image must be set.

_field_ optimize\_data\_file _: `bool`_ _=False_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.ContainerCodeExecutor.optimize_data_file "Link to this definition")

If true, extract and process data files from the model request
and attach them to the code executor.
Supported data file MimeTypes are \[text/csv\].

Default to False.

_field_ stateful _: `bool`_ _=False_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.ContainerCodeExecutor.stateful "Link to this definition")

Whether the code executor is stateful. Default to False.

execute\_code( _invocation\_context_, _code\_execution\_input_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.ContainerCodeExecutor.execute_code "Link to this definition")

Executes code and return the code execution result.

Return type:

`CodeExecutionResult`

Parameters:

- **invocation\_context** – The invocation context of the code execution.

- **code\_execution\_input** – The code execution input.


Returns:

The code execution result.

model\_post\_init( _context_, _/_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.ContainerCodeExecutor.model_post_init "Link to this definition")

This function is meant to behave like a BaseModel method to initialise private attributes.

It takes context as an argument since that’s what pydantic-core passes when calling it.

Return type:

`None`

Parameters:

- **self** – The BaseModel instance.

- **context** – The context.


_pydanticmodel_ google.adk.code\_executors.UnsafeLocalCodeExecutor [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.UnsafeLocalCodeExecutor "Link to this definition")

Bases: [`BaseCodeExecutor`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.BaseCodeExecutor "google.adk.code_executors.base_code_executor.BaseCodeExecutor")

A code executor that unsafely execute code in the current local context.

Initializes the UnsafeLocalCodeExecutor.

Show JSON schema

````
{
   "title": "UnsafeLocalCodeExecutor",
   "description": "A code executor that unsafely execute code in the current local context.",
   "type": "object",
   "properties": {
      "optimize_data_file": {
         "default": false,
         "title": "Optimize Data File",
         "type": "boolean"
      },
      "stateful": {
         "default": false,
         "title": "Stateful",
         "type": "boolean"
      },
      "error_retry_attempts": {
         "default": 2,
         "title": "Error Retry Attempts",
         "type": "integer"
      },
      "code_block_delimiters": {
         "default": [\
            [\
               "```tool_code\n",\
               "\n```"\
            ],\
            [\
               "```python\n",\
               "\n```"\
            ]\
         ],
         "items": {
            "maxItems": 2,
            "minItems": 2,
            "prefixItems": [\
               {\
                  "type": "string"\
               },\
               {\
                  "type": "string"\
               }\
            ],
            "type": "array"
         },
         "title": "Code Block Delimiters",
         "type": "array"
      },
      "execution_result_delimiters": {
         "default": [\
            "```tool_output\n",\
            "\n```"\
         ],
         "maxItems": 2,
         "minItems": 2,
         "prefixItems": [\
            {\
               "type": "string"\
            },\
            {\
               "type": "string"\
            }\
         ],
         "title": "Execution Result Delimiters",
         "type": "array"
      }
   }
}

````

Fields:

- `optimize_data_file (bool)`

- `stateful (bool)`


_field_ optimize\_data\_file _: `bool`_ _=False_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.UnsafeLocalCodeExecutor.optimize_data_file "Link to this definition")

If true, extract and process data files from the model request
and attach them to the code executor.
Supported data file MimeTypes are \[text/csv\].

Default to False.

_field_ stateful _: `bool`_ _=False_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.UnsafeLocalCodeExecutor.stateful "Link to this definition")

Whether the code executor is stateful. Default to False.

execute\_code( _invocation\_context_, _code\_execution\_input_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.UnsafeLocalCodeExecutor.execute_code "Link to this definition")

Executes code and return the code execution result.

Return type:

`CodeExecutionResult`

Parameters:

- **invocation\_context** – The invocation context of the code execution.

- **code\_execution\_input** – The code execution input.


Returns:

The code execution result.

_pydanticmodel_ google.adk.code\_executors.VertexAiCodeExecutor [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.VertexAiCodeExecutor "Link to this definition")

Bases: [`BaseCodeExecutor`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.BaseCodeExecutor "google.adk.code_executors.base_code_executor.BaseCodeExecutor")

A code executor that uses Vertex Code Interpreter Extension to execute code.

resource\_name [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.VertexAiCodeExecutor.resource_name "Link to this definition")

If set, load the existing resource name of the code
interpreter extension instead of creating a new one. Format:
projects/123/locations/us-central1/extensions/456

Initializes the VertexAiCodeExecutor.

Parameters:

- **resource\_name** – If set, load the existing resource name of the code
interpreter extension instead of creating a new one. Format:
projects/123/locations/us-central1/extensions/456

- **\*\*data** – Additional keyword arguments to be passed to the base class.


Show JSON schema

````
{
   "title": "VertexAiCodeExecutor",
   "description": "A code executor that uses Vertex Code Interpreter Extension to execute code.\n\nAttributes:\n  resource_name: If set, load the existing resource name of the code\n    interpreter extension instead of creating a new one. Format:\n    projects/123/locations/us-central1/extensions/456",
   "type": "object",
   "properties": {
      "optimize_data_file": {
         "default": false,
         "title": "Optimize Data File",
         "type": "boolean"
      },
      "stateful": {
         "default": false,
         "title": "Stateful",
         "type": "boolean"
      },
      "error_retry_attempts": {
         "default": 2,
         "title": "Error Retry Attempts",
         "type": "integer"
      },
      "code_block_delimiters": {
         "default": [\
            [\
               "```tool_code\n",\
               "\n```"\
            ],\
            [\
               "```python\n",\
               "\n```"\
            ]\
         ],
         "items": {
            "maxItems": 2,
            "minItems": 2,
            "prefixItems": [\
               {\
                  "type": "string"\
               },\
               {\
                  "type": "string"\
               }\
            ],
            "type": "array"
         },
         "title": "Code Block Delimiters",
         "type": "array"
      },
      "execution_result_delimiters": {
         "default": [\
            "```tool_output\n",\
            "\n```"\
         ],
         "maxItems": 2,
         "minItems": 2,
         "prefixItems": [\
            {\
               "type": "string"\
            },\
            {\
               "type": "string"\
            }\
         ],
         "title": "Execution Result Delimiters",
         "type": "array"
      },
      "resource_name": {
         "default": null,
         "title": "Resource Name",
         "type": "string"
      }
   }
}

````

Fields:

- `resource_name (str)`


_field_ resource\_name _: `str`_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id16 "Link to this definition")

If set, load the existing resource name of the code interpreter extension
instead of creating a new one.
Format: projects/123/locations/us-central1/extensions/456

execute\_code( _invocation\_context_, _code\_execution\_input_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.VertexAiCodeExecutor.execute_code "Link to this definition")

Executes code and return the code execution result.

Return type:

`CodeExecutionResult`

Parameters:

- **invocation\_context** – The invocation context of the code execution.

- **code\_execution\_input** – The code execution input.


Returns:

The code execution result.

model\_post\_init( _context_, _/_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.code_executors.VertexAiCodeExecutor.model_post_init "Link to this definition")

This function is meant to behave like a BaseModel method to initialise private attributes.

It takes context as an argument since that’s what pydantic-core passes when calling it.

Return type:

`None`

Parameters:

- **self** – The BaseModel instance.

- **context** – The context.


# google.adk.evaluation module [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#module-google.adk.evaluation "Link to this heading")

_class_ google.adk.evaluation.AgentEvaluator [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.evaluation.AgentEvaluator "Link to this definition")

Bases: `object`

An evaluator for Agents, mainly intented for helping with test cases.

_static_ evaluate( _agent\_module_, _eval\_dataset\_file\_path\_or\_dir_, _num\_runs=2_, _agent\_name=None_, _initial\_session\_file=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.evaluation.AgentEvaluator.evaluate "Link to this definition")

Evaluates an Agent given eval data.

Parameters:

- **agent\_module** – The path to python module that contains the definition of
the agent. There is convention in place here, where the code is going to
look for ‘root\_agent’ in the loaded module.

- **eval\_dataset** – The eval data set. This can be either a string representing
full path to the file containing eval dataset, or a directory that is
recusively explored for all files that have a .test.json suffix.

- **num\_runs** – Number of times all entries in the eval dataset should be
assessed.

- **agent\_name** – The name of the agent.

- **initial\_session\_file** – File that contains initial session state that is
needed by all the evals in the eval dataset.


_static_ find\_config\_for\_test\_file( _test\_file_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.evaluation.AgentEvaluator.find_config_for_test_file "Link to this definition")

Find the test\_config.json file in the same folder as the test file.

# google.adk.events module [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#module-google.adk.events "Link to this heading")

_pydanticmodel_ google.adk.events.Event [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event "Link to this definition")

Bases: `LlmResponse`

Represents an event in a conversation between agents and users.

It is used to store the content of the conversation, as well as the actions
taken by the agents like function calls, etc.

invocation\_id [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.invocation_id "Link to this definition")

The invocation ID of the event.

author [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.author "Link to this definition")

“user” or the name of the agent, indicating who appended the event
to the session.

actions [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.actions "Link to this definition")

The actions taken by the agent.

long\_running\_tool\_ids [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.long_running_tool_ids "Link to this definition")

The ids of the long running function calls.

branch [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.branch "Link to this definition")

The branch of the event.

id [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.id "Link to this definition")

The unique identifier of the event.

timestamp [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.timestamp "Link to this definition")

The timestamp of the event.

is\_final\_response [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.is_final_response "Link to this definition")

Whether the event is the final response of the agent.

get\_function\_calls [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.get_function_calls "Link to this definition")

Returns the function calls in the event.

Fields:

- `actions (google.adk.events.event_actions.EventActions)`

- `author (str)`

- `branch (str | None)`

- `id (str)`

- `invocation_id (str)`

- `long_running_tool_ids (set[str] | None)`

- `timestamp (float)`


_field_ actions _:EventActions_ _\[Optional\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id17 "Link to this definition")

The actions taken by the agent.

_field_ author _:str_ _\[Required\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id18 "Link to this definition")

‘user’ or the name of the agent, indicating who appended the event to the
session.

_field_ branch _:Optional\[str\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id19 "Link to this definition")

The branch of the event.

The format is like agent\_1.agent\_2.agent\_3, where agent\_1 is the parent of
agent\_2, and agent\_2 is the parent of agent\_3.

Branch is used when multiple sub-agent shouldn’t see their peer agents’
conversaction history.

_field_ id _:str_ _=''_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id20 "Link to this definition")

The unique identifier of the event.

_field_ invocation\_id _:str_ _=''_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id21 "Link to this definition")

The invocation ID of the event.

_field_ long\_running\_tool\_ids _:Optional\[set\[str\]\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id22 "Link to this definition")

Set of ids of the long running function calls.
Agent client will know from this field about which function call is long running.
only valid for function call event

_field_ timestamp _:float_ _\[Optional\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id23 "Link to this definition")

The timestamp of the event.

get\_function\_calls() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id24 "Link to this definition")

Returns the function calls in the event.

Return type:

`list`\[ `FunctionCall`\]

get\_function\_responses() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.get_function_responses "Link to this definition")

Returns the function responses in the event.

Return type:

`list`\[ `FunctionResponse`\]

has\_trailing\_code\_exeuction\_result() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.has_trailing_code_exeuction_result "Link to this definition")

Returns whether the event has a trailing code execution result.

Return type:

`bool`

is\_final\_response() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id25 "Link to this definition")

Returns whether the event is the final response of the agent.

Return type:

`bool`

model\_post\_init( _\_Event\_\_context_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.model_post_init "Link to this definition")

Post initialization logic for the event.

_static_ new\_id() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event.new_id "Link to this definition")_pydanticmodel_ google.adk.events.EventActions [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.EventActions "Link to this definition")

Bases: `BaseModel`

Represents the actions attached to an event.

Fields:

- `artifact_delta (dict[str, int])`

- `escalate (bool | None)`

- `requested_auth_configs (dict[str, google.adk.auth.auth_tool.AuthConfig])`

- `skip_summarization (bool | None)`

- `state_delta (dict[str, object])`

- `transfer_to_agent (str | None)`


_field_ artifact\_delta _:dict\[str,int\]_ _\[Optional\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.EventActions.artifact_delta "Link to this definition")

Indicates that the event is updating an artifact. key is the filename,
value is the version.

_field_ escalate _:Optional\[bool\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.EventActions.escalate "Link to this definition")

The agent is escalating to a higher level agent.

_field_ requested\_auth\_configs _:dict\[str,AuthConfig\]_ _\[Optional\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.EventActions.requested_auth_configs "Link to this definition")

Will only be set by a tool response indicating tool request euc.
dict key is the function call id since one function call response (from model)
could correspond to multiple function calls.
dict value is the required auth config.

_field_ skip\_summarization _:Optional\[bool\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.EventActions.skip_summarization "Link to this definition")

If true, it won’t call model to summarize function response.

Only used for function\_response event.

_field_ state\_delta _:dict\[str,object\]_ _\[Optional\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.EventActions.state_delta "Link to this definition")

Indicates that the event is updating the state with the given delta.

_field_ transfer\_to\_agent _:Optional\[str\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.EventActions.transfer_to_agent "Link to this definition")

If set, the event transfers to the specified agent.

# google.adk.examples module [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#module-google.adk.examples "Link to this heading")

_class_ google.adk.examples.BaseExampleProvider [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.examples.BaseExampleProvider "Link to this definition")

Bases: `ABC`

Base class for example providers.

This class defines the interface for providing examples for a given query.

_abstract_ get\_examples( _query_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.examples.BaseExampleProvider.get_examples "Link to this definition")

Returns a list of examples for a given query.

Return type:

`list`\[ [`Example`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.examples.Example "google.adk.examples.example.Example")\]

Parameters:

**query** – The query to get examples for.

Returns:

A list of Example objects.

_pydanticmodel_ google.adk.examples.Example [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.examples.Example "Link to this definition")

Bases: `BaseModel`

A few-shot example.

input [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.examples.Example.input "Link to this definition")

The input content for the example.

output [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.examples.Example.output "Link to this definition")

The expected output content for the example.

Fields:

- `input (google.genai.types.Content)`

- `output (list[google.genai.types.Content])`


_field_ input _: `Content`_ _\[Required\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id26 "Link to this definition")_field_ output _: `list`\[ `Content`\]_ _\[Required\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id27 "Link to this definition")_class_ google.adk.examples.VertexAiExampleStore( _examples\_store\_name_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.examples.VertexAiExampleStore "Link to this definition")

Bases: [`BaseExampleProvider`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.examples.BaseExampleProvider "google.adk.examples.base_example_provider.BaseExampleProvider")

Provides examples from Vertex example store.

Initializes the VertexAiExampleStore.

Parameters:

**examples\_store\_name** – The resource name of the vertex example store, in
the format of
`projects/{project}/locations/{location}/exampleStores/{example_store}`.

get\_examples( _query_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.examples.VertexAiExampleStore.get_examples "Link to this definition")

Returns a list of examples for a given query.

Return type:

`list`\[ [`Example`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.examples.Example "google.adk.examples.example.Example")\]

Parameters:

**query** – The query to get examples for.

Returns:

A list of Example objects.

# google.adk.memory module [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#module-google.adk.memory "Link to this heading")

_class_ google.adk.memory.BaseMemoryService [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.BaseMemoryService "Link to this definition")

Bases: `ABC`

Base class for memory services.

The service provides functionalities to ingest sessions into memory so that
the memory can be used for user queries.

_abstract_ add\_session\_to\_memory( _session_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.BaseMemoryService.add_session_to_memory "Link to this definition")

Adds a session to the memory service.

A session may be added multiple times during its lifetime.

Parameters:

**session** – The session to add.

_abstract_ search\_memory( _\*_, _app\_name_, _user\_id_, _query_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.BaseMemoryService.search_memory "Link to this definition")

Searches for sessions that match the query.

Return type:

`SearchMemoryResponse`

Parameters:

- **app\_name** – The name of the application.

- **user\_id** – The id of the user.

- **query** – The query to search for.


Returns:

A SearchMemoryResponse containing the matching memories.

_class_ google.adk.memory.InMemoryMemoryService [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.InMemoryMemoryService "Link to this definition")

Bases: [`BaseMemoryService`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.BaseMemoryService "google.adk.memory.base_memory_service.BaseMemoryService")

An in-memory memory service for prototyping purpose only.

Uses keyword matching instead of semantic search.

add\_session\_to\_memory( _session_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.InMemoryMemoryService.add_session_to_memory "Link to this definition")

Adds a session to the memory service.

A session may be added multiple times during its lifetime.

Parameters:

**session** – The session to add.

search\_memory( _\*_, _app\_name_, _user\_id_, _query_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.InMemoryMemoryService.search_memory "Link to this definition")

Prototyping purpose only.

Return type:

`SearchMemoryResponse`

session\_events _: `dict`\[ `str`, `list`\[ [`Event`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event "google.adk.events.event.Event")\]\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.InMemoryMemoryService.session_events "Link to this definition")

keys are app\_name/user\_id/session\_id

_class_ google.adk.memory.VertexAiRagMemoryService( _rag\_corpus=None_, _similarity\_top\_k=None_, _vector\_distance\_threshold=10_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.VertexAiRagMemoryService "Link to this definition")

Bases: [`BaseMemoryService`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.BaseMemoryService "google.adk.memory.base_memory_service.BaseMemoryService")

A memory service that uses Vertex AI RAG for storage and retrieval.

Initializes a VertexAiRagMemoryService.

Parameters:

- **rag\_corpus** – The name of the Vertex AI RAG corpus to use. Format:
`projects/{project}/locations/{location}/ragCorpora/{rag_corpus_id}`
or `{rag_corpus_id}`

- **similarity\_top\_k** – The number of contexts to retrieve.

- **vector\_distance\_threshold** – Only returns contexts with vector distance
smaller than the threshold..


add\_session\_to\_memory( _session_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.VertexAiRagMemoryService.add_session_to_memory "Link to this definition")

Adds a session to the memory service.

A session may be added multiple times during its lifetime.

Parameters:

**session** – The session to add.

search\_memory( _\*_, _app\_name_, _user\_id_, _query_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.VertexAiRagMemoryService.search_memory "Link to this definition")

Searches for sessions that match the query using rag.retrieval\_query.

Return type:

`SearchMemoryResponse`

# google.adk.models module [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#module-google.adk.models "Link to this heading")

Defines the interface to support a model.

_pydanticmodel_ google.adk.models.BaseLlm [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.BaseLlm "Link to this definition")

Bases: `BaseModel`

The BaseLLM class.

model [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.BaseLlm.model "Link to this definition")

The name of the LLM, e.g. gemini-1.5-flash or gemini-1.5-flash-001.

model\_config [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.BaseLlm.model_config "Link to this definition")

The model config

Show JSON schema

```
{
   "title": "BaseLlm",
   "description": "The BaseLLM class.\n\nAttributes:\n  model: The name of the LLM, e.g. gemini-1.5-flash or gemini-1.5-flash-001.\n  model_config: The model config",
   "type": "object",
   "properties": {
      "model": {
         "title": "Model",
         "type": "string"
      }
   },
   "required": [\
      "model"\
   ]
}

```

Fields:

- `model (str)`


_field_ model _:str_ _\[Required\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id28 "Link to this definition")

The name of the LLM, e.g. gemini-1.5-flash or gemini-1.5-flash-001.

connect( _llm\_request_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.BaseLlm.connect "Link to this definition")

Creates a live connection to the LLM.

Return type:

`BaseLlmConnection`

Parameters:

**llm\_request** – LlmRequest, the request to send to the LLM.

Returns:

BaseLlmConnection, the connection to the LLM.

_abstractasync_ generate\_content\_async( _llm\_request_, _stream=False_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.BaseLlm.generate_content_async "Link to this definition")

Generates one content from the given contents and tools.

Return type:

`AsyncGenerator`\[ `LlmResponse`, `None`\]

Parameters:

- **llm\_request** – LlmRequest, the request to send to the LLM.

- **stream** – bool = False, whether to do streaming call.


Yields:

a generator of types.Content.

For non-streaming call, it will only yield one Content.

For streaming call, it may yield more than one content, but all yielded
contents should be treated as one content by merging the
parts list.

_classmethod_ supported\_models() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.BaseLlm.supported_models "Link to this definition")

Returns a list of supported models in regex for LlmRegistry.

Return type:

`list`\[ `str`\]

_pydanticmodel_ google.adk.models.Gemini [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.Gemini "Link to this definition")

Bases: [`BaseLlm`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.BaseLlm "google.adk.models.base_llm.BaseLlm")

Integration for Gemini models.

model [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.Gemini.model "Link to this definition")

The name of the Gemini model.

Show JSON schema

```
{
   "title": "Gemini",
   "description": "Integration for Gemini models.\n\nAttributes:\n  model: The name of the Gemini model.",
   "type": "object",
   "properties": {
      "model": {
         "default": "gemini-1.5-flash",
         "title": "Model",
         "type": "string"
      }
   }
}

```

Fields:

- `model (str)`


_field_ model _:str_ _='gemini-1.5-flash'_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id29 "Link to this definition")

The name of the LLM, e.g. gemini-1.5-flash or gemini-1.5-flash-001.

connect( _llm\_request_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.Gemini.connect "Link to this definition")

Connects to the Gemini model and returns an llm connection.

Return type:

`BaseLlmConnection`

Parameters:

**llm\_request** – LlmRequest, the request to send to the Gemini model.

Yields:

BaseLlmConnection, the connection to the Gemini model.

_async_ generate\_content\_async( _llm\_request_, _stream=False_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.Gemini.generate_content_async "Link to this definition")

Sends a request to the Gemini model.

Return type:

`AsyncGenerator`\[ `LlmResponse`, `None`\]

Parameters:

- **llm\_request** – LlmRequest, the request to send to the Gemini model.

- **stream** – bool = False, whether to do streaming call.


Yields:

_LlmResponse_ – The model response.

_static_ supported\_models() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.Gemini.supported_models "Link to this definition")

Provides the list of supported models.

Return type:

`list`\[ `str`\]

Returns:

A list of supported models.

_property_ api\_client _:Client_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.Gemini.api_client "Link to this definition")

Provides the api client.

Returns:

The api client.

_class_ google.adk.models.LLMRegistry [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.LLMRegistry "Link to this definition")

Bases: `object`

Registry for LLMs.

_static_ new\_llm( _model_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.LLMRegistry.new_llm "Link to this definition")

Creates a new LLM instance.

Return type:

[`BaseLlm`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.BaseLlm "google.adk.models.base_llm.BaseLlm")

Parameters:

**model** – The model name.

Returns:

The LLM instance.

_static_ register( _llm\_cls_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.LLMRegistry.register "Link to this definition")

Registers a new LLM class.

Parameters:

**llm\_cls** – The class that implements the model.

_static_ resolve( _model_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.LLMRegistry.resolve "Link to this definition")

Resolves the model to a BaseLlm subclass.

Return type:

`type`\[ [`BaseLlm`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.models.BaseLlm "google.adk.models.base_llm.BaseLlm")\]

Parameters:

**model** – The model name.

Returns:

The BaseLlm subclass.

Raises:

**ValueError** – If the model is not found.

# google.adk.planners module [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#module-google.adk.planners "Link to this heading")

_class_ google.adk.planners.BasePlanner [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.BasePlanner "Link to this definition")

Bases: `ABC`

Abstract base class for all planners.

The planner allows the agent to generate plans for the queries to guide its
action.

_abstract_ build\_planning\_instruction( _readonly\_context_, _llm\_request_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.BasePlanner.build_planning_instruction "Link to this definition")

Builds the system instruction to be appended to the LLM request for planning.

Return type:

`Optional`\[ `str`\]

Parameters:

- **readonly\_context** – The readonly context of the invocation.

- **llm\_request** – The LLM request. Readonly.


Returns:

The planning system instruction, or None if no instruction is needed.

_abstract_ process\_planning\_response( _callback\_context_, _response\_parts_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.BasePlanner.process_planning_response "Link to this definition")

Processes the LLM response for planning.

Return type:

`Optional`\[ `List`\[ `Part`\]\]

Parameters:

- **callback\_context** – The callback context of the invocation.

- **response\_parts** – The LLM response parts. Readonly.


Returns:

The processed response parts, or None if no processing is needed.

_class_ google.adk.planners.BuiltInPlanner( _\*_, _thinking\_config_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.BuiltInPlanner "Link to this definition")

Bases: [`BasePlanner`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.BasePlanner "google.adk.planners.base_planner.BasePlanner")

The built-in planner that uses model’s built-in thinking features.

thinking\_config [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.BuiltInPlanner.thinking_config "Link to this definition")

Config for model built-in thinking features. An error
will be returned if this field is set for models that don’t support
thinking.

Initializes the built-in planner.

Parameters:

**thinking\_config** – Config for model built-in thinking features. An error
will be returned if this field is set for models that don’t support
thinking.

apply\_thinking\_config( _llm\_request_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.BuiltInPlanner.apply_thinking_config "Link to this definition")

Applies the thinking config to the LLM request.

Return type:

`None`

Parameters:

**llm\_request** – The LLM request to apply the thinking config to.

build\_planning\_instruction( _readonly\_context_, _llm\_request_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.BuiltInPlanner.build_planning_instruction "Link to this definition")

Builds the system instruction to be appended to the LLM request for planning.

Return type:

`Optional`\[ `str`\]

Parameters:

- **readonly\_context** – The readonly context of the invocation.

- **llm\_request** – The LLM request. Readonly.


Returns:

The planning system instruction, or None if no instruction is needed.

process\_planning\_response( _callback\_context_, _response\_parts_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.BuiltInPlanner.process_planning_response "Link to this definition")

Processes the LLM response for planning.

Return type:

`Optional`\[ `List`\[ `Part`\]\]

Parameters:

- **callback\_context** – The callback context of the invocation.

- **response\_parts** – The LLM response parts. Readonly.


Returns:

The processed response parts, or None if no processing is needed.

thinking\_config _: `ThinkingConfig`_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id30 "Link to this definition")

Config for model built-in thinking features. An error will be returned if this
field is set for models that don’t support thinking.

_class_ google.adk.planners.PlanReActPlanner [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.PlanReActPlanner "Link to this definition")

Bases: [`BasePlanner`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.BasePlanner "google.adk.planners.base_planner.BasePlanner")

Plan-Re-Act planner that constraints the LLM response to generate a plan before any action/observation.

Note: this planner does not require the model to support buil-in thinking
features or setting the thinking config.

build\_planning\_instruction( _readonly\_context_, _llm\_request_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.PlanReActPlanner.build_planning_instruction "Link to this definition")

Builds the system instruction to be appended to the LLM request for planning.

Return type:

`str`

Parameters:

- **readonly\_context** – The readonly context of the invocation.

- **llm\_request** – The LLM request. Readonly.


Returns:

The planning system instruction, or None if no instruction is needed.

process\_planning\_response( _callback\_context_, _response\_parts_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.planners.PlanReActPlanner.process_planning_response "Link to this definition")

Processes the LLM response for planning.

Return type:

`Optional`\[ `List`\[ `Part`\]\]

Parameters:

- **callback\_context** – The callback context of the invocation.

- **response\_parts** – The LLM response parts. Readonly.


Returns:

The processed response parts, or None if no processing is needed.

# google.adk.runners module [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#module-google.adk.runners "Link to this heading")

_class_ google.adk.runners.InMemoryRunner( _agent_, _\*_, _app\_name='InMemoryRunner'_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.InMemoryRunner "Link to this definition")

Bases: [`Runner`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.Runner "google.adk.runners.Runner")

An in-memory Runner for testing and development.

This runner uses in-memory implementations for artifact, session, and memory
services, providing a lightweight and self-contained environment for agent
execution.

agent [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.InMemoryRunner.agent "Link to this definition")

The root agent to run.

app\_name [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.InMemoryRunner.app_name "Link to this definition")

The application name of the runner. Defaults to
‘InMemoryRunner’.

Initializes the InMemoryRunner.

Parameters:

- **agent** – The root agent to run.

- **app\_name** – The application name of the runner. Defaults to
‘InMemoryRunner’.


_class_ google.adk.runners.Runner( _\*_, _app\_name_, _agent_, _artifact\_service=None_, _session\_service_, _memory\_service=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.Runner "Link to this definition")

Bases: `object`

The Runner class is used to run agents.

It manages the execution of an agent within a session, handling message
processing, event generation, and interaction with various services like
artifact storage, session management, and memory.

app\_name [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.Runner.app_name "Link to this definition")

The application name of the runner.

agent [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.Runner.agent "Link to this definition")

The root agent to run.

artifact\_service [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.Runner.artifact_service "Link to this definition")

The artifact service for the runner.

session\_service [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.Runner.session_service "Link to this definition")

The session service for the runner.

memory\_service [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.Runner.memory_service "Link to this definition")

The memory service for the runner.

Initializes the Runner.

Parameters:

- **app\_name** – The application name of the runner.

- **agent** – The root agent to run.

- **artifact\_service** – The artifact service for the runner.

- **session\_service** – The session service for the runner.

- **memory\_service** – The memory service for the runner.


agent _: [`BaseAgent`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.agents.BaseAgent "google.adk.agents.base_agent.BaseAgent")_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id31 "Link to this definition")

The root agent to run.

app\_name _: `str`_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id32 "Link to this definition")

The app name of the runner.

artifact\_service _: `Optional`\[ [`BaseArtifactService`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.artifacts.BaseArtifactService "google.adk.artifacts.base_artifact_service.BaseArtifactService")\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id33 "Link to this definition")

The artifact service for the runner.

close\_session( _session_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.Runner.close_session "Link to this definition")

Closes a session and adds it to the memory service (experimental feature).

Parameters:

**session** – The session to close.

memory\_service _: `Optional`\[ [`BaseMemoryService`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.memory.BaseMemoryService "google.adk.memory.base_memory_service.BaseMemoryService")\]_ _=None_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id34 "Link to this definition")

The memory service for the runner.

run( _\*_, _user\_id_, _session\_id_, _new\_message_, _run\_config=RunConfig(speech\_config=None_, _response\_modalities=None_, _save\_input\_blobs\_as\_artifacts=False_, _support\_cfc=False_, _streaming\_mode=<StreamingMode.NONE:None>_, _output\_audio\_transcription=None_, _max\_llm\_calls=500)_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.Runner.run "Link to this definition")

Runs the agent.

NOTE: This sync interface is only for local testing and convenience purpose.
Consider to use run\_async for production usage.

Return type:

`Generator`\[ [`Event`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event "google.adk.events.event.Event"), `None`, `None`\]

Parameters:

- **user\_id** – The user ID of the session.

- **session\_id** – The session ID of the session.

- **new\_message** – A new message to append to the session.

- **run\_config** – The run config for the agent.


Yields:

The events generated by the agent.

_async_ run\_async( _\*_, _user\_id_, _session\_id_, _new\_message_, _run\_config=RunConfig(speech\_config=None_, _response\_modalities=None_, _save\_input\_blobs\_as\_artifacts=False_, _support\_cfc=False_, _streaming\_mode=<StreamingMode.NONE:None>_, _output\_audio\_transcription=None_, _max\_llm\_calls=500)_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.Runner.run_async "Link to this definition")

Main entry method to run the agent in this runner.

Return type:

`AsyncGenerator`\[ [`Event`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event "google.adk.events.event.Event"), `None`\]

Parameters:

- **user\_id** – The user ID of the session.

- **session\_id** – The session ID of the session.

- **new\_message** – A new message to append to the session.

- **run\_config** – The run config for the agent.


Yields:

The events generated by the agent.

_async_ run\_live( _\*_, _session_, _live\_request\_queue_, _run\_config=RunConfig(speech\_config=None_, _response\_modalities=None_, _save\_input\_blobs\_as\_artifacts=False_, _support\_cfc=False_, _streaming\_mode=<StreamingMode.NONE:None>_, _output\_audio\_transcription=None_, _max\_llm\_calls=500)_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.runners.Runner.run_live "Link to this definition")

Runs the agent in live mode (experimental feature).

Return type:

`AsyncGenerator`\[ [`Event`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event "google.adk.events.event.Event"), `None`\]

Parameters:

- **session** – The session to use.

- **live\_request\_queue** – The queue for live requests.

- **run\_config** – The run config for the agent.


Yields:

The events generated by the agent.

session\_service _: [`BaseSessionService`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.BaseSessionService "google.adk.sessions.base_session_service.BaseSessionService")_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id35 "Link to this definition")

The session service for the runner.

# google.adk.sessions module [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#module-google.adk.sessions "Link to this heading")

_class_ google.adk.sessions.BaseSessionService [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.BaseSessionService "Link to this definition")

Bases: `ABC`

Base class for session services.

The service provides a set of methods for managing sessions and events.

append\_event( _session_, _event_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.BaseSessionService.append_event "Link to this definition")

Appends an event to a session object.

Return type:

[`Event`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event "google.adk.events.event.Event")

close\_session( _\*_, _session_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.BaseSessionService.close_session "Link to this definition")

Closes a session.

_abstract_ create\_session( _\*_, _app\_name_, _user\_id_, _state=None_, _session\_id=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.BaseSessionService.create_session "Link to this definition")

Creates a new session.

Return type:

[`Session`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session "google.adk.sessions.session.Session")

Parameters:

- **app\_name** – the name of the app.

- **user\_id** – the id of the user.

- **state** – the initial state of the session.

- **session\_id** – the client-provided id of the session. If not provided, a
generated ID will be used.


Returns:

The newly created session instance.

Return type:

session

_abstract_ delete\_session( _\*_, _app\_name_, _user\_id_, _session\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.BaseSessionService.delete_session "Link to this definition")

Deletes a session.

Return type:

`None`

_abstract_ get\_session( _\*_, _app\_name_, _user\_id_, _session\_id_, _config=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.BaseSessionService.get_session "Link to this definition")

Gets a session.

Return type:

`Optional`\[ [`Session`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session "google.adk.sessions.session.Session")\]

_abstract_ list\_events( _\*_, _app\_name_, _user\_id_, _session\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.BaseSessionService.list_events "Link to this definition")

Lists events in a session.

Return type:

`ListEventsResponse`

_abstract_ list\_sessions( _\*_, _app\_name_, _user\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.BaseSessionService.list_sessions "Link to this definition")

Lists all the sessions.

Return type:

`ListSessionsResponse`

_class_ google.adk.sessions.DatabaseSessionService( _db\_url_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.DatabaseSessionService "Link to this definition")

Bases: [`BaseSessionService`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.BaseSessionService "google.adk.sessions.base_session_service.BaseSessionService")

A session service that uses a database for storage.

Parameters:

**db\_url** – The database URL to connect to.

append\_event( _session_, _event_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.DatabaseSessionService.append_event "Link to this definition")

Appends an event to a session object.

Return type:

[`Event`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event "google.adk.events.event.Event")

create\_session( _\*_, _app\_name_, _user\_id_, _state=None_, _session\_id=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.DatabaseSessionService.create_session "Link to this definition")

Creates a new session.

Return type:

[`Session`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session "google.adk.sessions.session.Session")

Parameters:

- **app\_name** – the name of the app.

- **user\_id** – the id of the user.

- **state** – the initial state of the session.

- **session\_id** – the client-provided id of the session. If not provided, a
generated ID will be used.


Returns:

The newly created session instance.

Return type:

session

delete\_session( _app\_name_, _user\_id_, _session\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.DatabaseSessionService.delete_session "Link to this definition")

Deletes a session.

Return type:

`None`

get\_session( _\*_, _app\_name_, _user\_id_, _session\_id_, _config=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.DatabaseSessionService.get_session "Link to this definition")

Gets a session.

Return type:

`Optional`\[ [`Session`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session "google.adk.sessions.session.Session")\]

list\_events( _\*_, _app\_name_, _user\_id_, _session\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.DatabaseSessionService.list_events "Link to this definition")

Lists events in a session.

Return type:

`ListEventsResponse`

list\_sessions( _\*_, _app\_name_, _user\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.DatabaseSessionService.list_sessions "Link to this definition")

Lists all the sessions.

Return type:

`ListSessionsResponse`

_class_ google.adk.sessions.InMemorySessionService [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.InMemorySessionService "Link to this definition")

Bases: [`BaseSessionService`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.BaseSessionService "google.adk.sessions.base_session_service.BaseSessionService")

An in-memory implementation of the session service.

append\_event( _session_, _event_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.InMemorySessionService.append_event "Link to this definition")

Appends an event to a session object.

Return type:

[`Event`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event "google.adk.events.event.Event")

create\_session( _\*_, _app\_name_, _user\_id_, _state=None_, _session\_id=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.InMemorySessionService.create_session "Link to this definition")

Creates a new session.

Return type:

[`Session`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session "google.adk.sessions.session.Session")

Parameters:

- **app\_name** – the name of the app.

- **user\_id** – the id of the user.

- **state** – the initial state of the session.

- **session\_id** – the client-provided id of the session. If not provided, a
generated ID will be used.


Returns:

The newly created session instance.

Return type:

session

delete\_session( _\*_, _app\_name_, _user\_id_, _session\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.InMemorySessionService.delete_session "Link to this definition")

Deletes a session.

Return type:

`None`

get\_session( _\*_, _app\_name_, _user\_id_, _session\_id_, _config=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.InMemorySessionService.get_session "Link to this definition")

Gets a session.

Return type:

[`Session`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session "google.adk.sessions.session.Session")

list\_events( _\*_, _app\_name_, _user\_id_, _session\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.InMemorySessionService.list_events "Link to this definition")

Lists events in a session.

Return type:

`ListEventsResponse`

list\_sessions( _\*_, _app\_name_, _user\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.InMemorySessionService.list_sessions "Link to this definition")

Lists all the sessions.

Return type:

`ListSessionsResponse`

_pydanticmodel_ google.adk.sessions.Session [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session "Link to this definition")

Bases: `BaseModel`

Represents a series of interactions between a user and agents.

id [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session.id "Link to this definition")

The unique identifier of the session.

app\_name [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session.app_name "Link to this definition")

The name of the app.

user\_id [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session.user_id "Link to this definition")

The id of the user.

state [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session.state "Link to this definition")

The state of the session.

events [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session.events "Link to this definition")

The events of the session, e.g. user input, model response, function
call/response, etc.

last\_update\_time [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session.last_update_time "Link to this definition")

The last update time of the session.

Fields:

- `app_name (str)`

- `events (list[google.adk.events.event.Event])`

- `id (str)`

- `last_update_time (float)`

- `state (dict[str, Any])`

- `user_id (str)`


_field_ app\_name _: `str`_ _\[Required\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id36 "Link to this definition")

The name of the app.

_field_ events _: `list`\[ [`Event`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event "google.adk.events.event.Event")\]_ _\[Optional\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id37 "Link to this definition")

The events of the session, e.g. user input, model response, function
call/response, etc.

_field_ id _: `str`_ _\[Required\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id38 "Link to this definition")

The unique identifier of the session.

_field_ last\_update\_time _: `float`_ _=0.0_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id39 "Link to this definition")

The last update time of the session.

_field_ state _: `dict`\[ `str`, `Any`\]_ _\[Optional\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id40 "Link to this definition")

The state of the session.

_field_ user\_id _: `str`_ _\[Required\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#id41 "Link to this definition")

The id of the user.

_class_ google.adk.sessions.State( _value_, _delta_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.State "Link to this definition")

Bases: `object`

A state dict that maintain the current value and the pending-commit delta.

Parameters:

- **value** – The current value of the state dict.

- **delta** – The delta change to the current value that hasn’t been commited.


APP\_PREFIX _='app:'_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.State.APP_PREFIX "Link to this definition")TEMP\_PREFIX _='temp:'_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.State.TEMP_PREFIX "Link to this definition")USER\_PREFIX _='user:'_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.State.USER_PREFIX "Link to this definition")get( _key_, _default=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.State.get "Link to this definition")

Returns the value of the state dict for the given key.

Return type:

`Any`

has\_delta() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.State.has_delta "Link to this definition")

Whether the state has pending detla.

Return type:

`bool`

to\_dict() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.State.to_dict "Link to this definition")

Returns the state dict.

Return type:

`dict`\[ `str`, `Any`\]

update( _delta_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.State.update "Link to this definition")

Updates the state dict with the given delta.

_class_ google.adk.sessions.VertexAiSessionService( _project=None_, _location=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.VertexAiSessionService "Link to this definition")

Bases: [`BaseSessionService`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.BaseSessionService "google.adk.sessions.base_session_service.BaseSessionService")

Connects to the managed Vertex AI Session Service.

append\_event( _session_, _event_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.VertexAiSessionService.append_event "Link to this definition")

Appends an event to a session object.

Return type:

[`Event`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.Event "google.adk.events.event.Event")

create\_session( _\*_, _app\_name_, _user\_id_, _state=None_, _session\_id=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.VertexAiSessionService.create_session "Link to this definition")

Creates a new session.

Return type:

[`Session`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session "google.adk.sessions.session.Session")

Parameters:

- **app\_name** – the name of the app.

- **user\_id** – the id of the user.

- **state** – the initial state of the session.

- **session\_id** – the client-provided id of the session. If not provided, a
generated ID will be used.


Returns:

The newly created session instance.

Return type:

session

delete\_session( _\*_, _app\_name_, _user\_id_, _session\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.VertexAiSessionService.delete_session "Link to this definition")

Deletes a session.

Return type:

`None`

get\_session( _\*_, _app\_name_, _user\_id_, _session\_id_, _config=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.VertexAiSessionService.get_session "Link to this definition")

Gets a session.

Return type:

[`Session`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.Session "google.adk.sessions.session.Session")

list\_events( _\*_, _app\_name_, _user\_id_, _session\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.VertexAiSessionService.list_events "Link to this definition")

Lists events in a session.

Return type:

`ListEventsResponse`

list\_sessions( _\*_, _app\_name_, _user\_id_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.sessions.VertexAiSessionService.list_sessions "Link to this definition")

Lists all the sessions.

Return type:

`ListSessionsResponse`

# google.adk.tools module [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#module-google.adk.tools "Link to this heading")

_class_ google.adk.tools.APIHubToolset( _\*_, _apihub\_resource\_name_, _access\_token=None_, _service\_account\_json=None_, _name=''_, _description=''_, _lazy\_load\_spec=False_, _auth\_scheme=None_, _auth\_credential=None_, _apihub\_client=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.APIHubToolset "Link to this definition")

Bases: `object`

APIHubTool generates tools from a given API Hub resource.

Examples:

[\`\`](https://google.github.io/adk-docs/api-reference/google-adk.html#id42) \`
apihub\_toolset = APIHubToolset(

> apihub\_resource\_name=”projects/test-project/locations/us-central1/apis/test-api”,
> service\_account\_json=”…”,

)

\# Get all available tools
agent = LlmAgent(tools=apihub\_toolset.get\_tools())

\# Get a specific tool
agent = LlmAgent(tools=\[\
\
> …\
> apihub\_toolset.get\_tool(‘my\_tool’),\
\
## \]) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#id44 "Link to this heading")

**apihub\_resource\_name** is the resource name from API Hub. It must include

API name, and can optionally include API version and spec name.
\- If apihub\_resource\_name includes a spec resource name, the content of that

> spec will be used for generating the tools.

- If apihub\_resource\_name includes only an api or a version name, the
first spec of the first version of that API will be used.


Initializes the APIHubTool with the given parameters.

Examples:
[\`\`](https://google.github.io/adk-docs/api-reference/google-adk.html#id45) \`
apihub\_toolset = APIHubToolset(

> apihub\_resource\_name=”projects/test-project/locations/us-central1/apis/test-api”,
> service\_account\_json=”…”,

)

\# Get all available tools
agent = LlmAgent(tools=apihub\_toolset.get\_tools())

\# Get a specific tool
agent = LlmAgent(tools=\[\
\
> …\
> apihub\_toolset.get\_tool(‘my\_tool’),\
\
## \]) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html\#id47 "Link to this heading")

**apihub\_resource\_name** is the resource name from API Hub. It must include
API name, and can optionally include API version and spec name.
\- If apihub\_resource\_name includes a spec resource name, the content of that

> spec will be used for generating the tools.

- If apihub\_resource\_name includes only an api or a version name, the
first spec of the first version of that API will be used.


Example:
\\* projects/xxx/locations/us-central1/apis/apiname/…
\\* [https://console.cloud.google.com/apigee/api-hub/apis/apiname?project=xxx](https://console.cloud.google.com/apigee/api-hub/apis/apiname?project=xxx)

param apihub\_resource\_name:

The resource name of the API in API Hub.
Example: projects/test-project/locations/us-central1/apis/test-api.

param access\_token:

Google Access token. Generate with gcloud cli gcloud auth
auth print-access-token. Used for fetching API Specs from API Hub.

param service\_account\_json:

The service account config as a json string.
Required if not using default service credential. It is used for
creating the API Hub client and fetching the API Specs from API Hub.

param apihub\_client:

Optional custom API Hub client.

param name:

Name of the toolset. Optional.

param description:

Description of the toolset. Optional.

param auth\_scheme:

Auth scheme that applies to all the tool in the toolset.

param auth\_credential:

Auth credential that applies to all the tool in the
toolset.

param lazy\_load\_spec:

If True, the spec will be loaded lazily when needed.
Otherwise, the spec will be loaded immediately and the tools will be
generated during initialization.

get\_tool( _name_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.APIHubToolset.get_tool "Link to this definition")

Retrieves a specific tool by its name.

Return type:

`Optional`\[ `RestApiTool`\]

Example:
`` `
apihub_tool = apihub_toolset.get_tool('my_tool')
` ``

Parameters:

**name** – The name of the tool to retrieve.

Returns:

The tool with the given name, or None if no such tool exists.

get\_tools() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.APIHubToolset.get_tools "Link to this definition")

Retrieves all available tools.

Return type:

`List`\[ `RestApiTool`\]

Returns:

A list of all available RestApiTool objects.

_pydanticmodel_ google.adk.tools.AuthToolArguments [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.AuthToolArguments "Link to this definition")

Bases: `BaseModel`

the arguments for the special long running function tool that is used to

request end user credentials.

Fields:

- `auth_config (google.adk.auth.auth_tool.AuthConfig)`

- `function_call_id (str)`


_field_ auth\_config _: `AuthConfig`_ _\[Required\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.AuthToolArguments.auth_config "Link to this definition")_field_ function\_call\_id _: `str`_ _\[Required\]_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.AuthToolArguments.function_call_id "Link to this definition")_class_ google.adk.tools.BaseTool( _\*_, _name_, _description_, _is\_long\_running=False_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.BaseTool "Link to this definition")

Bases: `ABC`

The base class for all tools.

description _: `str`_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.BaseTool.description "Link to this definition")

The description of the tool.

is\_long\_running _: `bool`_ _=False_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.BaseTool.is_long_running "Link to this definition")

Whether the tool is a long running operation, which typically returns a
resource id first and finishes the operation later.

name _: `str`_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.BaseTool.name "Link to this definition")

The name of the tool.

_async_ process\_llm\_request( _\*_, _tool\_context_, _llm\_request_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.BaseTool.process_llm_request "Link to this definition")

Processes the outgoing LLM request for this tool.

Use cases:
\- Most common use case is adding this tool to the LLM request.
\- Some tools may just preprocess the LLM request before it’s sent out.

Return type:

`None`

Parameters:

- **tool\_context** – The context of the tool.

- **llm\_request** – The outgoing LLM request, mutable this method.


_async_ run\_async( _\*_, _args_, _tool\_context_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.BaseTool.run_async "Link to this definition")

Runs the tool with the given arguments and context.

NOTE
:rtype: `Any`

- Required if this tool needs to run at the client side.

- Otherwise, can be skipped, e.g. for a built-in GoogleSearch tool for
Gemini.


Parameters:

- **args** – The LLM-filled arguments.

- **ctx** – The context of the tool.


Returns:

The result of running the tool.

_class_ google.adk.tools.ExampleTool( _examples_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.ExampleTool "Link to this definition")

Bases: [`BaseTool`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.BaseTool "google.adk.tools.base_tool.BaseTool")

A tool that adds (few-shot) examples to the LLM request.

examples [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.ExampleTool.examples "Link to this definition")

The examples to add to the LLM request.

_async_ process\_llm\_request( _\*_, _tool\_context_, _llm\_request_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.ExampleTool.process_llm_request "Link to this definition")

Processes the outgoing LLM request for this tool.

Use cases:
\- Most common use case is adding this tool to the LLM request.
\- Some tools may just preprocess the LLM request before it’s sent out.

Return type:

`None`

Parameters:

- **tool\_context** – The context of the tool.

- **llm\_request** – The outgoing LLM request, mutable this method.


_class_ google.adk.tools.FunctionTool( _func_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.FunctionTool "Link to this definition")

Bases: [`BaseTool`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.BaseTool "google.adk.tools.base_tool.BaseTool")

A tool that wraps a user-defined Python function.

func [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.FunctionTool.func "Link to this definition")

The function to wrap.

_async_ run\_async( _\*_, _args_, _tool\_context_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.FunctionTool.run_async "Link to this definition")

Runs the tool with the given arguments and context.

NOTE
:rtype: `Any`

- Required if this tool needs to run at the client side.

- Otherwise, can be skipped, e.g. for a built-in GoogleSearch tool for
Gemini.


Parameters:

- **args** – The LLM-filled arguments.

- **ctx** – The context of the tool.


Returns:

The result of running the tool.

_class_ google.adk.tools.LongRunningFunctionTool( _func_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.LongRunningFunctionTool "Link to this definition")

Bases: [`FunctionTool`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.FunctionTool "google.adk.tools.function_tool.FunctionTool")

A function tool that returns the result asynchronously.

This tool is used for long-running operations that may take a significant
amount of time to complete. The framework will call the function. Once the
function returns, the response will be returned asynchronously to the
framework which is identified by the function\_call\_id.

Example:
`` `python
tool = LongRunningFunctionTool(a_long_running_function)
` ``

is\_long\_running [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.LongRunningFunctionTool.is_long_running "Link to this definition")

Whether the tool is a long running operation.

_class_ google.adk.tools.ToolContext( _invocation\_context_, _\*_, _function\_call\_id=None_, _event\_actions=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.ToolContext "Link to this definition")

Bases: `CallbackContext`

The context of the tool.

This class provides the context for a tool invocation, including access to
the invocation context, function call ID, event actions, and authentication
response. It also provides methods for requesting credentials, retrieving
authentication responses, listing artifacts, and searching memory.

invocation\_context [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.ToolContext.invocation_context "Link to this definition")

The invocation context of the tool.

function\_call\_id [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.ToolContext.function_call_id "Link to this definition")

The function call id of the current tool call. This id was
returned in the function call event from LLM to identify a function call.
If LLM didn’t return this id, ADK will assign one to it. This id is used
to map function call response to the original function call.

event\_actions [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.ToolContext.event_actions "Link to this definition")

The event actions of the current tool call.

_property_ actions _: [EventActions](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.events.EventActions "google.adk.events.event_actions.EventActions")_ [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.ToolContext.actions "Link to this definition")get\_auth\_response( _auth\_config_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.ToolContext.get_auth_response "Link to this definition")Return type:

`AuthCredential`

list\_artifacts() [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.ToolContext.list_artifacts "Link to this definition")

Lists the filenames of the artifacts attached to the current session.

Return type:

`list`\[ `str`\]

request\_credential( _auth\_config_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.ToolContext.request_credential "Link to this definition")Return type:

`None`

search\_memory( _query_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.ToolContext.search_memory "Link to this definition")

Searches the memory of the current user.

Return type:

`SearchMemoryResponse`

_class_ google.adk.tools.VertexAiSearchTool( _\*_, _data\_store\_id=None_, _search\_engine\_id=None_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.VertexAiSearchTool "Link to this definition")

Bases: [`BaseTool`](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.BaseTool "google.adk.tools.base_tool.BaseTool")

A built-in tool using Vertex AI Search.

data\_store\_id [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.VertexAiSearchTool.data_store_id "Link to this definition")

The Vertex AI search data store resource ID.

search\_engine\_id [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.VertexAiSearchTool.search_engine_id "Link to this definition")

The Vertex AI search engine resource ID.

Initializes the Vertex AI Search tool.

Parameters:

- **data\_store\_id** – The Vertex AI search data store resource ID in the format
of
“projects/{project}/locations/{location}/collections/{collection}/dataStores/{dataStore}”.

- **search\_engine\_id** – The Vertex AI search engine resource ID in the format of
“projects/{project}/locations/{location}/collections/{collection}/engines/{engine}”.


Raises:

- **ValueError** – If both data\_store\_id and search\_engine\_id are not specified

- **or both are specified.** –


_async_ process\_llm\_request( _\*_, _tool\_context_, _llm\_request_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.VertexAiSearchTool.process_llm_request "Link to this definition")

Processes the outgoing LLM request for this tool.

Use cases:
\- Most common use case is adding this tool to the LLM request.
\- Some tools may just preprocess the LLM request before it’s sent out.

Return type:

`None`

Parameters:

- **tool\_context** – The context of the tool.

- **llm\_request** – The outgoing LLM request, mutable this method.


google.adk.tools.exit\_loop( _tool\_context_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.exit_loop "Link to this definition")

Exits the loop.

Call this function only when you are instructed to do so.

google.adk.tools.transfer\_to\_agent( _agent\_name_, _tool\_context_) [¶](https://google.github.io/adk-docs/api-reference/google-adk.html#google.adk.tools.transfer_to_agent "Link to this definition")

Transfer the question to another agent.