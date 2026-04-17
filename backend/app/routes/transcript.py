from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional
import logging

from app.models import TranscriptCreate, TranscriptResponse, SourceType, TranscriptMetadata
from app.database.crud import (
    create_transcript,
    get_transcript_by_uuid,
    list_transcripts,
    update_transcript,
    soft_delete_transcript
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
MIN_CONTENT_LENGTH = 10
MAX_CONTENT_LENGTH = 1_000_000  # ~1MB of text


@router.post("/upload", response_model=TranscriptResponse, status_code=status.HTTP_201_CREATED)
async def upload_transcript(
    file: UploadFile = File(..., description="Text file containing the transcript"),
    title: Optional[str] = Form(None, description="Optional title for the transcript"),
    description: Optional[str] = Form(None, description="Optional description")
):
    """
    Upload a .txt file containing transcript text.
    
    - **file**: Text file (.txt) with transcript content (max 10MB)
    - **title**: Optional title for the transcript
    - **description**: Optional description
    
    Returns the created transcript with auto-generated UUID and timestamps.
    """
    
    # Validate file extension
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only .txt files are allowed."
        )
    
    logger.info(f"Processing uploaded file: {file.filename}")
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate file size
        file_size = len(content)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size of 10MB."
            )
        
        # Decode content
        try:
            transcript_text = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be valid UTF-8 encoded text."
            )
        
        # Validate content length
        text_length = len(transcript_text.strip())
        
        if text_length < MIN_CONTENT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Transcript text is too short. Minimum {MIN_CONTENT_LENGTH} characters required."
            )
        
        if text_length > MAX_CONTENT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Transcript text is too long. Maximum {MAX_CONTENT_LENGTH} characters allowed."
            )
        
        logger.info(f"File validated successfully. Text length: {text_length} characters")
        
        # Create transcript metadata
        metadata = TranscriptMetadata(
            title=title,
            description=description
        )
        
        # Create transcript data
        transcript_data = TranscriptCreate(
            transcript=transcript_text.strip(),
            source=SourceType.MANUAL,
            metadata=metadata
        )
        
        # Save to database
        created_transcript = await create_transcript(transcript_data)
        
        logger.info(f"Transcript created successfully with UUID: {created_transcript['uuid']}")
        
        return created_transcript
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the file."
        )
    finally:
        await file.close()


@router.get("/{uuid}", response_model=TranscriptResponse)
async def get_transcript(uuid: str):
    """
    Get a transcript by UUID.
    
    - **uuid**: The UUID of the transcript
    """
    transcript = await get_transcript_by_uuid(uuid)
    
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcript with UUID {uuid} not found."
        )
    
    return transcript


@router.get("/", response_model=list[TranscriptResponse])
async def list_all_transcripts(
    skip: int = 0,
    limit: int = 100,
    source: Optional[str] = None
):
    """
    List all transcripts with optional filtering.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (max 100)
    - **source**: Filter by source type (s3 or manual)
    """
    if limit > 100:
        limit = 100
    
    transcripts = await list_transcripts(
        skip=skip,
        limit=limit,
        source=source
    )
    
    return transcripts


@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transcript(uuid: str):
    """
    Soft delete a transcript by UUID.
    
    - **uuid**: The UUID of the transcript to delete
    """
    deleted = await soft_delete_transcript(uuid)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcript with UUID {uuid} not found."
        )
    
    return None
