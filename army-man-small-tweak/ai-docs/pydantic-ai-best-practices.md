# Condensed Pydantic-AI best practices in sparse priming representation

**Pydantic-AI: Core Directives (v.May2025)**

* **SCHEMA_CENTRIC_DEVELOPMENT:**
    * `PRIORITIZE: Pydantic.BaseModel AS LLM_OUTPUT_CONTRACT`
    * `ENFORCE: STRICT_VALIDATION(Pydantic_Validators) ON LLM_RESPONSE`
    * `TARGET: DATA_INTEGRITY, RUNTIME_ERROR_REDUCTION`
    * `OPTIONAL: Pydantic.BaseModel FOR LLM_INPUT_CLARITY`

* **AGENT_ARCHITECTURE:**
    * `DESIGN_PRINCIPLE: MODULARITY, TASK_SPECIFIC_AGENTS`
    * `PATTERN: SEPARATION_OF_CONCERNS`
    * `UTILIZE: DEPENDENCY_INJECTION (CONTEXT, SERVICES, CONFIG)`
    * `MULTI_AGENT_STRATEGY: ORCHESTRATE (e.g., LangGraph)`
        * `REQUIREMENT: TYPE_ALIGNMENT(PydanticAI_Output, Orchestrator_Input)`

* **LLM_INTERACTION_TOOLING:**
    * `GOAL: LLM_MODEL_AGNOSTIC_IMPLEMENTATION`
    * `CONFIG: LLM_PROVIDERS, API_KEYS (SECURELY)`
    * `EXTEND_CAPABILITIES: FUNCTION_TOOLS`
        * `TOOL_ARGS_SCHEMA: Pydantic.BaseModel`
        * `REGISTRATION: @agent.tool | Agent(tools=[...])`
    * `PROMPT_ENGINEERING: CLEAR, EFFECTIVE_SYSTEM_PROMPTS`
    * `USER_EXPERIENCE: STREAMING_RESPONSES WITH IMMEDIATE_VALIDATION`

* **RELIABILITY_OBSERVABILITY:**
    * `ACCURACY_ENHANCEMENT: RAG_PATTERN (Retrieval Augmented Generation)`
    * `ERROR_HANDLING: LLM_API_ERRORS, Pydantic.ValidationError`
    * `RETRY_MECHANISM: PydanticAI.ModelRetry`
    * `MONITORING: INTEGRATE_LOGGING (e.g., Pydantic_Logfire)`
    * `TESTING: UNIT_TESTS, INTEGRATION_TESTS (FACILITATED_BY_SCHEMAS)`

* **DEV_OPS_MAINTENANCE:**
    * `KNOWLEDGE_SOURCE: OFFICIAL_PYDANTIC_AI_DOCS, GITHUB_ISSUES (LATEST)`
    * `ENVIRONMENT: ISOLATED_VIRTUAL_ENVIRONMENTS`
    * `COMMON_PITFALLS_AWARENESS: Jupyter_EventLoop_Conflict (nest-asyncio), API_Key_Config`
    * `ADVANCED_WORKFLOWS: Pydantic_Graph FOR COMPLEX_STATEFUL_LOGIC`