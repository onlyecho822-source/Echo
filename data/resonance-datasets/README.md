# Resonance Datasets

This directory contains datasets for MultiReson Calculus verification and harmonic analysis.

## Structure

```
resonance-datasets/
├── calibration/          # Baseline calibration data
├── harmonics/            # Harmonic frequency analysis
├── emergence/            # Emergence pattern recordings
├── validation/           # Test validation sets
└── manifests/           # Dataset manifests and checksums
```

## Dataset Format

All datasets follow the Echo Resonance Data Format (ERDF):

```json
{
  "meta": {
    "version": "1.0",
    "created": "ISO-8601 timestamp",
    "author": "Creator name",
    "checksum": "SHA-256 hash"
  },
  "parameters": {
    "sample_rate": 1000,
    "duration_ms": 10000,
    "channels": 6
  },
  "data": [
    // Array of resonance measurements
  ]
}
```

## Available Datasets

### Calibration Sets
- `baseline_6agent.json` - 6-agent swarm baseline
- `single_agent_reference.json` - Single agent reference patterns

### Harmonic Analysis
- `percussion_harmonic_base.json` - PHB fundamental frequencies
- `multistate_transitions.json` - State transition recordings

### Emergence Patterns
- `loop_convergence_200.json` - 200-loop convergence data
- `drift_stabilization.json` - Drift patterns around loop 97

## Usage

```python
from echo.data import ResonanceDataset

# Load dataset
ds = ResonanceDataset.load("calibration/baseline_6agent.json")

# Analyze
coherence = ds.compute_coherence()
resonance = ds.compute_resonance_sync()
```

## Contributing

When adding new datasets:
1. Follow ERDF format
2. Include comprehensive metadata
3. Generate SHA-256 checksum
4. Add entry to manifest
5. Document in this README

## Provenance

All datasets include dual-hash verification (BLAKE3 + SHA-256) for integrity.
