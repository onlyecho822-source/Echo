"""Data models for the Echo Reverse Engineering Engine."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import hashlib
import uuid


class SourceType(Enum):
    """Types of information sources."""
    TEXT = "text"
    DOCUMENT = "document"
    WEB = "web"
    DATABASE = "database"
    API = "api"
    FILE = "file"
    TESTIMONY = "testimony"
    MEDIA = "media"
    UNKNOWN = "unknown"


class FactStatus(Enum):
    """Validation status of a fact."""
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    DISPUTED = "disputed"
    REFUTED = "refuted"
    PARTIALLY_VERIFIED = "partially_verified"


class ConnectionType(Enum):
    """Types of connections between entities."""
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    REFERENCES = "references"
    DERIVES_FROM = "derives_from"
    RELATED_TO = "related_to"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    CORROBORATES = "corroborates"


class ConfidenceLevel(Enum):
    """Confidence levels for analysis results."""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


@dataclass
class Source:
    """Represents an information source."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    source_type: SourceType = SourceType.UNKNOWN
    content: str = ""
    url: Optional[str] = None
    filepath: Optional[str] = None
    author: Optional[str] = None
    timestamp: Optional[datetime] = None
    collected_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    content_hash: str = ""

    def __post_init__(self):
        if self.content and not self.content_hash:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()

    def to_dict(self) -> dict:
        """Convert source to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "source_type": self.source_type.value,
            "content": self.content,
            "url": self.url,
            "filepath": self.filepath,
            "author": self.author,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "collected_at": self.collected_at.isoformat(),
            "metadata": self.metadata,
            "content_hash": self.content_hash,
        }


@dataclass
class Fact:
    """Represents an extracted fact."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    statement: str = ""
    source_ids: list[str] = field(default_factory=list)
    status: FactStatus = FactStatus.UNVERIFIED
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    extracted_at: datetime = field(default_factory=datetime.now)
    verified_at: Optional[datetime] = None
    context: str = ""
    entities: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert fact to dictionary."""
        return {
            "id": self.id,
            "statement": self.statement,
            "source_ids": self.source_ids,
            "status": self.status.value,
            "confidence": self.confidence.value,
            "extracted_at": self.extracted_at.isoformat(),
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "context": self.context,
            "entities": self.entities,
            "keywords": self.keywords,
            "supporting_evidence": self.supporting_evidence,
            "contradicting_evidence": self.contradicting_evidence,
            "metadata": self.metadata,
        }


@dataclass
class TimelineEvent:
    """Represents an event in a timeline."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    timestamp: Optional[datetime] = None
    timestamp_precision: str = "exact"  # exact, day, month, year, approximate
    source_ids: list[str] = field(default_factory=list)
    fact_ids: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    location: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "timestamp_precision": self.timestamp_precision,
            "source_ids": self.source_ids,
            "fact_ids": self.fact_ids,
            "entities": self.entities,
            "location": self.location,
            "confidence": self.confidence.value,
            "metadata": self.metadata,
        }


@dataclass
class Timeline:
    """Represents a reconstructed timeline of events."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    events: list[TimelineEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)

    def add_event(self, event: TimelineEvent):
        """Add an event and maintain chronological order."""
        self.events.append(event)
        self.events.sort(key=lambda e: e.timestamp or datetime.min)
        self._update_date_range()

    def _update_date_range(self):
        """Update start and end dates based on events."""
        dated_events = [e for e in self.events if e.timestamp]
        if dated_events:
            self.start_date = min(e.timestamp for e in dated_events)
            self.end_date = max(e.timestamp for e in dated_events)

    def to_dict(self) -> dict:
        """Convert timeline to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "events": [e.to_dict() for e in self.events],
            "created_at": self.created_at.isoformat(),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "metadata": self.metadata,
        }


@dataclass
class Connection:
    """Represents a connection between two entities."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_entity_id: str = ""
    target_entity_id: str = ""
    connection_type: ConnectionType = ConnectionType.RELATED_TO
    strength: float = 0.5  # 0.0 to 1.0
    description: str = ""
    evidence_ids: list[str] = field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert connection to dictionary."""
        return {
            "id": self.id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "connection_type": self.connection_type.value,
            "strength": self.strength,
            "description": self.description,
            "evidence_ids": self.evidence_ids,
            "confidence": self.confidence.value,
            "metadata": self.metadata,
        }


@dataclass
class ProvenanceNode:
    """A node in a provenance chain."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: str = ""
    entity_type: str = ""  # source, fact, claim
    timestamp: Optional[datetime] = None
    transformation: str = ""  # How it was transformed/derived
    parent_ids: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert node to dictionary."""
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "transformation": self.transformation,
            "parent_ids": self.parent_ids,
            "metadata": self.metadata,
        }


@dataclass
class ProvenanceChain:
    """Tracks the origin and transformation chain of information."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    root_id: str = ""  # The original source
    nodes: dict[str, ProvenanceNode] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

    def add_node(self, node: ProvenanceNode):
        """Add a node to the chain."""
        self.nodes[node.id] = node

    def get_ancestors(self, node_id: str) -> list[ProvenanceNode]:
        """Get all ancestors of a node."""
        ancestors = []
        node = self.nodes.get(node_id)
        if not node:
            return ancestors

        for parent_id in node.parent_ids:
            if parent_id in self.nodes:
                parent = self.nodes[parent_id]
                ancestors.append(parent)
                ancestors.extend(self.get_ancestors(parent_id))

        return ancestors

    def trace_to_origin(self, node_id: str) -> list[ProvenanceNode]:
        """Trace a node back to its origin(s)."""
        path = []
        visited = set()

        def trace(nid):
            if nid in visited or nid not in self.nodes:
                return
            visited.add(nid)
            node = self.nodes[nid]
            path.append(node)
            for parent_id in node.parent_ids:
                trace(parent_id)

        trace(node_id)
        return path

    def to_dict(self) -> dict:
        """Convert chain to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "root_id": self.root_id,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class Investigation:
    """Represents a complete investigation."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    query: str = ""
    sources: list[Source] = field(default_factory=list)
    facts: list[Fact] = field(default_factory=list)
    timelines: list[Timeline] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)
    provenance_chains: list[ProvenanceChain] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: str = "in_progress"  # in_progress, completed, archived
    conclusions: list[str] = field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    metadata: dict = field(default_factory=dict)

    def add_source(self, source: Source):
        """Add a source to the investigation."""
        self.sources.append(source)
        self.updated_at = datetime.now()

    def add_fact(self, fact: Fact):
        """Add a fact to the investigation."""
        self.facts.append(fact)
        self.updated_at = datetime.now()

    def get_source_by_id(self, source_id: str) -> Optional[Source]:
        """Get a source by its ID."""
        for source in self.sources:
            if source.id == source_id:
                return source
        return None

    def get_fact_by_id(self, fact_id: str) -> Optional[Fact]:
        """Get a fact by its ID."""
        for fact in self.facts:
            if fact.id == fact_id:
                return fact
        return None

    def get_verified_facts(self) -> list[Fact]:
        """Get all verified facts."""
        return [f for f in self.facts if f.status == FactStatus.VERIFIED]

    def get_disputed_facts(self) -> list[Fact]:
        """Get all disputed facts."""
        return [f for f in self.facts if f.status == FactStatus.DISPUTED]

    def to_dict(self) -> dict:
        """Convert investigation to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "query": self.query,
            "sources": [s.to_dict() for s in self.sources],
            "facts": [f.to_dict() for f in self.facts],
            "timelines": [t.to_dict() for t in self.timelines],
            "connections": [c.to_dict() for c in self.connections],
            "provenance_chains": [p.to_dict() for p in self.provenance_chains],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status,
            "conclusions": self.conclusions,
            "confidence": self.confidence.value,
            "metadata": self.metadata,
        }
