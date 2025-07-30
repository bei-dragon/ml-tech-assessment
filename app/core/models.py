import uuid
from pydantic import BaseModel, Field

class TranscriptAnalysis(BaseModel):
    """
    Represents the core business model for a transcript analysis.
    This model is used internally by the application's use cases.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="The unique identifier for the analysis.")
    summary: str = Field(..., description="A concise summary of the transcript.")
    action_items: list[str] = Field(..., description="A list of suggested next actions.")