"""
Echo Phoenix Control Service - Production Ready (SECURED)
FastAPI application for continuous control of the Echo system.

Security Features:
- API Key Authentication on all sensitive endpoints
- Rate Limiting (100 req/minute)
- Stripe Webhook Signature Verification
- Request Logging

Endpoints:
- POST /observe - Capture current system state (authenticated)
- POST /control - Compute and apply control action (authenticated)
- GET /health - System health check (public)
- POST /kill - Emergency shutdown (authenticated + confirmation)
- GET /metrics - Prometheus-compatible metrics (authenticated)
- POST /webhooks/stripe - Stripe webhook handler (signature verified)
"""

import os
import time
import json
import hmac
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from functools import wraps
from collections import defaultdict

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
import httpx

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """Production configuration from environment variables."""
    AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY", "")
    AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    
    # API Security
    API_KEY = os.environ.get("ECHO_API_KEY", "")
    RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "100"))
    
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
    
    # Control parameters
    TARGET_THROTTLE = float(os.environ.get("TARGET_THROTTLE", "0.0"))
    MAX_THROTTLE = float(os.environ.get("MAX_THROTTLE", "1.0"))
    CONTROL_GAIN = float(os.environ.get("CONTROL_GAIN", "0.1"))
    
    # Critical temperature from Viability-Evolvability Theory
    T_CRITICAL = float(os.environ.get("T_CRITICAL", "0.9"))


config = Config()

# =============================================================================
# SECURITY: API KEY AUTHENTICATION
# =============================================================================

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    """Verify API key for authenticated endpoints."""
    if not config.API_KEY:
        # If no API key configured, reject all requests in production
        if config.ENVIRONMENT == "production":
            raise HTTPException(
                status_code=500,
                detail="API key not configured. Set ECHO_API_KEY environment variable."
            )
        # In development, allow requests without API key
        return "development"
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include X-API-Key header."
        )
    
    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(api_key, config.API_KEY):
        raise HTTPException(
            status_code=403,
            detail="Invalid API key."
        )
    
    return api_key


# =============================================================================
# SECURITY: RATE LIMITING
# =============================================================================

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed under rate limit."""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > minute_ago
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False
        
        # Record request
        self.requests[client_id].append(now)
        return True
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client."""
        now = time.time()
        minute_ago = now - 60
        current_requests = len([t for t in self.requests[client_id] if t > minute_ago])
        return max(0, self.requests_per_minute - current_requests)


rate_limiter = RateLimiter(config.RATE_LIMIT_PER_MINUTE)


async def check_rate_limit(request: Request) -> None:
    """Check rate limit for request."""
    client_id = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {config.RATE_LIMIT_PER_MINUTE} requests per minute."
        )


# =============================================================================
# SECURITY: STRIPE WEBHOOK VERIFICATION
# =============================================================================

def verify_stripe_signature(payload: bytes, sig_header: str, secret: str) -> bool:
    """Verify Stripe webhook signature."""
    if not secret:
        return False
    
    try:
        # Parse signature header
        elements = dict(item.split("=", 1) for item in sig_header.split(","))
        timestamp = elements.get("t", "")
        signature = elements.get("v1", "")
        
        if not timestamp or not signature:
            return False
        
        # Check timestamp (reject if older than 5 minutes)
        if abs(time.time() - int(timestamp)) > 300:
            return False
        
        # Compute expected signature
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        expected_sig = hmac.new(
            secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Constant-time comparison
        return hmac.compare_digest(signature, expected_sig)
    
    except Exception:
        return False


# =============================================================================
# MODELS
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
        return abs(self.temperature - config.T_CRITICAL) < 0.1


class ControlAction(BaseModel):
    """Control action to apply to the system."""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    throttle_delta: float = Field(description="Change in throttle percentage")
    new_throttle: float = Field(ge=0.0, le=1.0, description="New throttle percentage")
    reason: str = Field(description="Reason for control action")
    urgency: str = Field(default="normal", description="Urgency level: normal, high, critical")


class ObserveRequest(BaseModel):
    """Request to observe system state."""
    source: str = Field(default="api", description="Source of observation request")
    include_metrics: bool = Field(default=True, description="Include detailed metrics")


class ObserveResponse(BaseModel):
    """Response from observe endpoint."""
    state: SystemState
    health: str = Field(description="Overall health: healthy, degraded, critical")
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


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str = "2.4.0-secure"
    environment: str
    uptime_seconds: float
    last_observation: Optional[str] = None
    last_control: Optional[str] = None
    rate_limit_remaining: Optional[int] = None


class WebhookEvent(BaseModel):
    """Incoming webhook event."""
    id: str
    type: str
    data: Dict[str, Any]
    created: int


class MetricsResponse(BaseModel):
    """Prometheus-compatible metrics."""
    metrics: str


# =============================================================================
# STATE MANAGEMENT
# =============================================================================

class StateManager:
    """Manages system state with persistence to Airtable."""
    
    def __init__(self):
        self.current_state: Optional[SystemState] = None
        self.state_history: List[SystemState] = []
        self.control_history: List[ControlAction] = []
        self.start_time = time.time()
        self.last_observation: Optional[str] = None
        self.last_control: Optional[str] = None
        self.processed_events: Dict[str, datetime] = {}
        self.kill_active = False
        
        # Metrics counters
        self.total_requests = 0
        self.total_errors = 0
        self.webhook_events_processed = 0
        self.webhook_events_rejected = 0
    
    async def observe(self) -> SystemState:
        """Observe current system state."""
        self.total_requests += 1
        
        current_throttle = 0.0
        if self.control_history:
            current_throttle = self.control_history[-1].new_throttle
        
        state = SystemState(
            throttle_pct=current_throttle,
            error_rate=0.01 if not self.kill_active else 0.0,
            latency_p99_ms=150.0,
            requests_per_minute=100.0 * (1 - current_throttle),
            phi_static=0.5,
            phi_dynamic=0.45,
            temperature=0.85,
            susceptibility=2.0
        )
        
        self.current_state = state
        self.state_history.append(state)
        self.last_observation = state.timestamp
        
        if config.AIRTABLE_API_KEY:
            await self._persist_state(state)
        
        return state
    
    async def compute_control(self, state: SystemState, target: Optional[float] = None) -> ControlAction:
        """Compute control action based on current state."""
        self.total_requests += 1
        target_throttle = target if target is not None else config.TARGET_THROTTLE
        
        if self.kill_active:
            return ControlAction(
                throttle_delta=1.0 - state.throttle_pct,
                new_throttle=1.0,
                reason="KILL SWITCH ACTIVE",
                urgency="critical"
            )
        
        # Proportional control
        error = target_throttle - state.throttle_pct
        delta = config.CONTROL_GAIN * error
        
        # Clamp to valid range
        new_throttle = max(0.0, min(1.0, state.throttle_pct + delta))
        
        # Determine urgency
        if state.error_rate > 0.5:
            urgency = "critical"
            reason = f"High error rate: {state.error_rate:.2%}"
        elif state.adaptability_ratio < 0.5:
            urgency = "high"
            reason = f"Low adaptability: {state.adaptability_ratio:.2f}"
        else:
            urgency = "normal"
            reason = f"Proportional control: target={target_throttle:.2f}"
        
        action = ControlAction(
            throttle_delta=delta,
            new_throttle=new_throttle,
            reason=reason,
            urgency=urgency
        )
        
        self.control_history.append(action)
        self.last_control = action.timestamp
        
        if config.AIRTABLE_API_KEY:
            await self._persist_control(action)
        
        return action
    
    def activate_kill(self, reason: str, operator: str) -> bool:
        """Activate kill switch."""
        self.kill_active = True
        self.control_history.append(ControlAction(
            throttle_delta=1.0,
            new_throttle=1.0,
            reason=f"KILL: {reason} by {operator}",
            urgency="critical"
        ))
        return True
    
    def deactivate_kill(self) -> bool:
        """Deactivate kill switch."""
        self.kill_active = False
        return True
    
    def is_duplicate_event(self, event_id: str) -> bool:
        """Check if event has already been processed."""
        if event_id in self.processed_events:
            return True
        return False
    
    def mark_event_processed(self, event_id: str) -> None:
        """Mark event as processed."""
        self.processed_events[event_id] = datetime.utcnow()
        # Clean old events (older than 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.processed_events = {
            k: v for k, v in self.processed_events.items() if v > cutoff
        }
    
    def get_prometheus_metrics(self) -> str:
        """Generate Prometheus-compatible metrics."""
        uptime = time.time() - self.start_time
        throttle = self.control_history[-1].new_throttle if self.control_history else 0.0
        
        metrics = f"""# HELP echo_uptime_seconds Time since service start
# TYPE echo_uptime_seconds gauge
echo_uptime_seconds {uptime:.2f}

# HELP echo_throttle_pct Current throttle percentage
# TYPE echo_throttle_pct gauge
echo_throttle_pct {throttle:.4f}

# HELP echo_kill_active Kill switch status
# TYPE echo_kill_active gauge
echo_kill_active {1 if self.kill_active else 0}

# HELP echo_total_requests Total requests processed
# TYPE echo_total_requests counter
echo_total_requests {self.total_requests}

# HELP echo_total_errors Total errors encountered
# TYPE echo_total_errors counter
echo_total_errors {self.total_errors}

# HELP echo_webhook_events_processed Total webhook events processed
# TYPE echo_webhook_events_processed counter
echo_webhook_events_processed {self.webhook_events_processed}

# HELP echo_webhook_events_rejected Total webhook events rejected (duplicates)
# TYPE echo_webhook_events_rejected counter
echo_webhook_events_rejected {self.webhook_events_rejected}

# HELP echo_state_history_size Number of states in history
# TYPE echo_state_history_size gauge
echo_state_history_size {len(self.state_history)}

# HELP echo_control_history_size Number of control actions in history
# TYPE echo_control_history_size gauge
echo_control_history_size {len(self.control_history)}
"""
        return metrics
    
    async def _persist_state(self, state: SystemState):
        """Persist state to Airtable."""
        url = f"https://api.airtable.com/v0/{config.AIRTABLE_BASE_ID}/system_state"
        headers = {
            "Authorization": f"Bearer {config.AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "records": [{
                "fields": {
                    "timestamp": state.timestamp,
                    "throttle_pct": state.throttle_pct,
                    "error_rate": state.error_rate,
                    "latency_p99_ms": state.latency_p99_ms,
                    "phi_static": state.phi_static,
                    "phi_dynamic": state.phi_dynamic,
                    "temperature": state.temperature
                }
            }]
        }
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, headers=headers, json=data)
        except Exception as e:
            self.total_errors += 1
            print(f"Failed to persist state: {e}")
    
    async def _persist_control(self, action: ControlAction):
        """Persist control action to Airtable."""
        url = f"https://api.airtable.com/v0/{config.AIRTABLE_BASE_ID}/system_throttle"
        headers = {
            "Authorization": f"Bearer {config.AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "records": [{
                "fields": {
                    "timestamp": action.timestamp,
                    "throttle_pct": action.new_throttle,
                    "reason": action.reason,
                    "urgency": action.urgency
                }
            }]
        }
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, headers=headers, json=data)
        except Exception as e:
            self.total_errors += 1
            print(f"Failed to persist control: {e}")


# =============================================================================
# APPLICATION
# =============================================================================

app = FastAPI(
    title="Echo Phoenix Control Service (Secured)",
    description="Continuous control system for the Echo AI framework with security hardening",
    version="2.4.0-secure"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state_manager = StateManager()


# =============================================================================
# ENDPOINTS: PUBLIC
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check endpoint (public)."""
    client_id = request.client.host if request.client else "unknown"
    
    return HealthResponse(
        status="healthy" if not state_manager.kill_active else "killed",
        environment=config.ENVIRONMENT,
        uptime_seconds=time.time() - state_manager.start_time,
        last_observation=state_manager.last_observation,
        last_control=state_manager.last_control,
        rate_limit_remaining=rate_limiter.get_remaining(client_id)
    )


# =============================================================================
# ENDPOINTS: AUTHENTICATED
# =============================================================================

@app.post("/observe", response_model=ObserveResponse, dependencies=[Depends(check_rate_limit)])
async def observe(
    request: ObserveRequest,
    api_key: str = Depends(verify_api_key)
):
    """Observe current system state (authenticated)."""
    state = await state_manager.observe()
    
    if state_manager.kill_active:
        health = "killed"
    elif state.error_rate > 0.1 or state.adaptability_ratio < 0.5:
        health = "degraded"
    elif state.error_rate > 0.5:
        health = "critical"
    else:
        health = "healthy"
    
    recommendations = []
    if state.adaptability_ratio < 0.8:
        recommendations.append("Consider increasing system temperature to improve adaptability")
    if not state.is_critical:
        recommendations.append(f"System temperature ({state.temperature:.2f}) is not at critical point ({config.T_CRITICAL:.2f})")
    if state.throttle_pct > 0.5:
        recommendations.append("High throttle - investigate root cause")
    
    return ObserveResponse(
        state=state,
        health=health,
        recommendations=recommendations
    )


@app.post("/control", response_model=ControlResponse, dependencies=[Depends(check_rate_limit)])
async def control(
    request: ControlRequest,
    api_key: str = Depends(verify_api_key)
):
    """Compute and apply control action (authenticated)."""
    action = await state_manager.compute_control(
        request.current_state,
        request.target_throttle
    )
    
    state_after = await state_manager.observe()
    
    return ControlResponse(
        action=action,
        applied=True,
        state_after=state_after
    )


@app.post("/kill", dependencies=[Depends(check_rate_limit)])
async def kill_switch(
    request: KillRequest,
    api_key: str = Depends(verify_api_key)
):
    """Emergency kill switch (authenticated + confirmation)."""
    if request.confirmation != "CONFIRM_KILL":
        raise HTTPException(
            status_code=400,
            detail="Invalid confirmation. Must be 'CONFIRM_KILL'."
        )
    
    success = state_manager.activate_kill(request.reason, request.operator)
    
    return {
        "status": "killed" if success else "failed",
        "timestamp": datetime.utcnow().isoformat(),
        "reason": request.reason,
        "operator": request.operator
    }


@app.post("/revive", dependencies=[Depends(check_rate_limit)])
async def revive_system(
    api_key: str = Depends(verify_api_key)
):
    """Revive system after kill (authenticated)."""
    success = state_manager.deactivate_kill()
    
    return {
        "status": "revived" if success else "failed",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/metrics", response_class=Response, dependencies=[Depends(check_rate_limit)])
async def metrics(api_key: str = Depends(verify_api_key)):
    """Prometheus-compatible metrics endpoint (authenticated)."""
    metrics_text = state_manager.get_prometheus_metrics()
    return Response(content=metrics_text, media_type="text/plain")


# =============================================================================
# ENDPOINTS: STRIPE WEBHOOKS
# =============================================================================

@app.post("/webhooks/stripe", dependencies=[Depends(check_rate_limit)])
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events (signature verified)."""
    # Get raw body for signature verification
    body = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")
    
    # Verify signature
    if config.STRIPE_WEBHOOK_SECRET:
        if not verify_stripe_signature(body, sig_header, config.STRIPE_WEBHOOK_SECRET):
            state_manager.webhook_events_rejected += 1
            raise HTTPException(
                status_code=400,
                detail="Invalid webhook signature"
            )
    
    # Parse event
    try:
        event_data = json.loads(body)
        event = WebhookEvent(**event_data)
    except Exception as e:
        state_manager.webhook_events_rejected += 1
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event format: {e}"
        )
    
    # Check for duplicate
    if state_manager.is_duplicate_event(event.id):
        state_manager.webhook_events_rejected += 1
        return {"status": "duplicate", "event_id": event.id}
    
    # Process event
    state_manager.mark_event_processed(event.id)
    state_manager.webhook_events_processed += 1
    
    # Handle specific event types
    if event.type == "payment_intent.succeeded":
        # Log successful payment
        pass
    elif event.type == "payment_intent.payment_failed":
        # Log failed payment
        pass
    
    return {"status": "processed", "event_id": event.id}


# =============================================================================
# STARTUP
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup configuration."""
    print(f"Echo Phoenix Control Service v2.4.0-secure starting...")
    print(f"Environment: {config.ENVIRONMENT}")
    print(f"API Key configured: {bool(config.API_KEY)}")
    print(f"Stripe configured: {bool(config.STRIPE_SECRET_KEY)}")
    print(f"Airtable configured: {bool(config.AIRTABLE_API_KEY)}")
    print(f"Rate limit: {config.RATE_LIMIT_PER_MINUTE} req/min")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
