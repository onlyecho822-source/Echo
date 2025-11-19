"""
Legal Precedent Models

Case law and precedent tracking for legal research.
"""

from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class PrecedentType(str, Enum):
    """Type of legal precedent."""
    BINDING = "binding"          # Must be followed
    PERSUASIVE = "persuasive"    # May be considered
    OVERRULED = "overruled"      # No longer valid
    DISTINGUISHED = "distinguished"
    SUPERSEDED = "superseded"


class PrecedentStatus(str, Enum):
    """Current status of a precedent."""
    GOOD_LAW = "good_law"
    QUESTIONED = "questioned"
    CRITICIZED = "criticized"
    LIMITED = "limited"
    OVERRULED = "overruled"
    SUPERSEDED = "superseded"


class CitationFormat(str, Enum):
    """Citation format standards."""
    BLUEBOOK = "bluebook"
    ALWD = "alwd"
    NEUTRAL = "neutral"
    REGIONAL = "regional"


class LegalPrecedent(BaseModel):
    """
    Legal precedent/case law model.

    Represents binding or persuasive legal authority.
    """
    id: UUID = Field(default_factory=uuid4)

    # Citation
    case_name: str  # e.g., "Miranda v. Arizona"
    citation: str   # e.g., "384 U.S. 436 (1966)"
    parallel_citations: List[str] = Field(default_factory=list)

    # Court Information
    court_id: Optional[UUID] = None
    jurisdiction_id: UUID
    court_name: str  # For historical reference

    # Dates
    decision_date: date
    argued_date: Optional[date] = None
    filed_date: Optional[date] = None

    # Classification
    precedent_type: PrecedentType
    status: PrecedentStatus = PrecedentStatus.GOOD_LAW

    # Legal Issues
    legal_issues: List[str] = Field(default_factory=list)
    holdings: List[str] = Field(default_factory=list)
    key_quotes: List[str] = Field(default_factory=list)

    # Parties
    plaintiff: Optional[str] = None
    defendant: Optional[str] = None

    # Judges
    author_judge: Optional[str] = None
    majority_judges: List[str] = Field(default_factory=list)
    concurring_judges: List[str] = Field(default_factory=list)
    dissenting_judges: List[str] = Field(default_factory=list)

    # Opinion Text
    syllabus: Optional[str] = None
    majority_opinion: Optional[str] = None
    concurrence: Optional[str] = None
    dissent: Optional[str] = None

    # Procedural History
    lower_court: Optional[str] = None
    lower_court_outcome: Optional[str] = None
    appellate_history: List[str] = Field(default_factory=list)

    # Relationships
    cases_cited: List[UUID] = Field(default_factory=list)
    cited_by: List[UUID] = Field(default_factory=list)
    distinguished_by: List[UUID] = Field(default_factory=list)
    overruled_by: Optional[UUID] = None

    # Legal Topics
    topics: List[str] = Field(default_factory=list)
    headnotes: List[str] = Field(default_factory=list)
    key_numbers: List[str] = Field(default_factory=list)  # West Key Numbers

    # Impact
    citation_count: int = 0
    impact_score: float = 0.0  # Calculated influence metric

    # Metadata
    source: Optional[str] = None  # Where this data came from
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class PrecedentSearchCriteria(BaseModel):
    """Search criteria for finding precedents."""
    keywords: Optional[str] = None
    jurisdiction_id: Optional[UUID] = None
    court_level: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    topics: Optional[List[str]] = None
    status: Optional[List[PrecedentStatus]] = None
    min_citations: Optional[int] = None

    class Config:
        use_enum_values = True


class CitationAnalysis(BaseModel):
    """Analysis of how a precedent has been cited."""
    precedent_id: UUID
    total_citations: int = 0
    positive_citations: int = 0
    negative_citations: int = 0
    distinguished: int = 0
    followed: int = 0
    cited_in_jurisdictions: Dict[str, int] = Field(default_factory=dict)
    citation_trend: List[Dict[str, int]] = Field(default_factory=list)  # By year
    most_cited_for: List[str] = Field(default_factory=list)  # Legal issues
    generated_at: datetime = Field(default_factory=datetime.utcnow)
