#!/usr/bin/env python3
"""
Aletheia Consent & Custody Ledger
==================================
Records parties, scope, duration, revocations, and enforces
minimization rules at export time.

Author: Echo Nexus Omega
Version: 1.0.0
"""

import json
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum


class ConsentScope(Enum):
    """Permitted uses for data."""
    RESEARCH = "research"
    VALIDATION = "validation"
    PUBLICATION = "publication"
    DERIVATIVE = "derivative"
    COMMERCIAL = "commercial"
    ARCHIVE = "archive"


class ConsentStatus(Enum):
    """Status of a consent record."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


@dataclass
class ConsentRecord:
    """Record of consent for data use."""
    consent_id: str
    artifact_ids: List[str]
    grantor: str  # Party granting consent
    grantee: str  # Party receiving consent
    scope: List[str]
    restrictions: List[str]
    granted_at: str
    expires_at: Optional[str]
    status: str
    steward_id: Optional[str]
    metadata: Dict[str, Any]
    signature: str  # Grantor's signature


@dataclass
class CustodyRecord:
    """Record of custody transfer."""
    custody_id: str
    artifact_id: str
    from_party: str
    to_party: str
    action: str
    timestamp: str
    location: Optional[str]
    notes: Optional[str]
    signature: str


@dataclass
class RevocationRecord:
    """Record of consent revocation."""
    revocation_id: str
    consent_id: str
    revoked_by: str
    revoked_at: str
    reason: str
    signature: str


class ConsentLedger:
    """
    Immutable ledger for consent and custody records.

    Features:
    - Append-only consent records
    - Custody chain tracking
    - Revocation support
    - Export-time minimization enforcement
    """

    def __init__(self, ledger_path: str):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.mkdir(parents=True, exist_ok=True)

        # Separate files for different record types
        self.consents_file = self.ledger_path / "consents.jsonl"
        self.custody_file = self.ledger_path / "custody.jsonl"
        self.revocations_file = self.ledger_path / "revocations.jsonl"

        # In-memory index for fast lookups
        self._consent_index: Dict[str, ConsentRecord] = {}
        self._custody_index: Dict[str, List[CustodyRecord]] = {}
        self._revocations: Set[str] = set()

        self._load_ledger()

    def _load_ledger(self):
        """Load ledger from disk."""
        # Load consents
        if self.consents_file.exists():
            with open(self.consents_file) as f:
                for line in f:
                    record = ConsentRecord(**json.loads(line))
                    self._consent_index[record.consent_id] = record

        # Load custody
        if self.custody_file.exists():
            with open(self.custody_file) as f:
                for line in f:
                    record = CustodyRecord(**json.loads(line))
                    if record.artifact_id not in self._custody_index:
                        self._custody_index[record.artifact_id] = []
                    self._custody_index[record.artifact_id].append(record)

        # Load revocations
        if self.revocations_file.exists():
            with open(self.revocations_file) as f:
                for line in f:
                    record = json.loads(line)
                    self._revocations.add(record["consent_id"])

    def _append_record(self, file_path: Path, record: dict):
        """Append a record to a ledger file."""
        with open(file_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def grant_consent(
        self,
        artifact_ids: List[str],
        grantor: str,
        grantee: str,
        scope: List[ConsentScope],
        restrictions: List[str] = None,
        duration_days: Optional[int] = None,
        steward_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Grant consent for data use.

        Returns: consent_id
        """
        consent_id = f"CONSENT-{secrets.token_hex(8).upper()}"
        now = datetime.now(timezone.utc)

        expires_at = None
        if duration_days:
            expires_at = (now + timedelta(days=duration_days)).isoformat().replace("+00:00", "Z")

        # Create consent record
        record = ConsentRecord(
            consent_id=consent_id,
            artifact_ids=artifact_ids,
            grantor=grantor,
            grantee=grantee,
            scope=[s.value if isinstance(s, ConsentScope) else s for s in scope],
            restrictions=restrictions or [],
            granted_at=now.isoformat().replace("+00:00", "Z"),
            expires_at=expires_at,
            status=ConsentStatus.ACTIVE.value,
            steward_id=steward_id,
            metadata=metadata or {},
            signature=self._sign_record(consent_id, grantor)
        )

        # Store
        self._consent_index[consent_id] = record
        self._append_record(self.consents_file, asdict(record))

        return consent_id

    def revoke_consent(self, consent_id: str, revoked_by: str, reason: str) -> str:
        """
        Revoke a consent grant.

        Returns: revocation_id
        """
        if consent_id not in self._consent_index:
            raise KeyError(f"Consent not found: {consent_id}")

        if consent_id in self._revocations:
            raise ValueError(f"Consent already revoked: {consent_id}")

        revocation_id = f"REVOKE-{secrets.token_hex(8).upper()}"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        record = RevocationRecord(
            revocation_id=revocation_id,
            consent_id=consent_id,
            revoked_by=revoked_by,
            revoked_at=now,
            reason=reason,
            signature=self._sign_record(revocation_id, revoked_by)
        )

        # Update status
        self._revocations.add(consent_id)
        self._consent_index[consent_id].status = ConsentStatus.REVOKED.value

        # Store
        self._append_record(self.revocations_file, asdict(record))

        return revocation_id

    def record_custody(
        self,
        artifact_id: str,
        from_party: str,
        to_party: str,
        action: str,
        location: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        Record a custody transfer.

        Returns: custody_id
        """
        custody_id = f"CUSTODY-{secrets.token_hex(8).upper()}"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        record = CustodyRecord(
            custody_id=custody_id,
            artifact_id=artifact_id,
            from_party=from_party,
            to_party=to_party,
            action=action,
            timestamp=now,
            location=location,
            notes=notes,
            signature=self._sign_record(custody_id, from_party)
        )

        # Store
        if artifact_id not in self._custody_index:
            self._custody_index[artifact_id] = []
        self._custody_index[artifact_id].append(record)
        self._append_record(self.custody_file, asdict(record))

        return custody_id

    def check_consent(
        self,
        artifact_id: str,
        grantee: str,
        required_scope: ConsentScope
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if consent exists for a given use.

        Returns: (has_consent, consent_id)
        """
        now = datetime.now(timezone.utc)

        for consent_id, record in self._consent_index.items():
            # Check artifact
            if artifact_id not in record.artifact_ids:
                continue

            # Check grantee
            if record.grantee != grantee and record.grantee != "*":
                continue

            # Check not revoked
            if consent_id in self._revocations:
                continue

            # Check not expired
            if record.expires_at:
                expiry = datetime.fromisoformat(record.expires_at.replace("Z", "+00:00"))
                if now > expiry:
                    continue

            # Check scope
            scope_value = required_scope.value if isinstance(required_scope, ConsentScope) else required_scope
            if scope_value in record.scope:
                return True, consent_id

        return False, None

    def get_consent_snapshot(self, artifact_ids: List[str]) -> Dict[str, Any]:
        """
        Get snapshot of consent state for artifacts.

        Used for export bundles.
        """
        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "artifacts": {}
        }

        for artifact_id in artifact_ids:
            artifact_consents = []
            for consent_id, record in self._consent_index.items():
                if artifact_id in record.artifact_ids:
                    artifact_consents.append({
                        "consent_id": consent_id,
                        "scope": record.scope,
                        "status": record.status,
                        "revoked": consent_id in self._revocations,
                        "expired": self._is_expired(record)
                    })

            snapshot["artifacts"][artifact_id] = {
                "consents": artifact_consents,
                "custody_chain": [
                    asdict(c) for c in self._custody_index.get(artifact_id, [])
                ]
            }

        return snapshot

    def get_custody_chain(self, artifact_id: str) -> List[CustodyRecord]:
        """Get full custody chain for an artifact."""
        return self._custody_index.get(artifact_id, [])

    def enforce_minimization(
        self,
        artifact_ids: List[str],
        grantee: str,
        requested_scope: ConsentScope
    ) -> List[str]:
        """
        Return only artifacts where consent allows the requested use.

        Enforces data minimization at export time.
        """
        allowed = []
        for artifact_id in artifact_ids:
            has_consent, _ = self.check_consent(artifact_id, grantee, requested_scope)
            if has_consent:
                allowed.append(artifact_id)
        return allowed

    def _is_expired(self, record: ConsentRecord) -> bool:
        """Check if consent is expired."""
        if not record.expires_at:
            return False
        expiry = datetime.fromisoformat(record.expires_at.replace("Z", "+00:00"))
        return datetime.now(timezone.utc) > expiry

    def _sign_record(self, record_id: str, party: str) -> str:
        """Generate signature for a record (placeholder)."""
        # In production, use actual cryptographic signing
        data = f"{record_id}:{party}:{datetime.now(timezone.utc).isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()


# Type hint for external use
from typing import Tuple


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Aletheia Consent Ledger CLI")
    parser.add_argument("--ledger", default="./ledger_data")
    subparsers = parser.add_subparsers(dest="command")

    # Grant consent
    grant_parser = subparsers.add_parser("grant", help="Grant consent")
    grant_parser.add_argument("--artifacts", required=True, help="Comma-separated artifact IDs")
    grant_parser.add_argument("--grantor", required=True)
    grant_parser.add_argument("--grantee", required=True)
    grant_parser.add_argument("--scope", required=True, help="Comma-separated scopes")
    grant_parser.add_argument("--days", type=int)

    # Check consent
    check_parser = subparsers.add_parser("check", help="Check consent")
    check_parser.add_argument("--artifact", required=True)
    check_parser.add_argument("--grantee", required=True)
    check_parser.add_argument("--scope", required=True)

    # List
    list_parser = subparsers.add_parser("list", help="List consents")

    args = parser.parse_args()

    ledger = ConsentLedger(args.ledger)

    if args.command == "grant":
        artifacts = args.artifacts.split(",")
        scopes = [ConsentScope(s.strip()) for s in args.scope.split(",")]
        consent_id = ledger.grant_consent(
            artifact_ids=artifacts,
            grantor=args.grantor,
            grantee=args.grantee,
            scope=scopes,
            duration_days=args.days
        )
        print(f"Consent granted: {consent_id}")

    elif args.command == "check":
        has_consent, consent_id = ledger.check_consent(
            args.artifact, args.grantee, ConsentScope(args.scope)
        )
        print(json.dumps({
            "has_consent": has_consent,
            "consent_id": consent_id
        }, indent=2))

    elif args.command == "list":
        consents = [asdict(c) for c in ledger._consent_index.values()]
        print(json.dumps(consents, indent=2))

    else:
        parser.print_help()
