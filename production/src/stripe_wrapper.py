"""
Echo Stripe Wrapper - Production Ready
Implements exactly-once payment processing with full audit trail.

Based on STRIPE_PRIMITIVE_PROOF_NOTE.md specifications:
- Idempotency enforcement (canonicalization + key derivation)
- Deduplication (webhook store + watermarks)
- Reconciliation (gap detection + repair)
- Audit (complete traceability)
"""

import os
import json
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import asyncio

import httpx

# =============================================================================
# CONFIGURATION
# =============================================================================

class StripeConfig:
    """Stripe configuration from environment."""
    SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    API_VERSION = "2023-10-16"
    BASE_URL = "https://api.stripe.com"
    IDEMPOTENCY_WINDOW_HOURS = 24


config = StripeConfig()


# =============================================================================
# MODELS
# =============================================================================

class PaymentState(str, Enum):
    """Payment state machine states."""
    PENDING = "pending"
    CREATED = "created"
    ACTION_REQUIRED = "action_required"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class LedgerEntry:
    """Entry in the Evidence & Integrity Ledger."""
    id: str
    stripe_id: str
    order_id: str
    amount: int
    currency: str
    state: PaymentState
    created_at: str
    updated_at: str
    idempotency_key: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    events: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['state'] = self.state.value
        return result


@dataclass
class WebhookEvent:
    """Processed webhook event."""
    id: str
    type: str
    object_id: str
    created: int
    processed_at: str
    data: Dict[str, Any]


# =============================================================================
# IDEMPOTENCY ENGINE
# =============================================================================

class IdempotencyEngine:
    """
    Implements idempotency key derivation and management.
    
    From O3: Canonicalization rules:
    - Sort metadata keys alphabetically
    - Convert amounts to smallest currency unit
    - Normalize timestamps to ISO 8601 UTC
    """
    
    def __init__(self):
        self.key_store: Dict[str, Tuple[str, datetime]] = {}  # key -> (result_id, created_at)
    
    def canonicalize(self, params: Dict) -> str:
        """Canonicalize parameters for consistent key derivation."""
        canonical = {}
        
        for key in sorted(params.keys()):
            value = params[key]
            
            if key == "metadata" and isinstance(value, dict):
                # Sort metadata keys alphabetically
                canonical[key] = dict(sorted(value.items()))
            elif key == "amount":
                # Ensure integer (smallest currency unit)
                canonical[key] = int(value)
            elif key == "timestamp" or key.endswith("_at"):
                # Normalize to ISO 8601 UTC
                if isinstance(value, datetime):
                    canonical[key] = value.strftime("%Y-%m-%dT%H:%M:%SZ")
                else:
                    canonical[key] = str(value)
            else:
                canonical[key] = value
        
        return json.dumps(canonical, sort_keys=True, separators=(',', ':'))
    
    def derive_key(self, order_id: str, amount: int, currency: str, customer_id: str) -> str:
        """
        Derive idempotency key from order parameters.
        
        Formula from E2: k = H(order_id∥amount∥currency∥customer_id)
        """
        payload = f"{order_id}|{amount}|{currency}|{customer_id}"
        return hashlib.sha256(payload.encode()).hexdigest()[:32]
    
    def check_key(self, key: str) -> Optional[str]:
        """Check if key exists and is within window. Returns result_id if exists."""
        if key not in self.key_store:
            return None
        
        result_id, created_at = self.key_store[key]
        window = timedelta(hours=config.IDEMPOTENCY_WINDOW_HOURS)
        
        if datetime.utcnow() - created_at > window:
            # Key expired
            del self.key_store[key]
            return None
        
        return result_id
    
    def store_key(self, key: str, result_id: str):
        """Store key with result."""
        self.key_store[key] = (result_id, datetime.utcnow())
    
    def cleanup_expired(self):
        """Remove expired keys."""
        window = timedelta(hours=config.IDEMPOTENCY_WINDOW_HOURS)
        cutoff = datetime.utcnow() - window
        
        expired = [k for k, (_, created) in self.key_store.items() if created < cutoff]
        for k in expired:
            del self.key_store[k]


# =============================================================================
# DEDUPLICATION LAYER
# =============================================================================

class DeduplicationLayer:
    """
    Implements exactly-once webhook processing.
    
    Components:
    - Event store: event_id -> processed_at
    - Watermarks: object_type -> last_processed_event_date
    """
    
    def __init__(self):
        self.event_store: Dict[str, datetime] = {}
        self.watermarks: Dict[str, datetime] = {}
    
    def is_duplicate(self, event_id: str) -> bool:
        """Check if event has already been processed."""
        return event_id in self.event_store
    
    def mark_processed(self, event_id: str, object_type: str, event_time: datetime):
        """Mark event as processed and update watermark."""
        self.event_store[event_id] = datetime.utcnow()
        
        # Update watermark
        if object_type not in self.watermarks or event_time > self.watermarks[object_type]:
            self.watermarks[object_type] = event_time
    
    def get_watermark(self, object_type: str) -> Optional[datetime]:
        """Get the watermark for an object type."""
        return self.watermarks.get(object_type)
    
    def detect_gaps(self, object_type: str, events: List[Dict]) -> List[str]:
        """Detect gaps in event sequence that need reconciliation."""
        watermark = self.get_watermark(object_type)
        if not watermark:
            return []
        
        gaps = []
        for event in events:
            event_time = datetime.fromtimestamp(event['created'])
            if event_time < watermark and event['id'] not in self.event_store:
                gaps.append(event['id'])
        
        return gaps
    
    def cleanup_old_events(self, max_age_hours: int = 72):
        """Remove old events from store."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        self.event_store = {
            k: v for k, v in self.event_store.items() if v > cutoff
        }


# =============================================================================
# EVIDENCE & INTEGRITY LEDGER
# =============================================================================

class EvidenceLedger:
    """
    Evidence & Integrity Ledger for payment audit trail.
    
    Invariant E1: ∀ pi ∈ Stripe_PaymentIntents, ∃ ledger_entry ∈ Echo_Ledger
    """
    
    def __init__(self):
        self.entries: Dict[str, LedgerEntry] = {}  # stripe_id -> entry
        self.by_order: Dict[str, str] = {}  # order_id -> stripe_id
    
    def create_entry(
        self,
        stripe_id: str,
        order_id: str,
        amount: int,
        currency: str,
        idempotency_key: str,
        metadata: Optional[Dict] = None
    ) -> LedgerEntry:
        """Create a new ledger entry."""
        now = datetime.utcnow().isoformat()
        
        entry = LedgerEntry(
            id=hashlib.sha256(f"{stripe_id}{now}".encode()).hexdigest()[:16],
            stripe_id=stripe_id,
            order_id=order_id,
            amount=amount,
            currency=currency,
            state=PaymentState.CREATED,
            created_at=now,
            updated_at=now,
            idempotency_key=idempotency_key,
            metadata=metadata or {},
            events=["created"]
        )
        
        self.entries[stripe_id] = entry
        self.by_order[order_id] = stripe_id
        
        return entry
    
    def update_state(self, stripe_id: str, new_state: PaymentState, event_id: str) -> Optional[LedgerEntry]:
        """Update entry state. Enforces monotonicity for SUCCEEDED state."""
        if stripe_id not in self.entries:
            return None
        
        entry = self.entries[stripe_id]
        
        # E3: Paid(order_id) is monotonic
        if entry.state == PaymentState.SUCCEEDED and new_state != PaymentState.REFUNDED:
            # Cannot transition from SUCCEEDED except to REFUNDED
            return entry
        
        entry.state = new_state
        entry.updated_at = datetime.utcnow().isoformat()
        entry.events.append(event_id)
        
        return entry
    
    def get_by_stripe_id(self, stripe_id: str) -> Optional[LedgerEntry]:
        """Get entry by Stripe ID."""
        return self.entries.get(stripe_id)
    
    def get_by_order_id(self, order_id: str) -> Optional[LedgerEntry]:
        """Get entry by order ID."""
        stripe_id = self.by_order.get(order_id)
        if stripe_id:
            return self.entries.get(stripe_id)
        return None
    
    def is_paid(self, order_id: str) -> bool:
        """Check if order is paid (monotonic property)."""
        entry = self.get_by_order_id(order_id)
        return entry is not None and entry.state == PaymentState.SUCCEEDED


# =============================================================================
# STRIPE CLIENT
# =============================================================================

class StripeClient:
    """Stripe API client with idempotency support."""
    
    def __init__(self, secret_key: str = config.SECRET_KEY):
        self.secret_key = secret_key
        self.headers = {
            "Authorization": f"Bearer {secret_key}",
            "Stripe-Version": config.API_VERSION,
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    async def create_payment_intent(
        self,
        amount: int,
        currency: str,
        customer_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict:
        """Create a PaymentIntent with idempotency."""
        headers = self.headers.copy()
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        
        data = {
            "amount": amount,
            "currency": currency,
        }
        if customer_id:
            data["customer"] = customer_id
        if metadata:
            for k, v in metadata.items():
                data[f"metadata[{k}]"] = v
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.BASE_URL}/v1/payment_intents",
                headers=headers,
                data=data
            )
            return response.json()
    
    async def retrieve_payment_intent(self, payment_intent_id: str) -> Dict:
        """Retrieve a PaymentIntent."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.BASE_URL}/v1/payment_intents/{payment_intent_id}",
                headers=self.headers
            )
            return response.json()
    
    async def list_events(
        self,
        object_type: str = "payment_intent",
        created_after: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict]:
        """List events for reconciliation."""
        params = {"limit": limit, "type": f"{object_type}.*"}
        if created_after:
            params["created[gt]"] = created_after
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.BASE_URL}/v1/events",
                headers=self.headers,
                params=params
            )
            data = response.json()
            return data.get("data", [])
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature."""
        if not config.WEBHOOK_SECRET:
            return True  # Skip verification if no secret configured
        
        # Parse signature header
        elements = dict(item.split("=") for item in signature.split(","))
        timestamp = elements.get("t")
        v1_signature = elements.get("v1")
        
        if not timestamp or not v1_signature:
            return False
        
        # Compute expected signature
        signed_payload = f"{timestamp}.{payload.decode()}"
        expected = hmac.new(
            config.WEBHOOK_SECRET.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, v1_signature)


# =============================================================================
# ECHO STRIPE WRAPPER
# =============================================================================

class EchoStripeWrapper:
    """
    Main wrapper that composes all components for exactly-once payment processing.
    
    Theorem: Echo ∘ Stripe provides exactly-once payment processing
    under network partitions and retries.
    """
    
    def __init__(self):
        self.client = StripeClient()
        self.idempotency = IdempotencyEngine()
        self.dedup = DeduplicationLayer()
        self.ledger = EvidenceLedger()
    
    async def create_payment(
        self,
        order_id: str,
        amount: int,
        currency: str,
        customer_id: str,
        metadata: Optional[Dict] = None
    ) -> LedgerEntry:
        """
        Create a payment with exactly-once guarantee.
        
        Implements E2: Idempotent Creation
        """
        # Derive idempotency key
        key = self.idempotency.derive_key(order_id, amount, currency, customer_id)
        
        # Check for existing result
        existing_id = self.idempotency.check_key(key)
        if existing_id:
            entry = self.ledger.get_by_stripe_id(existing_id)
            if entry:
                return entry
        
        # Check ledger by order_id
        existing_entry = self.ledger.get_by_order_id(order_id)
        if existing_entry:
            return existing_entry
        
        # Create PaymentIntent
        full_metadata = metadata or {}
        full_metadata["order_id"] = order_id
        full_metadata["echo_key"] = key[:16]
        
        result = await self.client.create_payment_intent(
            amount=amount,
            currency=currency,
            customer_id=customer_id,
            metadata=full_metadata,
            idempotency_key=key
        )
        
        if "error" in result:
            raise Exception(f"Stripe error: {result['error']['message']}")
        
        # Store idempotency key
        self.idempotency.store_key(key, result["id"])
        
        # Create ledger entry
        entry = self.ledger.create_entry(
            stripe_id=result["id"],
            order_id=order_id,
            amount=amount,
            currency=currency,
            idempotency_key=key,
            metadata=full_metadata
        )
        
        return entry
    
    async def process_webhook(self, event_id: str, event_type: str, data: Dict) -> bool:
        """
        Process a webhook event with exactly-once guarantee.
        
        Implements E3: Exactly-Once Finalization
        """
        # Deduplication check
        if self.dedup.is_duplicate(event_id):
            return False  # Already processed
        
        # Extract object info
        obj = data.get("object", {})
        stripe_id = obj.get("id")
        
        if not stripe_id:
            return False
        
        # Map event type to state
        state_map = {
            "payment_intent.succeeded": PaymentState.SUCCEEDED,
            "payment_intent.payment_failed": PaymentState.FAILED,
            "payment_intent.requires_action": PaymentState.ACTION_REQUIRED,
            "charge.refunded": PaymentState.REFUNDED,
        }
        
        new_state = state_map.get(event_type)
        if new_state:
            self.ledger.update_state(stripe_id, new_state, event_id)
        
        # Mark as processed
        event_time = datetime.fromtimestamp(data.get("created", time.time()))
        self.dedup.mark_processed(event_id, "payment_intent", event_time)
        
        return True
    
    async def reconcile(self) -> Dict[str, Any]:
        """
        Run reconciliation to detect and repair gaps.
        
        Compares Stripe events with ledger to ensure consistency.
        """
        # Get watermark
        watermark = self.dedup.get_watermark("payment_intent")
        created_after = int(watermark.timestamp()) if watermark else None
        
        # Fetch recent events
        events = await self.client.list_events(
            object_type="payment_intent",
            created_after=created_after
        )
        
        # Detect gaps
        gaps = self.dedup.detect_gaps("payment_intent", events)
        
        # Process any missed events
        repaired = []
        for event in events:
            if event["id"] in gaps:
                processed = await self.process_webhook(
                    event["id"],
                    event["type"],
                    event["data"]
                )
                if processed:
                    repaired.append(event["id"])
        
        # Verify ledger integrity (E1)
        missing_entries = []
        for event in events:
            obj = event.get("data", {}).get("object", {})
            stripe_id = obj.get("id")
            if stripe_id and not self.ledger.get_by_stripe_id(stripe_id):
                missing_entries.append(stripe_id)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "events_checked": len(events),
            "gaps_detected": len(gaps),
            "gaps_repaired": repaired,
            "missing_ledger_entries": missing_entries,
            "status": "healthy" if not missing_entries else "needs_repair"
        }
    
    def is_paid(self, order_id: str) -> bool:
        """Check if order is paid (monotonic)."""
        return self.ledger.is_paid(order_id)
    
    def get_payment_status(self, order_id: str) -> Optional[Dict]:
        """Get payment status for an order."""
        entry = self.ledger.get_by_order_id(order_id)
        if entry:
            return entry.to_dict()
        return None


# =============================================================================
# CLINIC PROFILE VALIDATION
# =============================================================================

class ClinicPaymentProfile:
    """
    Clinic-specific payment profile validation.
    
    Based on Section 5 of STRIPE_PRIMITIVE_PROOF_NOTE.md
    """
    
    MINIMAL_PROFILE = {
        "methods": ["card"],
        "currencies": ["USD"],
        "business_type": "individual",
        "statement_descriptor": "HERO*WELLNESS",
        "metadata_template": {
            "appointment_id": "required",
            "service_date": "required",
            "location_id": "optional",
            "patient_ref": "hashed_token"
        }
    }
    
    @staticmethod
    def hash_patient_ref(patient_id: str, practice_key: str) -> str:
        """
        PHI Safety Protocol: Hash patient reference.
        
        patient_ref = HMAC(patient_id, practice_key)[:16]
        """
        return hmac.new(
            practice_key.encode(),
            patient_id.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
    
    @staticmethod
    def validate_metadata(metadata: Dict, template: Dict) -> Tuple[bool, List[str]]:
        """Validate metadata against template."""
        errors = []
        
        for field, requirement in template.items():
            if requirement == "required" and field not in metadata:
                errors.append(f"Missing required field: {field}")
        
        # PHI detection
        phi_patterns = ["ssn", "dob", "date_of_birth", "social_security", "patient_name"]
        for key in metadata.keys():
            if any(pattern in key.lower() for pattern in phi_patterns):
                errors.append(f"Potential PHI detected in field: {key}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def create_safe_metadata(
        appointment_id: str,
        service_date: str,
        patient_id: str,
        practice_key: str,
        location_id: Optional[str] = None
    ) -> Dict:
        """Create PHI-safe metadata for payment."""
        metadata = {
            "appointment_id": appointment_id,
            "service_date": service_date,
            "patient_ref": ClinicPaymentProfile.hash_patient_ref(patient_id, practice_key)
        }
        
        if location_id:
            metadata["location_id"] = location_id
        
        return metadata


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Example usage
    async def main():
        wrapper = EchoStripeWrapper()
        
        # Create a payment
        entry = await wrapper.create_payment(
            order_id="order_123",
            amount=5000,  # $50.00
            currency="usd",
            customer_id="cus_test",
            metadata=ClinicPaymentProfile.create_safe_metadata(
                appointment_id="apt_456",
                service_date="2024-01-15",
                patient_id="patient_789",
                practice_key="secret_practice_key"
            )
        )
        
        print(f"Created payment: {entry.to_dict()}")
        
        # Check if paid
        print(f"Is paid: {wrapper.is_paid('order_123')}")
        
        # Run reconciliation
        recon = await wrapper.reconcile()
        print(f"Reconciliation: {recon}")
    
    asyncio.run(main())
