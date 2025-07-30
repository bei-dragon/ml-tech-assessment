import uuid
from pydantic import BaseModel, Field

# Although these schemas are identical to the core models for now,
# keeping them separate is a crucial architectural decision.
# It allows the API's public contract to evolve independently of the internal business logic.

class AnalysisResponse(BaseModel):
    """Schema for returning a single analysis result."""
    id: uuid.UUID = Field(..., description="The unique ID for the analysis.")
    summary: str = Field(..., description="The summary of the transcript.")
    action_items: list[str] = Field(..., description="The list of suggested next steps.")
    
    class Config:
        from_attributes = True

class BatchAnalysisRequest(BaseModel):
    """Schema for the batch analysis request body."""
    transcripts: list[str] = Field(..., min_length=1, description="A list of transcripts to analyze.")

class BatchAnalysisResponse(BaseModel):
    """Schema for returning a batch of analysis results."""
    results: list[AnalysisResponse]
