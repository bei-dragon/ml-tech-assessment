import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.v1 import schemas
from app.api import dependencies
from app.core import use_cases, exceptions
from app import prompts
import traceback

router = APIRouter(prefix="/v1", tags=["Analysis"])

@router.post(
    "/analysis",
    response_model=schemas.AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze a Single Transcript"
)
async def analyze_transcript(
    transcript: str = Query(..., description="The plain text transcript to be analyzed."),
    analyze_uc: use_cases.AnalyzeTranscriptUseCase = Depends(dependencies.get_analyze_transcript_use_case)
):
    """
    Accepts a transcript, analyzes it to produce a summary and action items,
    and returns the result along with a unique ID for future retrieval.
    """
    try:
        analysis = await analyze_uc.execute(
            transcript=transcript,
            system_prompt=prompts.SYSTEM_PROMPT,
            user_prompt=prompts.RAW_USER_PROMPT
        )
        return analysis
    except exceptions.InvalidTranscriptError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        traceback.print_exc() 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


@router.get(
    "/analysis/{analysis_id}",
    response_model=schemas.AnalysisResponse,
    summary="Get Analysis by ID"
)
async def get_analysis_by_id(
    analysis_id: uuid.UUID,
    get_uc: use_cases.GetAnalysisUseCase = Depends(dependencies.get_get_analysis_use_case)
):
    """
    Retrieves a previously stored transcript analysis using its unique ID.
    """
    try:
        analysis = await get_uc.execute(analysis_id)
        return analysis
    except exceptions.TranscriptNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/analysis/batch",
    response_model=schemas.BatchAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze Multiple Transcripts Concurrently"
)
async def analyze_batch_transcripts(
    request: schemas.BatchAnalysisRequest,
    analyze_multiple_uc: use_cases.AnalyzeMultipleTranscriptsUseCase = Depends(dependencies.get_analyze_multiple_transcripts_use_case)
):
    """
    (Optional) Accepts a list of transcripts and processes them in parallel,
    returning a list of analysis results.
    """
    try:
        results = await analyze_multiple_uc.execute(
            transcripts=request.transcripts,
            system_prompt=prompts.SYSTEM_PROMPT,
            user_prompt=prompts.RAW_USER_PROMPT
        )
        return {"results": results}
    except exceptions.InvalidTranscriptError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected internal error occurred.")