# EchoMap

**Spatial-Temporal Knowledge Mapping**

---

## Overview

EchoMap provides spatial-temporal visualization and navigation of the Echo Nexus knowledge fabric. It maps concepts, relationships, and evolution across both space and time.

## Features

- **Concept Mapping**: Visualize knowledge structures
- **Temporal Navigation**: Explore knowledge evolution
- **Relationship Graphs**: Map connections
- **Cluster Detection**: Find knowledge clusters
- **Path Finding**: Navigate between concepts

## Installation

```python
from echo_nexus.products import EchoMap, MapView

echomap = EchoMap()

# Create a map view
view = echomap.create_view(
    center="concept_a",
    radius=3,
    include_temporal=True
)
```

## API

### Core Methods

```python
# Create map view
view = echomap.create_view(center, radius)

# Navigate to concept
echomap.navigate_to(concept_id)

# Find path between concepts
path = echomap.find_path(source, target)

# Detect clusters
clusters = echomap.detect_clusters(min_size=5)

# Get temporal evolution
timeline = echomap.timeline(concept_id, start, end)
```

### Visualization

```python
# Export to various formats
view.export("graph.json")  # JSON graph
view.export("map.svg")     # SVG visualization
view.export("embed.png")   # 2D embedding

# Interactive view
echomap.interactive(port=8080)
```

## Map Structure

```python
{
    "nodes": [
        {
            "id": "concept_a",
            "label": "Machine Learning",
            "type": "concept",
            "position": {"x": 0.5, "y": 0.3},
            "metadata": {"capsules": 42}
        }
    ],
    "edges": [
        {
            "source": "concept_a",
            "target": "concept_b",
            "type": "related_to",
            "weight": 0.8,
            "temporal": {"start": "2024-01", "end": "2025-01"}
        }
    ],
    "clusters": [
        {
            "id": "cluster_1",
            "nodes": ["concept_a", "concept_b"],
            "centroid": {"x": 0.4, "y": 0.5}
        }
    ]
}
```

## Architecture

```
┌────────────────────────────────────┐
│           EchoMap                  │
├────────────────────────────────────┤
│  ┌──────────────────────────────┐  │
│  │    Graph Engine              │  │
│  │  - Node/edge management      │  │
│  │  - Graph algorithms          │  │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  ┌──────────────▼───────────────┐  │
│  │    Spatial Layout            │  │
│  │  - Force-directed            │  │
│  │  - Hierarchical              │  │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  ┌──────────────▼───────────────┐  │
│  │    Temporal Engine           │  │
│  │  - Timeline generation       │  │
│  │  - Evolution tracking        │  │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  ┌──────────────▼───────────────┐  │
│  │    Visualization Renderer    │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
```

## CLI Usage

```bash
# Generate map from concept
echo-map generate --center "ai" --radius 5 --output map.json

# Find path
echo-map path --from "ml" --to "deployment"

# Detect clusters
echo-map clusters --min-size 3 --algorithm louvain

# Launch interactive viewer
echo-map serve --port 8080
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `layout_algorithm` | str | "force" | force, hierarchical, circular |
| `temporal_resolution` | str | "day" | hour, day, week, month |
| `max_nodes` | int | 1000 | Maximum nodes in view |
| `edge_threshold` | float | 0.1 | Minimum edge weight |

---

*∇θ — knowledge mapped, paths illuminated.*
