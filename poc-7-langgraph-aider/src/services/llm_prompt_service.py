import asyncio
import logging
import os
from typing import Any, Optional, Type, TypeVar, List as PyList # Use PyList to avoid conflict if list is used as var name

from pydantic import BaseModel
from pydantic_ai.models import GeminiModel
from pydantic_ai.direct import model_request
from pydantic_ai.messages import UserMessage, SystemMessage, AIMessage, BaseMessage

from src.config import AppConfig # Assuming AppConfig is in src.config

logger = logging.getLogger(__name__)

# Define a TypeVar for more precise return type hinting
T = TypeVar('T', bound=BaseModel)

class LlmPromptService:
    """
    Service for interacting with LLMs (specifically Google Gemini via pydantic-ai)
    to get structured output based on Pydantic models.
    """
    def __init__(self, app_config: AppConfig):
        """
        Initializes the LlmPromptService.

        Args:
            app_config: The application configuration object.
        """
        self.app_config = app_config

    async def get_structured_output(
        self,
        messages: PyList[dict[str, str]],
        output_model_type: Type[T],
        llm_model_name: Optional[str] = None,
        model_parameters: Optional[dict[str, Any]] = None
    ) -> Optional[T]:
        """
        Sends prompts to the LLM and attempts to parse the response into the specified Pydantic model.

        Args:
            messages: A list of message dictionaries, each with "role" and "content".
                      Supported roles: "user", "system", "ai"/"assistant".
            output_model_type: The Pydantic model class to parse the LLM output into.
            llm_model_name: Optional. Specific Gemini model name to use.
                            If None, uses `app_config.gemini_text_model_name`.
            model_parameters: Optional. Dictionary of parameters to pass to the GeminiModel constructor
                              (e.g., temperature, top_p).

        Returns:
            An instance of `output_model_type` populated by the LLM, or None if an error occurs
            or the API key is not set.
        """
        if not os.getenv("GEMINI_API_KEY"):
            logger.error("GEMINI_API_KEY environment variable not set. Cannot make LLM calls.")
            print("GEMINI_API_KEY environment variable not set. Please set it to use the LLM service.")
            return None

        actual_model_name = llm_model_name or self.app_config.gemini_text_model_name
        if not actual_model_name:
            logger.error("LLM model name not configured or provided.")
            return None
        
        logger.debug(f"Using LLM model: {actual_model_name}")

        converted_messages: PyList[BaseMessage] = []
        for msg_dict in messages:
            role = msg_dict.get("role", "").lower()
            content = msg_dict.get("content")
            if not content:
                logger.warning(f"Message with role '{role}' has no content. Skipping.")
                continue
            
            if role == "user":
                converted_messages.append(UserMessage(content=content))
            elif role == "system":
                converted_messages.append(SystemMessage(content=content))
            elif role in ("ai", "assistant"):
                converted_messages.append(AIMessage(content=content))
            else:
                logger.warning(f"Unknown message role '{role}'. Treating as user message.")
                converted_messages.append(UserMessage(content=content))
        
        if not converted_messages:
            logger.error("No valid messages to send to LLM after conversion.")
            return None

        try:
            gemini_llm = GeminiModel(
                model=actual_model_name, 
                **(model_parameters or {})
            )
            
            logger.debug(f"Sending request to LLM with {len(converted_messages)} messages. Expecting {output_model_type.__name__}.")
            response = await model_request(
                model=gemini_llm,
                messages=converted_messages,
                output_type=output_model_type,
            )

            extracted_data: Optional[T] = response.data
            if extracted_data:
                logger.info(f"Successfully extracted structured data of type {output_model_type.__name__}.")
                return extracted_data
            else:
                logger.error(f"Could not extract data for {output_model_type.__name__}. Response was empty or parsing failed.")
                if response.error:
                    logger.error(f"  Error details: {response.error}")
                if response.raw:
                    raw_output = str(response.raw)
                    logger.error(f"  Raw response (first 300 chars): {raw_output[:300]}...")
                return None

        except Exception as e:
            logger.error(f"An error occurred during LLM request or processing: {e}", exc_info=True)
            print(f"\nAn error occurred with the LLM service: {e}")
            print("Please ensure your GEMINI_API_KEY is correctly set, valid, and the model name is correct.")
            print("You might also need to enable the 'Generative Language API' in your Google Cloud project.")
            return None
