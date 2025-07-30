from functools import lru_cache
from app import configurations, adapters, ports, prompts
from app.core import use_cases

@lru_cache(maxsize=1)
def get_env_configs() -> configurations.EnvConfigs:
    """Caches environment configurations to avoid repeated file reads."""
    return configurations.EnvConfigs()

@lru_cache(maxsize=1)
def get_llm_adapter() -> ports.LLm:
    """Creates a singleton instance of the OpenAI adapter."""
    configs = get_env_configs()
    return adapters.openai.OpenAIAdapter(
        api_key=configs.OPENAI_API_KEY,
        model=configs.OPENAI_MODEL
    )

@lru_cache(maxsize=1)
def get_repo_adapter() -> ports.AnalysisRepository:
    """Creates a singleton instance of the in-memory repository."""
    return adapters.persistence.InMemoryAnalysisRepository()

# --- Use Case Providers ---

def get_analyze_transcript_use_case() -> use_cases.AnalyzeTranscriptUseCase:
    """Factory for the AnalyzeTranscriptUseCase."""
    return use_cases.AnalyzeTranscriptUseCase(get_llm_adapter(), get_repo_adapter())

def get_get_analysis_use_case() -> use_cases.GetAnalysisUseCase:
    """Factory for the GetAnalysisUseCase."""
    return use_cases.GetAnalysisUseCase(get_repo_adapter())
    
def get_analyze_multiple_transcripts_use_case() -> use_cases.AnalyzeMultipleTranscriptsUseCase:
    """Factory for the AnalyzeMultipleTranscriptsUseCase."""
    return use_cases.AnalyzeMultipleTranscriptsUseCase(get_llm_adapter(), get_repo_adapter())