"""
Pydantic schemas for request/response models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MediaType(str, Enum):
    """Types of media that can be fact-checked."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    TEXT = "text"
    LIVE_STREAM = "live_stream"


class ProcessingStatus(str, Enum):
    """Status of processing a fact-check request."""
    PENDING = "pending"
    PROCESSING = "processing"
    EXTRACTING_CLAIMS = "extracting_claims"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    ERROR = "error"


class VerificationStatus(str, Enum):
    """Result of fact verification."""
    TRUE = "true"
    FALSE = "false"
    PARTIALLY_TRUE = "partially_true"
    MISLEADING = "misleading"
    UNVERIFIABLE = "unverifiable"
    OPINION = "opinion"
    SATIRE = "satire"


class SourceReference(BaseModel):
    """Reference to a source used for verification."""
    title: str
    url: Optional[str] = None
    snippet: Optional[str] = None
    credibility_score: Optional[float] = Field(None, ge=0, le=1)
    published_date: Optional[str] = None


class ClaimResult(BaseModel):
    """Result for a single claim verification."""
    claim_id: str
    original_text: str
    claim_type: str = "factual"  # factual, opinion, prediction, etc.
    verification_status: VerificationStatus
    confidence_score: float = Field(ge=0, le=1)
    explanation: str
    corrected_info: Optional[str] = None
    sources: list[SourceReference] = []
    timestamp_start: Optional[float] = None  # For audio/video
    timestamp_end: Optional[float] = None
    context: Optional[str] = None


class FactCheckRequest(BaseModel):
    """Request to fact-check content."""
    content_type: MediaType
    text_content: Optional[str] = None
    file_id: Optional[str] = None
    url: Optional[str] = None
    options: dict[str, Any] = {}


class FactCheckResult(BaseModel):
    """Complete fact-check result."""
    request_id: str
    status: ProcessingStatus
    media_type: MediaType
    extracted_text: Optional[str] = None
    total_claims: int = 0
    claims: list[ClaimResult] = []
    summary: Optional[str] = None
    overall_credibility: Optional[float] = Field(None, ge=0, le=1)
    processing_time_seconds: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class FactCheckResponse(BaseModel):
    """API response wrapper."""
    success: bool
    data: Optional[FactCheckResult] = None
    message: Optional[str] = None


class WebSocketMessage(BaseModel):
    """Message format for WebSocket communication."""
    type: str  # status_update, claim_result, error, complete
    request_id: str
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LiveStreamConfig(BaseModel):
    """Configuration for live stream fact-checking."""
    stream_url: Optional[str] = None
    audio_enabled: bool = True
    video_enabled: bool = True
    check_interval_seconds: float = 5.0
    buffer_duration_seconds: float = 10.0


class TranscriptionResult(BaseModel):
    """Result of audio transcription."""
    text: str
    segments: list[dict[str, Any]] = []
    language: Optional[str] = None
    duration_seconds: Optional[float] = None


class OCRResult(BaseModel):
    """Result of OCR processing."""
    text: str
    confidence: Optional[float] = None
    regions: list[dict[str, Any]] = []
