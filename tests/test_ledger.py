"""Tests for immutable ledger core."""

import json
import tempfile
from pathlib import Path

import pytest

from echo_core.ledger import ImmutableLedger, LedgerEntry


class TestLedgerEntry:
    """Test LedgerEntry creation and hashing."""

    def test_entry_creation(self):
        """Test creating a ledger entry."""
        entry = LedgerEntry(
            entry_type="test_entry",
            data={"key": "value"},
            previous_hash="0" * 64,
            sequence=0,
        )

        assert entry.entry_type == "test_entry"
        assert entry.data == {"key": "value"}
        assert entry.previous_hash == "0" * 64
        assert entry.sequence == 0
        assert len(entry.hash) == 64  # SHA-256 hex
        assert entry.timestamp is not None

    def test_hash_deterministic(self):
        """Test that hash is deterministic for same content."""
        entry1 = LedgerEntry(
            entry_type="test",
            data={"key": "value"},
            previous_hash="0" * 64,
            sequence=0,
        )
        
        # Manually set same timestamp
        timestamp = entry1.timestamp
        
        entry2 = LedgerEntry(
            entry_type="test",
            data={"key": "value"},
            previous_hash="0" * 64,
            sequence=0,
        )
        entry2.timestamp = timestamp
        entry2.hash = entry2._compute_hash()

        assert entry1.hash == entry2.hash

    def test_hash_changes_with_data(self):
        """Test that hash changes when data changes."""
        entry1 = LedgerEntry(
            entry_type="test",
            data={"key": "value1"},
            previous_hash="0" * 64,
            sequence=0,
        )
        
        entry2 = LedgerEntry(
            entry_type="test",
            data={"key": "value2"},
            previous_hash="0" * 64,
            sequence=0,
        )

        assert entry1.hash != entry2.hash

    def test_to_dict(self):
        """Test converting entry to dictionary."""
        entry = LedgerEntry(
            entry_type="test",
            data={"key": "value"},
            previous_hash="0" * 64,
            sequence=0,
        )

        d = entry.to_dict()
        assert d["entry_type"] == "test"
        assert d["data"] == {"key": "value"}
        assert d["previous_hash"] == "0" * 64
        assert d["sequence"] == 0
        assert "hash" in d
        assert "timestamp" in d

    def test_from_dict(self):
        """Test reconstructing entry from dictionary."""
        entry1 = LedgerEntry(
            entry_type="test",
            data={"key": "value"},
            previous_hash="0" * 64,
            sequence=0,
        )

        d = entry1.to_dict()
        entry2 = LedgerEntry.from_dict(d)

        assert entry2.entry_type == entry1.entry_type
        assert entry2.data == entry1.data
        assert entry2.hash == entry1.hash

    def test_from_dict_detects_tampering(self):
        """Test that from_dict detects hash tampering."""
        entry = LedgerEntry(
            entry_type="test",
            data={"key": "value"},
            previous_hash="0" * 64,
            sequence=0,
        )

        d = entry.to_dict()
        d["hash"] = "0" * 64  # Tamper with hash

        with pytest.raises(ValueError, match="Hash mismatch"):
            LedgerEntry.from_dict(d)


class TestImmutableLedger:
    """Test ImmutableLedger functionality."""

    @pytest.fixture
    def temp_ledger_path(self):
        """Create temporary ledger path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "test_ledger.jsonl"

    def test_ledger_creation(self, temp_ledger_path):
        """Test creating a new ledger."""
        ledger = ImmutableLedger(temp_ledger_path)
        assert len(ledger.entries) == 0
        assert ledger.verify_integrity()

    def test_append_entry(self, temp_ledger_path):
        """Test appending entry to ledger."""
        ledger = ImmutableLedger(temp_ledger_path)
        
        entry = ledger.append("test_entry", {"key": "value"})
        
        assert entry.entry_type == "test_entry"
        assert entry.data == {"key": "value"}
        assert entry.sequence == 0
        assert entry.previous_hash == ImmutableLedger.GENESIS_HASH
        assert len(ledger.entries) == 1

    def test_append_multiple_entries(self, temp_ledger_path):
        """Test appending multiple entries creates chain."""
        ledger = ImmutableLedger(temp_ledger_path)
        
        entry1 = ledger.append("entry1", {"n": 1})
        entry2 = ledger.append("entry2", {"n": 2})
        entry3 = ledger.append("entry3", {"n": 3})
        
        assert entry1.sequence == 0
        assert entry2.sequence == 1
        assert entry3.sequence == 2
        
        assert entry2.previous_hash == entry1.hash
        assert entry3.previous_hash == entry2.hash
        
        assert len(ledger.entries) == 3

    def test_persistence(self, temp_ledger_path):
        """Test that entries are persisted to disk."""
        ledger1 = ImmutableLedger(temp_ledger_path)
        ledger1.append("entry1", {"n": 1})
        ledger1.append("entry2", {"n": 2})
        
        # Load from disk
        ledger2 = ImmutableLedger(temp_ledger_path)
        
        assert len(ledger2.entries) == 2
        assert ledger2.entries[0].data == {"n": 1}
        assert ledger2.entries[1].data == {"n": 2}

    def test_integrity_verification(self, temp_ledger_path):
        """Test integrity verification passes for valid chain."""
        ledger = ImmutableLedger(temp_ledger_path)
        ledger.append("entry1", {"n": 1})
        ledger.append("entry2", {"n": 2})
        ledger.append("entry3", {"n": 3})
        
        assert ledger.verify_integrity()

    def test_integrity_fails_on_tampering(self, temp_ledger_path):
        """Test integrity verification fails if ledger is tampered."""
        ledger = ImmutableLedger(temp_ledger_path)
        ledger.append("entry1", {"n": 1})
        ledger.append("entry2", {"n": 2})
        
        # Tamper with data
        ledger.entries[1].data["n"] = 999
        
        assert not ledger.verify_integrity()

    def test_integrity_fails_on_broken_chain(self, temp_ledger_path):
        """Test integrity verification fails if chain is broken."""
        ledger = ImmutableLedger(temp_ledger_path)
        ledger.append("entry1", {"n": 1})
        ledger.append("entry2", {"n": 2})
        
        # Break the chain
        ledger.entries[1].previous_hash = "0" * 64
        
        assert not ledger.verify_integrity()

    def test_get_entries_by_type(self, temp_ledger_path):
        """Test filtering entries by type."""
        ledger = ImmutableLedger(temp_ledger_path)
        ledger.append("type_a", {"n": 1})
        ledger.append("type_b", {"n": 2})
        ledger.append("type_a", {"n": 3})
        
        type_a_entries = ledger.get_entries_by_type("type_a")
        
        assert len(type_a_entries) == 2
        assert all(e.entry_type == "type_a" for e in type_a_entries)

    def test_get_entries_by_belief_id(self, temp_ledger_path):
        """Test filtering entries by belief_id."""
        ledger = ImmutableLedger(temp_ledger_path)
        ledger.append("entry1", {"belief_id": "belief-1"})
        ledger.append("entry2", {"belief_id": "belief-2"})
        ledger.append("entry3", {"belief_id": "belief-1"})
        
        belief1_entries = ledger.get_entries_by_belief_id("belief-1")
        
        assert len(belief1_entries) == 2
        assert all(e.data["belief_id"] == "belief-1" for e in belief1_entries)

    def test_audit_report(self, temp_ledger_path):
        """Test generating audit report."""
        ledger = ImmutableLedger(temp_ledger_path)
        ledger.append("type_a", {"n": 1})
        ledger.append("type_b", {"n": 2})
        ledger.append("type_a", {"n": 3})
        
        report = ledger.audit_report()
        
        assert report["total_entries"] == 3
        assert report["integrity_verified"] is True
        assert report["entry_types"]["type_a"] == 2
        assert report["entry_types"]["type_b"] == 1

    def test_load_detects_tampering(self, temp_ledger_path):
        """Test that loading ledger detects tampering."""
        ledger1 = ImmutableLedger(temp_ledger_path)
        ledger1.append("entry1", {"n": 1})
        ledger1.append("entry2", {"n": 2})
        
        # Tamper with file
        with open(temp_ledger_path, "r") as f:
            lines = f.readlines()
        
        # Change data in second entry
        entry_dict = json.loads(lines[1])
        entry_dict["data"]["n"] = 999
        lines[1] = json.dumps(entry_dict) + "\n"
        
        with open(temp_ledger_path, "w") as f:
            f.writelines(lines)
        
        # Loading should fail
        with pytest.raises(ValueError, match="Hash mismatch"):
            ImmutableLedger(temp_ledger_path)
