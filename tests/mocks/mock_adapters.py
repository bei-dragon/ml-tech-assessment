# File: tests/mocks/mock_adapters.py

import pydantic
from app import ports # <--- CHANGE THIS: Import the 'ports' module
# The specific imports below are no longer necessary if 'ports' is imported
# from app.ports.llm import LLm
# from app.ports.repository import AnalysisRepository

class MockLLMAdapter(ports.LLm):
    """
    A mock implementation of the LLm port for testing purposes.
    This adapter does not make any external API calls and returns a
    fixed, predictable response. It simulates the behavior of the
    real OpenAI adapter's structured output.
    """
    
    def run_completion(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]) -> pydantic.BaseModel:
        # This synchronous version is not used by our async API, but we implement it for completeness.
        mock_data = {
            "summary": "This is a mock summary.",
            "action_items": ["Mock action item 1", "Mock action item 2"]
        }
        # We instantiate the DTO that the use case expects, just like the real adapter.
        return dto(**mock_data)

    async def run_completion_async(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]) -> pydantic.BaseModel:
        # The async version is what our API tests will use.
        mock_data = {
            "summary": "This is a mock summary.",
            "action_items": ["Mock action item 1", "Mock action item 2"]
        }
        return dto(**mock_data)
