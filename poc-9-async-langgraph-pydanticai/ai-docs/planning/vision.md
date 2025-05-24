# Vision Statement for PoC-9: Async LangGraph with Pydantic-AI

## 1. Core Goal

The primary goal of PoC-9 is to demonstrate the correct and effective use of `asyncio` throughout a LangGraph-based application that leverages `pydantic-ai` for interactions with Large Language Models (LLMs). This PoC will rectify the `asyncio.run()` anti-pattern observed in PoC-7 by ensuring the entire application runs within a single `asyncio.run(main())` call in the main execution script.

## 2. Background & Problem Addressed

PoC-7 highlighted a common challenge: integrating asynchronous libraries (like `pydantic-ai` which uses async HTTP calls for LLM communication) into a synchronous or mixed-async workflow. The use of `nest_asyncio` and multiple `asyncio.run()` calls in PoC-7 served as a temporary workaround but introduced potential instability and is not a recommended practice for robust `asyncio` applications. This can lead to "event loop already running" errors or unexpected behavior with nested loops.

PoC-9 aims to establish a clean, fully asynchronous pattern from the outset.

## 3. What This PoC Will Demonstrate

This PoC will build a very basic LangGraph application with the following key characteristics:

*   **Fully Asynchronous Execution:** The main application entry point will be an `async def main()` function, executed once via `asyncio.run(main())`.
*   **Async LangGraph Nodes:** All nodes within the LangGraph will be `async def` functions.
*   **Correct `pydantic-ai` Integration:** An `LLMPromptService` (similar to PoC-7's) will be used, but its asynchronous methods will be correctly `await`ed from within the async graph nodes.
*   **Simple Workflow:** A minimal graph (e.g., a start node and a summarization node) will be implemented to showcase the async flow. The summarization node will use the `LLMPromptService` to process some text with an LLM (e.g., `gemini-2.0-flash-exp`).
*   **Clear Structure:** The file and directory structure will largely mirror PoC-7 for familiarity, but internal implementations will be async-native.
*   **No `nest_asyncio`:** This POC will explicitly avoid the use of `nest_asyncio`.

## 4. Why This PoC is Important

Successfully demonstrating these capabilities in PoC-9 will:

*   Provide a clear, correct template for future LangGraph and `pydantic-ai` based projects that require asynchronous operations.
*   Validate that `asyncio` can be managed cleanly without resorting to workarounds like `nest_asyncio`.
*   Serve as a foundational example for building more complex, scalable, and stable asynchronous AI applications.
*   Reinforce best practices for `asyncio` programming within the context of LLM orchestration.

This PoC focuses on the fundamental `asyncio` integration with LangGraph and `pydantic-ai`, setting a solid architectural precedent.
