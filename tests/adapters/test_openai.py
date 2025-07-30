import os
import pytest
from app import configurations
import pydantic
from tests.adapters import mock_data
from app.adapters import openai


class Response(pydantic.BaseModel):
    summary: str
    action_items: list[str]

# This decorator will skip the test if the OPENAI_API_KEY is not in the environment
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY environment variable not set")
def test_openai_adapter() -> None:
    # Configuration
    env_variables = configurations.EnvConfigs()

    system_prompt = mock_data.SYSTEM_PROMPT
    raw_user_prompt = mock_data.RAW_USER_PROMPT
    transcript = mock_data.TRANSCRIPT

    user_prompt = raw_user_prompt.format(
        transcript=transcript)
    openai_adapter = openai.OpenAIAdapter(env_variables.OPENAI_API_KEY, env_variables.OPENAI_MODEL)

    # action
    response = openai_adapter.run_completion(system_prompt, user_prompt, Response)
    serialized_response = response.model_dump()

    # assert
    print(serialized_response)
    assert "summary" in serialized_response.keys()
    assert "action_items" in serialized_response.keys()