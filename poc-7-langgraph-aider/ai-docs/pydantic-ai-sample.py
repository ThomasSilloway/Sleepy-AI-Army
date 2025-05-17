import asyncio
import os
from pydantic import BaseModel, Field
from pydantic_ai.models import GeminiModel  # Import GeminiModel
from pydantic_ai.direct import model_request
from pydantic_ai.messages import UserMessage

# 1. Define the structure of the data you want to extract
class LocationInfo(BaseModel):
    city: str = Field(description="The name of the city")
    country: str = Field(description="The country where the city is located")
    population: int = Field(description="The estimated population of the city", ge=0)

async def main():
    # Check if the API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY environment variable not set.")
        print("Please get an API key from https://aistudio.google.com and set the variable.")
        return

    # 2. Initialize the GeminiModel
    # You can choose a specific Gemini model name.
    # Common choices include 'gemini-pro' or 'gemini-1.5-flash-latest' for text-based tasks.
    # Check the Google AI documentation for the latest model names.
    gemini_llm = GeminiModel(model="gemini-1.5-flash-latest") # Or "gemini-pro"

    # 3. Prepare your input message(s)
    input_text = "Tell me about Paris. I'm interested in its location and approximate population."
    messages = [
        UserMessage(content=f"Extract key information about the location mentioned in the text: {input_text}"),
        UserMessage(content=f"Ensure the output is a JSON object matching the LocationInfo schema with city, country, and population.")
    ]
    print(f"Input text: \"{input_text}\"")

    # 4. Make the direct model request
    try:
        response = await model_request(
            model=gemini_llm,
            messages=messages,
            output_type=LocationInfo,
            # You can add a system_prompt here or include it in messages as a SystemMessage
            # system_prompt="You are an expert geographer and data extractor."
        )

        # 5. The parsed Pydantic model is in response.data
        extracted_info: LocationInfo | None = response.data

        if extracted_info:
            print(f"\nExtracted Location Information:")
            print(f"  City: {extracted_info.city}")
            print(f"  Country: {extracted_info.country}")
            print(f"  Population: {extracted_info.population}")
        else:
            print("\nCould not extract location information or response was empty.")
            if response.error:
                print(f"  Error details: {response.error}")
            if response.raw:
                # Be cautious printing raw response if it's very large or contains sensitive info
                raw_output = str(response.raw)
                print(f"  Raw response (first 200 chars): {raw_output[:200]}...")


    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please ensure your GEMINI_API_KEY is correctly set, valid, and the model name is correct.")
        print("You might also need to enable the 'Generative Language API' in your Google Cloud project if using a project-linked key.")


if __name__ == "__main__":
    asyncio.run(main())
