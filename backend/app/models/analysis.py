from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


class AnalysisStatus(str, Enum):
    """Enum for analysis status."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class AnalysisResult(BaseModel):
    """Model for LLM analysis result."""
    sentiment: Optional[str] = Field(None, description="Overall sentiment: positive, negative, neutral")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score 0-1")
    key_phrases: Optional[List[str]] = Field(default_factory=list, description="Key phrases extracted")
    emotions: Optional[List[str]] = Field(default_factory=list, description="Emotions detected")
    summary: Optional[str] = Field(None, description="Brief summary")
    detailed_feedback: Optional[str] = Field(None, description="Detailed feedback from LLM")
    raw_response: Optional[Dict[str, Any]] = Field(None, description="Full OpenAI API response")

    class Config:
        json_schema_extra = {
            "example": {
                "sentiment": "positive",
                "confidence": 0.85,
                "key_phrases": ["great service", "very helpful"],
                "emotions": ["satisfaction", "happiness"],
                "summary": "Customer is satisfied with the service",
                "detailed_feedback": "The customer expressed high satisfaction..."
            }
        }


class ModelInfo(BaseModel):
    """Information about the AI model used."""
    model: str = Field(..., description="Model name, e.g., gpt-4, gpt-3.5-turbo")
    tokens_used: Optional[int] = Field(None, description="Total tokens consumed")
    cost: Optional[float] = Field(None, description="API cost in USD")


# Request Models (for API input)
class AnalysisCreate(BaseModel):
    """Model for creating a new analysis."""
    transcript_id: str = Field(..., description="UUID of the transcript to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transcript_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class AnalysisUpdate(BaseModel):
    """Model for updating an analysis (e.g., after processing)."""
    result: Optional[AnalysisResult] = None
    status: Optional[AnalysisStatus] = None
    error_message: Optional[str] = None
    model_info: Optional[ModelInfo] = None
    analyzed_at: Optional[datetime] = None


# Response Models (for API output)
class AnalysisResponse(BaseModel):
    """Model for analysis responses."""
    id: str = Field(..., alias="_id", description="MongoDB ObjectId as string")
    uuid: str = Field(..., description="UUID for external references")
    transcript_id: str = Field(..., description="UUID of associated transcript")
    result: Optional[AnalysisResult] = None
    status: AnalysisStatus
    error_message: Optional[str] = None
    model_info: Optional[ModelInfo] = None
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    analyzed_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "uuid": "223e4567-e89b-12d3-a456-426614174111",
                "transcript_id": "123e4567-e89b-12d3-a456-426614174000",
                "result": {
                    "sentiment": "positive",
                    "confidence": 0.85,
                    "summary": "Customer is satisfied"
                },
                "status": "success",
                "model_info": {
                    "model": "gpt-4",
                    "tokens_used": 500
                },
                "is_deleted": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "analyzed_at": "2024-01-01T00:01:00Z"
            }
        }


# Database Model (for MongoDB storage)
class AnalysisDB(BaseModel):
    """Internal model for MongoDB storage."""
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transcript_id: str
    result: Optional[AnalysisResult] = None
    status: AnalysisStatus = AnalysisStatus.PENDING
    error_message: Optional[str] = None
    model_info: Optional[ModelInfo] = None
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    analyzed_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB insertion."""
        return self.model_dump(exclude_none=True)
