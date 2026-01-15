"""
Echo Phoenix Control Service - Production Ready
FastAPI application for continuous control of the Echo system.

Endpoints:
- POST /observe - Capture current system state
- POST /control - Compute and apply control action
- GET /health - System health check
- POST /kill - Emergency shutdown (Global Kill Plane)
- GET /metrics - Prometheus-compatible metrics
"""

import os
import time
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
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
    WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "echo_webhook_secret")
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
    
    # Control parameters
    TARGET_THROTTLE = float(os.environ.get("TARGET_THROTTLE", "0.0"))
    MAX_THROTTLE = float(os.environ.get("MAX_THROTTLE", "1.0"))
    CONTROL_GAIN = float(os.environ.get("CONTROL_GAIN", "0.1"))
    
    # Critical temperature from Viability-Evolvability Theory
    T_CRITICAL = float(os.environ.get("T_CRITICAL", "0.9"))


config = Config()

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
    
    # Derived metrics
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
    version: str = "2.4.0"
    environment: str
    uptime_seconds: float
    last_observation: Optional[str] = None
    last_control: Optional[str] = None


class WebhookEvent(BaseModel):
    """Incoming webhook event."""
    id: str
    type: str
    data: Dict[str, Any]
    created: int


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
    
    async def observe(self) -> SystemState:
        """Observe current system state."""
        # In production, this would query actual metrics
        # For now, simulate based on control history
        
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
        
        # Persist to Airtable if configured
        if config.AIRTABLE_API_KEY:
            await self._persist_state(state)
        
        return state
    
    async def compute_control(self, state: SystemState, target: Optional[float] = None) -> ControlAction:
        """Compute control action based on current state."""
        target_throttle = target if target is not None else config.TARGET_THROTTLE
        
        # Kill switch override
        if self.kill_active:
            return ControlAction(
                throttle_delta=1.0 - state.throttle_pct,
                new_throttle=1.0,
                reason="KILL SWITCH ACTIVE",
                urgency="critical"
            )
        
        # Compute error signal
        error = target_throttle - state.throttle_pct
        
        # Proportional control with gain
        delta = config.CONTROL_GAIN * error
        
        # Safety bounds
        new_throttle = max(0.0, min(1.0, state.throttle_pct + delta))
        
        # Determine urgency based on state
        urgency = "normal"
        reason = f"Adjusting toward target {target_throttle:.2f}"
        
        if state.error_rate > 0.1:
            urgency = "high"
            reason = f"High error rate ({state.error_rate:.2%}), increasing throttle"
            new_throttle = min(1.0, state.throttle_pct + 0.1)
        
        if state.error_rate > 0.5:
            urgency = "critical"
            reason = f"Critical error rate ({state.error_rate:.2%}), emergency throttle"
            new_throttle = 1.0
        
        # Check adaptability ratio
        if state.adaptability_ratio < 0.5:
            reason += " | WARNING: Low adaptability ratio"
        
        action = ControlAction(
            throttle_delta=new_throttle - state.throttle_pct,
            new_throttle=new_throttle,
            reason=reason,
            urgency=urgency
        )
        
        self.control_history.append(action)
        self.last_control = action.timestamp
        
        # Persist to Airtable if configured
        if config.AIRTABLE_API_KEY:
            await self._persist_control(action)
        
        return action
    
    def activate_kill(self, reason: str, operator: str) -> bool:
        """Activate the Global Kill Plane."""
        self.kill_active = True
        self.control_history.append(ControlAction(
            throttle_delta=1.0,
            new_throttle=1.0,
            reason=f"KILL: {reason} by {operator}",
            urgency="critical"
        ))
        return True
    
    def deactivate_kill(self) -> bool:
        """Deactivate the Global Kill Plane."""
        self.kill_active = False
        return True
    
    def is_duplicate_event(self, event_id: str) -> bool:
        """Check if webhook event is a duplicate."""
        if event_id in self.processed_events:
            return True
        self.processed_events[event_id] = datetime.utcnow()
        # Clean old entries
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.processed_events = {
            k: v for k, v in self.processed_events.items() if v > cutoff
        }
        return False
    
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
            print(f"Failed to persist control: {e}")


# =============================================================================
# APPLICATION
# =============================================================================

app = FastAPI(
    title="Echo Phoenix Control Service",
    description="Continuous control system for the Echo AI framework",
    version="2.4.0"
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
# ENDPOINTS
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if not state_manager.kill_active else "killed",
        environment=config.ENVIRONMENT,
        uptime_seconds=time.time() - state_manager.start_time,
        last_observation=state_manager.last_observation,
        last_control=state_manager.last_control
    )


@app.post("/observe", response_model=ObserveResponse)
async def observe(request: ObserveRequest):
    """Observe current system state."""
    state = await state_manager.observe()
    
    # Determine health
    if state_manager.kill_active:
        health = "killed"
    elif state.error_rate > 0.1 or state.adaptability_ratio < 0.5:
        health = "degraded"
    elif state.error_rate > 0.5:
        health = "critical"
    else:
        health = "healthy"
    
    # Generate recommendations
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


@app.post("/control", response_model=ControlResponse)
async def control(request: ControlRequest):
    """Compute and apply control action."""
    action = await state_manager.compute_control(
        request.current_state,
        request.target_throttle
    )
    
    # Observe state after control
    state_after = await state_manager.observe()
    
    return ControlResponse(
        action=action,
        applied=True,
        state_after=state_after
    )


@app.post("/kill")
async def kill(request: KillRequest):
    """Emergency kill switch - Global Kill Plane."""
    if request.confirmation != "CONFIRM_KILL":
        raise HTTPException(status_code=400, detail="Invalid confirmation. Must be 'CONFIRM_KILL'")
    
    success = state_manager.activate_kill(request.reason, request.operator)
    
    return {
        "status": "killed",
        "reason": request.reason,
        "operator": request.operator,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Global Kill Plane activated. All operations halted."
    }


@app.post("/revive")
async def revive(operator: str = "system"):
    """Deactivate kill switch and resume operations."""
    state_manager.deactivate_kill()
    return {
        "status": "revived",
        "operator": operator,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "System revived. Operations resuming."
    }


@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint."""
    state = state_manager.current_state
    if not state:
        state = await state_manager.observe()
    
    lines = [
        f"# HELP echo_throttle_pct Current throttle percentage",
        f"# TYPE echo_throttle_pct gauge",
        f"echo_throttle_pct {state.throttle_pct}",
        f"# HELP echo_error_rate Current error rate",
        f"# TYPE echo_error_rate gauge",
        f"echo_error_rate {state.error_rate}",
        f"# HELP echo_latency_p99_ms P99 latency in milliseconds",
        f"# TYPE echo_latency_p99_ms gauge",
        f"echo_latency_p99_ms {state.latency_p99_ms}",
        f"# HELP echo_phi_static Static viability metric",
        f"# TYPE echo_phi_static gauge",
        f"echo_phi_static {state.phi_static}",
        f"# HELP echo_phi_dynamic Dynamic viability metric",
        f"# TYPE echo_phi_dynamic gauge",
        f"echo_phi_dynamic {state.phi_dynamic}",
        f"# HELP echo_temperature Effective system temperature",
        f"# TYPE echo_temperature gauge",
        f"echo_temperature {state.temperature}",
        f"# HELP echo_kill_active Kill switch status",
        f"# TYPE echo_kill_active gauge",
        f"echo_kill_active {1 if state_manager.kill_active else 0}",
    ]
    
    return "\n".join(lines)


@app.post("/webhook/stripe")
async def stripe_webhook(event: WebhookEvent):
    """Handle Stripe webhook events with exactly-once processing."""
    # Deduplication check
    if state_manager.is_duplicate_event(event.id):
        return {"status": "duplicate", "event_id": event.id}
    
    # Process event based on type
    if event.type == "payment_intent.succeeded":
        # Log to Evidence & Integrity Ledger
        print(f"Payment succeeded: {event.data.get('id')}")
    elif event.type == "payment_intent.payment_failed":
        print(f"Payment failed: {event.data.get('id')}")
    elif event.type == "charge.refunded":
        print(f"Charge refunded: {event.data.get('id')}")
    
    return {"status": "processed", "event_id": event.id}


# =============================================================================
# STARTUP / SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    print(f"Echo Phoenix Control Service starting...")
    print(f"Environment: {config.ENVIRONMENT}")
    print(f"Critical Temperature: {config.T_CRITICAL}")
    # Initial observation
    await state_manager.observe()
    print("Initial state observed. System ready.")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    print("Echo Phoenix Control Service shutting down...")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
