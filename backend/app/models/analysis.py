from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum
import uuid


class AnalysisStatus(str, Enum):
    """Enum for analysis status."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class MetricScore(BaseModel):
    """Model for individual metric scoring."""
    score: int = Field(..., ge=0, le=10, description="Score from 1-10")
    evidence: List[str] = Field(default_factory=list, description="Quote snippets from transcript")
    rationale: str = Field(..., description="Brief explanation of the score")


class AskingToTellingMetric(BaseModel):
    """Model for asking to telling ratio metric."""
    score: int = Field(..., ge=0, le=10, description="Score from 1-10")
    estimated_ratio: str = Field(..., description="Estimated ratio like '1:2' or '3:1'")
    evidence: List[str] = Field(default_factory=list, description="Quote snippets")
    rationale: str = Field(..., description="Brief explanation")


class CallSummary(BaseModel):
    """Model for call summary."""
    overall_call_sentiment: str = Field(..., description="Positive/Neutral/Negative")
    lead_temperature: str = Field(..., description="Cold/Warm/Hot")
    meeting_likelihood: int = Field(..., ge=0, le=100, description="Percentage 0-100")
    follow_up_readiness: int = Field(..., ge=0, le=100, description="Percentage 0-100")


class PrimaryMetrics(BaseModel):
    """Model for primary analysis dimensions."""
    live_tone_score: MetricScore
    objection_recovery_arc: MetricScore
    champion_signals: MetricScore
    buying_commitment_momentum: MetricScore
    competitive_mention_sentiment: MetricScore
    call_closing_sentiment: MetricScore


class ParameterMetrics(BaseModel):
    """Model for parameter analysis dimensions."""
    prospect_tone: MetricScore
    pain_urgency: MetricScore
    champion_strength: MetricScore
    objection_temperature: MetricScore
    buying_commitment: MetricScore
    competitive_position: MetricScore
    trust_openness: MetricScore
    expansion_potential: MetricScore
    decision_friction_indicators: MetricScore
    asking_to_telling_ratio: AskingToTellingMetric
    transparency_score: MetricScore


class AnalysisResult(BaseModel):
    """Model for B2B sales conversation intelligence analysis result."""
    summary: Optional[Union[CallSummary, dict]] = Field(None, description="High-level call summary")
    primary_metrics: Optional[Union[PrimaryMetrics, dict]] = Field(None, description="Primary analysis dimensions")
    parameter_metrics: Optional[Union[ParameterMetrics, dict]] = Field(None, description="Detailed parameter metrics")
    notable_buying_signals: List[str] = Field(default_factory=list, description="Key buying signals detected")
    objections_detected: List[str] = Field(default_factory=list, description="Objections raised")
    risks_detected: List[str] = Field(default_factory=list, description="Risks identified")
    next_best_action: List[str] = Field(default_factory=list, description="Recommended next actions")
    
    # Digital-specific fields
    engagement_depth: Optional[dict] = Field(None, description="Digital engagement metrics")
    content_consumption: Optional[dict] = Field(None, description="Content consumption metrics")
    time_investment: Optional[dict] = Field(None, description="Time investment analysis")
    drop_off_signals: List[str] = Field(default_factory=list, description="Drop-off signals")
    conversion_signals: List[str] = Field(default_factory=list, description="Conversion signals")
    friction_points: List[str] = Field(default_factory=list, description="Friction points")

    class Config:
        json_schema_extra = {
            "example": {
                "summary": {
                    "overall_call_sentiment": "Positive",
                    "lead_temperature": "Warm",
                    "meeting_likelihood": 75,
                    "follow_up_readiness": 80
                },
                "primary_metrics": {
                    "live_tone_score": {"score": 7, "evidence": ["Great to connect"], "rationale": "Positive engagement"}
                },
                "notable_buying_signals": ["Mentioned budget available"],
                "objections_detected": ["Price concerns"],
                "risks_detected": ["Decision timeline unclear"],
                "next_best_action": ["Send pricing proposal", "Schedule demo"]
            }
        }


# Digital Journey Analysis Models
class DigitalEngagementMetric(BaseModel):
    """Model for digital engagement metrics."""
    score: int = Field(..., ge=0, le=10, description="Score from 1-10")
    key_actions: List[str] = Field(default_factory=list, description="Key actions taken by user")
    rationale: str = Field(..., description="Brief explanation of the score")


class TimeInvestmentAnalysis(BaseModel):
    """Model for time investment analysis."""
    total_session_time: str = Field(..., description="Total time in session (e.g., '32m 44s')")
    high_value_content_time: str = Field(..., description="Time on high-value content (e.g., '20m 5s')")
    average_time_per_content: str = Field(..., description="Average time per content piece")
    depth_score: int = Field(..., ge=0, le=10, description="Time investment depth score 1-10")


class DigitalJourneySummary(BaseModel):
    """Model for digital journey summary."""
    session_temperature: str = Field(..., description="Cold/Warm/Hot")
    conversion_readiness: int = Field(..., ge=0, le=100, description="Percentage 0-100")
    journey_stage: str = Field(..., description="e.g., Research, Comparison, Decision")
    content_pieces_consumed: int = Field(..., description="Number of content pieces viewed")
    high_intent_actions: List[str] = Field(default_factory=list, description="High-intent actions taken")


class DigitalAnalysisResult(BaseModel):
    """Model for digital journey analysis result."""
    summary: DigitalJourneySummary = Field(..., description="High-level journey summary")
    engagement_depth: DigitalEngagementMetric = Field(..., description="Engagement depth analysis")
    content_consumption: DigitalEngagementMetric = Field(..., description="Content consumption quality")
    time_investment: TimeInvestmentAnalysis = Field(..., description="Time investment analysis")
    drop_off_signals: List[str] = Field(default_factory=list, description="Drop-off or abandonment signals")
    conversion_signals: List[str] = Field(default_factory=list, description="Positive conversion signals")
    friction_points: List[str] = Field(default_factory=list, description="Friction or hesitation points")
    next_best_action: List[str] = Field(default_factory=list, description="Recommended follow-ups")

    class Config:
        json_schema_extra = {
            "example": {
                "summary": {
                    "session_temperature": "Warm",
                    "conversion_readiness": 65,
                    "journey_stage": "Comparison",
                    "content_pieces_consumed": 7,
                    "high_intent_actions": ["Downloaded whitepaper", "Viewed pricing guide"]
                },
                "engagement_depth": {
                    "score": 7,
                    "key_actions": ["Extended vlog watch", "Multiple pricing views"],
                    "rationale": "High engagement with premium content"
                },
                "content_consumption": {
                    "score": 8,
                    "key_actions": ["Zscaler whitepaper", "Akamai whitepaper", "Email security ebook"],
                    "rationale": "Consumed multiple high-value assets"
                },
                "time_investment": {
                    "total_session_time": "35m 18s",
                    "high_value_content_time": "20m 5s",
                    "average_time_per_content": "5m 2s",
                    "depth_score": 8
                },
                "drop_off_signals": ["Abandoned form at phone number"],
                "conversion_signals": ["Downloaded whitepaper", "Returned after 3 hours"],
                "friction_points": ["Form abandonment", "Phone number field"],
                "next_best_action": ["Send email campaign", "Retarget with demo offer"]
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
    transcript: Optional[Dict[str, Any]] = Field(None, description="Associated transcript object")
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
