"""
Echo Phoenix Control Service - Data Models
Complete type definitions for the entire system.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


# =============================================================================
# ENUMS
# =============================================================================

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    KILLED = "killed"


class PaymentState(str, Enum):
    PENDING = "pending"
    CREATED = "created"
    ACTION_REQUIRED = "action_required"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class Urgency(str, Enum):
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ResourceType(str, Enum):
    PAYMENT = "payment"
    THROTTLE = "throttle"
    STATE = "state"
    WEBHOOK = "webhook"
    KILL = "kill"


class NonceType(str, Enum):
    IDEMPOTENCY_KEY = "idempotency_key"
    WEBHOOK_EVENT = "webhook_event"
    CONTROL_ACTION = "control_action"


# =============================================================================
# SYSTEM STATE MODELS
# =============================================================================

class SystemState(BaseModel):
    """Current state of the Echo system."""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    throttle_pct: float = Field(ge=0.0, le=1.0, description="Current throttle percentage")
    error_rate: float = Field(ge=0.0, le=1.0, description="Error rate in last window")
    latency_p99_ms: float = Field(ge=0, description="P99 latency in milliseconds")
    requests_per_minute: float = Field(ge=0, description="Request rate")
    phi_static: float = Field(ge=0, description="Static viability metric")
    phi_dynamic: float = Field(ge=0, description="Dynamic viability metric")
    temperature: float = Field(ge=0, description="Effective system temperature")
    susceptibility: float = Field(ge=0, description="System susceptibility to perturbation")
    
    @property
    def adaptability_ratio(self) -> float:
        """Φ_d / Φ_s - key health indicator."""
        if self.phi_static == 0:
            return float('inf')
        return self.phi_dynamic / self.phi_static
    
    @property
    def is_critical(self) -> bool:
        """Check if system is near critical temperature."""
        T_CRITICAL = 0.9
        return abs(self.temperature - T_CRITICAL) < 0.1


class ControlAction(BaseModel):
    """Control action to apply to the system."""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    throttle_delta: float = Field(description="Change in throttle percentage")
    new_throttle: float = Field(ge=0.0, le=1.0, description="New throttle percentage")
    reason: str = Field(description="Reason for control action")
    urgency: Urgency = Field(default=Urgency.NORMAL, description="Urgency level")


# =============================================================================
# API REQUEST/RESPONSE MODELS
# =============================================================================

class ObserveRequest(BaseModel):
    """Request to observe system state."""
    source: str = Field(default="api", description="Source of observation request")
    include_metrics: bool = Field(default=True, description="Include detailed metrics")


class ObserveResponse(BaseModel):
    """Response from observe endpoint."""
    state: SystemState
    health: HealthStatus = Field(description="Overall health status")
    recommendations: List[str] = Field(default_factory=list)


class ControlRequest(BaseModel):
    """Request to compute control action."""
    current_state: SystemState
    target_throttle: Optional[float] = None
    override: bool = Field(default=False, description="Override safety checks")


class ControlResponse(BaseModel):
    """Response from control endpoint."""
    action: ControlAction
    applied: bool = Field(description="Whether action was applied")
    state_after: Optional[SystemState] = None


class KillRequest(BaseModel):
    """Emergency kill request."""
    reason: str = Field(description="Reason for kill")
    operator: str = Field(description="Operator initiating kill")
    confirmation: str = Field(description="Must be 'CONFIRM_KILL'")


class KillResponse(BaseModel):
    """Response from kill endpoint."""
    status: str
    reason: str
    operator: str
    timestamp: str
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: HealthStatus
    version: str = "2.4.0"
    environment: str
    uptime_seconds: float
    last_observation: Optional[str] = None
    last_control: Optional[str] = None


# =============================================================================
# PAYMENT MODELS
# =============================================================================

class PaymentRequest(BaseModel):
    """Request to create a payment."""
    order_id: str = Field(description="Application order ID")
    amount: int = Field(gt=0, description="Amount in smallest currency unit")
    currency: str = Field(default="usd", description="Three-letter currency code")
    customer_id: str = Field(description="Stripe customer ID")
    metadata: Optional[Dict[str, str]] = Field(default=None, description="Additional metadata")


class PaymentResponse(BaseModel):
    """Response from payment creation."""
    ledger_id: str
    stripe_id: str
    order_id: str
    amount: int
    currency: str
    state: PaymentState
    idempotency_key: str
    created_at: str


class WebhookEvent(BaseModel):
    """Incoming webhook event."""
    id: str
    type: str
    data: Dict[str, Any]
    created: int


class ReconciliationResult(BaseModel):
    """Result of reconciliation job."""
    timestamp: str
    events_checked: int
    gaps_detected: int
    gaps_repaired: List[str]
    missing_entries: List[str]
    status: str


# =============================================================================
# AIRTABLE MODELS
# =============================================================================

class ThrottleRecord(BaseModel):
    """Airtable system_throttle record."""
    timestamp: str
    throttle_pct: float
    reason: str
    urgency: Urgency
    operator: str
    active: bool


class StateRecord(BaseModel):
    """Airtable system_state record."""
    timestamp: str
    throttle_pct: float
    error_rate: float
    latency_p99_ms: float
    requests_per_minute: float
    phi_static: float
    phi_dynamic: float
    temperature: float
    health: HealthStatus


class NonceRecord(BaseModel):
    """Airtable used_nonces record."""
    nonce: str
    type: NonceType
    result_id: str
    created_at: str
    expires_at: str


class LedgerRecord(BaseModel):
    """Airtable payment_ledger record."""
    ledger_id: str
    stripe_id: str
    order_id: str
    amount: int
    currency: str
    state: PaymentState
    created_at: str
    updated_at: str
    idempotency_key: str
    metadata: str  # JSON string
    events: str  # JSON array string


class AuditRecord(BaseModel):
    """Airtable audit_log record."""
    timestamp: str
    action: str
    actor: str
    resource_type: ResourceType
    resource_id: str
    details: str  # JSON string
    result: str


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "HealthStatus",
    "PaymentState",
    "Urgency",
    "ResourceType",
    "NonceType",
    # System models
    "SystemState",
    "ControlAction",
    # API models
    "ObserveRequest",
    "ObserveResponse",
    "ControlRequest",
    "ControlResponse",
    "KillRequest",
    "KillResponse",
    "HealthResponse",
    # Payment models
    "PaymentRequest",
    "PaymentResponse",
    "WebhookEvent",
    "ReconciliationResult",
    # Airtable models
    "ThrottleRecord",
    "StateRecord",
    "NonceRecord",
    "LedgerRecord",
    "AuditRecord",
]
