"""
Aletheia Truth Verification Engine - Core Data Models

Defines the fundamental data structures for artifacts, evidence,
narratives, and truth verification across multiple domains.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class EvidenceType(Enum):
    """Categories of evidence the system can process."""
    GENETIC = "genetic"
    MATERIAL = "material"
    LINGUISTIC = "linguistic"
    SYMBOLIC = "symbolic"
    ARCHAEOLOGICAL = "archaeological"
    DOCUMENTARY = "documentary"
    ORAL_TRADITION = "oral_tradition"
    ASTRONOMICAL = "astronomical"
    GEOLOGICAL = "geological"
    ARTISTIC = "artistic"


class ConfidenceLevel(Enum):
    """Confidence levels for truth assertions."""
    SPECULATIVE = 0.2
    LOW = 0.4
    MODERATE = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


class NarrativeStatus(Enum):
    """Status of a historical narrative."""
    OFFICIAL = "official"
    SUPPRESSED = "suppressed"
    CONTESTED = "contested"
    RECONSTRUCTED = "reconstructed"
    VERIFIED = "verified"


@dataclass
class GeoLocation:
    """Geographic location with uncertainty."""
    latitude: float
    longitude: float
    name: str
    region: str
    uncertainty_km: float = 0.0

    def distance_to(self, other: 'GeoLocation') -> float:
        """Calculate approximate distance to another location in km."""
        from math import radians, sin, cos, sqrt, atan2
        R = 6371  # Earth's radius in km

        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c


@dataclass
class TimePeriod:
    """A time period with uncertainty ranges."""
    start_year: int
    end_year: int
    calendar_system: str = "CE"
    uncertainty_years: int = 0

    def overlaps(self, other: 'TimePeriod') -> bool:
        """Check if two time periods overlap."""
        return not (self.end_year < other.start_year or
                   other.end_year < self.start_year)

    def contains_year(self, year: int) -> bool:
        """Check if a year falls within this period."""
        return self.start_year <= year <= self.end_year


@dataclass
class Symbol:
    """A symbolic element that can be tracked across cultures."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    visual_pattern: str = ""  # Description or pattern identifier
    cultures: list[str] = field(default_factory=list)
    meanings: dict[str, str] = field(default_factory=dict)  # culture -> meaning
    time_periods: list[TimePeriod] = field(default_factory=list)
    related_symbols: list[str] = field(default_factory=list)
    astronomical_correlation: Optional[str] = None

    def shared_meaning_with(self, other: 'Symbol') -> float:
        """Calculate semantic similarity with another symbol."""
        if not self.meanings or not other.meanings:
            return 0.0

        shared_cultures = set(self.meanings.keys()) & set(other.meanings.keys())
        if not shared_cultures:
            return 0.0

        # Simple word overlap for meaning similarity
        similarities = []
        for culture in shared_cultures:
            words1 = set(self.meanings[culture].lower().split())
            words2 = set(other.meanings[culture].lower().split())
            if words1 and words2:
                overlap = len(words1 & words2) / len(words1 | words2)
                similarities.append(overlap)

        return sum(similarities) / len(similarities) if similarities else 0.0


@dataclass
class MaterialComposition:
    """Material analysis data for an artifact."""
    primary_material: str
    secondary_materials: list[str] = field(default_factory=list)
    trace_elements: dict[str, float] = field(default_factory=dict)
    isotope_ratios: dict[str, float] = field(default_factory=dict)
    probable_origin: Optional[GeoLocation] = None
    origin_confidence: float = 0.0
    analysis_method: str = ""
    analysis_date: Optional[datetime] = None


@dataclass
class GeneticMarker:
    """Genetic data for tracing origins and migrations."""
    haplogroup: str
    snp_markers: list[str] = field(default_factory=list)
    population_frequencies: dict[str, float] = field(default_factory=dict)
    migration_path: list[GeoLocation] = field(default_factory=list)
    estimated_age_years: int = 0
    confidence: float = 0.0


@dataclass
class Evidence:
    """A piece of evidence supporting or contradicting a narrative."""
    id: str = field(default_factory=lambda: str(uuid4()))
    evidence_type: EvidenceType = EvidenceType.DOCUMENTARY
    description: str = ""
    source: str = ""
    source_reliability: float = 0.5
    date_recorded: Optional[datetime] = None
    time_period: Optional[TimePeriod] = None
    location: Optional[GeoLocation] = None
    content: str = ""

    # Type-specific data
    material_data: Optional[MaterialComposition] = None
    genetic_data: Optional[GeneticMarker] = None
    symbols: list[Symbol] = field(default_factory=list)

    # Verification status
    verified: bool = False
    verification_method: str = ""
    confidence_score: float = 0.0

    # Provenance
    chain_of_custody: list[dict] = field(default_factory=list)
    potential_biases: list[str] = field(default_factory=list)


@dataclass
class Artifact:
    """A physical or textual artifact under analysis."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    artifact_type: str = ""  # manuscript, sculpture, painting, etc.

    # Origin information
    claimed_origin: Optional[GeoLocation] = None
    true_origin: Optional[GeoLocation] = None
    origin_confidence: float = 0.0

    # Temporal information
    claimed_date: Optional[TimePeriod] = None
    true_date: Optional[TimePeriod] = None
    date_confidence: float = 0.0

    # Current status
    current_location: Optional[GeoLocation] = None
    current_holder: str = ""
    acquisition_method: str = ""

    # Analysis data
    material_composition: Optional[MaterialComposition] = None
    symbols: list[Symbol] = field(default_factory=list)
    inscriptions: list[str] = field(default_factory=list)
    languages_present: list[str] = field(default_factory=list)

    # Evidence chain
    evidence: list[Evidence] = field(default_factory=list)
    provenance_gaps: list[TimePeriod] = field(default_factory=list)

    # Cultural significance
    cultural_context: dict[str, str] = field(default_factory=dict)
    suppressed_meanings: list[str] = field(default_factory=list)


@dataclass
class HistoricalEvent:
    """A historical event that can be verified or contested."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    time_period: Optional[TimePeriod] = None
    location: Optional[GeoLocation] = None

    # Participants and cultures involved
    participants: list[str] = field(default_factory=list)
    cultures_affected: list[str] = field(default_factory=list)

    # Evidence
    supporting_evidence: list[Evidence] = field(default_factory=list)
    contradicting_evidence: list[Evidence] = field(default_factory=list)

    # Narrative status
    official_narrative: str = ""
    reconstructed_narrative: str = ""
    narrative_status: NarrativeStatus = NarrativeStatus.OFFICIAL

    # Impact tracking
    knowledge_transfers: list[str] = field(default_factory=list)
    artifacts_moved: list[str] = field(default_factory=list)
    narratives_suppressed: list[str] = field(default_factory=list)


@dataclass
class Narrative:
    """A historical narrative that can be verified, contested, or corrected."""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    status: NarrativeStatus = NarrativeStatus.OFFICIAL

    # Source tracking
    primary_sources: list[Evidence] = field(default_factory=list)
    secondary_sources: list[Evidence] = field(default_factory=list)

    # Related entities
    artifacts: list[Artifact] = field(default_factory=list)
    events: list[HistoricalEvent] = field(default_factory=list)
    cultures: list[str] = field(default_factory=list)

    # Verification
    truth_score: float = 0.0
    confidence_score: float = 0.0
    discrepancies: list[str] = field(default_factory=list)

    # Bias analysis
    beneficiaries: list[str] = field(default_factory=list)
    suppressed_voices: list[str] = field(default_factory=list)
    control_mechanisms: list[str] = field(default_factory=list)

    # Correction
    corrected_narrative: str = ""
    correction_evidence: list[Evidence] = field(default_factory=list)
    questions_raised: list[str] = field(default_factory=list)


@dataclass
class TruthAssertion:
    """A truth claim with supporting evidence and confidence scoring."""
    id: str = field(default_factory=lambda: str(uuid4()))
    assertion: str = ""
    domain: str = ""  # historical, scientific, metaphysical

    # Evidence basis
    supporting_evidence: list[Evidence] = field(default_factory=list)
    contradicting_evidence: list[Evidence] = field(default_factory=list)

    # Scoring
    truth_confidence: float = 0.0
    evidence_strength: float = 0.0
    source_reliability: float = 0.0
    cross_domain_correlation: float = 0.0

    # Context
    paradigm_assumptions: list[str] = field(default_factory=list)
    alternative_interpretations: list[str] = field(default_factory=list)

    # Output
    conclusion: str = ""
    next_questions: list[str] = field(default_factory=list)
    recommended_investigations: list[str] = field(default_factory=list)


@dataclass
class CorrectiveDossier:
    """A comprehensive output document for a corrected narrative."""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    # The reconstruction
    official_narrative: str = ""
    reconstructed_truth: str = ""

    # Evidence synthesis
    primary_evidence: list[Evidence] = field(default_factory=list)
    evidence_by_type: dict[str, list[Evidence]] = field(default_factory=dict)

    # The path of erasure
    erasure_timeline: list[HistoricalEvent] = field(default_factory=list)
    key_actors: list[str] = field(default_factory=list)
    mechanisms_of_suppression: list[str] = field(default_factory=list)

    # Implications
    immediate_implications: list[str] = field(default_factory=list)
    broader_implications: list[str] = field(default_factory=list)
    cosmic_implications: list[str] = field(default_factory=list)

    # Action items
    artifacts_to_repatriate: list[Artifact] = field(default_factory=list)
    questions_to_investigate: list[str] = field(default_factory=list)
    instruments_to_build: list[str] = field(default_factory=list)

    # Confidence metrics
    overall_confidence: float = 0.0
    evidence_convergence_score: float = 0.0
    paradigm_shift_potential: float = 0.0


@dataclass
class CosmicQuery:
    """A query about fundamental reality and existence."""
    id: str = field(default_factory=lambda: str(uuid4()))
    question: str = ""
    domain: str = ""  # ontological, metaphysical, consciousness, etc.

    # Cross-cultural analysis
    cultural_expressions: dict[str, str] = field(default_factory=dict)
    shared_concepts: list[str] = field(default_factory=list)
    convergent_patterns: list[str] = field(default_factory=list)

    # Scientific correlations
    physics_correlations: list[str] = field(default_factory=list)
    consciousness_correlations: list[str] = field(default_factory=list)

    # Analysis output
    reframed_question: str = ""
    investigation_paths: list[str] = field(default_factory=list)
    paradigm_assumptions_challenged: list[str] = field(default_factory=list)

    # Synthesis
    synthesis: str = ""
    confidence_in_synthesis: float = 0.0
