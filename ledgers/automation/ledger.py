#!/usr/bin/env python3
"""
Echo Universe - Immutable Governance Ledger
============================================

This ledger implements a Merkle tree-based append-only log for governance events.
Each entry is cryptographically chained to the previous entry, making tampering detectable.

Constitutional Authority: This ledger is the source of truth for all automated governance actions.
Any modification to historical entries will break the cryptographic chain and be immediately visible.

Design Principles:
- Append-only: Entries can never be modified or deleted
- Cryptographically chained: Each entry contains hash of previous entry
- Self-verifying: Chain integrity can be verified at any time
- Human-readable: JSONL format for transparency and auditability
"""

import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ImmutableLedger:
    """
    Cryptographically-chained append-only ledger for governance events.
    
    Each entry contains:
    - timestamp: ISO 8601 timestamp
    - event_type: Type of governance event
    - data: Event-specific data
    - previous_hash: SHA-256 hash of previous entry
    - entry_hash: SHA-256 hash of current entry
    """
    
    def __init__(self, ledger_path: str = "ledgers/automation/coordination_log.jsonl"):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize ledger if it doesn't exist
        if not self.ledger_path.exists():
            self._initialize_ledger()
    
    def _initialize_ledger(self):
        """Create genesis entry for new ledger."""
        genesis_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "event_type": "ledger_genesis",
            "data": {
                "message": "Echo Universe Governance Ledger Initialized",
                "version": "1.0.0",
                "constitutional_authority": "Immutable audit trail for automated governance"
            },
            "previous_hash": "0" * 64,  # Genesis has no previous entry
            "entry_hash": None  # Will be computed
        }
        
        # Compute hash for genesis entry
        genesis_entry["entry_hash"] = self._compute_entry_hash(genesis_entry)
        
        # Write genesis entry
        with open(self.ledger_path, 'w') as f:
            f.write(json.dumps(genesis_entry) + '\n')
    
    def _compute_entry_hash(self, entry: Dict[str, Any]) -> str:
        """
        Compute SHA-256 hash of entry.
        
        Hash includes: timestamp, event_type, data, and previous_hash.
        The entry_hash field itself is excluded from the hash computation.
        """
        hash_input = {
            "timestamp": entry["timestamp"],
            "event_type": entry["event_type"],
            "data": entry["data"],
            "previous_hash": entry["previous_hash"]
        }
        
        # Create deterministic JSON string (sorted keys, no whitespace)
        canonical_json = json.dumps(hash_input, sort_keys=True, separators=(',', ':'))
        
        # Compute SHA-256 hash
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    
    def get_last_entry(self) -> Optional[Dict[str, Any]]:
        """Get the most recent entry from the ledger."""
        if not self.ledger_path.exists():
            return None
        
        with open(self.ledger_path, 'r') as f:
            lines = f.readlines()
            if not lines:
                return None
            return json.loads(lines[-1])
    
    def append(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Append a new entry to the ledger.
        
        Args:
            event_type: Type of governance event (e.g., "coordination_audit", "pr_created")
            data: Event-specific data
            
        Returns:
            The newly created entry
            
        Raises:
            ValueError: If chain integrity is broken
        """
        # Get previous entry to chain from
        last_entry = self.get_last_entry()
        if last_entry is None:
            raise ValueError("Ledger not initialized. Genesis entry missing.")
        
        # Create new entry
        new_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "data": data,
            "previous_hash": last_entry["entry_hash"],
            "entry_hash": None  # Will be computed
        }
        
        # Compute hash for new entry
        new_entry["entry_hash"] = self._compute_entry_hash(new_entry)
        
        # Append to ledger file
        with open(self.ledger_path, 'a') as f:
            f.write(json.dumps(new_entry) + '\n')
        
        return new_entry
    
    def verify_integrity(self) -> tuple[bool, Optional[str]]:
        """
        Verify the cryptographic integrity of the entire ledger.
        
        Returns:
            (is_valid, error_message)
            - is_valid: True if chain is intact, False if tampering detected
            - error_message: Description of integrity violation, or None if valid
        """
        if not self.ledger_path.exists():
            return False, "Ledger file does not exist"
        
        with open(self.ledger_path, 'r') as f:
            entries = [json.loads(line) for line in f]
        
        if not entries:
            return False, "Ledger is empty"
        
        # Verify genesis entry
        genesis = entries[0]
        if genesis["previous_hash"] != "0" * 64:
            return False, "Genesis entry has invalid previous_hash"
        
        # Verify each entry's hash and chain linkage
        for i, entry in enumerate(entries):
            # Recompute hash and verify it matches
            computed_hash = self._compute_entry_hash(entry)
            if computed_hash != entry["entry_hash"]:
                return False, f"Entry {i} has invalid hash (tampering detected)"
            
            # Verify chain linkage (except for genesis)
            if i > 0:
                if entry["previous_hash"] != entries[i-1]["entry_hash"]:
                    return False, f"Entry {i} has broken chain linkage"
        
        return True, None
    
    def get_all_entries(self) -> List[Dict[str, Any]]:
        """Get all entries from the ledger."""
        if not self.ledger_path.exists():
            return []
        
        with open(self.ledger_path, 'r') as f:
            return [json.loads(line) for line in f]
    
    def get_entries_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Get all entries of a specific event type."""
        return [e for e in self.get_all_entries() if e["event_type"] == event_type]
    
    def export_audit_report(self, output_path: str):
        """
        Export a human-readable audit report.
        
        Args:
            output_path: Path to write the audit report
        """
        entries = self.get_all_entries()
        is_valid, error = self.verify_integrity()
        
        with open(output_path, 'w') as f:
            f.write("ECHO UNIVERSE - GOVERNANCE LEDGER AUDIT REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.datetime.utcnow().isoformat()}Z\n")
            f.write(f"Total Entries: {len(entries)}\n")
            f.write(f"Chain Integrity: {'VALID' if is_valid else 'BROKEN'}\n")
            
            if not is_valid:
                f.write(f"Integrity Error: {error}\n")
            
            f.write("\n" + "=" * 80 + "\n\n")
            
            for i, entry in enumerate(entries):
                f.write(f"Entry #{i}\n")
                f.write(f"Timestamp: {entry['timestamp']}\n")
                f.write(f"Event Type: {entry['event_type']}\n")
                f.write(f"Previous Hash: {entry['previous_hash'][:16]}...\n")
                f.write(f"Entry Hash: {entry['entry_hash'][:16]}...\n")
                f.write(f"Data: {json.dumps(entry['data'], indent=2)}\n")
                f.write("\n" + "-" * 80 + "\n\n")


def main():
    """Command-line interface for ledger operations."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ledger.py init                    - Initialize new ledger")
        print("  ledger.py append <type> <data>    - Append entry")
        print("  ledger.py verify                  - Verify chain integrity")
        print("  ledger.py export <output>         - Export audit report")
        print("  ledger.py list                    - List all entries")
        sys.exit(1)
    
    command = sys.argv[1]
    ledger = ImmutableLedger()
    
    if command == "init":
        print("Ledger initialized (or already exists)")
        print(f"Location: {ledger.ledger_path}")
        
    elif command == "append":
        if len(sys.argv) < 4:
            print("Error: append requires event_type and data")
            sys.exit(1)
        event_type = sys.argv[2]
        data = json.loads(sys.argv[3])
        entry = ledger.append(event_type, data)
        print(f"Entry appended: {entry['entry_hash'][:16]}...")
        
    elif command == "verify":
        is_valid, error = ledger.verify_integrity()
        if is_valid:
            print("✓ Ledger integrity VALID - No tampering detected")
        else:
            print(f"✗ Ledger integrity BROKEN - {error}")
            sys.exit(1)
            
    elif command == "export":
        if len(sys.argv) < 3:
            print("Error: export requires output path")
            sys.exit(1)
        output_path = sys.argv[2]
        ledger.export_audit_report(output_path)
        print(f"Audit report exported to: {output_path}")
        
    elif command == "list":
        entries = ledger.get_all_entries()
        for i, entry in enumerate(entries):
            print(f"{i}: {entry['timestamp']} - {entry['event_type']}")
            
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
