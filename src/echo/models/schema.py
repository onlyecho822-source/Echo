"""
Unified data model for Echo Phoenix.

All data flowing through Phoenix is normalized to this schema,
regardless of source protocol or format.
"""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field
import hashlib
import json


class Metadata(BaseModel):
    """Metadata about the data source and transformation."""

    source_id: str = Field(..., description="Unique identifier of the data source")
    source_protocol: str = Field(..., description="Original protocol (rest, grpc, mqtt)")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the data was fetched"
    )
    transform_version: str = Field(
        default="1.0",
        description="Version of the adapter/transform used"
    )
    original_format: str = Field(
        default="json",
        description="Original data format before normalization"
    )


class DataPayload(BaseModel):
    """The actual data content, normalized to a common structure."""

    data: dict[str, Any] = Field(..., description="The normalized data payload")
    schema_version: str = Field(
        default="1.0",
        description="Version of the data schema"
    )

    def content_hash(self) -> str:
        """Generate SHA-256 hash of the payload for content addressing."""
        # Canonical JSON serialization for consistent hashing
        canonical = json.dumps(self.data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()


class EchoMessage(BaseModel):
    """
    The unified message format for all data in Echo Phoenix.

    This is the core abstraction - every piece of data, regardless of
    source protocol or format, gets wrapped in this structure.
    """

    id: str = Field(..., description="Unique message identifier")
    metadata: Metadata = Field(..., description="Source and transform metadata")
    payload: DataPayload = Field(..., description="The actual data")
    content_hash: str = Field(
        default="",
        description="SHA-256 hash of payload for verification"
    )
    signature: str | None = Field(
        default=None,
        description="Optional cryptographic signature"
    )

    def model_post_init(self, __context: Any) -> None:
        """Compute content hash after initialization if not provided."""
        if not self.content_hash:
            object.__setattr__(self, 'content_hash', self.payload.content_hash())

    def verify_integrity(self) -> bool:
        """Verify the content hash matches the payload."""
        return self.content_hash == self.payload.content_hash()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TransformResult(BaseModel):
    """Result of a data transformation operation."""

    success: bool
    message: EchoMessage | None = None
    error: str | None = None
    source_bytes: int = 0
    transform_time_ms: float = 0.0
