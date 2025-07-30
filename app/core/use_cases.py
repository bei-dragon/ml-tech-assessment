import asyncio
import uuid
from app import ports
from app.core import models, exceptions

class AnalyzeTranscriptUseCase:
    """Orchestrates the analysis of a single transcript."""

    def __init__(self, llm_port: ports.LLm, repo_port: ports.AnalysisRepository):
        self._llm_port = llm_port
        self._repo_port = repo_port

    async def execute(self, transcript: str, system_prompt: str, user_prompt: str) -> models.TranscriptAnalysis:
        if not transcript or not transcript.strip():
            raise exceptions.InvalidTranscriptError("Transcript cannot be empty.")

        # The DTO for the LLM adapter is defined by its expected output structure
        class LLMResponseDTO(models.TranscriptAnalysis):
            pass

        formatted_user_prompt = user_prompt.format(transcript=transcript)
        
        analysis_dto = await self._llm_port.run_completion_async(
            system_prompt=system_prompt,
            user_prompt=formatted_user_prompt,
            dto=LLMResponseDTO
        )

        analysis = models.TranscriptAnalysis.model_validate(analysis_dto)
        
        await self._repo_port.save(analysis)
        
        return analysis

class GetAnalysisUseCase:
    """Handles retrieving a previously completed analysis."""

    def __init__(self, repo_port: ports.AnalysisRepository):
        self._repo_port = repo_port

    async def execute(self, analysis_id: uuid.UUID) -> models.TranscriptAnalysis:
        analysis = await self._repo_port.get_by_id(analysis_id)
        if not analysis:
            raise exceptions.TranscriptNotFoundError(f"Analysis with ID {analysis_id} not found.")
        return analysis

class AnalyzeMultipleTranscriptsUseCase:
    """(Optional) Orchestrates concurrent analysis of multiple transcripts."""

    def __init__(self, llm_port: ports.LLm, repo_port: ports.AnalysisRepository):
        self._llm_port = llm_port
        self._repo_port = repo_port
    
    async def execute(self, transcripts: list[str], system_prompt: str, user_prompt: str) -> list[models.TranscriptAnalysis]:
        if not all(transcripts):
            raise exceptions.InvalidTranscriptError("No transcript in a batch can be empty.")
            
        class LLMResponseDTO(models.TranscriptAnalysis):
            pass
            
        async def analyze_and_save(transcript: str) -> models.TranscriptAnalysis:
            formatted_user_prompt = user_prompt.format(transcript=transcript)
            analysis_dto = await self._llm_port.run_completion_async(
                system_prompt=system_prompt,
                user_prompt=formatted_user_prompt,
                dto=LLMResponseDTO
            )
            analysis = models.TranscriptAnalysis.model_validate(analysis_dto)
            await self._repo_port.save(analysis)
            return analysis

        tasks = [analyze_and_save(transcript) for transcript in transcripts]
        results = await asyncio.gather(*tasks)
        return results