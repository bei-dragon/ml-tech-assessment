import uuid
from abc import ABC, abstractmethod
from app.core import models
from typing import Optional

class AnalysisRepository(ABC):
    """
    A port defining the contract for persistence operations related to transcript analysis.
    This allows the core application to be independent of the actual storage implementation.
    """

    @abstractmethod
    async def get_by_id(self, analysis_id: uuid.UUID) -> Optional[models.TranscriptAnalysis]:
        """Retrieves an analysis by its unique ID."""
        pass

    @abstractmethod
    async def save(self, analysis: models.TranscriptAnalysis) -> None:
        """Saves a new or updated analysis."""
        pass