from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional, List, Dict, Any
import logging
import asyncio

from app.models import TranscriptCreate, TranscriptResponse, SourceType, TranscriptMetadata
from app.models.transcript import TranscriptType
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
MAX_BULK_FILES = 20  # Maximum files per bulk upload


@router.post("/upload", response_model=TranscriptResponse, status_code=status.HTTP_201_CREATED)
async def upload_transcript(
    file: UploadFile = File(..., description="Text file containing the transcript"),
    type: str = Form(..., description="Type of transcript: 'voice' or 'digital'"),
    title: Optional[str] = Form(None, description="Optional title for the transcript"),
    description: Optional[str] = Form(None, description="Optional description")
):
    """
    Upload a .txt file containing transcript text.
    
    - **file**: Text file (.txt) with transcript content (max 10MB)
    - **type**: Type of transcript ('voice' for B2B sales calls, 'digital' for user journeys) - REQUIRED
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
        
        # Validate transcript type
        try:
            transcript_type = TranscriptType(type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid transcript type: '{type}'. Must be 'voice' or 'digital'."
            )
        
        # Create transcript metadata
        metadata = TranscriptMetadata(
            title=title,
            description=description
        )
        
        # Create transcript data
        transcript_data = TranscriptCreate(
            transcript=transcript_text.strip(),
            source=SourceType.MANUAL,
            type=transcript_type,
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


async def process_single_file(
    file: UploadFile,
    transcript_type: TranscriptType = TranscriptType.VOICE,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a single file and return result.
    Used by both single and bulk upload endpoints.
    """
    result = {
        "filename": file.filename,
        "status": "failed",
        "error": None,
        "transcript": None
    }
    
    try:
        # Validate file extension
        if not file.filename.endswith('.txt'):
            result["error"] = "Invalid file format. Only .txt files are allowed."
            return result
        
        # Use filename (without extension) as title if not provided
        if not title and file.filename:
            title = file.filename.rsplit('.', 1)[0]  # Remove .txt extension
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        file_size = len(content)
        if file_size > MAX_FILE_SIZE:
            result["error"] = f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size of 10MB."
            return result
        
        # Decode content
        try:
            transcript_text = content.decode('utf-8')
        except UnicodeDecodeError:
            result["error"] = "File must be valid UTF-8 encoded text."
            return result
        
        # Validate content length
        text_length = len(transcript_text.strip())
        
        if text_length < MIN_CONTENT_LENGTH:
            result["error"] = f"Transcript text is too short. Minimum {MIN_CONTENT_LENGTH} characters required."
            return result
        
        if text_length > MAX_CONTENT_LENGTH:
            result["error"] = f"Transcript text is too long. Maximum {MAX_CONTENT_LENGTH} characters allowed."
            return result
        
        # Create transcript metadata
        metadata = TranscriptMetadata(
            title=title,
            description=description
        )
        
        # Create transcript data
        transcript_data = TranscriptCreate(
            transcript=transcript_text.strip(),
            source=SourceType.MANUAL,
            type=transcript_type,
            metadata=metadata
        )
        
        # Save to database
        created_transcript = await create_transcript(transcript_data)
        
        result["status"] = "success"
        result["transcript"] = created_transcript
        
        logger.info(f"File processed successfully: {file.filename} -> UUID: {created_transcript['uuid']}")
        
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        result["error"] = f"Processing error: {str(e)}"
    
    return result


@router.post("/bulk-upload", status_code=status.HTTP_200_OK)
async def bulk_upload_transcripts(
    files: List[UploadFile] = File(..., description="Multiple text files (max 20)"),
    type: str = Form(..., description="Type of transcript: 'voice' or 'digital' - applies to ALL files")
):
    """
    Upload multiple .txt files at once. All files will be assigned the same transcript type.
    
    - **files**: List of text files (.txt) with transcript content (max 20 files, each max 10MB)
    - **type**: Type for ALL transcripts ('voice' or 'digital') - REQUIRED
    
    Returns a summary of successful and failed uploads with details for each file.
    """
    
    # Validate number of files
    if len(files) > MAX_BULK_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many files. Maximum {MAX_BULK_FILES} files allowed per bulk upload."
        )
    
    if len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided."
        )
    
    # Validate transcript type
    try:
        transcript_type = TranscriptType(type.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transcript type: '{type}'. Must be 'voice' or 'digital'."
        )
    
    logger.info(f"Processing bulk upload of {len(files)} files with type '{transcript_type.value}'")
    
    try:
        # Process all files in parallel with the specified type
        tasks = [process_single_file(file, transcript_type) for file in files]
        results = await asyncio.gather(*tasks)
        
        # Calculate summary
        successful = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] == "failed"]
        
        response = {
            "total": len(files),
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }
        
        logger.info(f"Bulk upload completed: {len(successful)} successful, {len(failed)} failed")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in bulk upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during bulk upload."
        )
    finally:
        # Close all files
        for file in files:
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
