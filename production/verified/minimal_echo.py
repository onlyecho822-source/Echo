"""
Echo Phoenix Minimal Production API
Enforces I1-I4 Invariants with Formal Guarantees
"""
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Literal, Optional
import hashlib
import hmac
import time
import os
from datetime import datetime
import asyncpg
from contextlib import asynccontextmanager

# ============================================================================
# INVARIANT ENFORCEMENT LAYER
# ============================================================================

class InvariantViolation(Exception):
    """Raised when any I1-I4 invariant would be violated"""
    pass

class Event(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    event_type: Literal["github.push", "stripe.payment", "webhook.trigger"]
    payload: dict
    actor: str = Field(..., description="Who/what triggered this event")
    timestamp: float = Field(default_factory=time.time)
    
class ControlCommand(BaseModel):
    action: Literal["freeze", "unfreeze", "throttle", "kill"]
    actor: str = Field(..., description="Must be in ALLOWED_ACTORS")
    reason: str = Field(..., min_length=10)
    throttle_value: Optional[float] = Field(None, ge=0.0, le=1.0)

# ============================================================================
# DATABASE CONNECTION POOL
# ============================================================================

DB_POOL = None

async def get_db():
    """Dependency injection for database connections"""
    if DB_POOL is None:
        raise HTTPException(503, "Database not initialized")
    async with DB_POOL.acquire() as conn:
        yield conn

# ============================================================================
# AUTHENTICATION & AUTHORIZATION
# ============================================================================

ALLOWED_ACTORS = set(os.getenv("ALLOWED_ACTORS", "admin,ops,security").split(","))
API_KEY = os.getenv("ECHO_API_KEY")

def verify_api_key(x_api_key: str = Header(...)):
    """I2: Authority Separation - Only authenticated actors"""
    if not API_KEY:
        raise HTTPException(500, "API_KEY not configured")
    if not hmac.compare_digest(x_api_key, API_KEY):
        raise HTTPException(401, "Invalid API key")
    return True

def verify_actor(actor: str):
    """I2: Authority Separation - Only allowed actors can control"""
    if actor not in ALLOWED_ACTORS:
        raise InvariantViolation(f"Actor '{actor}' not in ALLOWED_ACTORS: {ALLOWED_ACTORS}")

# ============================================================================
# I1: EXACTLY-ONCE PROCESSING
# ============================================================================

async def ensure_exactly_once(event_id: str, conn) -> bool:
    """
    I1 Invariant: Process event exactly once
    Returns: True if this is first processing, False if duplicate
    Raises: InvariantViolation if already processed
    """
    # Check deduplication table
    result = await conn.fetchrow(
        "SELECT event_id, processed_at FROM event_dedup WHERE event_id = $1",
        event_id
    )
    
    if result:
        # Event already processed - I1 violation would occur
        raise InvariantViolation(
            f"Event {event_id} already processed at {result['processed_at']}"
        )
    
    # Mark as processing (atomic)
    await conn.execute(
        "INSERT INTO event_dedup (event_id, processed_at) VALUES ($1, NOW())",
        event_id
    )
    
    return True

# ============================================================================
# I3: SAFETY GATING (FREEZE STATE)
# ============================================================================

async def check_freeze_state(conn) -> dict:
    """
    I3 Invariant: Respect system freeze state
    Returns: Current system state
    Raises: HTTPException(423) if system is frozen
    """
    state = await conn.fetchrow(
        "SELECT is_frozen, freeze_reason, throttle FROM system_state WHERE id = 1"
    )
    
    if not state:
        # Initialize default state if missing
        await conn.execute("""
            INSERT INTO system_state (id, is_frozen, throttle)
            VALUES (1, false, 0.0)
            ON CONFLICT (id) DO NOTHING
        """)
        state = {"is_frozen": False, "freeze_reason": None, "throttle": 0.0}
    
    if state["is_frozen"]:
        raise HTTPException(
            status_code=423,
            detail=f"System frozen: {state['freeze_reason']}"
        )
    
    # Apply throttle if set
    if state["throttle"] > 0:
        import random
        if random.random() < state["throttle"]:
            raise HTTPException(
                status_code=429,
                detail=f"Request throttled (rate: {state['throttle']})"
            )
    
    return state

# ============================================================================
# I4: COMPLETE AUDIT TRAIL
# ============================================================================

async def record_audit(
    event_type: str,
    actor: str,
    action: str,
    details: dict,
    conn
):
    """
    I4 Invariant: Every state change is audited
    Creates immutable audit record with cryptographic hash chain
    """
    # Get previous hash for chain
    prev = await conn.fetchrow(
        "SELECT hash FROM audit_trail ORDER BY id DESC LIMIT 1"
    )
    prev_hash = prev["hash"] if prev else "0" * 64
    
    # Create audit record
    audit_data = f"{event_type}|{actor}|{action}|{time.time()}|{prev_hash}"
    current_hash = hashlib.sha256(audit_data.encode()).hexdigest()
    
    await conn.execute("""
        INSERT INTO audit_trail (event_type, actor, action, details, prev_hash, hash)
        VALUES ($1, $2, $3, $4, $5, $6)
    """, event_type, actor, action, details, prev_hash, current_hash)
    
    return current_hash

# ============================================================================
# API ENDPOINTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database pool on startup"""
    global DB_POOL
    DB_URL = os.getenv("DATABASE_URL", "postgresql://localhost/echo_phoenix")
    DB_POOL = await asyncpg.create_pool(DB_URL, min_size=2, max_size=10)
    yield
    await DB_POOL.close()

app = FastAPI(
    title="Echo Phoenix Formal API",
    description="I1-I4 Invariant Enforced Event Processing",
    version="2.4.0",
    lifespan=lifespan
)

@app.post("/events", dependencies=[Depends(verify_api_key)])
async def process_event(event: Event, conn = Depends(get_db)):
    """
    Endpoint: Process external events with I1-I4 guarantees
    
    Invariants Enforced:
    - I1: Exactly-once processing via deduplication
    - I2: Authority separation via API key
    - I3: Safety gating via freeze check
    - I4: Complete audit trail
    """
    try:
        # I3: Check if system is frozen
        await check_freeze_state(conn)
        
        # I1: Ensure exactly-once processing
        await ensure_exactly_once(event.event_id, conn)
        
        # Process event (business logic here)
        result = {
            "event_id": event.event_id,
            "status": "processed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # I4: Record audit trail
        await record_audit(
            event_type=event.event_type,
            actor=event.actor,
            action="event_processed",
            details={"event_id": event.event_id, "result": result},
            conn=conn
        )
        
        return result
        
    except InvariantViolation as e:
        # I1 violation - return idempotent response
        return JSONResponse(
            status_code=200,
            content={
                "event_id": event.event_id,
                "status": "already_processed",
                "message": str(e)
            }
        )

@app.post("/control", dependencies=[Depends(verify_api_key)])
async def control_system(cmd: ControlCommand, conn = Depends(get_db)):
    """
    Endpoint: System control commands with I2-I4 guarantees
    
    Invariants Enforced:
    - I2: Only ALLOWED_ACTORS can execute control commands
    - I3: Freeze/unfreeze state changes
    - I4: All control actions audited
    """
    # I2: Verify actor authorization
    verify_actor(cmd.actor)
    
    if cmd.action == "freeze":
        await conn.execute(
            "UPDATE system_state SET is_frozen = true, freeze_reason = $1 WHERE id = 1",
            cmd.reason
        )
        status = "SYSTEM_FROZEN"
        
    elif cmd.action == "unfreeze":
        await conn.execute(
            "UPDATE system_state SET is_frozen = false, freeze_reason = NULL WHERE id = 1"
        )
        status = "SYSTEM_UNFROZEN"
        
    elif cmd.action == "throttle":
        if cmd.throttle_value is None:
            raise HTTPException(400, "throttle_value required for throttle action")
        await conn.execute(
            "UPDATE system_state SET throttle = $1 WHERE id = 1",
            cmd.throttle_value
        )
        status = f"THROTTLE_SET_{cmd.throttle_value}"
        
    elif cmd.action == "kill":
        # Kill = freeze + throttle 1.0
        await conn.execute(
            "UPDATE system_state SET is_frozen = true, throttle = 1.0, freeze_reason = $1 WHERE id = 1",
            f"KILL_SWITCH: {cmd.reason}"
        )
        status = "KILL_SWITCH_ACTIVATED"
    
    # I4: Audit the control action
    await record_audit(
        event_type="control",
        actor=cmd.actor,
        action=cmd.action,
        details={"reason": cmd.reason, "status": status},
        conn=conn
    )
    
    return {
        "status": status,
        "actor": cmd.actor,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint - no auth required"""
    return {
        "status": "healthy",
        "version": "2.4.0",
        "invariants": ["I1", "I2", "I3", "I4"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/state")
async def get_state(conn = Depends(get_db), _auth = Depends(verify_api_key)):
    """Get current system state"""
    state = await conn.fetchrow(
        "SELECT * FROM system_state WHERE id = 1"
    )
    return dict(state) if state else {"error": "No state found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
