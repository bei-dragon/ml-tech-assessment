import uuid
from typing import Optional
from app.core import models
from app.ports import repository

# A simple in-memory dictionary to act as our database for this assessment.
IN_MEMORY_DB: dict[uuid.UUID, models.TranscriptAnalysis] = {}

class InMemoryAnalysisRepository(repository.AnalysisRepository):
    """
    A concrete implementation of the AnalysisRepository port that uses an in-memory
    dictionary for storage. This is a secondary/driven adapter.
    """
    
    async def get_by_id(self, analysis_id: uuid.UUID) -> Optional[models.TranscriptAnalysis]:
        return IN_MEMORY_DB.get(analysis_id)

    async def save(self, analysis: models.TranscriptAnalysis) -> None:
        IN_MEMORY_DB[analysis.id] = analysis