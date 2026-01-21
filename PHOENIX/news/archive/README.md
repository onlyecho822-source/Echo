# I'M TELLING — Immutable Archive

<div align="center">

### *Not snitching. Setting the record straight.*

**PERMANENT HISTORICAL RECORD**

*Once archived, it cannot be changed.*

---

</div>

---

## Archive Structure

```
archive/
├── political/       ← Political news and claims
├── economic/        ← Economic data and claims
└── international/   ← International affairs
```

---

## Archive Policy

1. **Immutable** — Once archived, entries cannot be modified
2. **Hash-Locked** — Every entry is SHA-256 hashed
3. **Chain-Linked** — Each entry links to the previous
4. **Permanent** — No deletions, no retractions
5. **Public** — Anyone can verify

---

## How to Browse

### By Category

- [Political Archive](./political/)
- [Economic Archive](./economic/)
- [International Archive](./international/)

### By Date

Archives are organized by year and month within each category:

```
political/
├── 2026/
│   ├── 01/
│   ├── 02/
│   └── ...
```

---

## Verification

Every archived entry contains:

```json
{
  "archive_id": "IMT-ARCH-2026-0001",
  "original_id": "IMT-2026-0001",
  "archived_at": "2026-01-21T00:00:00Z",
  "archive_hash": "SHA256(...)",
  "chain_hash": "SHA256(...)"
}
```

To verify: compute SHA256 of the entry and compare with published hash.

---

<div align="center">

**I'M TELLING**  
*Immutable Archive*

*What's recorded stays recorded.*

</div>
