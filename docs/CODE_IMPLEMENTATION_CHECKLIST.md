# ECP v2.2: Code Implementation Checklist

**What You Need to Write**

After comprehensive review, here's exactly what code you need to write to make ECP v2.2 production-ready.

---

## CURRENT STATUS

### ✅ What We Have (Partial Implementations)
- Basic file structure and stubs
- Some core modules with partial logic
- Configuration files (policy.json)
- Documentation (complete)

### ❌ What's Missing (YOU NEED TO WRITE)
- **Complete implementations** of all core modules
- **Database integration** (currently file-based only)
- **API endpoints** (server.py is stub)
- **Tests** (none exist)
- **CLI tools** (none exist)
- **Monitoring scripts** (none exist)
- **Docker/deployment configs** (none exist)

---

## PRIORITY 1: CORE TRANSPARENCY LEDGER (CRITICAL)

These are the absolute minimum files needed for ECP v2.2 to function.

### 1.1 Transparency Ledger Core (`transparency_ledger.py`)

**Location:** `reference-implementation/ai_coordination/core/transparency_ledger.py`

**What it does:** The heart of ECP v2.2 - immutable decision recording

**What you need to write:**

```python
"""
Transparency Ledger - Immutable Decision Record

This is the ONLY mandatory component of ECP v2.2.
Everything else is optional.
"""

import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class TransparencyLedger:
    """
    Immutable, append-only ledger for recording all agent decisions.
    
    Key Properties:
    - Append-only (no modifications or deletions)
    - Hash-chained (each entry contains hash of previous)
    - Plain-language explanations required
    - Timestamped and attributed
    """
    
    def __init__(self, storage_path: Path):
        """Initialize ledger with storage backend."""
        self.storage_path = storage_path
        self.ledger_file = storage_path / "ledger.jsonl"
        self.index_file = storage_path / "ledger_index.json"
        self._ensure_initialized()
    
    def _ensure_initialized(self):
        """Create ledger files if they don't exist."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        if not self.ledger_file.exists():
            # Create genesis entry
            genesis = self._create_genesis_entry()
            self._append_to_file(genesis)
            self._update_index(genesis)
    
    def _create_genesis_entry(self) -> dict:
        """Create the first entry in the ledger."""
        return {
            "id": "genesis",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "system",
            "agent": "system",
            "action": "initialize_ledger",
            "explanation": "Transparency Ledger initialized",
            "context": {},
            "previous_hash": "0" * 64,
            "hash": self._calculate_hash({
                "id": "genesis",
                "timestamp": datetime.utcnow().isoformat(),
                "previous_hash": "0" * 64
            })
        }
    
    def record_decision(
        self,
        agent: str,
        action: str,
        explanation: str,
        context: Dict,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Record a decision to the ledger.
        
        Args:
            agent: Name/ID of the agent making the decision
            action: What action is being taken (e.g., "deploy_code", "transfer_funds")
            explanation: Plain-language explanation of WHY (REQUIRED)
            context: Relevant context (inputs, state, etc.)
            metadata: Optional additional metadata
        
        Returns:
            entry_id: Unique ID of the ledger entry
        
        Raises:
            ValueError: If explanation is missing or too short
        """
        # Validate explanation
        if not explanation or len(explanation) < 10:
            raise ValueError("Explanation must be at least 10 characters")
        
        # Get previous entry hash
        previous_hash = self._get_latest_hash()
        
        # Create entry
        entry = {
            "id": self._generate_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "type": "decision",
            "agent": agent,
            "action": action,
            "explanation": explanation,
            "context": context,
            "metadata": metadata or {},
            "previous_hash": previous_hash
        }
        
        # Calculate hash
        entry["hash"] = self._calculate_hash(entry)
        
        # Append to ledger
        self._append_to_file(entry)
        self._update_index(entry)
        
        return entry["id"]
    
    def verify_integrity(self) -> tuple[bool, Optional[str]]:
        """
        Verify the integrity of the entire ledger.
        
        Returns:
            (is_valid, error_message)
        """
        entries = self._read_all_entries()
        
        for i, entry in enumerate(entries):
            # Verify hash
            calculated_hash = self._calculate_hash(entry, exclude_hash=True)
            if calculated_hash != entry["hash"]:
                return False, f"Hash mismatch at entry {i}: {entry['id']}"
            
            # Verify chain
            if i > 0:
                if entry["previous_hash"] != entries[i-1]["hash"]:
                    return False, f"Chain broken at entry {i}: {entry['id']}"
        
        return True, None
    
    def query(
        self,
        agent: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query the ledger with filters.
        
        Args:
            agent: Filter by agent name
            action: Filter by action type
            start_time: Filter by start timestamp (ISO format)
            end_time: Filter by end timestamp (ISO format)
            limit: Maximum number of results
        
        Returns:
            List of matching entries
        """
        entries = self._read_all_entries()
        results = []
        
        for entry in entries:
            # Apply filters
            if agent and entry.get("agent") != agent:
                continue
            if action and entry.get("action") != action:
                continue
            if start_time and entry.get("timestamp") < start_time:
                continue
            if end_time and entry.get("timestamp") > end_time:
                continue
            
            results.append(entry)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_entry(self, entry_id: str) -> Optional[Dict]:
        """Get a specific entry by ID."""
        index = self._load_index()
        if entry_id not in index:
            return None
        
        offset = index[entry_id]["offset"]
        with open(self.ledger_file, 'r') as f:
            f.seek(offset)
            line = f.readline()
            return json.loads(line)
    
    # Private helper methods
    
    def _generate_id(self) -> str:
        """Generate unique entry ID."""
        return f"entry_{int(time.time() * 1000000)}"
    
    def _calculate_hash(self, entry: dict, exclude_hash: bool = False) -> str:
        """Calculate SHA-256 hash of entry."""
        # Create a copy without the hash field
        entry_copy = {k: v for k, v in entry.items() if k != "hash" or not exclude_hash}
        
        # Serialize deterministically
        serialized = json.dumps(entry_copy, sort_keys=True)
        
        # Calculate hash
        return hashlib.sha256(serialized.encode()).hexdigest()
    
    def _get_latest_hash(self) -> str:
        """Get hash of the most recent entry."""
        try:
            with open(self.ledger_file, 'rb') as f:
                # Seek to end and read backwards to find last line
                f.seek(0, 2)  # End of file
                file_size = f.tell()
                
                # Read last 10KB (should contain last entry)
                seek_pos = max(0, file_size - 10240)
                f.seek(seek_pos)
                lines = f.read().decode().split('\n')
                
                # Get last non-empty line
                for line in reversed(lines):
                    if line.strip():
                        entry = json.loads(line)
                        return entry["hash"]
                
                return "0" * 64  # Shouldn't happen if genesis exists
        except Exception:
            return "0" * 64
    
    def _append_to_file(self, entry: dict):
        """Append entry to ledger file."""
        with open(self.ledger_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _update_index(self, entry: dict):
        """Update the index file for fast lookups."""
        index = self._load_index()
        
        # Get current file size (offset for this entry)
        offset = self.ledger_file.stat().st_size - len(json.dumps(entry)) - 1
        
        index[entry["id"]] = {
            "offset": offset,
            "timestamp": entry["timestamp"],
            "agent": entry.get("agent"),
            "action": entry.get("action")
        }
        
        self.index_file.write_text(json.dumps(index, indent=2))
    
    def _load_index(self) -> dict:
        """Load the index file."""
        if not self.index_file.exists():
            return {}
        return json.loads(self.index_file.read_text())
    
    def _read_all_entries(self) -> List[Dict]:
        """Read all entries from ledger (use sparingly, can be large)."""
        entries = []
        with open(self.ledger_file, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        return entries
```

**Style Guidelines:**
- ✅ Type hints on all methods
- ✅ Comprehensive docstrings
- ✅ Error handling with specific exceptions
- ✅ Private methods prefixed with `_`
- ✅ Immutability enforced (no delete/update methods)
- ✅ Hash chain verification built-in

---

### 1.2 Simple API Server (`api_server.py`)

**Location:** `reference-implementation/ai_coordination/api/api_server.py`

**What it does:** REST API for interacting with the ledger

**What you need to write:**

```python
"""
Simple REST API for Transparency Ledger

Provides HTTP endpoints for:
- Recording decisions
- Querying ledger
- Verifying integrity
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, Dict, List
import uvicorn

from ..core.transparency_ledger import TransparencyLedger

app = FastAPI(
    title="Echo Coordination Protocol API",
    description="Transparency Ledger REST API",
    version="2.2.0"
)

# Initialize ledger
LEDGER_PATH = Path("/var/lib/ecp/ledger")
ledger = TransparencyLedger(LEDGER_PATH)

# Request/Response Models

class DecisionRequest(BaseModel):
    agent: str = Field(..., description="Agent making the decision")
    action: str = Field(..., description="Action being taken")
    explanation: str = Field(..., min_length=10, description="Plain-language explanation")
    context: Dict = Field(default_factory=dict, description="Relevant context")
    metadata: Optional[Dict] = Field(default=None, description="Optional metadata")

class DecisionResponse(BaseModel):
    entry_id: str
    status: str = "recorded"

class QueryRequest(BaseModel):
    agent: Optional[str] = None
    action: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    limit: int = Field(default=100, le=1000)

class IntegrityResponse(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    total_entries: int

# Endpoints

@app.post("/decisions", response_model=DecisionResponse)
async def record_decision(request: DecisionRequest):
    """Record a new decision to the ledger."""
    try:
        entry_id = ledger.record_decision(
            agent=request.agent,
            action=request.action,
            explanation=request.explanation,
            context=request.context,
            metadata=request.metadata
        )
        return DecisionResponse(entry_id=entry_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/query", response_model=List[Dict])
async def query_ledger(request: QueryRequest):
    """Query the ledger with filters."""
    try:
        results = ledger.query(
            agent=request.agent,
            action=request.action,
            start_time=request.start_time,
            end_time=request.end_time,
            limit=request.limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/entries/{entry_id}")
async def get_entry(entry_id: str):
    """Get a specific entry by ID."""
    entry = ledger.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@app.get("/integrity", response_model=IntegrityResponse)
async def verify_integrity():
    """Verify the integrity of the entire ledger."""
    is_valid, error = ledger.verify_integrity()
    
    # Count entries
    total = len(ledger._read_all_entries())
    
    return IntegrityResponse(
        is_valid=is_valid,
        error_message=error,
        total_entries=total
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.2.0"}

# Run server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Style Guidelines:**
- ✅ FastAPI with Pydantic models
- ✅ Proper HTTP status codes
- ✅ Error handling with HTTPException
- ✅ Type hints everywhere
- ✅ OpenAPI docs auto-generated

---

## PRIORITY 2: OPTIONAL SERVICES (IMPORTANT)

These are the "advisory" services that make ECP v2.2 useful but aren't mandatory.

### 2.1 Friction Calculator (`friction_calculator.py`)

**Location:** `reference-implementation/ai_coordination/services/friction_calculator.py`

**What it does:** Calculates how much "friction" (delay, requirements) should be applied to a decision

**What you need to write:**

```python
"""
Friction Calculator - Advisory Service

Suggests procedural hurdles for high-risk decisions.
Agents can ignore these suggestions (they're not mandatory).
"""

from typing import Dict, List
from enum import Enum

class FrictionLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class FrictionRequirement:
    """A suggested requirement to add friction."""
    def __init__(self, type: str, description: str, estimated_time: int):
        self.type = type  # "delay", "approval", "documentation", "review"
        self.description = description
        self.estimated_time = estimated_time  # seconds

class FrictionCalculator:
    """
    Calculates suggested friction for decisions.
    
    Friction is based on:
    - Impact (how many systems/users affected)
    - Reversibility (can it be undone easily)
    - Precedent (has this been done before)
    - Velocity (how fast is the agent acting)
    """
    
    def __init__(self, config: Dict):
        self.config = config
    
    def calculate_friction(
        self,
        action: str,
        context: Dict,
        agent_history: List[Dict]
    ) -> tuple[FrictionLevel, List[FrictionRequirement]]:
        """
        Calculate suggested friction level and requirements.
        
        Args:
            action: The action being taken
            context: Context of the decision
            agent_history: Recent decisions by this agent
        
        Returns:
            (friction_level, requirements)
        """
        # Calculate impact score
        impact_score = self._calculate_impact(action, context)
        
        # Calculate reversibility score
        reversibility_score = self._calculate_reversibility(action, context)
        
        # Calculate precedent score
        precedent_score = self._calculate_precedent(action, agent_history)
        
        # Calculate velocity score
        velocity_score = self._calculate_velocity(agent_history)
        
        # Combine scores
        total_score = (
            impact_score * 0.4 +
            reversibility_score * 0.3 +
            precedent_score * 0.2 +
            velocity_score * 0.1
        )
        
        # Determine friction level
        if total_score < 0.2:
            level = FrictionLevel.NONE
        elif total_score < 0.4:
            level = FrictionLevel.LOW
        elif total_score < 0.6:
            level = FrictionLevel.MEDIUM
        elif total_score < 0.8:
            level = FrictionLevel.HIGH
        else:
            level = FrictionLevel.CRITICAL
        
        # Generate requirements
        requirements = self._generate_requirements(level, action, context)
        
        return level, requirements
    
    def _calculate_impact(self, action: str, context: Dict) -> float:
        """Calculate impact score (0.0 to 1.0)."""
        # High-impact actions
        high_impact_keywords = ["deploy", "delete", "transfer", "modify", "shutdown"]
        
        if any(keyword in action.lower() for keyword in high_impact_keywords):
            return 0.8
        
        # Check context for impact indicators
        if "users_affected" in context:
            users = context["users_affected"]
            if users > 1000:
                return 0.9
            elif users > 100:
                return 0.6
            elif users > 10:
                return 0.3
        
        return 0.1
    
    def _calculate_reversibility(self, action: str, context: Dict) -> float:
        """Calculate reversibility score (0.0 = easily reversible, 1.0 = irreversible)."""
        irreversible_keywords = ["delete", "destroy", "burn", "transfer", "send"]
        
        if any(keyword in action.lower() for keyword in irreversible_keywords):
            return 0.9
        
        if context.get("reversible") is False:
            return 1.0
        
        return 0.2
    
    def _calculate_precedent(self, action: str, agent_history: List[Dict]) -> float:
        """Calculate precedent score (0.0 = done many times, 1.0 = never done)."""
        # Count how many times this action has been done
        similar_actions = [
            h for h in agent_history
            if h.get("action") == action
        ]
        
        count = len(similar_actions)
        
        if count == 0:
            return 1.0
        elif count < 5:
            return 0.6
        elif count < 20:
            return 0.3
        else:
            return 0.1
    
    def _calculate_velocity(self, agent_history: List[Dict]) -> float:
        """Calculate velocity score (0.0 = slow, 1.0 = very fast)."""
        # Count actions in last hour
        # (Simplified - in production, parse timestamps)
        recent_count = len(agent_history[:10])  # Last 10 actions
        
        if recent_count > 50:
            return 1.0
        elif recent_count > 20:
            return 0.7
        elif recent_count > 10:
            return 0.4
        else:
            return 0.1
    
    def _generate_requirements(
        self,
        level: FrictionLevel,
        action: str,
        context: Dict
    ) -> List[FrictionRequirement]:
        """Generate specific friction requirements based on level."""
        requirements = []
        
        if level == FrictionLevel.NONE:
            return requirements
        
        if level.value >= FrictionLevel.LOW.value:
            requirements.append(FrictionRequirement(
                type="documentation",
                description="Document the decision and rationale",
                estimated_time=60
            ))
        
        if level.value >= FrictionLevel.MEDIUM.value:
            requirements.append(FrictionRequirement(
                type="delay",
                description="Wait 5 minutes before executing",
                estimated_time=300
            ))
        
        if level.value >= FrictionLevel.HIGH.value:
            requirements.append(FrictionRequirement(
                type="approval",
                description="Require approval from one other agent",
                estimated_time=600
            ))
        
        if level == FrictionLevel.CRITICAL:
            requirements.append(FrictionRequirement(
                type="review",
                description="Require human review before proceeding",
                estimated_time=3600
            ))
        
        return requirements
```

**Style Guidelines:**
- ✅ Clear scoring methodology
- ✅ Configurable weights
- ✅ Enum for friction levels
- ✅ Dataclass for requirements
- ✅ Extensible design

---

### 2.2 Transparency Dashboard (Web UI)

**Location:** `dashboard/index.html` + `dashboard/app.js`

**What it does:** Human-readable web interface to view all decisions

**What you need to write:**

**`dashboard/index.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECP Transparency Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #2196F3;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .decisions {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .decision {
            padding: 20px;
            border-bottom: 1px solid #eee;
        }
        .decision:last-child { border-bottom: none; }
        .decision-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .decision-agent {
            font-weight: bold;
            color: #2196F3;
        }
        .decision-time {
            color: #999;
            font-size: 14px;
        }
        .decision-action {
            font-size: 18px;
            margin-bottom: 10px;
        }
        .decision-explanation {
            color: #666;
            line-height: 1.5;
        }
        .integrity {
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 4px;
            display: inline-block;
            margin-top: 10px;
        }
        .integrity.invalid {
            background: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 ECP Transparency Dashboard</h1>
            <p>Real-time view of all agent decisions</p>
            <div id="integrity"></div>
        </header>
        
        <div class="stats" id="stats">
            <!-- Stats will be populated by JavaScript -->
        </div>
        
        <div class="decisions" id="decisions">
            <!-- Decisions will be populated by JavaScript -->
        </div>
    </div>
    
    <script src="app.js"></script>
</body>
</html>
```

**`dashboard/app.js`:**
```javascript
// ECP Transparency Dashboard

const API_BASE = 'http://localhost:8000';

// Fetch and display data
async function loadDashboard() {
    try {
        // Load integrity status
        const integrity = await fetch(`${API_BASE}/integrity`).then(r => r.json());
        displayIntegrity(integrity);
        
        // Load recent decisions
        const decisions = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ limit: 50 })
        }).then(r => r.json());
        
        displayStats(decisions);
        displayDecisions(decisions);
        
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

function displayIntegrity(integrity) {
    const div = document.getElementById('integrity');
    const className = integrity.is_valid ? 'integrity' : 'integrity invalid';
    const status = integrity.is_valid ? '✓ Ledger Integrity Verified' : '✗ Integrity Check Failed';
    
    div.innerHTML = `<div class="${className}">${status}</div>`;
    
    if (!integrity.is_valid) {
        div.innerHTML += `<p style="color: red; margin-top: 10px;">Error: ${integrity.error_message}</p>`;
    }
}

function displayStats(decisions) {
    const stats = {
        total: decisions.length,
        agents: new Set(decisions.map(d => d.agent)).size,
        actions: new Set(decisions.map(d => d.action)).size,
        today: decisions.filter(d => isToday(d.timestamp)).length
    };
    
    document.getElementById('stats').innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${stats.total}</div>
            <div class="stat-label">Total Decisions</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.agents}</div>
            <div class="stat-label">Active Agents</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.actions}</div>
            <div class="stat-label">Action Types</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.today}</div>
            <div class="stat-label">Today</div>
        </div>
    `;
}

function displayDecisions(decisions) {
    const html = decisions.map(d => `
        <div class="decision">
            <div class="decision-header">
                <span class="decision-agent">${escapeHtml(d.agent)}</span>
                <span class="decision-time">${formatTime(d.timestamp)}</span>
            </div>
            <div class="decision-action">${escapeHtml(d.action)}</div>
            <div class="decision-explanation">${escapeHtml(d.explanation)}</div>
        </div>
    `).join('');
    
    document.getElementById('decisions').innerHTML = html;
}

// Utility functions

function isToday(timestamp) {
    const date = new Date(timestamp);
    const today = new Date();
    return date.toDateString() === today.toDateString();
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-refresh every 5 seconds
setInterval(loadDashboard, 5000);

// Initial load
loadDashboard();
```

**Style Guidelines:**
- ✅ Vanilla JavaScript (no frameworks needed)
- ✅ Clean, minimal design
- ✅ Auto-refresh
- ✅ XSS protection (escapeHtml)
- ✅ Responsive layout

---

## PRIORITY 3: TESTS (ESSENTIAL FOR PRODUCTION)

You need tests to prove the system works.

### 3.1 Ledger Tests (`test_transparency_ledger.py`)

**Location:** `tests/test_transparency_ledger.py`

**What you need to write:**

```python
"""
Tests for Transparency Ledger

Run with: pytest tests/test_transparency_ledger.py
"""

import pytest
import tempfile
from pathlib import Path
from reference_implementation.ai_coordination.core.transparency_ledger import TransparencyLedger

@pytest.fixture
def ledger():
    """Create a temporary ledger for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield TransparencyLedger(Path(tmpdir))

def test_ledger_initialization(ledger):
    """Test that ledger initializes with genesis entry."""
    entries = ledger._read_all_entries()
    assert len(entries) == 1
    assert entries[0]["id"] == "genesis"

def test_record_decision(ledger):
    """Test recording a decision."""
    entry_id = ledger.record_decision(
        agent="test_agent",
        action="test_action",
        explanation="This is a test decision",
        context={"key": "value"}
    )
    
    assert entry_id is not None
    
    entry = ledger.get_entry(entry_id)
    assert entry["agent"] == "test_agent"
    assert entry["action"] == "test_action"
    assert entry["explanation"] == "This is a test decision"

def test_explanation_required(ledger):
    """Test that explanation is required."""
    with pytest.raises(ValueError):
        ledger.record_decision(
            agent="test_agent",
            action="test_action",
            explanation="",  # Too short
            context={}
        )

def test_hash_chain(ledger):
    """Test that hash chain is maintained."""
    # Record multiple decisions
    id1 = ledger.record_decision("agent1", "action1", "Explanation 1", {})
    id2 = ledger.record_decision("agent2", "action2", "Explanation 2", {})
    
    entry1 = ledger.get_entry(id1)
    entry2 = ledger.get_entry(id2)
    
    # Entry 2's previous_hash should match entry 1's hash
    assert entry2["previous_hash"] == entry1["hash"]

def test_integrity_verification(ledger):
    """Test integrity verification."""
    # Record some decisions
    ledger.record_decision("agent1", "action1", "Explanation 1", {})
    ledger.record_decision("agent2", "action2", "Explanation 2", {})
    
    # Verify integrity
    is_valid, error = ledger.verify_integrity()
    assert is_valid is True
    assert error is None

def test_query_by_agent(ledger):
    """Test querying by agent."""
    ledger.record_decision("agent1", "action1", "Explanation 1", {})
    ledger.record_decision("agent2", "action2", "Explanation 2", {})
    ledger.record_decision("agent1", "action3", "Explanation 3", {})
    
    results = ledger.query(agent="agent1")
    assert len(results) == 2
    assert all(r["agent"] == "agent1" for r in results)

def test_query_by_action(ledger):
    """Test querying by action."""
    ledger.record_decision("agent1", "deploy", "Deploy app", {})
    ledger.record_decision("agent2", "delete", "Delete file", {})
    ledger.record_decision("agent3", "deploy", "Deploy service", {})
    
    results = ledger.query(action="deploy")
    assert len(results) == 2
    assert all(r["action"] == "deploy" for r in results)

def test_query_limit(ledger):
    """Test query limit."""
    for i in range(10):
        ledger.record_decision(f"agent{i}", "action", f"Explanation {i}", {})
    
    results = ledger.query(limit=5)
    assert len(results) <= 5
```

**Style Guidelines:**
- ✅ pytest framework
- ✅ Fixtures for setup/teardown
- ✅ Test one thing per test
- ✅ Clear test names
- ✅ Use temporary directories

---

## PRIORITY 4: DEPLOYMENT (REQUIRED FOR PRODUCTION)

### 4.1 Docker Configuration

**`Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY reference-implementation/ ./reference-implementation/
COPY dashboard/ ./dashboard/

# Create ledger directory
RUN mkdir -p /var/lib/ecp/ledger

# Expose API port
EXPOSE 8000

# Expose dashboard port
EXPOSE 8080

# Run API server
CMD ["python", "-m", "reference_implementation.ai_coordination.api.api_server"]
```

**`docker-compose.yml`:**
```yaml
version: '3.8'

services:
  ecp-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ledger-data:/var/lib/ecp/ledger
    environment:
      - LEDGER_PATH=/var/lib/ecp/ledger
    restart: unless-stopped
  
  ecp-dashboard:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./dashboard:/usr/share/nginx/html:ro
    restart: unless-stopped

volumes:
  ledger-data:
```

**`requirements.txt`:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pytest==7.4.3
```

---

## SUMMARY: WHAT YOU NEED TO WRITE

### Critical (Must Have)
1. ✅ **transparency_ledger.py** (400 lines) - Core ledger implementation
2. ✅ **api_server.py** (150 lines) - REST API
3. ✅ **test_transparency_ledger.py** (100 lines) - Tests
4. ✅ **Dockerfile** (20 lines) - Container config
5. ✅ **docker-compose.yml** (25 lines) - Orchestration

### Important (Should Have)
6. ✅ **friction_calculator.py** (200 lines) - Advisory friction service
7. ✅ **dashboard/index.html** (80 lines) - Web UI
8. ✅ **dashboard/app.js** (100 lines) - Dashboard logic

### Optional (Nice to Have)
9. **network_opinion_poll.py** (150 lines) - Multi-agent polling
10. **cli.py** (100 lines) - Command-line interface
11. **monitoring.py** (150 lines) - Health checks and metrics

---

## TOTAL LINES OF CODE TO WRITE

**Critical:** ~695 lines  
**Important:** ~380 lines  
**Optional:** ~400 lines  

**Total:** ~1,475 lines of production code

---

## CODING STYLE GUIDELINES

### General Principles
- ✅ **Type hints everywhere** - Python 3.10+ style
- ✅ **Docstrings for all public methods** - Google style
- ✅ **Error handling** - Specific exceptions, not bare `except`
- ✅ **Logging** - Use `logging` module, not `print()`
- ✅ **Configuration** - Environment variables, not hardcoded
- ✅ **Immutability** - No delete/update methods on ledger
- ✅ **Testing** - pytest, fixtures, one assertion per test
- ✅ **Security** - Input validation, SQL injection prevention, XSS protection

### Code Organization
```
reference-implementation/
├── ai_coordination/
│   ├── core/
│   │   └── transparency_ledger.py  ← YOU WRITE THIS
│   ├── api/
│   │   └── api_server.py           ← YOU WRITE THIS
│   ├── services/
│   │   └── friction_calculator.py  ← YOU WRITE THIS
│   └── __init__.py
├── dashboard/
│   ├── index.html                  ← YOU WRITE THIS
│   └── app.js                      ← YOU WRITE THIS
└── tests/
    └── test_transparency_ledger.py ← YOU WRITE THIS
```

---

## NEXT STEPS

1. **Start with Priority 1** (transparency_ledger.py + api_server.py)
2. **Write tests** (test_transparency_ledger.py)
3. **Test locally** (`pytest tests/`)
4. **Add Priority 2** (friction_calculator.py + dashboard)
5. **Dockerize** (Dockerfile + docker-compose.yml)
6. **Deploy** (`docker-compose up`)

---

**Questions? Start with transparency_ledger.py - it's the heart of the system.**
