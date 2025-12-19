"""Immutable ledger core with hash-chain integrity.

This is Echo's memory prosthetic - an append-only ledger that refuses to lie.

Design principles:
- Append-only: No deletion, only deprecation
- Hash-chained: Tampering is visible
- Causality-tracked: Sequence matters, not just time
- Self-auditing: Can verify its own integrity
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class LedgerEntry:
    """A single immutable entry in the ledger."""

    def __init__(
        self,
        entry_type: str,
        data: Dict[str, Any],
        previous_hash: str,
        sequence: int,
    ) -> None:
        """Create a new ledger entry.

        Args:
            entry_type: Type of entry (belief_created, evidence_added, etc.)
            data: Entry data (must be JSON-serializable)
            previous_hash: Hash of previous entry (for chain integrity)
            sequence: Sequence number (causality tracking)
        """
        self.entry_type = entry_type
        self.data = data
        self.previous_hash = previous_hash
        self.sequence = sequence
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of entry contents.

        Hash includes:
        - entry_type
        - data (JSON-serialized)
        - previous_hash (chain link)
        - sequence (causality)
        - timestamp (when, not why)

        Returns:
            Hex-encoded SHA-256 hash
        """
        content = {
            "entry_type": self.entry_type,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "sequence": self.sequence,
            "timestamp": self.timestamp,
        }
        content_json = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_json.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for serialization."""
        return {
            "entry_type": self.entry_type,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LedgerEntry":
        """Reconstruct entry from dictionary."""
        entry = cls(
            entry_type=data["entry_type"],
            data=data["data"],
            previous_hash=data["previous_hash"],
            sequence=data["sequence"],
        )
        # Restore original timestamp (don't recompute)
        entry.timestamp = data["timestamp"]
        # Recompute hash with restored timestamp
        entry.hash = entry._compute_hash()
        # Verify hash matches
        if entry.hash != data["hash"]:
            raise ValueError(
                f"Hash mismatch: computed {entry.hash}, stored {data['hash']}"
            )
        return entry


class ImmutableLedger:
    """Append-only ledger with hash-chain integrity.

    This is Echo's memory - it refuses to lie.

    Properties:
    - Append-only: Cannot delete entries
    - Hash-chained: Tampering breaks the chain
    - Self-auditing: Can verify its own integrity
    - Causality-tracked: Sequence matters
    """

    GENESIS_HASH = "0" * 64  # SHA-256 of nothing

    def __init__(self, ledger_path: Optional[Path] = None) -> None:
        """Initialize ledger.

        Args:
            ledger_path: Path to ledger file (default: ~/.echo/ledger.jsonl)
        """
        if ledger_path is None:
            ledger_path = Path.home() / ".echo" / "ledger.jsonl"

        self.ledger_path = ledger_path
        self.entries: List[LedgerEntry] = []
        self._load()

    def _load(self) -> None:
        """Load ledger from disk."""
        if not self.ledger_path.exists():
            return

        with open(self.ledger_path, "r") as f:
            for line in f:
                if line.strip():
                    entry_dict = json.loads(line)
                    entry = LedgerEntry.from_dict(entry_dict)
                    self.entries.append(entry)

        # Verify chain integrity after loading
        if not self.verify_integrity():
            raise ValueError("Ledger integrity check failed - chain is broken")

    def append(self, entry_type: str, data: Dict[str, Any]) -> LedgerEntry:
        """Append a new entry to the ledger.

        Args:
            entry_type: Type of entry
            data: Entry data (must be JSON-serializable)

        Returns:
            The created entry
        """
        # Get previous hash and sequence
        if self.entries:
            previous_hash = self.entries[-1].hash
            sequence = self.entries[-1].sequence + 1
        else:
            previous_hash = self.GENESIS_HASH
            sequence = 0

        # Create entry
        entry = LedgerEntry(
            entry_type=entry_type,
            data=data,
            previous_hash=previous_hash,
            sequence=sequence,
        )

        # Append to memory
        self.entries.append(entry)

        # Persist to disk (append-only)
        self._persist(entry)

        return entry

    def _persist(self, entry: LedgerEntry) -> None:
        """Persist entry to disk (append-only).

        Args:
            entry: Entry to persist
        """
        # Ensure directory exists
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        # Append to file (JSONL format)
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def verify_integrity(self) -> bool:
        """Verify hash-chain integrity.

        Returns:
            True if chain is intact, False if tampered
        """
        if not self.entries:
            return True

        # First entry must link to genesis
        if self.entries[0].previous_hash != self.GENESIS_HASH:
            return False

        # Each entry must link to previous
        for i in range(1, len(self.entries)):
            if self.entries[i].previous_hash != self.entries[i - 1].hash:
                return False

        # Verify each entry's hash is correct
        for entry in self.entries:
            expected_hash = entry._compute_hash()
            if entry.hash != expected_hash:
                return False

        return True

    def get_entries_by_type(self, entry_type: str) -> List[LedgerEntry]:
        """Get all entries of a specific type.

        Args:
            entry_type: Type to filter by

        Returns:
            List of matching entries
        """
        return [e for e in self.entries if e.entry_type == entry_type]

    def get_entries_by_belief_id(self, belief_id: str) -> List[LedgerEntry]:
        """Get all entries related to a specific belief.

        Args:
            belief_id: Belief ID to filter by

        Returns:
            List of matching entries
        """
        return [
            e
            for e in self.entries
            if e.data.get("belief_id") == belief_id
        ]

    def audit_report(self) -> Dict[str, Any]:
        """Generate self-audit report.

        Returns:
            Audit report with integrity status and statistics
        """
        return {
            "total_entries": len(self.entries),
            "integrity_verified": self.verify_integrity(),
            "first_entry": self.entries[0].timestamp if self.entries else None,
            "last_entry": self.entries[-1].timestamp if self.entries else None,
            "entry_types": {
                entry_type: len(self.get_entries_by_type(entry_type))
                for entry_type in set(e.entry_type for e in self.entries)
            },
        }
