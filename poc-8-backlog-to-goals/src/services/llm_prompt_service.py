# poc-8-backlog-to-goals/src/services/llm_prompt_service.py
"""
Provides the LlmPromptService class for interacting with Language Models (LLMs),
specifically Google Gemini, using the pydantic-ai library. It facilitates
sending structured prompts and receiving responses parsed into Pydantic models.
"""

import logging
import os
import re
from typing import Any, Optional, TypeVar, List, Dict # Added List, Dict

from pydantic import BaseModel
from pydantic_ai.direct import model_request
from pydantic_ai.messages import (
    ModelRequest,
    ModelRequestPart,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.models import ModelRequestParameters
from pydantic_ai.exceptions import ModelError as PydanticAIModelError
import httpx

from src.config import AppConfig

logger: logging.Logger = logging.getLogger(__name__)

# Define a TypeVar for more precise return type hinting
T = TypeVar('T', bound=BaseModel)

class LlmPromptService:
    """
    Service for interacting with LLMs (specifically Google Gemini via pydantic-ai)
    to get structured output based on Pydantic models.
    Uses pydantic_ai.direct.model_request.
    """
    app_config: AppConfig
    gemini_model_prefix: str

    def __init__(self, app_config: AppConfig) -> None:
        """
        Initializes the LlmPromptService.

        Args:
            app_config: The application configuration object.
        """
        self.app_config = app_config
        self.gemini_model_prefix = "google-gla:" # Standard prefix for pydantic-ai with Gemini

    def _strip_json_fencing(self, text_content: str) -> str:
        """
        Strips Markdown JSON fencing (e.g., ```json ... ```) from a string.

        Args:
            text_content: The text content, potentially with JSON fencing.

        Returns:
            The text content with JSON fencing removed, or the original string if no fencing is found.
        """
        # Regex to find ```json ... ``` or ``` ... ```
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text_content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return text_content

    async def get_structured_output(
        self,
        messages: List[Dict[str, str]],
        output_pydantic_model_type: type[T],
        llm_model_name: Optional[str] = None,
        model_parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[T]:
        """
        Sends prompts to the LLM and attempts to parse the response into the specified Pydantic model.

        Args:
            messages: A list of message dictionaries, each with "role" and "content".
                      Supported roles: "user", "system". "ai"/"assistant" roles are logged and skipped.
            output_pydantic_model_type: The Pydantic model class to parse the LLM output into.
            llm_model_name: Specific base Gemini model name to use (e.g., "gemini-1.5-flash-latest").
                            If None, an error is logged, and None is returned.
            model_parameters: Optional dictionary of parameters to pass to the LLM
                              (e.g., {"temperature": 0.7, "top_p": 0.9}).

        Returns:
            An instance of `output_pydantic_model_type` populated by the LLM, or None if an error occurs.
        """
        if not os.getenv("GEMINI_API_KEY"): # Checked by pydantic-ai, but good for early exit/clearer error
            logger.error("GEMINI_API_KEY environment variable not set. Cannot make LLM calls.")
            return None

        if not llm_model_name:
            logger.error("LLM model name not provided to get_structured_output. Cannot proceed.")
            return None

        prefixed_model_name: str = f"{self.gemini_model_prefix}{llm_model_name}"
        logger.debug(f"Using LLM model: {prefixed_model_name}")

        request_parts: List[ModelRequestPart] = []
        for msg_dict in messages:
            role: str = msg_dict.get("role", "").lower()
            content: Optional[str] = msg_dict.get("content")
            if not content:
                logger.warning(f"Message with role '{role}' has no content. Skipping.")
                continue

            if role == "user":
                request_parts.append(UserPromptPart(content=content))
            elif role == "system":
                request_parts.append(SystemPromptPart(content=content))
            elif role in ("ai", "assistant"):
                logger.info(f"AI/Assistant message found with content: '{content[:100]}...'. This version of pydantic-ai's Gemini adapter may not support passing assistant history this way. Skipping this part for now.")
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
            except Exception as e: # Catching broad Exception as Pydantic validation errors can vary
                logger.warning(f"Could not instantiate ModelRequestParameters from {model_parameters}: {e}. Proceeding without them.")

        try:
            logger.debug(f"Sending request to LLM with {len(request_parts)} parts. Expecting {output_pydantic_model_type.__name__}.")
            for i, part in enumerate(request_parts): # This loop is for debug logging
                if hasattr(part, 'part_kind') and hasattr(part, 'content'):
                    # Standard ModelRequestPart types like UserPromptPart, SystemPromptPart
                    logger.debug(f"  Part {i+1}: Type={getattr(part, 'part_kind', type(part).__name__)}, Content='{str(getattr(part, 'content', 'N/A'))[:100]}...'")
                elif isinstance(part, ModelResponse) and part.parts and hasattr(part.parts[0], 'content'):
                     # This case should not happen anymore as ModelResponse parts are skipped
                    logger.debug(f"  Part {i+1}: Type=ModelResponse, Content='{str(getattr(part.parts[0], 'content', 'N/A'))[:100]}...'")
                else:
                    logger.debug(f"  Part {i+1}: Type={type(part).__name__}, Content not directly loggable in this format.")
            
            model_req_object: ModelRequest = ModelRequest(parts=request_parts, instructions=None)

            response: ModelResponse = await model_request(
                model=prefixed_model_name,
                messages=[model_req_object],
                model_request_parameters=mrp_instance
            )

            if response and response.parts:
                first_part = response.parts[0]
                if isinstance(first_part, TextPart):
                    stripped_content: str = self._strip_json_fencing(first_part.content)
                    logger.debug(f"Received response from LLM (stripped): {stripped_content}")
                    try:
                        parsed_result: T = output_pydantic_model_type.model_validate_json(stripped_content)
                        logger.debug(f"Parsed result: {parsed_result}")
                        return parsed_result
                    except Exception as e: # More specific Pydantic ValidationError could be caught
                        logger.error(f"Failed to parse LLM response into {output_pydantic_model_type.__name__}: {e}", exc_info=True)
                        return None
                else:
                    logger.warning(f"First part of the response is not a TextPart (Type: {type(first_part).__name__}). Cannot parse.")
                    return None
            else:
                logger.warning("No valid parts in LLM response. Cannot parse.")
                return None
        
        except PydanticAIModelError as e:
            logger.error(f"Pydantic-AI specific error during LLM request for model {prefixed_model_name}: {e}", exc_info=True)
            return None
        except httpx.RequestError as e:
            logger.error(f"HTTP network error during LLM request for model {prefixed_model_name}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during LLM request or processing for model {prefixed_model_name}: {e}", exc_info=True)
            return None
