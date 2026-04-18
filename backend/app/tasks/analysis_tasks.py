"""
Celery tasks for sentiment analysis processing.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any

from app.celery_app import celery_app
from app.database.connection import get_transcripts_collection, get_analyses_collection
from app.database.crud import create_analysis
from app.models import AnalysisCreate, AnalysisStatus, AnalysisUpdate, AnalysisResult, ModelInfo
from app.services.openai_service import analyze_sentiment
from app.config import settings

logger = logging.getLogger(__name__)


def find_unprocessed_transcripts(batch_size: int = 5) -> List[Dict[str, Any]]:
    """
    Find transcripts that haven't been analyzed yet.
    
    Args:
        batch_size: Maximum number of transcripts to process
        
    Returns:
        List of transcript documents
    """
    transcripts_collection = get_transcripts_collection()
    analyses_collection = get_analyses_collection()
    
    # Get all transcript_ids that have been analyzed
    analyzed_transcript_ids = set(
        doc["transcript_id"] 
        for doc in analyses_collection.find(
            {"is_deleted": False},
            {"transcript_id": 1}
        )
    )
    
    logger.info(f"Found {len(analyzed_transcript_ids)} already analyzed transcripts")
    
    # Find transcripts that are not in the analyzed set
    unprocessed = list(
        transcripts_collection.find(
            {
                "uuid": {"$nin": list(analyzed_transcript_ids)},
                "is_deleted": False
            }
        ).limit(batch_size)
    )
    
    logger.info(f"Found {len(unprocessed)} unprocessed transcripts (limit: {batch_size})")
    
    return unprocessed


@celery_app.task(bind=True, name="app.tasks.analysis_tasks.analyze_unprocessed_transcripts")
def analyze_unprocessed_transcripts(self, batch_size: int = None):
    """
    Process unprocessed transcripts in batches.
    
    This task:
    1. Finds transcripts that don't have analysis records
    2. Takes up to batch_size transcripts
    3. Creates analysis records for each
    4. Calls OpenAI API for sentiment analysis
    5. Updates records with results
    
    Args:
        batch_size: Number of transcripts to process (default from settings)
    """
    if batch_size is None:
        batch_size = settings.analysis_batch_size
    
    logger.info(f"Starting batch analysis task (batch_size={batch_size})")
    
    try:
        # Find unprocessed transcripts
        unprocessed_transcripts = find_unprocessed_transcripts(batch_size)
        
        if not unprocessed_transcripts:
            logger.info("No unprocessed transcripts found")
            return {
                "status": "completed",
                "processed": 0,
                "message": "No unprocessed transcripts found"
            }
        
        results = {
            "total": len(unprocessed_transcripts),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Process each transcript
        for transcript in unprocessed_transcripts:
            transcript_uuid = transcript["uuid"]
            logger.info(f"Processing transcript: {transcript_uuid}")
            
            try:
                # Create initial analysis record
                analysis_data = AnalysisCreate(transcript_id=transcript_uuid)
                created_analysis = create_analysis(analysis_data)
                analysis_uuid = created_analysis["uuid"]
                
                logger.info(f"Created analysis record: {analysis_uuid}")
                
                # Update status to processing
                analyses_collection = get_analyses_collection()
                analyses_collection.update_one(
                    {"uuid": analysis_uuid},
                    {
                        "$set": {
                            "status": AnalysisStatus.PROCESSING.value,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                # Call OpenAI for sentiment analysis
                logger.info(f"Calling OpenAI API for transcript: {transcript_uuid}")
                sentiment_result = analyze_sentiment(
                    transcript_text=transcript["transcript"],
                    transcript_id=transcript_uuid
                )
                
                # Update analysis with results
                update_data = {
                    "result": sentiment_result["result"],
                    "status": AnalysisStatus.SUCCESS.value,
                    "model_info": sentiment_result["model_info"],
                    "analyzed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                analyses_collection.update_one(
                    {"uuid": analysis_uuid},
                    {"$set": update_data}
                )
                
                logger.info(f"Successfully analyzed transcript: {transcript_uuid}")
                results["successful"] += 1
                
            except Exception as e:
                logger.error(f"Error processing transcript {transcript_uuid}: {str(e)}")
                results["failed"] += 1
                results["errors"].append({
                    "transcript_id": transcript_uuid,
                    "error": str(e)
                })
                
                # Update analysis status to failed
                try:
                    analyses_collection.update_one(
                        {"uuid": analysis_uuid},
                        {
                            "$set": {
                                "status": AnalysisStatus.FAILED.value,
                                "error_message": str(e),
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                except:
                    pass
        
        logger.info(f"Batch analysis completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Fatal error in batch analysis task: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)
