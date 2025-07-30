from fastapi import FastAPI
from app.api.v1 import endpoints

app = FastAPI(
    title="Transcript Analysis API",
    description="A web API for analyzing transcripts using AI to generate summaries and action items.",
    version="1.0.0"
)

app.include_router(endpoints.router)

@app.get("/", tags=["Health"])
def health_check():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "ok"}