"""
CRUD operations for MongoDB collections.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
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
