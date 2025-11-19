# Aletheia Reality Decoding System

An auditable, operator-first system that collects sealed raw evidence, runs reproducible analyses, and produces verifiable, challengeable truth-packets.

## Mission

Create a defensible pipeline that turns raw artifacts and measurements into signed, reproducible evidence bundles and ranked hypotheses, with human-led governance, transparent methods, and measured risk controls.

## Core Components

### 1. Ingest + Sealing (`/Ingest`)

Seal artifacts with cryptographic hashes, signatures, and timestamps.

```powershell
# Seal an XRF spectral file
.\Aletheia\Ingest\Seal-Artifact.ps1 `
    -FilePath "data/sample.csv" `
    -FileType "XRF-CSV" `
    -Operator "Dr. Smith" `
    -CopyToVault
```

### 2. Methods Registry (`/Methods`)

Stores protocols, instrument configs, script hashes, and environment manifests for reproducibility.

- `spectra-analysis-v1` - XRF spectral analysis
- `radiocarbon-calibration-v1` - C14 date calibration
- `genomic-variant-calling-v1` - Variant calling pipeline

### 3. Orchestrator

Wires Echo Ethics Dimmer to all operations with appropriate prompts and review requirements.

```powershell
# Run analysis with current Echo mode
.\Aletheia\AletheiaOrchestrator.ps1 `
    -Operation "Analyze" `
    -ArtifactID "aletheia:xrfcsv:abc123..." `
    -Query "Determine elemental composition"

# View metrics
.\Aletheia\AletheiaOrchestrator.ps1 -ShowMetrics

# Check pending L2 reviews
.\Aletheia\AletheiaOrchestrator.ps1 -ShowPendingReviews
```

## Echo Ethics Integration

Operations adapt based on current Echo mode:

| Mode | Analysis Style | Review |
|------|---------------|--------|
| L5 Safe Harbor | Conservative, established methods | No |
| L4 Defensive | Threat-aware, validity concerns | No |
| L3 Investigative | Structural analysis, competing hypotheses | No |
| L2 Black Lens | Full hypothesis enumeration | **Required** |

**Critical**: All L2 outputs require Devil Lens human review before operational use.

## Manifest Schema

Every artifact is sealed with:

- `stableID` - Permanent identifier
- `contentHash` - SHA-256 of raw file
- `metadata` - Type, capture info, sensitivity
- `custody` - Chain of custody entries
- `consent` - Consent scope and status
- `signature` - Cryptographic signature
- `timestamp` - Trusted timestamp proof

See `/Schemas/ManifestSchema.json` for full specification.

## Directory Structure

```
Aletheia/
  Ingest/          # Sealing tools
  Vault/           # Encrypted storage
  Methods/         # Analysis protocols
  KnowledgeGraph/  # Entity relationships
  Schemas/         # JSON schemas + examples
  Logs/            # Operation logs + metrics
  Exports/         # Export bundles
```

## Key Metrics

- **Provenance Completeness** - Manifest fields present
- **Reproducibility Rate** - Analyses reproduced by validators
- **Challenge Resolution Time** - Median days to resolve
- **Mode Fidelity** - Outputs match selected Echo mode
- **Data Minimization Rate** - Minimal exports used

## Governance Roles

- **Custodian** - Store and seal artifacts
- **Validator** - Verify method reproducibility
- **Steward** - Protect community rights
- **Reviewer** - Domain expert review
- **Legal Observer** - Compliance oversight

## Next Steps (MVP)

1. [x] Manifest schema
2. [x] Ingest + sealing CLI
3. [ ] Encrypted vault with export bundles
4. [ ] Knowledge graph for one case study
5. [ ] Devil Lens review workflow UI
6. [ ] Validator reproduction report

---

*Aletheia: Stop being sold stories. Start acting on provable facts.*
