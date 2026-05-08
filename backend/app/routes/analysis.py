from fastapi import APIRouter, HTTPException, status
from typing import Optional
import logging

from app.models import AnalysisResponse
from app.database.crud import (
    get_analysis_by_uuid,
    list_analyses,
    get_analyses_by_transcript,
    get_recent_analyses,
    get_analysis_trends,
    get_detailed_metrics_trends
)
from app.tasks.analysis_tasks import analyze_unprocessed_transcripts

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
async def trigger_analysis(batch_size: Optional[int] = None):
    """
    Manually trigger the analysis job to process unprocessed transcripts.
    
    - **batch_size**: Optional number of transcripts to process (default: 5)
    
    This endpoint immediately queues a Celery task to analyze transcripts.
    You can monitor the task progress in Flower UI at http://localhost:5555
    """
    try:
        # Queue the Celery task
        task = analyze_unprocessed_transcripts.delay(batch_size)
        
        logger.info(f"Analysis task queued with ID: {task.id}")
        
        return {
            "message": "Analysis task queued successfully",
            "task_id": task.id,
            "batch_size": batch_size or 5,
            "status": "PENDING",
            "monitor_url": "http://localhost:5555/task/{task.id}"
        }
    except Exception as e:
        logger.error(f"Error triggering analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger analysis: {str(e)}"
        )


# IMPORTANT: Specific routes must come before generic path parameters
@router.get("/stats/recent")
async def get_recent_analyses_stats(hours: int = 24):
    """
    Get analyses from the last N hours with transcript information.
    
    - **hours**: Number of hours to look back (default: 24)
    
    Returns count and list of recent analyses with their transcripts.
    """
    if hours > 168:  # Max 1 week
        hours = 168
    
    result = await get_recent_analyses(hours=hours)
    
    return result


@router.get("/stats/trends")
async def get_analysis_trends_stats(weeks: int = 8):
    """
    Get weekly analysis trends for the last N weeks.
    
    - **weeks**: Number of weeks to analyze (default: 8, max: 52)
    
    Returns weekly aggregated data suitable for charting.
    """
    if weeks > 52:
        weeks = 52
    
    trends = await get_analysis_trends(weeks=weeks)
    
    return {
        "weeks": weeks,
        "data": trends
    }


@router.get("/stats/detailed-metrics")
async def get_detailed_metrics_stats(weeks: int = 8):
    """
    Get detailed metrics trends including sentiment, lead temperature, and averages.
    
    - **weeks**: Number of weeks to analyze (default: 8, max: 52)
    
    Returns detailed weekly metrics for visualization.
    """
    if weeks > 52:
        weeks = 52
    
    metrics = await get_detailed_metrics_trends(weeks=weeks)
    
    return {
        "weeks": weeks,
        "data": metrics
    }


@router.get("/", response_model=list[AnalysisResponse])
async def list_all_analyses(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
):
    """
    List all analyses with optional filtering.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (max 100)
    - **status**: Filter by status (pending, processing, success, failed)
    """
    if limit > 100:
        limit = 100
    
    analyses = await list_analyses(
        skip=skip,
        limit=limit,
        status=status
    )
    
    return analyses


@router.get("/transcript/{transcript_uuid}", response_model=list[AnalysisResponse])
async def get_analyses_for_transcript(transcript_uuid: str):
    """
    Get all analyses for a specific transcript.
    
    - **transcript_uuid**: The UUID of the transcript
    """
    analyses = await get_analyses_by_transcript(transcript_uuid)
    
    return analyses


@router.get("/{uuid}", response_model=AnalysisResponse)
async def get_analysis(uuid: str):
    """
    Get an analysis by UUID.
    
    - **uuid**: The UUID of the analysis
    """
    analysis = await get_analysis_by_uuid(uuid)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with UUID {uuid} not found."
        )
    
    return analysis
