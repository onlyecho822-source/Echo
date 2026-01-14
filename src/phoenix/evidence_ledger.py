"""
EVIDENCE & INTEGRITY LEDGER (EIL) - Tamper-Evident Implementation
Specification: Echo Integration Topology v1.0
Purpose: Append-only, tamper-evident ledger with per-row hash chaining.

Addresses Devil Lens Finding #4:
- EIL must be append-only + tamper-evident
- Per-row hash chaining (even if Airtable is the UI layer)

Author: Manus AI
Date: 2026-01-14
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4


class EvidenceType(Enum):
    """Types of evidence that can be recorded."""
    CLAIM = "claim"
    VERIFICATION = "verification"
    EXECUTION = "execution"
    CONSENSUS = "consensus"
    DISSENT = "dissent"
    GKP_EVENT = "gkp_event"
    UTILITY_SCORE = "utility_score"
    STATE_CHANGE = "state_change"


class ValidityStatus(Enum):
    """Validity status of evidence."""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    DISPUTED = "disputed"
    EXPIRED = "expired"


@dataclass
class EvidenceRecord:
    """
    A single record in the Evidence & Integrity Ledger.
    
    Implements tamper-evident design with:
    - event_id (idempotency)
    - sha256(payload)
    - previous_hash (chain)
    """
    # Core identifiers
    event_id: str
    sequence_number: int
    
    # Evidence content
    evidence_type: EvidenceType
    payload: Dict[str, Any]
    source: str
    
    # Validity tracking
    validity_status: ValidityStatus
    validity_window_start: str
    validity_window_end: Optional[str]
    
    # Hash chain (tamper-evident)
    payload_hash: str
    previous_hash: str
    record_hash: str
    
    # Metadata
    created_at: str
    created_by: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "sequence_number": self.sequence_number,
            "evidence_type": self.evidence_type.value,
            "payload": self.payload,
            "source": self.source,
            "validity_status": self.validity_status.value,
            "validity_window_start": self.validity_window_start,
            "validity_window_end": self.validity_window_end,
            "payload_hash": self.payload_hash,
            "previous_hash": self.previous_hash,
            "record_hash": self.record_hash,
            "created_at": self.created_at,
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "EvidenceRecord":
        """Create from dictionary."""
        return cls(
            event_id=data["event_id"],
            sequence_number=data["sequence_number"],
            evidence_type=EvidenceType(data["evidence_type"]),
            payload=data["payload"],
            source=data["source"],
            validity_status=ValidityStatus(data["validity_status"]),
            validity_window_start=data["validity_window_start"],
            validity_window_end=data.get("validity_window_end"),
            payload_hash=data["payload_hash"],
            previous_hash=data["previous_hash"],
            record_hash=data["record_hash"],
            created_at=data["created_at"],
            created_by=data["created_by"]
        )


class EvidenceIntegrityLedger:
    """
    Tamper-evident Evidence & Integrity Ledger.
    
    Features:
    - Append-only (no updates or deletes)
    - Per-row hash chaining
    - Integrity verification
    - Export to Airtable-compatible format
    """
    
    # Genesis block hash (constant)
    GENESIS_HASH = "0" * 64
    
    def __init__(self, ledger_id: str = None):
        """
        Initialize the ledger.
        
        Args:
            ledger_id: Unique identifier for this ledger instance
        """
        self.ledger_id = ledger_id or f"eil_{uuid4().hex[:16]}"
        self._records: List[EvidenceRecord] = []
        self._event_ids: set = set()  # For idempotency
        self._created_at = datetime.utcnow().isoformat() + "Z"
    
    @property
    def last_hash(self) -> str:
        """Get the hash of the last record (or genesis hash if empty)."""
        if not self._records:
            return self.GENESIS_HASH
        return self._records[-1].record_hash
    
    @property
    def sequence_number(self) -> int:
        """Get the next sequence number."""
        return len(self._records)
    
    def append(
        self,
        evidence_type: EvidenceType,
        payload: Dict[str, Any],
        source: str,
        created_by: str,
        validity_status: ValidityStatus = ValidityStatus.UNVERIFIED,
        validity_window_end: Optional[str] = None,
        event_id: Optional[str] = None
    ) -> Tuple[bool, Optional[EvidenceRecord], str]:
        """
        Append a new record to the ledger.
        
        Args:
            evidence_type: Type of evidence
            payload: Evidence payload (any JSON-serializable data)
            source: Source of the evidence
            created_by: Who created this record
            validity_status: Initial validity status
            validity_window_end: When this evidence expires (optional)
            event_id: Custom event ID for idempotency (optional)
            
        Returns:
            (success, record, message)
        """
        # Generate or validate event_id
        if event_id is None:
            event_id = f"evt_{uuid4().hex}"
        
        # Idempotency check
        if event_id in self._event_ids:
            return False, None, f"Duplicate event_id: {event_id}"
        
        # Compute payload hash
        payload_json = json.dumps(payload, sort_keys=True, default=str)
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
        
        # Get previous hash
        previous_hash = self.last_hash
        
        # Create timestamp
        created_at = datetime.utcnow().isoformat() + "Z"
        
        # Compute record hash (includes all fields)
        record_data = {
            "event_id": event_id,
            "sequence_number": self.sequence_number,
            "evidence_type": evidence_type.value,
            "payload_hash": payload_hash,
            "source": source,
            "validity_status": validity_status.value,
            "validity_window_start": created_at,
            "validity_window_end": validity_window_end,
            "previous_hash": previous_hash,
            "created_at": created_at,
            "created_by": created_by
        }
        record_json = json.dumps(record_data, sort_keys=True)
        record_hash = hashlib.sha256(record_json.encode()).hexdigest()
        
        # Create record
        record = EvidenceRecord(
            event_id=event_id,
            sequence_number=self.sequence_number,
            evidence_type=evidence_type,
            payload=payload,
            source=source,
            validity_status=validity_status,
            validity_window_start=created_at,
            validity_window_end=validity_window_end,
            payload_hash=payload_hash,
            previous_hash=previous_hash,
            record_hash=record_hash,
            created_at=created_at,
            created_by=created_by
        )
        
        # Append to ledger
        self._records.append(record)
        self._event_ids.add(event_id)
        
        return True, record, "Record appended successfully"
    
    def verify_integrity(self) -> Tuple[bool, List[str]]:
        """
        Verify the integrity of the entire ledger.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if not self._records:
            return True, []
        
        # Verify first record links to genesis
        if self._records[0].previous_hash != self.GENESIS_HASH:
            errors.append(f"Record 0: Invalid genesis link")
        
        # Verify hash chain
        for i, record in enumerate(self._records):
            # Verify payload hash
            payload_json = json.dumps(record.payload, sort_keys=True, default=str)
            expected_payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
            
            if record.payload_hash != expected_payload_hash:
                errors.append(f"Record {i}: Payload hash mismatch")
            
            # Verify record hash
            record_data = {
                "event_id": record.event_id,
                "sequence_number": record.sequence_number,
                "evidence_type": record.evidence_type.value,
                "payload_hash": record.payload_hash,
                "source": record.source,
                "validity_status": record.validity_status.value,
                "validity_window_start": record.validity_window_start,
                "validity_window_end": record.validity_window_end,
                "previous_hash": record.previous_hash,
                "created_at": record.created_at,
                "created_by": record.created_by
            }
            record_json = json.dumps(record_data, sort_keys=True)
            expected_record_hash = hashlib.sha256(record_json.encode()).hexdigest()
            
            if record.record_hash != expected_record_hash:
                errors.append(f"Record {i}: Record hash mismatch")
            
            # Verify chain link (except first record)
            if i > 0:
                if record.previous_hash != self._records[i-1].record_hash:
                    errors.append(f"Record {i}: Chain link broken")
        
        return len(errors) == 0, errors
    
    def get_record(self, event_id: str) -> Optional[EvidenceRecord]:
        """Get a record by event_id."""
        for record in self._records:
            if record.event_id == event_id:
                return record
        return None
    
    def get_records_by_type(self, evidence_type: EvidenceType) -> List[EvidenceRecord]:
        """Get all records of a specific type."""
        return [r for r in self._records if r.evidence_type == evidence_type]
    
    def get_records_by_source(self, source: str) -> List[EvidenceRecord]:
        """Get all records from a specific source."""
        return [r for r in self._records if r.source == source]
    
    def export_to_airtable_format(self) -> List[Dict]:
        """
        Export ledger to Airtable-compatible format.
        
        Returns list of records ready for Airtable API.
        """
        return [
            {
                "fields": {
                    "Event ID": r.event_id,
                    "Sequence": r.sequence_number,
                    "Type": r.evidence_type.value,
                    "Payload": json.dumps(r.payload),
                    "Source": r.source,
                    "Validity": r.validity_status.value,
                    "Valid From": r.validity_window_start,
                    "Valid Until": r.validity_window_end or "",
                    "Payload Hash": r.payload_hash,
                    "Previous Hash": r.previous_hash,
                    "Record Hash": r.record_hash,
                    "Created At": r.created_at,
                    "Created By": r.created_by
                }
            }
            for r in self._records
        ]
    
    def export_to_json(self) -> str:
        """Export entire ledger to JSON."""
        return json.dumps({
            "ledger_id": self.ledger_id,
            "created_at": self._created_at,
            "record_count": len(self._records),
            "last_hash": self.last_hash,
            "records": [r.to_dict() for r in self._records]
        }, indent=2)
    
    def get_proof_pack(self) -> Dict:
        """
        Generate a Proof Pack for the ledger.
        
        Addresses Devil Lens requirement for verification artifacts.
        """
        is_valid, errors = self.verify_integrity()
        
        return {
            "ledger_id": self.ledger_id,
            "created_at": self._created_at,
            "record_count": len(self._records),
            "first_hash": self._records[0].record_hash if self._records else None,
            "last_hash": self.last_hash,
            "integrity_verified": is_valid,
            "integrity_errors": errors,
            "verification_timestamp": datetime.utcnow().isoformat() + "Z",
            "hash_algorithm": "SHA-256",
            "chain_type": "linear_hash_chain"
        }


class EILConnector:
    """
    Connector for syncing EIL with external systems (Airtable, etc.).
    
    Note: This is a specification. Actual API calls would be implemented
    based on the target system's API.
    """
    
    def __init__(self, ledger: EvidenceIntegrityLedger):
        self.ledger = ledger
        self._sync_log: List[Dict] = []
    
    def sync_to_airtable(
        self,
        base_id: str,
        table_name: str,
        api_key: str
    ) -> Tuple[bool, str]:
        """
        Sync ledger records to Airtable.
        
        Args:
            base_id: Airtable base ID
            table_name: Target table name
            api_key: Airtable API key
            
        Returns:
            (success, message)
            
        Note: This is a specification. Implementation would use Airtable API.
        """
        records = self.ledger.export_to_airtable_format()
        
        # Log sync attempt
        self._sync_log.append({
            "target": "airtable",
            "base_id": base_id,
            "table_name": table_name,
            "record_count": len(records),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "specification_only"
        })
        
        # In production, this would:
        # 1. Connect to Airtable API
        # 2. Create/update records
        # 3. Verify sync success
        # 4. Return result
        
        return True, f"Specification: Would sync {len(records)} records to Airtable"
    
    def generate_zapier_webhook_payload(self, record: EvidenceRecord) -> Dict:
        """
        Generate payload for Zapier webhook trigger.
        
        Args:
            record: Evidence record to send
            
        Returns:
            Webhook payload
        """
        return {
            "event_id": record.event_id,
            "evidence_type": record.evidence_type.value,
            "payload_hash": record.payload_hash,
            "record_hash": record.record_hash,
            "previous_hash": record.previous_hash,
            "source": record.source,
            "validity_status": record.validity_status.value,
            "created_at": record.created_at,
            "created_by": record.created_by,
            # Include payload for processing
            "payload": record.payload
        }


# ============================================================================
# MAIN: Example Usage and Tests
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("EVIDENCE & INTEGRITY LEDGER - Test Suite")
    print("=" * 60)
    
    # Create ledger
    ledger = EvidenceIntegrityLedger(ledger_id="test_eil_001")
    
    # Append test records
    print("\n--- Appending Records ---")
    
    success, record, msg = ledger.append(
        evidence_type=EvidenceType.CLAIM,
        payload={"claim": "Echo v2.2 is production ready", "confidence": 0.85},
        source="manus_ai",
        created_by="manus_ai",
        validity_status=ValidityStatus.UNVERIFIED
    )
    print(f"Record 1: {msg}")
    print(f"  Event ID: {record.event_id}")
    print(f"  Record Hash: {record.record_hash}")
    
    success, record, msg = ledger.append(
        evidence_type=EvidenceType.VERIFICATION,
        payload={"verified_claim": record.event_id, "verifier": "claude_ai", "result": True},
        source="claude_ai",
        created_by="claude_ai",
        validity_status=ValidityStatus.VERIFIED
    )
    print(f"Record 2: {msg}")
    print(f"  Event ID: {record.event_id}")
    print(f"  Previous Hash: {record.previous_hash[:16]}...")
    print(f"  Record Hash: {record.record_hash}")
    
    success, record, msg = ledger.append(
        evidence_type=EvidenceType.EXECUTION,
        payload={"pathway_id": "eil_logger_v0", "utility_score": 0.89, "success": True},
        source="phoenix_engine",
        created_by="phoenix_engine",
        validity_status=ValidityStatus.VERIFIED
    )
    print(f"Record 3: {msg}")
    print(f"  Event ID: {record.event_id}")
    print(f"  Previous Hash: {record.previous_hash[:16]}...")
    print(f"  Record Hash: {record.record_hash}")
    
    # Test idempotency
    print("\n--- Testing Idempotency ---")
    success, _, msg = ledger.append(
        evidence_type=EvidenceType.CLAIM,
        payload={"test": "duplicate"},
        source="test",
        created_by="test",
        event_id=record.event_id  # Duplicate!
    )
    print(f"Duplicate attempt: {msg}")
    
    # Verify integrity
    print("\n--- Verifying Integrity ---")
    is_valid, errors = ledger.verify_integrity()
    print(f"Integrity Valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    # Generate Proof Pack
    print("\n--- Proof Pack ---")
    proof_pack = ledger.get_proof_pack()
    print(json.dumps(proof_pack, indent=2))
    
    # Export to Airtable format
    print("\n--- Airtable Export Sample ---")
    airtable_records = ledger.export_to_airtable_format()
    print(f"Records ready for Airtable: {len(airtable_records)}")
    print(json.dumps(airtable_records[0], indent=2))
    
    # Test tampering detection
    print("\n--- Tampering Detection Test ---")
    # Simulate tampering by modifying a record's payload
    original_payload = ledger._records[0].payload.copy()
    ledger._records[0].payload["claim"] = "TAMPERED CLAIM"
    
    is_valid, errors = ledger.verify_integrity()
    print(f"After tampering - Integrity Valid: {is_valid}")
    print(f"Errors detected: {errors}")
    
    # Restore
    ledger._records[0].payload = original_payload
    
    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)
