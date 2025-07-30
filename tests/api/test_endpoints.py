import uuid
import pytest
from fastapi.testclient import TestClient

# Main app object
from app.api.main import app

# Dependencies to be overridden and the classes needed to create the mocks
from app.api import dependencies
from app.core import use_cases
from app.adapters.persistence import InMemoryAnalysisRepository, IN_MEMORY_DB
from tests.mocks.mock_adapters import MockLLMAdapter

@pytest.fixture
def client(monkeypatch):
    """
    A pytest fixture that prepares a fully mocked TestClient for each test.
    This is the standard way to ensure tests are isolated and do not make real network calls.
    """
    # Step 1: Set dummy environment variables. This satisfies the Pydantic model's
    # validation when the app first loads, preventing startup errors.
    monkeypatch.setenv("OPENAI_API_KEY", "a-mock-key-that-will-not-be-used")
    monkeypatch.setenv("OPENAI_MODEL", "a-mock-model")

    # Step 2: Create the mock and real objects that our use cases will need.
    mock_llm_adapter = MockLLMAdapter()
    in_memory_repo = InMemoryAnalysisRepository()
    
    # Step 3: Clear the global in-memory database before each test runs.
    # This is crucial to prevent data from one test leaking into another.
    IN_MEMORY_DB.clear()

    # Step 4: Define the override functions. FastAPI will use these instead of the real ones.
    # We are replacing the entire use case factory.
    def get_mock_analyze_uc_override():
        return use_cases.AnalyzeTranscriptUseCase(mock_llm_adapter, in_memory_repo)

    def get_mock_get_analysis_uc_override():
        return use_cases.GetAnalysisUseCase(in_memory_repo)

    def get_mock_analyze_multiple_uc_override():
        return use_cases.AnalyzeMultipleTranscriptsUseCase(mock_llm_adapter, in_memory_repo)

    # Step 5: Apply the overrides to the app. This is the core of the mocking strategy.
    app.dependency_overrides[dependencies.get_analyze_transcript_use_case] = get_mock_analyze_uc_override
    app.dependency_overrides[dependencies.get_get_analysis_use_case] = get_mock_get_analysis_uc_override
    app.dependency_overrides[dependencies.get_analyze_multiple_transcripts_use_case] = get_mock_analyze_multiple_uc_override
    
    # Step 6: Create and yield the test client *after* the mocks are in place.
    with TestClient(app) as test_client:
        yield test_client

    # Step 7: Cleanup runs after each test, clearing the overrides for full isolation.
    app.dependency_overrides.clear()


# --- Tests ---
# Each test now takes `client` as an argument, which is the fully mocked TestClient.

def test_analyze_transcript_success(client):
    """
    Tests the successful analysis of a single transcript.
    Verifies that the endpoint returns 201 and the mock data.
    """
    response = client.post("/v1/analysis?transcript=some-text-here")
    
    assert response.status_code == 201
    
    data = response.json()
    assert data["summary"] == "This is a mock summary."
    assert data["action_items"] == ["Mock action item 1", "Mock action item 2"]
    assert "id" in data

def test_analyze_transcript_empty_input(client):
    """
    Tests the validation for an empty transcript.
    Verifies that the endpoint returns 400.
    """
    response = client.post("/v1/analysis?transcript=")
    assert response.status_code == 400
    assert response.json()["detail"] == "Transcript cannot be empty."

def test_get_analysis_by_id_success_and_not_found(client):
    """
    Tests retrieving an analysis by ID, including success and failure cases.
    """
    # 1. First, create an analysis to ensure there's something in our in-memory repo.
    create_response = client.post("/v1/analysis?transcript=data-for-retrieval")
    assert create_response.status_code == 201
    created_data = create_response.json()
    analysis_id = created_data["id"]

    # 2. Test successful retrieval
    get_response = client.get(f"/v1/analysis/{analysis_id}")
    assert get_response.status_code == 200
    retrieved_data = get_response.json()
    assert retrieved_data["id"] == analysis_id
    assert retrieved_data["summary"] == "This is a mock summary."

    # 3. Test failure case (analysis not found)
    random_id = uuid.uuid4()
    not_found_response = client.get(f"/v1/analysis/{random_id}")
    assert not_found_response.status_code == 404
    assert not_found_response.json()["detail"] == f"Analysis with ID {random_id} not found."

def test_analyze_batch_transcripts_success(client):
    """
    Tests the successful concurrent analysis of multiple transcripts.
    """
    request_body = {
        "transcripts": ["transcript 1", "transcript 2"]
    }
    response = client.post("/v1/analysis/batch", json=request_body)

    assert response.status_code == 201
    data = response.json()
    
    assert "results" in data
    assert len(data["results"]) == 2
    
    # Check the content of the first result to ensure it used the mock
    first_result = data["results"][0]
    assert first_result["summary"] == "This is a mock summary."
    assert first_result["action_items"] == ["Mock action item 1", "Mock action item 2"]