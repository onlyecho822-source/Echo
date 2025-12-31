# Echo Universe - Immutable Governance Ledger

## Constitutional Authority

This ledger is the **source of truth** for all automated governance actions within the Echo Universe. It implements a Merkle tree-based, cryptographically-chained append-only log that makes any tampering immediately detectable.

## Design Principles

1. **Append-Only**: Entries can never be modified or deleted
2. **Cryptographically Chained**: Each entry contains the SHA-256 hash of the previous entry
3. **Self-Verifying**: Chain integrity can be verified at any time
4. **Human-Readable**: JSONL format for transparency and auditability
5. **Immutable**: Any modification breaks the cryptographic chain

## Architecture

Each ledger entry contains:

- `timestamp`: ISO 8601 UTC timestamp
- `event_type`: Type of governance event (e.g., "coordination_audit", "pr_created")
- `data`: Event-specific data payload
- `previous_hash`: SHA-256 hash of the previous entry (links the chain)
- `entry_hash`: SHA-256 hash of the current entry (proves integrity)

The hash is computed over the canonical JSON representation of `{timestamp, event_type, data, previous_hash}`, ensuring that any change to these fields will produce a different hash and break the chain.

## Usage

### Initialize Ledger

```bash
python3 ledgers/automation/ledger.py init
```

Creates a new ledger with a genesis entry. Safe to run multiple times (idempotent).

### Append Entry

```bash
python3 ledgers/automation/ledger.py append "event_type" '{"key": "value"}'
```

Appends a new entry to the ledger. The entry is automatically chained to the previous entry.

### Verify Integrity

```bash
python3 ledgers/automation/ledger.py verify
```

Verifies the cryptographic integrity of the entire ledger. Returns exit code 0 if valid, 1 if tampering detected.

### Export Audit Report

```bash
python3 ledgers/automation/ledger.py export output.txt
```

Exports a human-readable audit report showing all entries and chain integrity status.

### List All Entries

```bash
python3 ledgers/automation/ledger.py list
```

Lists all entries in the ledger with timestamps and event types.

## Integration with Constitutional Automation

The coordination audit workflow (`.github/workflows/constitutional-coordination-audit.yml`) automatically appends entries to this ledger for all governance actions:

- **coordination_audit_initiated**: When a weekly audit begins
- **coordination_audit_completed**: When audit analysis is complete
- **pr_created**: When automation creates a pull request
- **pr_merged**: When a governance PR is merged
- **audit_failure**: When an audit detects issues

## Tampering Detection

The ledger is designed to make tampering **detectable, not preventable**. Any modification to a historical entry will:

1. Change the `entry_hash` of that entry
2. Break the chain linkage to subsequent entries
3. Cause `verify` to fail with a specific error message

This creates an **immutable audit trail** that can be independently verified by any party with access to the repository.

## Example: Testing Tampering Detection

```bash
# Create a backup
cp ledgers/automation/coordination_log.jsonl ledgers/automation/backup.jsonl

# Tamper with the ledger
sed -i 's/success/TAMPERED/g' ledgers/automation/coordination_log.jsonl

# Verify (will fail)
python3 ledgers/automation/ledger.py verify
# Output: ✗ Ledger integrity BROKEN - Entry 1 has invalid hash (tampering detected)

# Restore from backup
mv ledgers/automation/backup.jsonl ledgers/automation/coordination_log.jsonl
```

## Constitutional Significance

This ledger implements the **separation of powers** principle:

- **Automation** can append entries (executive action)
- **Humans** must ratify changes via PR review (legislative oversight)
- **Ledger** provides immutable record (judicial accountability)

Without this ledger, the constitutional governance system would rely on voluntary compliance and mutable records. With it, all governance actions are cryptographically verifiable and historically traceable.

## File Structure

```
ledgers/
├── README.md                           # This file
└── automation/
    ├── ledger.py                       # Ledger implementation
    ├── coordination_log.jsonl          # The ledger itself (append-only)
    └── audit_report.txt                # Human-readable audit report (generated)
```

## Security Considerations

1. **Not Encryption**: This ledger provides integrity verification, not confidentiality. All entries are readable.
2. **Git History**: The ledger file is committed to Git, providing an additional layer of historical verification.
3. **Deletion Detection**: If the entire ledger file is deleted, the absence is obvious. If entries are removed, the chain breaks.
4. **Replay Attacks**: Timestamps are included in the hash, making it difficult to replay old entries.

## Next Steps

- Integrate ledger with GitHub Actions workflow
- Add automated integrity checks on every PR
- Create visualization dashboard for ledger entries
- Implement ledger replication for redundancy
