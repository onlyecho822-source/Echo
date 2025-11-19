"""
Decision Logger - Transparent Decision Recording
================================================

Records all governance decisions with full transparency,
enabling external audits and accountability.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import hashlib
import json


@dataclass
class DecisionRecord:
    """A complete record of a governance decision."""
    id: str
    decision_id: str
    title: str
    decision_type: str
    description: str
    proposer: str
    required_bodies: List[str]
    votes: List[Dict[str, Any]]
    outcome: str
    rationale: str
    dissenting_opinions: List[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    hash: str  # For integrity verification


class DecisionLogger:
    """
    Logs all governance decisions for transparency and audit.

    Features:
    - Immutable decision records
    - Cryptographic integrity
    - Export for external audit
    - Search and query
    """

    def __init__(self):
        self._records: List[DecisionRecord] = []
        self._record_index: Dict[str, DecisionRecord] = {}

    def log_decision(
        self,
        decision_id: str,
        title: str,
        decision_type: str,
        description: str,
        proposer: str,
        required_bodies: List[str],
        votes: List[Dict[str, Any]],
        outcome: str,
        rationale: str,
        dissenting_opinions: Optional[List[str]] = None,
        created_at: Optional[datetime] = None,
        resolved_at: Optional[datetime] = None
    ) -> DecisionRecord:
        """Log a governance decision."""
        record_id = str(uuid.uuid4())

        record = DecisionRecord(
            id=record_id,
            decision_id=decision_id,
            title=title,
            decision_type=decision_type,
            description=description,
            proposer=proposer,
            required_bodies=required_bodies,
            votes=votes,
            outcome=outcome,
            rationale=rationale,
            dissenting_opinions=dissenting_opinions or [],
            created_at=created_at or datetime.utcnow(),
            resolved_at=resolved_at,
            hash=""
        )

        # Calculate hash
        record.hash = self._calculate_hash(record)

        self._records.append(record)
        self._record_index[record_id] = record

        return record

    def _calculate_hash(self, record: DecisionRecord) -> str:
        """Calculate cryptographic hash of record."""
        content = {
            'id': record.id,
            'decision_id': record.decision_id,
            'title': record.title,
            'outcome': record.outcome,
            'votes': record.votes
        }
        return hashlib.sha256(
            json.dumps(content, sort_keys=True, default=str).encode()
        ).hexdigest()

    def get_record(self, record_id: str) -> Optional[DecisionRecord]:
        """Get a record by ID."""
        return self._record_index.get(record_id)

    def get_records_by_outcome(self, outcome: str) -> List[DecisionRecord]:
        """Get all records with a specific outcome."""
        return [r for r in self._records if r.outcome == outcome]

    def get_records_by_type(self, decision_type: str) -> List[DecisionRecord]:
        """Get all records of a specific decision type."""
        return [r for r in self._records if r.decision_type == decision_type]

    def get_records_in_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[DecisionRecord]:
        """Get records within a date range."""
        return [
            r for r in self._records
            if start_date <= r.created_at <= end_date
        ]

    def export_for_audit(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Export records for external audit."""
        records = self._records

        if start_date:
            records = [r for r in records if r.created_at >= start_date]
        if end_date:
            records = [r for r in records if r.created_at <= end_date]

        return [
            {
                'id': r.id,
                'decision_id': r.decision_id,
                'title': r.title,
                'decision_type': r.decision_type,
                'proposer': r.proposer,
                'required_bodies': r.required_bodies,
                'vote_count': len(r.votes),
                'outcome': r.outcome,
                'rationale': r.rationale,
                'dissenting_count': len(r.dissenting_opinions),
                'created_at': r.created_at.isoformat(),
                'resolved_at': r.resolved_at.isoformat() if r.resolved_at else None,
                'hash': r.hash
            }
            for r in records
        ]

    def verify_integrity(self) -> Dict[str, Any]:
        """Verify integrity of all records."""
        errors = []

        for record in self._records:
            expected_hash = self._calculate_hash(record)
            if record.hash != expected_hash:
                errors.append(f"Record {record.id}: hash mismatch")

        return {
            'valid': len(errors) == 0,
            'records_checked': len(self._records),
            'errors': errors
        }

    def get_decision_statistics(self) -> Dict[str, Any]:
        """Get statistics on logged decisions."""
        if not self._records:
            return {'total': 0}

        return {
            'total': len(self._records),
            'by_outcome': self._count_by_field('outcome'),
            'by_type': self._count_by_field('decision_type'),
            'with_dissent': len([
                r for r in self._records if r.dissenting_opinions
            ]),
            'average_votes': sum(
                len(r.votes) for r in self._records
            ) / len(self._records)
        }

    def _count_by_field(self, field: str) -> Dict[str, int]:
        """Count records by a specific field."""
        counts: Dict[str, int] = {}
        for record in self._records:
            value = getattr(record, field)
            counts[value] = counts.get(value, 0) + 1
        return counts

    def search_records(self, keyword: str) -> List[DecisionRecord]:
        """Search records by keyword in title or description."""
        keyword_lower = keyword.lower()
        return [
            r for r in self._records
            if keyword_lower in r.title.lower() or
               keyword_lower in r.description.lower()
        ]

    def generate_transparency_report(self) -> Dict[str, Any]:
        """Generate a public transparency report."""
        stats = self.get_decision_statistics()

        return {
            'report_generated': datetime.utcnow().isoformat(),
            'total_decisions': stats.get('total', 0),
            'outcomes': stats.get('by_outcome', {}),
            'decision_types': stats.get('by_type', {}),
            'transparency_metrics': {
                'decisions_with_dissent': stats.get('with_dissent', 0),
                'average_votes_per_decision': stats.get('average_votes', 0),
                'integrity_verified': self.verify_integrity()['valid']
            }
        }
