# Luminax

**Illumination and Insight Generation**

---

## Overview

Luminax is the insight generation engine for Echo Nexus. It illuminates patterns, connections, and emergent truths from the knowledge fabric, providing actionable intelligence.

## Features

- **Pattern Illumination**: Discover hidden patterns
- **Connection Mapping**: Find relationships
- **Insight Synthesis**: Generate actionable intelligence
- **Confidence Scoring**: Quantify certainty
- **Explanation Generation**: Understand why

## Installation

```python
from echo_nexus.products import Luminax, InsightQuery

luminax = Luminax()

# Generate insights
insights = luminax.illuminate(query="market trends")
```

## API

### Core Methods

```python
# Illuminate patterns
insights = luminax.illuminate(
    query="user behavior",
    depth=3,
    min_confidence=0.7
)

# Find connections
connections = luminax.connect(
    source="feature_a",
    target="outcome_b"
)

# Synthesize insight
synthesis = luminax.synthesize(insights)

# Explain insight
explanation = luminax.explain(insight_id)
```

### Filtering

```python
# Filter by confidence
high_confidence = insights.filter(confidence__gte=0.9)

# Filter by type
patterns = insights.filter(type="pattern")

# Filter by domain
domain_insights = insights.filter(domain="security")
```

## Insight Structure

```python
{
    "id": "ins_8a7b6c5d",
    "type": "pattern",
    "content": "User engagement peaks after feature announcement",
    "confidence": 0.87,
    "evidence": ["cap_1", "cap_2", "cap_3"],
    "connections": [
        {"from": "feature_x", "to": "engagement", "strength": 0.82}
    ],
    "explanation": "Based on temporal correlation and user feedback...",
    "generated_at": "2025-01-15T10:30:00Z"
}
```

## Architecture

```
┌─────────────────────────────────────┐
│            Luminax                  │
├─────────────────────────────────────┤
│  ┌─────────────────────────────┐    │
│  │    Query Processor          │    │
│  └──────────────┬──────────────┘    │
│                 │                   │
│  ┌──────────────▼──────────────┐    │
│  │    Pattern Detector         │    │
│  └──────────────┬──────────────┘    │
│                 │                   │
│  ┌──────────────▼──────────────┐    │
│  │    Connection Mapper        │    │
│  └──────────────┬──────────────┘    │
│                 │                   │
│  ┌──────────────▼──────────────┐    │
│  │    Insight Synthesizer      │    │
│  └──────────────┬──────────────┘    │
│                 │                   │
│  ┌──────────────▼──────────────┐    │
│  │    Explanation Generator    │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_depth` | int | 5 | Maximum exploration depth |
| `min_confidence` | float | 0.5 | Minimum confidence threshold |
| `max_insights` | int | 100 | Maximum insights per query |
| `explanation_detail` | str | "medium" | low, medium, high |

---

*∇θ — patterns illuminated, insights crystallized.*
