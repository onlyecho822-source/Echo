"""Provenance tracking module."""

from datetime import datetime
from typing import Optional
from echo_engine.core.models import (
    Source,
    Fact,
    ProvenanceChain,
    ProvenanceNode,
)
from echo_engine.core.exceptions import ProvenanceError


class ProvenanceTracker:
    """
    Tracks the provenance (origin and transformation) of information.

    Builds chains that trace facts back to their original sources,
    documenting how information was derived and transformed.
    """

    def __init__(self, config: Optional[dict] = None):
        """Initialize the provenance tracker."""
        self.config = config or {}
        self.chains: dict[str, ProvenanceChain] = {}

    def build_chain(
        self,
        fact: Fact,
        sources: list[Source],
        name: str = "",
    ) -> ProvenanceChain:
        """
        Build a provenance chain for a fact.

        Args:
            fact: The fact to trace
            sources: Available sources
            name: Optional name for the chain

        Returns:
            A ProvenanceChain tracing the fact to its origins
        """
        chain = ProvenanceChain(
            name=name or f"Provenance: {fact.statement[:40]}...",
        )

        # Create node for the fact
        fact_node = ProvenanceNode(
            entity_id=fact.id,
            entity_type="fact",
            timestamp=fact.extracted_at,
            transformation="extracted",
        )

        # Find and link source nodes
        source_nodes = []
        for source_id in fact.source_ids:
            source = self._find_source(source_id, sources)
            if source:
                source_node = ProvenanceNode(
                    entity_id=source.id,
                    entity_type="source",
                    timestamp=source.timestamp or source.collected_at,
                    transformation="original",
                    metadata={
                        "source_name": source.name,
                        "source_type": source.source_type.value,
                    },
                )
                chain.add_node(source_node)
                source_nodes.append(source_node)

                if not chain.root_id:
                    chain.root_id = source_node.id

        # Link fact to sources
        fact_node.parent_ids = [n.id for n in source_nodes]
        chain.add_node(fact_node)

        self.chains[chain.id] = chain
        return chain

    def _find_source(self, source_id: str, sources: list[Source]) -> Optional[Source]:
        """Find a source by ID."""
        for source in sources:
            if source.id == source_id:
                return source
        return None

    def trace_origin(self, chain_id: str, entity_id: str) -> list[dict]:
        """
        Trace an entity back to its origin(s).

        Args:
            chain_id: The chain to search
            entity_id: The entity to trace

        Returns:
            List of steps from entity to origin
        """
        if chain_id not in self.chains:
            raise ProvenanceError(f"Chain not found: {chain_id}")

        chain = self.chains[chain_id]

        # Find the node
        target_node = None
        for node in chain.nodes.values():
            if node.entity_id == entity_id:
                target_node = node
                break

        if not target_node:
            raise ProvenanceError(f"Entity not found in chain: {entity_id}")

        # Trace path
        path = chain.trace_to_origin(target_node.id)

        return [
            {
                "step": i + 1,
                "entity_id": node.entity_id,
                "entity_type": node.entity_type,
                "transformation": node.transformation,
                "timestamp": node.timestamp.isoformat() if node.timestamp else None,
                "metadata": node.metadata,
            }
            for i, node in enumerate(path)
        ]

    def add_derivation(
        self,
        chain_id: str,
        derived_fact: Fact,
        source_facts: list[Fact],
        transformation: str,
    ) -> ProvenanceNode:
        """
        Add a derived fact to an existing chain.

        Args:
            chain_id: The chain to extend
            derived_fact: The newly derived fact
            source_facts: Facts this was derived from
            transformation: Description of the derivation

        Returns:
            The new ProvenanceNode
        """
        if chain_id not in self.chains:
            raise ProvenanceError(f"Chain not found: {chain_id}")

        chain = self.chains[chain_id]

        # Find parent nodes
        parent_ids = []
        for source_fact in source_facts:
            for node in chain.nodes.values():
                if node.entity_id == source_fact.id:
                    parent_ids.append(node.id)
                    break

        # Create new node
        new_node = ProvenanceNode(
            entity_id=derived_fact.id,
            entity_type="fact",
            timestamp=derived_fact.extracted_at,
            transformation=transformation,
            parent_ids=parent_ids,
        )

        chain.add_node(new_node)
        return new_node

    def get_lineage(self, chain_id: str, entity_id: str) -> dict:
        """
        Get the complete lineage of an entity.

        Args:
            chain_id: The chain to search
            entity_id: The entity to trace

        Returns:
            Lineage information including ancestors and descendants
        """
        if chain_id not in self.chains:
            raise ProvenanceError(f"Chain not found: {chain_id}")

        chain = self.chains[chain_id]

        # Find the node
        target_node = None
        for node in chain.nodes.values():
            if node.entity_id == entity_id:
                target_node = node
                break

        if not target_node:
            raise ProvenanceError(f"Entity not found in chain: {entity_id}")

        # Get ancestors
        ancestors = chain.get_ancestors(target_node.id)

        # Get descendants
        descendants = self._get_descendants(chain, target_node.id)

        return {
            "entity_id": entity_id,
            "entity_type": target_node.entity_type,
            "ancestors": [
                {
                    "entity_id": a.entity_id,
                    "entity_type": a.entity_type,
                    "transformation": a.transformation,
                }
                for a in ancestors
            ],
            "descendants": [
                {
                    "entity_id": d.entity_id,
                    "entity_type": d.entity_type,
                    "transformation": d.transformation,
                }
                for d in descendants
            ],
            "depth": len(ancestors),
        }

    def _get_descendants(
        self,
        chain: ProvenanceChain,
        node_id: str
    ) -> list[ProvenanceNode]:
        """Get all descendants of a node."""
        descendants = []

        for node in chain.nodes.values():
            if node_id in node.parent_ids:
                descendants.append(node)
                descendants.extend(self._get_descendants(chain, node.id))

        return descendants

    def merge_chains(
        self,
        chain_ids: list[str],
        name: str,
    ) -> ProvenanceChain:
        """
        Merge multiple provenance chains.

        Args:
            chain_ids: IDs of chains to merge
            name: Name for the merged chain

        Returns:
            The merged ProvenanceChain
        """
        merged = ProvenanceChain(
            name=name,
            metadata={"merged_from": chain_ids},
        )

        for chain_id in chain_ids:
            if chain_id not in self.chains:
                continue

            source_chain = self.chains[chain_id]

            # Copy nodes
            for node_id, node in source_chain.nodes.items():
                merged.add_node(ProvenanceNode(
                    id=node.id,
                    entity_id=node.entity_id,
                    entity_type=node.entity_type,
                    timestamp=node.timestamp,
                    transformation=node.transformation,
                    parent_ids=node.parent_ids.copy(),
                    metadata=node.metadata.copy(),
                ))

            # Use first chain's root
            if not merged.root_id and source_chain.root_id:
                merged.root_id = source_chain.root_id

        self.chains[merged.id] = merged
        return merged

    def export_chain(self, chain_id: str) -> dict:
        """
        Export a chain to a dictionary format.

        Args:
            chain_id: The chain to export

        Returns:
            Dictionary representation of the chain
        """
        if chain_id not in self.chains:
            raise ProvenanceError(f"Chain not found: {chain_id}")

        return self.chains[chain_id].to_dict()

    def get_chain_statistics(self, chain_id: str) -> dict:
        """
        Get statistics about a provenance chain.

        Args:
            chain_id: The chain to analyze

        Returns:
            Statistics dictionary
        """
        if chain_id not in self.chains:
            raise ProvenanceError(f"Chain not found: {chain_id}")

        chain = self.chains[chain_id]

        # Count by entity type
        type_counts = {}
        for node in chain.nodes.values():
            type_counts[node.entity_type] = type_counts.get(node.entity_type, 0) + 1

        # Calculate depth
        max_depth = 0
        for node in chain.nodes.values():
            depth = len(chain.get_ancestors(node.id))
            max_depth = max(max_depth, depth)

        # Count transformations
        transformation_counts = {}
        for node in chain.nodes.values():
            t = node.transformation
            transformation_counts[t] = transformation_counts.get(t, 0) + 1

        return {
            "chain_id": chain_id,
            "total_nodes": len(chain.nodes),
            "entity_types": type_counts,
            "max_depth": max_depth,
            "transformations": transformation_counts,
            "root_id": chain.root_id,
        }
