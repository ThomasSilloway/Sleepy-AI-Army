## **Report: Goal Manifest Generation Strategy (Updated)**

**Date:** May 17, 2025  
**Objective:** To define a robust, maintainable, and reliable process for generating the goal-manifest.md file within the PoC7 LangGraph Orchestrator application. The primary challenge to overcome was the tendency of the previous Aider-based approach to overstep its mandate of manifest generation and attempt code modifications.  
**Chosen Approach:**  
The selected strategy involves a clear separation of concerns, leveraging specialized libraries and service classes:

1. **Structured Data Extraction via LLM:** An LLM (specifically Google's Gemini, accessed via the pydantic-ai library) will be used to analyze the task\_description\_content. Its sole responsibility will be to extract and infer key data points and populate a predefined Pydantic model, referred to as ManifestConfigLLM. The LLM will *not* be responsible for generating the final markdown structure.  
2. **Templating for Rendering:** The Jinja2 templating engine will be used to render the final goal-manifest.md file. It will take the data from the populated Pydantic model, along with other programmatically determined information (like timestamps), and fill in a structured markdown template.  
3. **Service-Oriented Architecture:** The logic for LLM interaction and template rendering will be encapsulated within dedicated service classes, making the LangGraph node (generate\_manifest\_node) a lean orchestrator.

**Libraries to be Used:**

1. **pydantic:** For defining the structure of the data to be extracted by the LLM (ManifestConfigLLM and its sub-models) and ensuring data validation.  
2. **pydantic-ai:** Specifically, its GeminiModel and model\_request functionality will be used to interact with the Gemini LLM and get structured output conforming to our Pydantic models.  
3. **Jinja2:** For rendering the final goal-manifest.md from a template file and a context dictionary.  
4. **asyncio:** Required for making asynchronous calls with pydantic-ai's model\_request, to be managed within the generate\_manifest\_node or the LlmPromptService.

**Class Structure and Interfaces:**  
Two new service classes will be introduced:  
**1\. LlmPromptService**

* **Purpose:** To abstract and manage interactions with LLMs for obtaining structured data based on Pydantic models. It will internally use pydantic-ai (initially with GeminiModel).  
* **Location:** src/services/llm\_prompt\_service.py  
* **Pydantic Models for LLM Output:** The service will work with Pydantic models defined elsewhere (e.g., src/models/manifest\_models.py), such as ManifestConfigLLM, ArtifactDetail, and AIQuestion, to specify the desired structure of the LLM's output.  
* **Service Class Interface:**  
  * **\_\_init\_\_(self, app\_config: AppConfig)**: The constructor will take an AppConfig instance for accessing necessary configurations like API keys or default model names.  
  * **async get\_structured\_output(self, messages: List\[Dict\[str, str\]\], output\_model\_type: Type\[PydanticModelType\], llm\_model\_name: str, model\_parameters: Optional\[Dict\[str, Any\]\] \= None) \-\> Optional\[PydanticModelType\]**:  
    * messages: A list of dictionaries representing the prompt, where each dictionary has "role" (e.g., "user", "system") and "content" keys. This allows for flexible prompt construction.  
    * output\_model\_type: The Pydantic class (e.g., ManifestConfigLLM) that the LLM should populate.  
    * llm\_model\_name: A string identifying the specific LLM to be called (e.g., "gemini-1.5-flash-latest").  
    * model\_parameters: An optional dictionary for LLM-specific parameters like temperature, max\_tokens, etc.  
    * Returns an instance of the output\_model\_type populated by the LLM, or None if an error occurs.

**2\. WriteFileFromTemplateService** (Formerly TemplateRenderingService)

* **Purpose:** To abstract the template rendering mechanism (initially Jinja2) and the subsequent file writing.  
* **Location:** src/services/write\_file\_from\_template\_service.py  
* **Service Class Interface:**  
  * **\_\_init\_\_(self)**: The constructor may not require arguments if it's stateless.  
  * **render\_and\_write\_file(self, template\_abs\_path\_str: str, context: Dict\[str, Any\], output\_abs\_path\_str: str) \-\> bool**:  
    * template\_abs\_path\_str: The absolute file path to the template file (e.g., a .j2 Jinja2 template).  
    * context: A dictionary containing the data to be used for rendering the template.  
    * output\_abs\_path\_str: The absolute file path where the rendered content should be written.  
    * Returns True if rendering and writing are successful, False otherwise.

**Orchestration in generate\_manifest\_node.py:**  
The generate\_manifest\_node in src/nodes/manifest\_generation.py will be refactored to:

1. Obtain instances of LlmPromptService and WriteFileFromTemplateService (and ChangelogService) from the runnable\_config.  
2. Retrieve necessary data like task\_description\_content, the path to the Jinja2 template (manifest\_template\_path), and the manifest\_output\_path from the WorkflowState.  
3. Construct the messages list for the LlmPromptService, instructing it to populate the ManifestConfigLLM model based on the task\_description\_content.  
4. Call llm\_prompt\_service.get\_structured\_output(...) to get the populated ManifestConfigLLM object.  
5. If the LLM call is successful, prepare a jinja\_context dictionary. This dictionary will include the data from the ManifestConfigLLM object, the full task\_description\_content, a programmatically generated generation\_timestamp, and other default/static values.  
6. Call write\_file\_from\_template\_service.render\_and\_write\_file(...) with the template path, the prepared context, and the target output file path for the manifest.  
7. Update WorkflowState with success/failure information based on the outcome of the service calls and file writing.  
8. Call the ChangelogService to record the event.

**Flow Summary:**  
WorkflowState (task description) \-\> generate\_manifest\_node (orchestrator) \-\> LlmPromptService (uses pydantic-ai with Gemini to fetch structured ManifestConfigLLM data) \-\> generate\_manifest\_node (prepares complete context for template) \-\> WriteFileFromTemplateService (uses Jinja2 to render the template with context and write to goal-manifest.md) \-\> generate\_manifest\_node (updates WorkflowState, calls ChangelogService).  
This approach provides a clear separation of concerns: the LLM focuses on data extraction and structured content suggestion via pydantic-ai, Python orchestrates and enriches this data, and the WriteFileFromTemplateService (using Jinja2) handles the final presentation and file output. This design aims for increased reliability, maintainability, and testability for the manifest generation process.