"""
Audit System - Comprehensive Logging and Transparency
=====================================================

Provides complete audit logging with tiered transparency that protects
privacy while enabling external scrutiny. All significant actions are
logged with full provenance.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import hashlib
import json


class AuditLevel(Enum):
    """Levels of audit detail."""
    FULL = auto()       # Complete details including internals
    STANDARD = auto()   # Standard operational details
    SUMMARY = auto()    # Summary only
    MINIMAL = auto()    # Existence only


class AccessTier(Enum):
    """Access tiers for audit logs."""
    PUBLIC = auto()         # Anyone can access
    STAKEHOLDER = auto()    # Registered stakeholders
    OVERSIGHT = auto()      # Oversight bodies only
    INTERNAL = auto()       # System internals only


class EventType(Enum):
    """Types of auditable events."""
    ACTION = auto()         # Action taken
    DECISION = auto()       # Decision made
    INFERENCE = auto()      # Inference drawn
    MODIFICATION = auto()   # System modification
    OVERRIDE = auto()       # Human override
    ERROR = auto()          # Error occurred
    ALIGNMENT = auto()      # Alignment-related event


@dataclass
class AuditEntry:
    """A single audit log entry."""
    id: str
    timestamp: datetime
    event_type: EventType
    access_tier: AccessTier
    summary: str
    details: Dict[str, Any]
    actor: str  # Who/what performed this
    affected_entities: List[str]
    reversible: bool
    hash: str  # For integrity verification
    parent_id: Optional[str] = None  # For linked events


@dataclass
class AuditQuery:
    """Query parameters for searching audit logs."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[List[EventType]] = None
    access_tier: Optional[AccessTier] = None
    actor: Optional[str] = None
    keyword: Optional[str] = None


class AuditSystem:
    """
    Manages audit logging and transparency.

    Features:
    - Immutable audit trail
    - Tiered access control
    - Cryptographic integrity
    - Query and search capabilities
    - Privacy-preserving summaries
    """

    def __init__(self):
        self._entries: List[AuditEntry] = []
        self._entry_index: Dict[str, AuditEntry] = {}
        self._chain_hash: str = "genesis"

    def log(
        self,
        event_type: EventType,
        summary: str,
        details: Dict[str, Any],
        actor: str,
        access_tier: AccessTier = AccessTier.STAKEHOLDER,
        affected_entities: Optional[List[str]] = None,
        reversible: bool = True,
        parent_id: Optional[str] = None
    ) -> str:
        """
        Log an auditable event.

        Returns the entry ID.
        """
        entry_id = str(uuid.uuid4())

        # Create entry
        entry = AuditEntry(
            id=entry_id,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            access_tier=access_tier,
            summary=summary,
            details=details,
            actor=actor,
            affected_entities=affected_entities or [],
            reversible=reversible,
            hash="",  # Will be set below
            parent_id=parent_id
        )

        # Calculate hash (includes previous hash for chain integrity)
        entry.hash = self._calculate_hash(entry)
        self._chain_hash = entry.hash

        # Store entry
        self._entries.append(entry)
        self._entry_index[entry_id] = entry

        return entry_id

    def _calculate_hash(self, entry: AuditEntry) -> str:
        """Calculate cryptographic hash for entry integrity."""
        content = {
            'id': entry.id,
            'timestamp': entry.timestamp.isoformat(),
            'event_type': entry.event_type.name,
            'summary': entry.summary,
            'actor': entry.actor,
            'previous_hash': self._chain_hash
        }
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()

    def query(
        self,
        query: AuditQuery,
        requester_tier: AccessTier
    ) -> List[AuditEntry]:
        """
        Query audit logs with access control.

        Returns entries the requester is authorized to see.
        """
        results = []

        for entry in self._entries:
            # Access control
            if not self._can_access(entry.access_tier, requester_tier):
                continue

            # Apply filters
            if query.start_time and entry.timestamp < query.start_time:
                continue
            if query.end_time and entry.timestamp > query.end_time:
                continue
            if query.event_types and entry.event_type not in query.event_types:
                continue
            if query.actor and entry.actor != query.actor:
                continue
            if query.keyword and query.keyword.lower() not in entry.summary.lower():
                continue

            results.append(entry)

        return results

    def _can_access(self, entry_tier: AccessTier, requester_tier: AccessTier) -> bool:
        """Check if requester can access entry."""
        tier_hierarchy = {
            AccessTier.PUBLIC: 0,
            AccessTier.STAKEHOLDER: 1,
            AccessTier.OVERSIGHT: 2,
            AccessTier.INTERNAL: 3
        }

        return tier_hierarchy[requester_tier] >= tier_hierarchy[entry_tier]

    def get_entry(
        self,
        entry_id: str,
        requester_tier: AccessTier
    ) -> Optional[AuditEntry]:
        """Get a specific audit entry."""
        entry = self._entry_index.get(entry_id)
        if entry and self._can_access(entry.access_tier, requester_tier):
            return entry
        return None

    def get_public_summary(self) -> Dict[str, Any]:
        """Get a public summary of audit activity."""
        public_entries = [
            e for e in self._entries
            if e.access_tier == AccessTier.PUBLIC
        ]

        return {
            'total_public_entries': len(public_entries),
            'by_event_type': {
                t.name: len([e for e in public_entries if e.event_type == t])
                for t in EventType
            },
            'latest_timestamp': max(
                (e.timestamp for e in public_entries),
                default=None
            ),
            'actors': list(set(e.actor for e in public_entries))
        }

    def verify_integrity(self) -> Dict[str, Any]:
        """Verify the integrity of the audit chain."""
        if not self._entries:
            return {'valid': True, 'message': 'No entries to verify'}

        previous_hash = "genesis"
        valid = True
        errors = []

        for i, entry in enumerate(self._entries):
            expected_hash = self._calculate_entry_hash_with_previous(
                entry, previous_hash
            )
            if entry.hash != expected_hash:
                valid = False
                errors.append(f"Entry {i} ({entry.id}): hash mismatch")

            previous_hash = entry.hash

        return {
            'valid': valid,
            'entries_checked': len(self._entries),
            'errors': errors
        }

    def _calculate_entry_hash_with_previous(
        self,
        entry: AuditEntry,
        previous_hash: str
    ) -> str:
        """Calculate hash with specific previous hash."""
        content = {
            'id': entry.id,
            'timestamp': entry.timestamp.isoformat(),
            'event_type': entry.event_type.name,
            'summary': entry.summary,
            'actor': entry.actor,
            'previous_hash': previous_hash
        }
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()

    def export_for_review(
        self,
        requester_tier: AccessTier,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Export audit entries for external review."""
        query = AuditQuery(start_time=start_time, end_time=end_time)
        entries = self.query(query, requester_tier)

        return [
            {
                'id': e.id,
                'timestamp': e.timestamp.isoformat(),
                'event_type': e.event_type.name,
                'summary': e.summary,
                'actor': e.actor,
                'reversible': e.reversible,
                'hash': e.hash
            }
            for e in entries
        ]

    def get_action_trace(self, entry_id: str) -> List[AuditEntry]:
        """
        Get the trace of actions leading to a specific entry.

        Follows parent links to build the trace.
        """
        trace = []
        current_id = entry_id

        while current_id:
            entry = self._entry_index.get(current_id)
            if not entry:
                break
            trace.append(entry)
            current_id = entry.parent_id

        return list(reversed(trace))

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate a compliance/audit report."""
        return {
            'total_entries': len(self._entries),
            'integrity_status': self.verify_integrity(),
            'by_access_tier': {
                t.name: len([e for e in self._entries if e.access_tier == t])
                for t in AccessTier
            },
            'by_event_type': {
                t.name: len([e for e in self._entries if e.event_type == t])
                for t in EventType
            },
            'irreversible_actions': len([
                e for e in self._entries if not e.reversible
            ]),
            'time_range': {
                'earliest': min(
                    (e.timestamp for e in self._entries),
                    default=None
                ),
                'latest': max(
                    (e.timestamp for e in self._entries),
                    default=None
                )
            }
        }
