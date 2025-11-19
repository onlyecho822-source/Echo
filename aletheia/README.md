# Aletheia - Reality Decoding System

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()
[![Echo Nexus](https://img.shields.io/badge/Echo-Nexus%20Omega-purple.svg)]()

> An auditable, operator-first Reality Decoding System that collects sealed raw evidence, runs reproducible analyses, and produces verifiable, challengeable truth-packets.

**Author:** Echo Nexus Omega
**Operator:** Nathan Poinsette

---

## Mission

Build Aletheia: an auditable, operator-first Reality Decoding System that collects sealed raw evidence, runs reproducible analyses across genetics, materials, and texts, and produces verifiable, challengeable truth-packets—so societies can stop being sold stories and start acting on provable facts.

---

## Three Mission Pillars

1. **Capture with integrity** — Ingest raw files and immediately seal each item with content hash, manifest, signature, and trusted timestamp.

2. **Verify with reproducibility** — Run analyses only on copies; record full method manifests; produce derivation graphs that let a third party reproduce results end-to-end.

3. **Expose with accountability** — Publish evidence bundles, ranked hypotheses, and provenance graphs; support structured challenges, reanalysis, and reversible corrections.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      ALETHEIA SYSTEM                        │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│   INGEST    │    VAULT    │   ANALYSIS  │    DASHBOARD      │
│   + SEAL    │  (Encrypted)│   PIPELINES │   + CHALLENGES    │
├─────────────┼─────────────┼─────────────┼───────────────────┤
│ CLI Tool    │ AES-256-GCM │ Spectral    │ Knowledge Graph   │
│ Manifests   │ Export      │ Radiocarbon │ Evidence Chains   │
│ Dual-Hash   │ Bundles     │ Genomic     │ Devil Lens Review │
└─────────────┴─────────────┴─────────────┴───────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  CONSENT LEDGER   │
                    │  METHODS REGISTRY │
                    └───────────────────┘
```

---

## Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

Required packages:
- Python 3.9+
- cryptography
- blake3 (optional, falls back to blake2s)

### 1. Ingest and Seal an Artifact

```bash
python cli/ingest.py \
  --file sample_data.vcf.gz \
  --type VCF \
  --output manifest.json
```

### 2. Store in Encrypted Vault

```bash
python vault/encrypted_vault.py store \
  --file sample_data.vcf.gz \
  --manifest manifest.json \
  --vault ./vault_data
```

### 3. Run Re-analysis Pipeline

```bash
# Generate pipeline spec
python pipelines/reanalysis_spec.py spec --type radiocarbon --output pipeline.json

# Run reproducibility checklist
python pipelines/reanalysis_spec.py check --spec pipeline.json --output report.json
```

### 4. Set Echo Ethics Mode

```bash
# Check mode configuration
python prompts/echo_ethics_dimmer.py info --mode L3

# Generate system prompt for mode
python prompts/echo_ethics_dimmer.py prompt --mode L3 --output prompt.txt
```

---

## Components

### Deliverable A: Manifest Schema

Location: `schemas/`

- `manifest_schema.json` - JSON Schema for evidence manifests
- `samples/` - Example manifests for different artifact types
  - `manifest_genomic.json` - VCF/FASTQ genetic data
  - `manifest_spectra.json` - XRF spectral analysis
  - `manifest_radiocarbon.json` - C14 dating measurements

### Deliverable B: CLI Ingest + Sealing

Location: `cli/ingest.py`

Features:
- SHA-256 + BLAKE3 dual-hash provenance
- Ed25519 digital signatures
- OpenTimestamps integration (placeholder)
- Automatic manifest generation

### Deliverable C: Re-analysis Pipeline Spec

Location: `pipelines/reanalysis_spec.py`

Includes:
- XRF spectral analysis pipeline
- Radiocarbon calibration pipeline
- Environment capture and hashing
- Reproducibility checklist with 12 validation checks
- Derivation graph generation

### Deliverable D: Echo Ethics Dimmer

Location: `prompts/echo_ethics_dimmer.py`

Modes:
- **L5 Safe** - Conservative, maximum restrictions
- **L4 Defensive** - Threat modeling only
- **L3 Investigative** - Structural analysis with hypotheses
- **L2 Black Lens** - Full enumeration, Devil Lens review required

---

## Supporting Infrastructure

### Encrypted Vault

Location: `vault/encrypted_vault.py`

- AES-256-GCM encryption at rest
- Per-artifact key derivation
- Verifiable export bundles
- Audit logging

### Consent Ledger

Location: `ledger/consent_ledger.py`

- Append-only consent records
- Custody chain tracking
- Revocation support
- Export-time minimization enforcement

### Methods Registry

Location: `registry/methods_registry.py`

- Protocol versioning
- Script hash tracking
- Environment manifests
- Instrument configurations

### Knowledge Graph

Location: `graph/knowledge_graph.py`

- Entity types: artifact, person, institution, event, test
- Edge types: custody, claim, contradiction, derivation
- Claim tracking with evidence
- Contradiction detection

---

## Configuration

Main configuration: `config/echo_ethics_config.yaml`

```yaml
default_mode: L5_Safe

security:
  encryption:
    algorithm: AES-256-GCM
  signing:
    algorithm: Ed25519

privacy:
  minimization:
    enabled: true
```

---

## Governance Model

### Roles

| Role | Responsibility |
|------|----------------|
| Custodian | Store/seal artifacts |
| Validator | Verify reproducibility |
| Steward | Protect community rights |
| Reviewer | Domain expert review |
| Legal Observer | Compliance monitoring |

### Review Paths

- **Automated** - Rule-based validation
- **Human Optional** - Expert review available
- **Human Required** - Must be reviewed
- **Devil Lens** - Adversarial review for L2 outputs

---

## Key Metrics

| Metric | Target |
|--------|--------|
| Provenance Completeness | ≥95% |
| Reproducibility Rate | ≥90% |
| Challenge Resolution Time | <72 hours |
| Mode Fidelity | ≥95% |
| Data Minimization Rate | ≥80% |

---

## Security

- **Encryption**: AES-256-GCM for data at rest
- **Signing**: Ed25519 signatures on all manifests
- **Hashing**: SHA-256 + BLAKE3 dual-hash provenance
- **Timestamps**: OpenTimestamps or RFC3161 TSA
- **Key Management**: PBKDF2-SHA256 key derivation

---

## File Structure

```
aletheia/
├── README.md
├── schemas/
│   ├── manifest_schema.json
│   └── samples/
│       ├── manifest_genomic.json
│       ├── manifest_spectra.json
│       └── manifest_radiocarbon.json
├── cli/
│   └── ingest.py
├── pipelines/
│   └── reanalysis_spec.py
├── prompts/
│   └── echo_ethics_dimmer.py
├── vault/
│   └── encrypted_vault.py
├── ledger/
│   └── consent_ledger.py
├── registry/
│   └── methods_registry.py
├── graph/
│   └── knowledge_graph.py
├── config/
│   └── echo_ethics_config.yaml
├── docs/
└── tests/
```

---

## API Reference

### Ingest CLI

```bash
python cli/ingest.py --file <path> --type <type> --output <manifest>
```

### Vault CLI

```bash
python vault/encrypted_vault.py store --file <path> --manifest <manifest>
python vault/encrypted_vault.py list
python vault/encrypted_vault.py verify --id <artifact_id>
```

### Pipeline CLI

```bash
python pipelines/reanalysis_spec.py spec --type <xrf|radiocarbon> --output <spec>
python pipelines/reanalysis_spec.py check --spec <spec> --output <report>
python pipelines/reanalysis_spec.py env --output <env.json>
```

### Echo Dimmer CLI

```bash
python prompts/echo_ethics_dimmer.py info --mode <L5|L4|L3|L2>
python prompts/echo_ethics_dimmer.py prompt --mode <mode> --output <file>
python prompts/echo_ethics_dimmer.py validate --mode <mode> --operation <op>
```

---

## Roadmap

### Phase 1 (Current) - MVP
- [x] Manifest schema and samples
- [x] CLI ingest + sealing tool
- [x] Re-analysis pipeline specs
- [x] Echo Ethics Dimmer
- [x] Encrypted vault
- [x] Consent ledger
- [x] Methods registry
- [x] Knowledge graph

### Phase 2 - Enhanced
- [ ] Vector embeddings for semantic search
- [ ] PostgreSQL/Neo4j backend
- [ ] FastAPI service layer
- [ ] Web dashboard
- [ ] Blockchain anchoring

### Phase 3 - Production
- [ ] Multi-tenant deployment
- [ ] HSM key management
- [ ] Real-time monitoring
- [ ] International compliance
- [ ] Public API

---

## License

Proprietary - Echo Nexus Omega

---

## Author

**Nathan Poinsette**
Founder • Archivist • Systems Engineer
Echo Nexus Omega

---

∇θ — Truth preserved, provenance sealed.
