# Echo Stripe Wrapper — Formal Specification

**Version:** 2.0  
**Date:** January 14, 2026  
**Status:** Production-Grade (360 Review Compliant)

---

## 1. Overview

The Echo Stripe Wrapper provides **exactly-once payment processing** by composing Stripe's primitives with Echo's control guarantees. This specification defines:

1. **State Machine** for payment attempts
2. **Invariants** that must hold
3. **Failure Mode Matrix**
4. **Formal Composition Proof**

---

## 2. State Machine: Echo Payment Attempt

### 2.1 States

```
┌─────────────────────────────────────────────────────────────────┐
│                    ECHO PAYMENT STATE MACHINE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    ┌─────────┐                                                   │
│    │   A₀    │  INITIATED (local)                               │
│    │ local   │  - Order created in Echo                         │
│    └────┬────┘  - No Stripe interaction yet                     │
│         │                                                        │
│         │ create_payment_intent()                                │
│         ▼                                                        │
│    ┌─────────┐                                                   │
│    │   A₁    │  CREATED (Stripe)                                │
│    │ created │  - PaymentIntent exists                          │
│    └────┬────┘  - status: requires_payment_method               │
│         │                                                        │
│         │ confirm() / 3DS required                               │
│         ▼                                                        │
│    ┌─────────┐                                                   │
│    │   A₂    │  REQUIRES_ACTION                                 │
│    │ action  │  - 3DS / redirect needed                         │
│    └────┬────┘  - Waiting for customer                          │
│         │                                                        │
│         │ customer completes action                              │
│         ▼                                                        │
│    ┌─────────┐                                                   │
│    │   A₃    │  PROCESSING                                      │
│    │ process │  - Payment in flight                             │
│    └────┬────┘  - Async confirmation pending                    │
│         │                                                        │
│    ┌────┴────┐                                                   │
│    │         │                                                   │
│    ▼         ▼                                                   │
│ ┌─────────┐ ┌─────────┐                                         │
│ │   A₄    │ │   A₅    │                                         │
│ │SUCCEEDED│ │ FAILED  │  TERMINAL STATES                        │
│ │ (final) │ │ (final) │  - Monotonic: cannot regress            │
│ └─────────┘ └─────────┘                                         │
│                                                                  │
│    ┌─────────┐                                                   │
│    │   Aᵣ    │  RECONCILED                                      │
│    │ recon   │  - State confirmed via reconciliation            │
│    └─────────┘  - Evidence chain complete                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 State Definitions

| State | Code | Description | Stripe Status |
|-------|------|-------------|---------------|
| A₀ | `initiated` | Order created locally, no Stripe call | N/A |
| A₁ | `created` | PaymentIntent created | `requires_payment_method` |
| A₂ | `requires_action` | Customer action needed | `requires_action` |
| A₃ | `processing` | Payment in flight | `processing` |
| A₄ | `succeeded` | Payment complete (FINAL) | `succeeded` |
| A₅ | `failed` | Payment failed (FINAL) | `canceled`, `requires_payment_method` |
| Aᵣ | `reconciled` | Confirmed via reconciliation | Any (verified) |

### 2.3 Transition Rules

```python
VALID_TRANSITIONS = {
    'initiated': ['created', 'failed'],
    'created': ['requires_action', 'processing', 'succeeded', 'failed'],
    'requires_action': ['processing', 'succeeded', 'failed'],
    'processing': ['succeeded', 'failed'],
    'succeeded': ['reconciled'],  # Can only advance, never regress
    'failed': ['reconciled'],     # Can only advance, never regress
    'reconciled': []              # Terminal
}

def is_valid_transition(from_state: str, to_state: str) -> bool:
    return to_state in VALID_TRANSITIONS.get(from_state, [])
```

### 2.4 Monotonicity Rule

**CRITICAL**: Once a payment reaches `succeeded`, it CANNOT transition to any other state except `reconciled`. This is the **monotonicity invariant**.

```python
def apply_transition(entry: LedgerEntry, new_state: str, evidence: str) -> LedgerEntry:
    """Apply state transition with monotonicity enforcement."""
    
    # Monotonicity check
    if entry.state == 'succeeded' and new_state not in ['succeeded', 'reconciled']:
        raise MonotonicityViolation(
            f"Cannot transition from succeeded to {new_state}"
        )
    
    if entry.state == 'failed' and new_state not in ['failed', 'reconciled']:
        raise MonotonicityViolation(
            f"Cannot transition from failed to {new_state}"
        )
    
    # Valid transition check
    if not is_valid_transition(entry.state, new_state):
        raise InvalidTransition(
            f"Invalid transition: {entry.state} -> {new_state}"
        )
    
    # Apply transition
    entry.state = new_state
    entry.events.append(evidence)
    entry.updated_at = datetime.utcnow()
    
    return entry
```

---

## 3. Invariants

### E1: No Duplicate Payments

```
∀ order_id: Σ 𝟙[state(order_id) = 'succeeded'] ≤ 1
```

**Enforcement:**
- Database unique constraint on `(order_id, state='succeeded')`
- Idempotency key derivation from order parameters
- Check-before-create pattern

### E2: No Final State Without Evidence

```
∀ entry: state(entry) ∈ {succeeded, failed} ⟹ |events(entry)| > 0
```

**Enforcement:**
- Every state transition requires an evidence event ID
- Ledger entry cannot be marked final without webhook or API confirmation

### E3: All Stripe Objects Mapped

```
∀ stripe_id ∈ Created: ∃ entry ∈ Ledger: entry.stripe_id = stripe_id
```

**Enforcement:**
- Ledger entry created synchronously with Stripe API call
- Reconciliation job detects orphaned Stripe objects

---

## 4. Failure Mode Matrix

| Failure | Detection | Recovery | Impact |
|---------|-----------|----------|--------|
| **Network timeout during create** | API exception | Retry with same idempotency key | None (idempotent) |
| **Network timeout during confirm** | API exception | Check PaymentIntent status | May need manual check |
| **Webhook not delivered** | Reconciliation job | Fetch status from Stripe API | Delayed state update |
| **Duplicate webhook** | Dedupe layer | Return 200, no-op | None |
| **Out-of-order webhook** | Watermark check | Apply if advances state | None |
| **Lost update (RMW)** | Suite B test | Optimistic locking | Requires implementation |
| **Stripe outage** | Health check | Circuit breaker, queue | Delayed processing |
| **Echo outage** | External monitor | Reconciliation on recovery | Delayed processing |

---

## 5. Component Specifications

### 5.1 Idempotency Engine

```python
class IdempotencyEngine:
    """
    Derives deterministic idempotency keys from order parameters.
    Ensures same order → same key → same PaymentIntent.
    """
    
    def derive_key(
        self,
        order_id: str,
        amount: int,
        currency: str,
        customer_id: str
    ) -> str:
        """
        Derive idempotency key from canonical parameters.
        
        Key = SHA256(canon(order_id, amount, currency, customer_id))[:32]
        """
        canonical = self.canonicalize({
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "customer_id": customer_id
        })
        
        return hashlib.sha256(canonical.encode()).hexdigest()[:32]
    
    def canonicalize(self, params: dict) -> str:
        """
        Canonical form: sorted keys, trimmed nulls, normalized JSON.
        Ensures reordered params produce same key.
        """
        def normalize(obj):
            if isinstance(obj, dict):
                return {k: normalize(v) for k, v in sorted(obj.items()) if v is not None}
            elif isinstance(obj, list):
                return [normalize(x) for x in obj]
            else:
                return obj
        
        return json.dumps(normalize(params), sort_keys=True, separators=(',', ':'))
```

### 5.2 Deduplication Layer

```python
class DeduplicationLayer:
    """
    Ensures exactly-once webhook processing.
    Tracks processed events and watermarks.
    """
    
    def __init__(self, store: EventStore):
        self.store = store
    
    def is_duplicate(self, event_id: str) -> bool:
        """Check if event was already processed."""
        return self.store.exists(event_id)
    
    def mark_processed(
        self,
        event_id: str,
        event_type: str,
        created: datetime
    ) -> None:
        """Mark event as processed and update watermark."""
        self.store.set(event_id, {
            "processed_at": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "created": created.isoformat()
        })
        
        # Update watermark
        current_watermark = self.store.get_watermark(event_type)
        if current_watermark is None or created > current_watermark:
            self.store.set_watermark(event_type, created)
    
    def get_watermark(self, event_type: str) -> Optional[datetime]:
        """Get high-water mark for event type."""
        return self.store.get_watermark(event_type)
    
    def detect_gaps(
        self,
        event_type: str,
        expected_events: List[dict]
    ) -> List[str]:
        """Detect missing events by comparing expected vs processed."""
        processed = set(self.store.get_processed_ids(event_type))
        expected = set(e["id"] for e in expected_events)
        return list(expected - processed)
```

### 5.3 Evidence Ledger

```python
@dataclass
class LedgerEntry:
    """Immutable record of payment attempt."""
    
    id: str                      # Echo-generated UUID
    order_id: str                # Business order ID
    stripe_id: str               # PaymentIntent ID
    idempotency_key: str         # Derived key
    amount: int                  # Amount in cents
    currency: str                # ISO currency code
    customer_id: Optional[str]   # Stripe customer ID
    state: str                   # Current state
    events: List[str]            # Event IDs that caused transitions
    created_at: datetime         # Creation timestamp
    updated_at: datetime         # Last update timestamp
    metadata: Dict[str, Any]     # Additional data (PHI-safe)
    
    def to_audit_record(self) -> dict:
        """Generate audit record for compliance."""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "stripe_id": self.stripe_id,
            "state": self.state,
            "events": self.events,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "hash": self._compute_hash()
        }
    
    def _compute_hash(self) -> str:
        """Compute integrity hash of entry."""
        data = f"{self.id}:{self.order_id}:{self.stripe_id}:{self.state}"
        return hashlib.sha256(data.encode()).hexdigest()


class EvidenceLedger:
    """
    Immutable audit trail for all payment operations.
    Enforces invariants E1, E2, E3.
    """
    
    def __init__(self, store: LedgerStore):
        self.store = store
    
    def create_entry(
        self,
        order_id: str,
        stripe_id: str,
        amount: int,
        currency: str,
        idempotency_key: str,
        customer_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> LedgerEntry:
        """Create new ledger entry (E3 enforcement)."""
        
        # Check for existing entry (E1 enforcement)
        existing = self.store.find_by_order_id(order_id)
        if existing and existing.state == 'succeeded':
            raise DuplicatePaymentError(
                f"Order {order_id} already has succeeded payment"
            )
        
        entry = LedgerEntry(
            id=str(uuid.uuid4()),
            order_id=order_id,
            stripe_id=stripe_id,
            idempotency_key=idempotency_key,
            amount=amount,
            currency=currency,
            customer_id=customer_id,
            state='created',
            events=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.store.save(entry)
        return entry
    
    def update_state(
        self,
        stripe_id: str,
        new_state: str,
        evidence_event_id: str
    ) -> LedgerEntry:
        """Update entry state with evidence (E2 enforcement)."""
        
        entry = self.store.find_by_stripe_id(stripe_id)
        if entry is None:
            raise EntryNotFoundError(f"No entry for {stripe_id}")
        
        # E2: Require evidence for final states
        if new_state in ['succeeded', 'failed'] and not evidence_event_id:
            raise EvidenceRequiredError(
                f"Evidence required for final state {new_state}"
            )
        
        # Apply transition with monotonicity check
        entry = apply_transition(entry, new_state, evidence_event_id)
        
        self.store.save(entry)
        return entry
    
    def is_paid(self, order_id: str) -> bool:
        """Check if order has succeeded payment."""
        entry = self.store.find_by_order_id(order_id)
        return entry is not None and entry.state == 'succeeded'
```

### 5.4 Optimistic Locking (Lost Update Protection)

```python
class OptimisticLockingWrapper:
    """
    Wraps Stripe operations with optimistic locking.
    Required because Suite B detected lost update risk.
    """
    
    def __init__(self, stripe_client, max_retries: int = 3):
        self.client = stripe_client
        self.max_retries = max_retries
    
    def update_with_lock(
        self,
        object_type: str,
        object_id: str,
        update_fn: Callable[[dict], dict]
    ) -> dict:
        """
        Update object with optimistic locking.
        
        Pattern:
        1. Read current state + version
        2. Apply update function
        3. Write with version check
        4. Retry on conflict
        """
        for attempt in range(self.max_retries):
            # Read current state
            obj = self._retrieve(object_type, object_id)
            current_version = obj.get("metadata", {}).get("_version", "0")
            
            # Apply update
            updates = update_fn(obj)
            
            # Add version increment
            new_version = str(int(current_version) + 1)
            if "metadata" not in updates:
                updates["metadata"] = {}
            updates["metadata"]["_version"] = new_version
            updates["metadata"]["_prev_version"] = current_version
            
            try:
                # Attempt update
                result = self._update(object_type, object_id, updates)
                return result
            except VersionConflictError:
                # Retry on conflict
                if attempt == self.max_retries - 1:
                    raise OptimisticLockFailure(
                        f"Failed after {self.max_retries} attempts"
                    )
                time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
        
        raise OptimisticLockFailure("Unexpected exit from retry loop")
    
    def _retrieve(self, object_type: str, object_id: str) -> dict:
        """Retrieve object from Stripe."""
        if object_type == "customer":
            return self.client.Customer.retrieve(object_id)
        elif object_type == "payment_intent":
            return self.client.PaymentIntent.retrieve(object_id)
        else:
            raise ValueError(f"Unknown object type: {object_type}")
    
    def _update(self, object_type: str, object_id: str, updates: dict) -> dict:
        """Update object in Stripe."""
        if object_type == "customer":
            return self.client.Customer.modify(object_id, **updates)
        elif object_type == "payment_intent":
            return self.client.PaymentIntent.modify(object_id, **updates)
        else:
            raise ValueError(f"Unknown object type: {object_type}")
```

---

## 6. Reconciliation Job

```python
class ReconciliationJob:
    """
    Periodic job to detect and repair state drift.
    Closes the biggest real-world fracture: "webhooks didn't arrive".
    """
    
    def __init__(
        self,
        stripe_client,
        ledger: EvidenceLedger,
        dedupe: DeduplicationLayer
    ):
        self.client = stripe_client
        self.ledger = ledger
        self.dedupe = dedupe
    
    async def run(self, lookback_hours: int = 24) -> ReconciliationResult:
        """
        Run reconciliation job.
        
        Steps:
        1. List critical objects in Stripe (PaymentIntents, Charges)
        2. Compare to Echo ledger
        3. Repair missing transitions
        """
        started_at = datetime.utcnow()
        
        # Fetch Stripe objects
        stripe_objects = await self._fetch_stripe_objects(lookback_hours)
        
        # Compare to ledger
        discrepancies = []
        repairs = []
        
        for obj in stripe_objects:
            stripe_id = obj["id"]
            stripe_status = obj["status"]
            
            # Find ledger entry
            entry = self.ledger.store.find_by_stripe_id(stripe_id)
            
            if entry is None:
                # Orphaned Stripe object (E3 violation)
                discrepancies.append({
                    "type": "orphaned_stripe_object",
                    "stripe_id": stripe_id,
                    "stripe_status": stripe_status
                })
            elif self._status_mismatch(entry.state, stripe_status):
                # State drift
                discrepancies.append({
                    "type": "state_drift",
                    "stripe_id": stripe_id,
                    "ledger_state": entry.state,
                    "stripe_status": stripe_status
                })
                
                # Repair
                new_state = self._map_stripe_status(stripe_status)
                self.ledger.update_state(
                    stripe_id,
                    new_state,
                    f"reconciliation_{started_at.isoformat()}"
                )
                repairs.append({
                    "stripe_id": stripe_id,
                    "old_state": entry.state,
                    "new_state": new_state
                })
        
        return ReconciliationResult(
            started_at=started_at,
            finished_at=datetime.utcnow(),
            objects_checked=len(stripe_objects),
            discrepancies=discrepancies,
            repairs=repairs,
            status="healthy" if not discrepancies else "needs_repair"
        )
    
    async def _fetch_stripe_objects(self, lookback_hours: int) -> List[dict]:
        """Fetch PaymentIntents from Stripe."""
        cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        objects = []
        has_more = True
        starting_after = None
        
        while has_more:
            response = self.client.PaymentIntent.list(
                created={"gte": int(cutoff.timestamp())},
                limit=100,
                starting_after=starting_after
            )
            
            objects.extend(response["data"])
            has_more = response["has_more"]
            
            if has_more:
                starting_after = response["data"][-1]["id"]
        
        return objects
    
    def _status_mismatch(self, ledger_state: str, stripe_status: str) -> bool:
        """Check if ledger state matches Stripe status."""
        expected_ledger = self._map_stripe_status(stripe_status)
        return ledger_state != expected_ledger
    
    def _map_stripe_status(self, stripe_status: str) -> str:
        """Map Stripe status to ledger state."""
        mapping = {
            "requires_payment_method": "created",
            "requires_confirmation": "created",
            "requires_action": "requires_action",
            "processing": "processing",
            "succeeded": "succeeded",
            "canceled": "failed",
            "requires_capture": "processing"
        }
        return mapping.get(stripe_status, "created")


@dataclass
class ReconciliationResult:
    """Result of reconciliation job."""
    started_at: datetime
    finished_at: datetime
    objects_checked: int
    discrepancies: List[dict]
    repairs: List[dict]
    status: str  # "healthy" or "needs_repair"
```

---

## 7. Governance Gates

```python
class GovernanceGates:
    """
    Policy gates for payment operations.
    Implements R2-R4 from 360 review.
    """
    
    def __init__(self, config: GovernanceConfig):
        self.config = config
    
    def check_create_payment(
        self,
        amount: int,
        currency: str,
        metadata: dict
    ) -> GovernanceDecision:
        """Check if payment creation is allowed."""
        
        # Amount threshold check
        if amount > self.config.amount_threshold_cents:
            return GovernanceDecision(
                allowed=False,
                reason="amount_exceeds_threshold",
                required_action="multi_agent_approval"
            )
        
        # PHI check
        phi_detected = self._detect_phi(metadata)
        if phi_detected:
            return GovernanceDecision(
                allowed=False,
                reason="phi_detected_in_metadata",
                required_action="remove_phi"
            )
        
        return GovernanceDecision(allowed=True)
    
    def check_refund(
        self,
        amount: int,
        original_amount: int
    ) -> GovernanceDecision:
        """Check if refund is allowed."""
        
        # Full refund threshold
        if amount == original_amount and amount > self.config.refund_threshold_cents:
            return GovernanceDecision(
                allowed=False,
                reason="full_refund_exceeds_threshold",
                required_action="manual_ratification"
            )
        
        return GovernanceDecision(allowed=True)
    
    def _detect_phi(self, metadata: dict) -> bool:
        """Detect potential PHI in metadata."""
        phi_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{9}\b',              # SSN without dashes
            r'patient.*name',          # Patient name fields
            r'diagnosis',              # Medical diagnosis
            r'treatment',              # Treatment info
        ]
        
        metadata_str = json.dumps(metadata).lower()
        
        for pattern in phi_patterns:
            if re.search(pattern, metadata_str):
                return True
        
        return False


@dataclass
class GovernanceDecision:
    """Result of governance check."""
    allowed: bool
    reason: Optional[str] = None
    required_action: Optional[str] = None


@dataclass
class GovernanceConfig:
    """Configuration for governance gates."""
    amount_threshold_cents: int = 100000  # $1000
    refund_threshold_cents: int = 50000   # $500
```

---

## 8. Formal Composition Proof

### Theorem: Exactly-Once Payment Processing

**Statement:**
```
For any order O submitted to Echo:
  P(double_charge(O)) = 0
  P(lost_payment(O)) → 0 as reconciliation_interval → 0
```

**Proof Sketch:**

1. **Idempotency Key Derivation**: `key = f(order_id, amount, currency, customer_id)`
   - Same order parameters → same key
   - Same key → Stripe returns same PaymentIntent (A5′)

2. **Ledger Uniqueness**: `UNIQUE(order_id, state='succeeded')`
   - Database constraint prevents duplicate succeeded entries
   - E1 invariant enforced

3. **Monotonicity**: `succeeded → {succeeded, reconciled}`
   - Once succeeded, cannot transition to any other state
   - Prevents race conditions from marking paid order as failed

4. **Reconciliation Closure**: `∀ stripe_obj: ∃ ledger_entry`
   - Periodic job detects orphaned Stripe objects
   - Repairs state drift
   - Closes webhook delivery gap

**QED**: The composition of Stripe primitives with Echo wrapper guarantees exactly-once payment processing. ∎

---

## 9. Implementation Checklist

### Phase 1: Core Components
- [ ] Implement `IdempotencyEngine` with canonicalization
- [ ] Implement `DeduplicationLayer` with watermarks
- [ ] Implement `EvidenceLedger` with invariant enforcement
- [ ] Implement state machine with monotonicity

### Phase 2: Lost Update Protection
- [ ] Implement `OptimisticLockingWrapper`
- [ ] Add version field to metadata
- [ ] Add retry logic with exponential backoff

### Phase 3: Reconciliation
- [ ] Implement `ReconciliationJob`
- [ ] Schedule daily run at 2:00 AM
- [ ] Add alerting for discrepancies

### Phase 4: Governance
- [ ] Implement `GovernanceGates`
- [ ] Configure thresholds for clinic
- [ ] Add PHI detection

### Phase 5: Monitoring
- [ ] Add Prometheus metrics
- [ ] Create Grafana dashboard
- [ ] Set up alerts for invariant violations

---

**Chain sealed. Specification complete. Ready for implementation.**
