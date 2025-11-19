#!/usr/bin/env python3
"""
Aletheia Knowledge Graph
=========================
Stores entities and relationships for the Reality Decoding System.

Entity types: artifact, person, institution, event, test
Edge types: custody, claim, contradiction, derivation, jurisdiction, confidence

Author: Echo Nexus Omega
Version: 1.0.0
"""

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class EntityType(Enum):
    ARTIFACT = "artifact"
    PERSON = "person"
    INSTITUTION = "institution"
    EVENT = "event"
    TEST = "test"
    METHOD = "method"
    CLAIM = "claim"


class EdgeType(Enum):
    CUSTODY = "custody"
    CLAIM = "claim"
    CONTRADICTION = "contradiction"
    DERIVATION = "derivation"
    JURISDICTION = "jurisdiction"
    CONFIDENCE = "confidence"
    SUPPORTS = "supports"
    REFUTES = "refutes"
    RELATED = "related"


@dataclass
class Entity:
    """Node in the knowledge graph."""
    entity_id: str
    entity_type: str
    name: str
    properties: Dict[str, Any]
    created_at: str
    source_artifact_id: Optional[str]


@dataclass
class Edge:
    """Relationship in the knowledge graph."""
    edge_id: str
    edge_type: str
    source_id: str
    target_id: str
    properties: Dict[str, Any]
    confidence: float
    created_at: str
    evidence_ids: List[str]


@dataclass
class Claim:
    """A claim with evidence and confidence."""
    claim_id: str
    statement: str
    entity_ids: List[str]
    evidence_ids: List[str]
    confidence: float
    status: str  # "proposed", "supported", "contested", "refuted"
    created_at: str
    last_updated: str


class KnowledgeGraph:
    """
    Knowledge graph for Aletheia evidence and claims.

    Supports:
    - Entity and relationship storage
    - Claim tracking with evidence
    - Contradiction detection
    - Confidence scoring
    """

    def __init__(self, graph_path: str):
        self.graph_path = Path(graph_path)
        self.graph_path.mkdir(parents=True, exist_ok=True)

        self.entities_file = self.graph_path / "entities.json"
        self.edges_file = self.graph_path / "edges.json"
        self.claims_file = self.graph_path / "claims.json"

        self.entities: Dict[str, Entity] = {}
        self.edges: Dict[str, Edge] = {}
        self.claims: Dict[str, Claim] = {}

        self._load_graph()

    def _load_graph(self):
        """Load graph from disk."""
        if self.entities_file.exists():
            with open(self.entities_file) as f:
                data = json.load(f)
                self.entities = {k: Entity(**v) for k, v in data.items()}

        if self.edges_file.exists():
            with open(self.edges_file) as f:
                data = json.load(f)
                self.edges = {k: Edge(**v) for k, v in data.items()}

        if self.claims_file.exists():
            with open(self.claims_file) as f:
                data = json.load(f)
                self.claims = {k: Claim(**v) for k, v in data.items()}

    def _save_graph(self):
        """Save graph to disk."""
        with open(self.entities_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.entities.items()}, f, indent=2)

        with open(self.edges_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.edges.items()}, f, indent=2)

        with open(self.claims_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.claims.items()}, f, indent=2)

    def add_entity(
        self,
        entity_type: EntityType,
        name: str,
        properties: Dict[str, Any] = None,
        source_artifact_id: Optional[str] = None
    ) -> str:
        """
        Add an entity to the graph.

        Returns: entity_id
        """
        type_prefix = entity_type.value[:4].upper()
        entity_id = f"ENT-{type_prefix}-{secrets.token_hex(6).upper()}"

        entity = Entity(
            entity_id=entity_id,
            entity_type=entity_type.value,
            name=name,
            properties=properties or {},
            created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            source_artifact_id=source_artifact_id
        )

        self.entities[entity_id] = entity
        self._save_graph()

        return entity_id

    def add_edge(
        self,
        edge_type: EdgeType,
        source_id: str,
        target_id: str,
        properties: Dict[str, Any] = None,
        confidence: float = 1.0,
        evidence_ids: List[str] = None
    ) -> str:
        """
        Add a relationship to the graph.

        Returns: edge_id
        """
        if source_id not in self.entities:
            raise KeyError(f"Source entity not found: {source_id}")
        if target_id not in self.entities:
            raise KeyError(f"Target entity not found: {target_id}")

        edge_id = f"EDGE-{secrets.token_hex(8).upper()}"

        edge = Edge(
            edge_id=edge_id,
            edge_type=edge_type.value,
            source_id=source_id,
            target_id=target_id,
            properties=properties or {},
            confidence=confidence,
            created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            evidence_ids=evidence_ids or []
        )

        self.edges[edge_id] = edge
        self._save_graph()

        return edge_id

    def add_claim(
        self,
        statement: str,
        entity_ids: List[str],
        evidence_ids: List[str],
        confidence: float = 0.5
    ) -> str:
        """
        Add a claim to the graph.

        Returns: claim_id
        """
        claim_id = f"CLAIM-{secrets.token_hex(8).upper()}"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        claim = Claim(
            claim_id=claim_id,
            statement=statement,
            entity_ids=entity_ids,
            evidence_ids=evidence_ids,
            confidence=confidence,
            status="proposed",
            created_at=now,
            last_updated=now
        )

        self.claims[claim_id] = claim
        self._save_graph()

        return claim_id

    def update_claim_status(
        self,
        claim_id: str,
        status: str,
        confidence: Optional[float] = None
    ):
        """Update a claim's status and confidence."""
        if claim_id not in self.claims:
            raise KeyError(f"Claim not found: {claim_id}")

        claim = self.claims[claim_id]
        claim.status = status
        if confidence is not None:
            claim.confidence = confidence
        claim.last_updated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        self._save_graph()

    def find_contradictions(self, claim_id: str) -> List[str]:
        """Find claims that contradict a given claim."""
        contradicting = []

        for edge in self.edges.values():
            if edge.edge_type == EdgeType.CONTRADICTION.value:
                if edge.source_id == claim_id:
                    contradicting.append(edge.target_id)
                elif edge.target_id == claim_id:
                    contradicting.append(edge.source_id)

        return contradicting

    def get_entity_neighbors(
        self,
        entity_id: str,
        edge_types: List[EdgeType] = None
    ) -> List[Tuple[str, str, float]]:
        """
        Get neighboring entities.

        Returns: [(neighbor_id, edge_type, confidence), ...]
        """
        neighbors = []

        for edge in self.edges.values():
            if edge_types and EdgeType(edge.edge_type) not in edge_types:
                continue

            if edge.source_id == entity_id:
                neighbors.append((edge.target_id, edge.edge_type, edge.confidence))
            elif edge.target_id == entity_id:
                neighbors.append((edge.source_id, edge.edge_type, edge.confidence))

        return neighbors

    def get_evidence_chain(self, claim_id: str) -> Dict[str, Any]:
        """
        Get full evidence chain for a claim.

        Returns chain of artifacts and derivations supporting the claim.
        """
        if claim_id not in self.claims:
            raise KeyError(f"Claim not found: {claim_id}")

        claim = self.claims[claim_id]

        chain = {
            "claim_id": claim_id,
            "statement": claim.statement,
            "confidence": claim.confidence,
            "status": claim.status,
            "evidence": [],
            "entities": [],
            "supporting_edges": [],
            "contradictions": self.find_contradictions(claim_id)
        }

        # Gather evidence
        for artifact_id in claim.evidence_ids:
            chain["evidence"].append(artifact_id)

        # Gather entities
        for entity_id in claim.entity_ids:
            if entity_id in self.entities:
                chain["entities"].append(asdict(self.entities[entity_id]))

        # Find supporting edges
        for edge in self.edges.values():
            if edge.edge_type in [EdgeType.SUPPORTS.value, EdgeType.DERIVATION.value]:
                if any(eid in [edge.source_id, edge.target_id] for eid in claim.entity_ids):
                    chain["supporting_edges"].append(asdict(edge))

        return chain

    def export_subgraph(
        self,
        entity_ids: List[str],
        include_edges: bool = True,
        include_claims: bool = True
    ) -> Dict[str, Any]:
        """Export a subgraph containing specified entities."""
        subgraph = {
            "entities": {},
            "edges": {},
            "claims": {},
            "exported_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

        # Add entities
        for entity_id in entity_ids:
            if entity_id in self.entities:
                subgraph["entities"][entity_id] = asdict(self.entities[entity_id])

        # Add edges
        if include_edges:
            for edge_id, edge in self.edges.items():
                if edge.source_id in entity_ids or edge.target_id in entity_ids:
                    subgraph["edges"][edge_id] = asdict(edge)

        # Add claims
        if include_claims:
            for claim_id, claim in self.claims.items():
                if any(eid in entity_ids for eid in claim.entity_ids):
                    subgraph["claims"][claim_id] = asdict(claim)

        return subgraph

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        entity_counts = {}
        for entity in self.entities.values():
            entity_counts[entity.entity_type] = entity_counts.get(entity.entity_type, 0) + 1

        edge_counts = {}
        for edge in self.edges.values():
            edge_counts[edge.edge_type] = edge_counts.get(edge.edge_type, 0) + 1

        claim_status_counts = {}
        for claim in self.claims.values():
            claim_status_counts[claim.status] = claim_status_counts.get(claim.status, 0) + 1

        return {
            "total_entities": len(self.entities),
            "total_edges": len(self.edges),
            "total_claims": len(self.claims),
            "entities_by_type": entity_counts,
            "edges_by_type": edge_counts,
            "claims_by_status": claim_status_counts
        }


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Aletheia Knowledge Graph CLI")
    parser.add_argument("--graph", default="./graph_data")
    subparsers = parser.add_subparsers(dest="command")

    # Stats
    subparsers.add_parser("stats", help="Show graph statistics")

    # Add entity
    add_entity_parser = subparsers.add_parser("add-entity", help="Add entity")
    add_entity_parser.add_argument("--type", required=True, choices=[e.value for e in EntityType])
    add_entity_parser.add_argument("--name", required=True)

    # List
    list_parser = subparsers.add_parser("list", help="List entities")
    list_parser.add_argument("--type", choices=[e.value for e in EntityType])

    args = parser.parse_args()

    graph = KnowledgeGraph(args.graph)

    if args.command == "stats":
        stats = graph.get_statistics()
        print(json.dumps(stats, indent=2))

    elif args.command == "add-entity":
        entity_id = graph.add_entity(
            EntityType(args.type),
            args.name
        )
        print(f"Created entity: {entity_id}")

    elif args.command == "list":
        for entity in graph.entities.values():
            if args.type and entity.entity_type != args.type:
                continue
            print(f"{entity.entity_id}: {entity.name} [{entity.entity_type}]")

    else:
        parser.print_help()
