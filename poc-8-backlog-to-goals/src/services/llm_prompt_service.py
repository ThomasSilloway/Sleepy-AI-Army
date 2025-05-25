import logging
import os
import re
from typing import Any, Optional, TypeVar

from pydantic import BaseModel
from pydantic_ai.direct import model_request
from pydantic_ai.messages import (
    ModelRequest,
    ModelRequestPart,  # Union of request part types
    ModelResponse,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.models import ModelRequestParameters  # For temperature, etc.
from src.config import AppConfig

logger = logging.getLogger(__name__)

# Define a TypeVar for more precise return type hinting
T = TypeVar('T', bound=BaseModel)

class LlmPromptService:
    """
    Service for interacting with LLMs (specifically Google Gemini via pydantic-ai)
    to get structured output based on Pydantic models.
    Uses pydantic_ai.direct.model_request.
    """
    def __init__(self, app_config: AppConfig):
        """
        Initializes the LlmPromptService.

        Args:
            app_config: The application configuration object.
        """
        self.app_config = app_config
        self.gemini_model_prefix = "google-gla:" # Standard prefix for pydantic-ai with Gemini

    def _strip_json_fencing(self, text_content: str) -> str:
        """
        Strips Markdown JSON fencing (```json ... ```) from a string.
        """
        match = re.search(r"```json\s*(.*?)\s*```", text_content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        # Fallback for cases where only ``` might be present or if there's no explicit "json"
        match_generic = re.search(r"```\s*(.*?)\s*```", text_content, re.DOTALL)
        if match_generic:
            return match_generic.group(1).strip()
        return text_content # Return original if no fencing is found

    async def get_structured_output(
        self,
        messages: list[dict[str, str]],
        output_pydantic_model_type: type[T],
        llm_model_name: Optional[str] = None, # Base model name, e.g., "gemini-1.5-flash-latest"
        model_parameters: Optional[dict[str, Any]] = None
    ) -> Optional[T]:
        """
        Sends prompts to the LLM and attempts to parse the response into the specified Pydantic model.

        Args:
            messages: A list of message dictionaries, each with "role" and "content".
                      Supported roles: "user", "system". "ai"/"assistant" roles are logged and skipped.
            output_pydantic_model_type: The Pydantic model class to parse the LLM output into.
            llm_model_name: Optional. Specific base Gemini model name to use (e.g., "gemini-1.5-flash-latest").
                            If None, an error is logged and None is returned.
            model_parameters: Optional. Dictionary of parameters to pass to the LLM
                              (e.g., {"temperature": 0.7, "top_p": 0.9}).

        Returns:
            An instance of `output_pydantic_model_type` populated by the LLM, or None if an error occurs
            or the API key is not set.
        """
        if not os.getenv("GEMINI_API_KEY"):
            logger.error("GEMINI_API_KEY environment variable not set. Cannot make LLM calls.")
            print("GEMINI_API_KEY environment variable not set. Please set it to use the LLM service.")
            return None

        if not llm_model_name:
            logger.error("LLM model name not provided to get_structured_output. Cannot proceed.")
            return None

        prefixed_model_name = f"{self.gemini_model_prefix}{llm_model_name}"
        logger.debug(f"Using LLM model: {prefixed_model_name}")

        request_parts: list[ModelRequestPart] = []
        for msg_dict in messages:
            role = msg_dict.get("role", "").lower()
            content = msg_dict.get("content")
            if not content:
                logger.warning(f"Message with role '{role}' has no content. Skipping.")
                continue

            if role == "user":
                request_parts.append(UserPromptPart(content=content))
            elif role == "system":
                request_parts.append(SystemPromptPart(content=content))
            elif role in ("ai", "assistant"):
                assistant_text_part = TextPart(content=content)
                # ModelResponse has other optional fields like 'usage', 'model_name', 'timestamp'.
                # If these are not available from your history source, they will take default values.
                assistant_response = ModelResponse(parts=[assistant_text_part])
                request_parts.append(assistant_response)
            else:
                logger.warning(f"Unknown message role '{role}'. Treating as user message.")
                request_parts.append(UserPromptPart(content=content))

        if not request_parts:
            logger.error("No valid ModelRequestParts to send to LLM after conversion.")
            return None

        mrp_instance: Optional[ModelRequestParameters] = None
        if model_parameters:
            try:
                mrp_instance = ModelRequestParameters(**model_parameters)
                logger.debug(f"Using model parameters: {model_parameters}")
            except Exception as e:
                logger.warning(f"Could not instantiate ModelRequestParameters from {model_parameters}: {e}. Proceeding without them.")

        try:
            logger.debug(f"Sending request to LLM with {len(request_parts)} parts. Expecting {output_pydantic_model_type.__name__}.")
            for i, part in enumerate(request_parts):
                logger.debug(f"  Part {i+1}: Type={part.part_kind}, Content='{str(part.content)[:100]}...'")

            # Consolidate parts into a single ModelRequest
            # Instructions can also be added here if they are dynamic per request
            # For now, assuming instructions are handled by SystemPromptParts or globally
            model_req_object = ModelRequest(parts=request_parts, instructions=None)

            response: ModelResponse = await model_request(
                model=prefixed_model_name,
                messages=[model_req_object], # Pass a list containing one ModelRequest
                model_request_parameters=mrp_instance
            )

            # Extract the data from ModelResponse and parse it into the Pydantic model
            if response and response.parts:
                # Assuming the first part is the relevant one for parsing
                first_part = response.parts[0]
                if isinstance(first_part, TextPart):
                    logger.debug(f"Received response from LLM: {first_part.content}")
                    # Strip any json fencing characters if needed
                    stripped_content = self._strip_json_fencing(first_part.content)
                    logger.debug(f"Received response from LLM (stripped): {stripped_content}")

                    # Attempt to parse the content into the specified Pydantic model
                    try:
                        parsed_result = output_pydantic_model_type.model_validate_json(stripped_content)
                        logger.debug(f"Parsed result: {parsed_result}")
                        return parsed_result
                    except Exception as e:
                        logger.error(f"Failed to parse LLM response into {output_pydantic_model_type.__name__}: {e}")
                        return None
                else:
                    logger.warning("First part of the response is not a TextPart. Cannot parse.")
                    return None
            else:
                logger.warning("No valid parts in LLM response. Cannot parse.")
                return None

        except Exception as e:
            logger.error(f"An error occurred during LLM request or processing: {e}", exc_info=True)
            print(f"\nAn error occurred with the LLM service: {e}")
            return None
