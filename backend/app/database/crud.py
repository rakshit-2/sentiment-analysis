"""
CRUD operations for MongoDB collections.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId

from app.database.connection import get_transcripts_collection, get_analyses_collection
from app.models import (
    TranscriptDB, TranscriptCreate, TranscriptUpdate,
    AnalysisDB, AnalysisCreate, AnalysisUpdate
)


# Transcript CRUD Operations

async def create_transcript(transcript_data: TranscriptCreate) -> Dict[str, Any]:
    """Create a new transcript in the database."""
    collection = get_transcripts_collection()
    
    # Create DB model with auto-generated fields
    db_transcript = TranscriptDB(
        **transcript_data.model_dump(exclude_none=True)
    )
    
    # Insert into MongoDB
    result = collection.insert_one(db_transcript.to_dict())
    
    # Fetch and return the created document
    created_doc = collection.find_one({"_id": result.inserted_id})
    created_doc["_id"] = str(created_doc["_id"])
    
    return created_doc


async def get_transcript_by_uuid(uuid: str, include_deleted: bool = False) -> Optional[Dict[str, Any]]:
    """Get a transcript by UUID."""
    collection = get_transcripts_collection()
    
    query = {"uuid": uuid}
    if not include_deleted:
        query["is_deleted"] = False
    
    transcript = collection.find_one(query)
    if transcript:
        transcript["_id"] = str(transcript["_id"])
    
    return transcript


async def list_transcripts(
    skip: int = 0,
    limit: int = 100,
    source: Optional[str] = None,
    include_deleted: bool = False
) -> List[Dict[str, Any]]:
    """List transcripts with optional filtering."""
    collection = get_transcripts_collection()
    
    query = {}
    if not include_deleted:
        query["is_deleted"] = False
    if source:
        query["source"] = source
    
    transcripts = list(
        collection.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    
    for transcript in transcripts:
        transcript["_id"] = str(transcript["_id"])
    
    return transcripts


async def update_transcript(uuid: str, update_data: TranscriptUpdate) -> Optional[Dict[str, Any]]:
    """Update a transcript."""
    collection = get_transcripts_collection()
    
    update_dict = update_data.model_dump(exclude_none=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    result = collection.find_one_and_update(
        {"uuid": uuid, "is_deleted": False},
        {"$set": update_dict},
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
    
    return result


async def soft_delete_transcript(uuid: str) -> bool:
    """Soft delete a transcript."""
    collection = get_transcripts_collection()
    
    result = collection.update_one(
        {"uuid": uuid, "is_deleted": False},
        {
            "$set": {
                "is_deleted": True,
                "deleted_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return result.modified_count > 0


# Analysis CRUD Operations

async def create_analysis(analysis_data: AnalysisCreate) -> Dict[str, Any]:
    """Create a new analysis in the database."""
    collection = get_analyses_collection()
    
    # Create DB model with auto-generated fields
    db_analysis = AnalysisDB(
        **analysis_data.model_dump(exclude_none=True)
    )
    
    # Insert into MongoDB
    result = collection.insert_one(db_analysis.to_dict())
    
    # Fetch and return the created document
    created_doc = collection.find_one({"_id": result.inserted_id})
    created_doc["_id"] = str(created_doc["_id"])
    
    return created_doc


async def get_analysis_by_uuid(uuid: str, include_deleted: bool = False) -> Optional[Dict[str, Any]]:
    """Get an analysis by UUID."""
    collection = get_analyses_collection()
    
    query = {"uuid": uuid}
    if not include_deleted:
        query["is_deleted"] = False
    
    analysis = collection.find_one(query)
    if analysis:
        analysis["_id"] = str(analysis["_id"])
    
    return analysis


async def get_analyses_by_transcript(
    transcript_uuid: str,
    include_deleted: bool = False
) -> List[Dict[str, Any]]:
    """Get all analyses for a specific transcript."""
    collection = get_analyses_collection()
    
    query = {"transcript_id": transcript_uuid}
    if not include_deleted:
        query["is_deleted"] = False
    
    analyses = list(
        collection.find(query).sort("created_at", -1)
    )
    
    for analysis in analyses:
        analysis["_id"] = str(analysis["_id"])
    
    return analyses


async def list_analyses(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    include_deleted: bool = False
) -> List[Dict[str, Any]]:
    """List analyses with optional filtering."""
    collection = get_analyses_collection()
    
    query = {}
    if not include_deleted:
        query["is_deleted"] = False
    if status:
        query["status"] = status
    
    analyses = list(
        collection.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    
    for analysis in analyses:
        analysis["_id"] = str(analysis["_id"])
    
    return analyses


async def get_recent_analyses(hours: int = 24) -> Dict[str, Any]:
    """Get analyses from the last N hours with transcript info."""
    analyses_collection = get_analyses_collection()
    transcripts_collection = get_transcripts_collection()
    
    # Calculate the time threshold
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    # Query for recent analyses
    query = {
        "is_deleted": False,
        "created_at": {"$gte": time_threshold}
    }
    
    analyses = list(
        analyses_collection.find(query)
        .sort("created_at", -1)
    )
    
    # Enrich with transcript data
    enriched_analyses = []
    for analysis in analyses:
        analysis["_id"] = str(analysis["_id"])
        
        # Fetch associated transcript
        transcript = transcripts_collection.find_one({
            "uuid": analysis["transcript_id"],
            "is_deleted": False
        })
        
        if transcript:
            transcript["_id"] = str(transcript["_id"])
            analysis["transcript"] = transcript
        
        enriched_analyses.append(analysis)
    
    return {
        "count": len(enriched_analyses),
        "hours": hours,
        "analyses": enriched_analyses
    }


async def get_analysis_trends(days: int = 60) -> List[Dict[str, Any]]:
    """Get daily analysis trends for the last N days."""
    collection = get_analyses_collection()
    
    # Calculate the start date
    end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days - 1)
    
    # MongoDB aggregation pipeline
    pipeline = [
        {
            "$match": {
                "is_deleted": False,
                "created_at": {"$gte": start_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"},
                    "day": {"$dayOfMonth": "$created_at"}
                },
                "count": {"$sum": 1},
                "first_date": {"$min": "$created_at"}
            }
        },
        {
            "$sort": {"first_date": 1}
        }
    ]
    
    results = list(collection.aggregate(pipeline))
    
    # Create a dictionary of dates with counts
    date_counts = {}
    for result in results:
        date_str = result["first_date"].strftime("%Y-%m-%d")
        date_counts[date_str] = result["count"]
    
    # Generate all dates in the range and fill in missing dates with 0
    trends = []
    current_date = start_date
    for _ in range(days):
        date_str = current_date.strftime("%Y-%m-%d")
        trends.append({
            "date": date_str,
            "count": date_counts.get(date_str, 0)
        })
        current_date += timedelta(days=1)
    
    return trends


async def get_detailed_metrics_trends(days: int = 60) -> List[Dict[str, Any]]:
    """Get detailed metrics trends with analysis result aggregations."""
    collection = get_analyses_collection()
    
    # Calculate the start date
    end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days - 1)
    
    # MongoDB aggregation pipeline
    pipeline = [
        {
            "$match": {
                "is_deleted": False,
                "created_at": {"$gte": start_date},
                "status": "success",  # Only successful analyses
                "result": {"$exists": True}
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"},
                    "day": {"$dayOfMonth": "$created_at"}
                },
                "total_analyses": {"$sum": 1},
                "first_date": {"$min": "$created_at"},
                # Sentiment aggregation
                "sentiments": {"$push": "$result.summary.overall_call_sentiment"},
                # Lead temperature aggregation
                "lead_temps": {"$push": "$result.summary.lead_temperature"},
                # Average metrics
                "meeting_likelihoods": {"$push": "$result.summary.meeting_likelihood"},
                "follow_up_readiness": {"$push": "$result.summary.follow_up_readiness"}
            }
        },
        {
            "$sort": {"first_date": 1}
        }
    ]
    
    results = list(collection.aggregate(pipeline))
    
    # Create a dictionary of dates with their metrics
    date_metrics = {}
    for result in results:
        date_str = result["first_date"].strftime("%Y-%m-%d")
        
        # Count sentiment categories
        sentiments = result.get("sentiments", [])
        sentiment_counts = {
            "positive": sum(1 for s in sentiments if s and "positive" in s.lower()),
            "negative": sum(1 for s in sentiments if s and "negative" in s.lower()),
            "neutral": sum(1 for s in sentiments if s and "neutral" in s.lower()),
            "mixed": sum(1 for s in sentiments if s and "mixed" in s.lower())
        }
        
        # Count lead temperature categories
        lead_temps = result.get("lead_temps", [])
        lead_temp_counts = {
            "hot": sum(1 for t in lead_temps if t and "hot" in t.lower()),
            "warm": sum(1 for t in lead_temps if t and "warm" in t.lower()),
            "cold": sum(1 for t in lead_temps if t and "cold" in t.lower())
        }
        
        # Calculate averages
        meeting_likes = [m for m in result.get("meeting_likelihoods", []) if m is not None]
        follow_ups = [f for f in result.get("follow_up_readiness", []) if f is not None]
        
        avg_meeting = sum(meeting_likes) / len(meeting_likes) if meeting_likes else 0
        avg_follow_up = sum(follow_ups) / len(follow_ups) if follow_ups else 0
        
        date_metrics[date_str] = {
            "total_analyses": result["total_analyses"],
            "lead_temperature": lead_temp_counts,
            "sentiment": sentiment_counts,
            "averages": {
                "meeting_likelihood": round(avg_meeting, 1),
                "follow_up_readiness": round(avg_follow_up, 1)
            },
            "success_rate": 100.0  # Since we filtered for success only
        }
    
    # Generate all dates in the range and fill in missing dates with zeros
    trends = []
    current_date = start_date
    for _ in range(days):
        date_str = current_date.strftime("%Y-%m-%d")
        
        if date_str in date_metrics:
            trends.append({
                "date": date_str,
                **date_metrics[date_str]
            })
        else:
            # Fill missing dates with zero values
            trends.append({
                "date": date_str,
                "total_analyses": 0,
                "lead_temperature": {
                    "hot": 0,
                    "warm": 0,
                    "cold": 0
                },
                "sentiment": {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "mixed": 0
                },
                "averages": {
                    "meeting_likelihood": 0,
                    "follow_up_readiness": 0
                },
                "success_rate": 0
            })
        
        current_date += timedelta(days=1)
    
    return trends


async def update_analysis(uuid: str, update_data: AnalysisUpdate) -> Optional[Dict[str, Any]]:
    """Update an analysis."""
    collection = get_analyses_collection()
    
    update_dict = update_data.model_dump(exclude_none=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    result = collection.find_one_and_update(
        {"uuid": uuid, "is_deleted": False},
        {"$set": update_dict},
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
    
    return result


async def soft_delete_analysis(uuid: str) -> bool:
    """Soft delete an analysis."""
    collection = get_analyses_collection()
    
    result = collection.update_one(
        {"uuid": uuid, "is_deleted": False},
        {
            "$set": {
                "is_deleted": True,
                "deleted_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return result.modified_count > 0


# Synchronous versions for Celery tasks

def create_analysis_sync(analysis_data: AnalysisCreate) -> Dict[str, Any]:
    """Create a new analysis in the database (synchronous version for Celery)."""
    collection = get_analyses_collection()
    
    # Create DB model with auto-generated fields
    db_analysis = AnalysisDB(
        **analysis_data.model_dump(exclude_none=True)
    )
    
    # Insert into MongoDB
    result = collection.insert_one(db_analysis.to_dict())
    
    # Fetch and return the created document
    created_doc = collection.find_one({"_id": result.inserted_id})
    created_doc["_id"] = str(created_doc["_id"])
    
    return created_doc
