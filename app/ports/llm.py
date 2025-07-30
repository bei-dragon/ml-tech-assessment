import pydantic
from abc import ABC, abstractmethod


class LLm(ABC):
    @abstractmethod
    def run_completion(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]) -> pydantic.BaseModel:
        """A synchronous method for LLM completion."""
        pass

    @abstractmethod
    async def run_completion_async(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]) -> pydantic.BaseModel:
        """An asynchronous method for LLM completion."""
        pass