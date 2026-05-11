from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class SourceType(str, Enum):
    """Enum for transcript source types."""
    S3 = "s3"
    MANUAL = "manual"


class TranscriptType(str, Enum):
    """Enum for transcript types (content/interaction type)."""
    VOICE = "voice"      # B2B sales call transcripts
    DIGITAL = "digital"  # User journey/website interaction transcripts


class S3Metadata(BaseModel):
    """S3 metadata for transcripts sourced from S3."""
    bucket: str
    key: str
    s3_uri: str


class TranscriptMetadata(BaseModel):
    """Additional metadata for transcripts."""
    title: Optional[str] = None
    description: Optional[str] = None


# Request Models (for API input)
class TranscriptCreate(BaseModel):
    """Model for creating a new transcript."""
    transcript: str = Field(..., description="The transcript text content")
    source: SourceType = Field(..., description="Source of the transcript")
    type: TranscriptType = Field(..., description="Type of transcript (voice or digital)")
    s3_metadata: Optional[S3Metadata] = Field(None, description="S3 metadata if source is s3")
    metadata: Optional[TranscriptMetadata] = Field(default_factory=TranscriptMetadata)

    class Config:
        json_schema_extra = {
            "example": {
                "transcript": "This is a sample transcript text...",
                "source": "manual",
                "type": "voice",
                "metadata": {
                    "title": "Customer Call - Jan 2024",
                    "description": "Support call regarding billing"
                }
            }
        }


class TranscriptUpdate(BaseModel):
    """Model for updating an existing transcript."""
    transcript: Optional[str] = None
    metadata: Optional[TranscriptMetadata] = None


# Response Models (for API output)
class TranscriptResponse(BaseModel):
    """Model for transcript responses."""
    id: str = Field(..., alias="_id", description="MongoDB ObjectId as string")
    uuid: str = Field(..., description="UUID for external references")
    transcript: str
    source: SourceType
    type: TranscriptType
    s3_metadata: Optional[S3Metadata] = None
    metadata: TranscriptMetadata
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "transcript": "This is a sample transcript...",
                "source": "manual",
                "type": "voice",
                "metadata": {
                    "title": "Customer Call",
                    "description": "Support call"
                },
                "is_deleted": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


# Database Model (for MongoDB storage)
class TranscriptDB(BaseModel):
    """Internal model for MongoDB storage."""
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transcript: str
    source: SourceType
    type: TranscriptType = TranscriptType.VOICE  # Default to VOICE for backward compatibility
    s3_metadata: Optional[S3Metadata] = None
    metadata: TranscriptMetadata = Field(default_factory=TranscriptMetadata)
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB insertion."""
        return self.model_dump(exclude_none=True)
