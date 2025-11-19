"""
Party Models

Defendants, attorneys, and other case participants.
"""

from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class PartyType(str, Enum):
    """Type of party in a case."""
    DEFENDANT = "defendant"
    PLAINTIFF = "plaintiff"
    PROSECUTOR = "prosecutor"
    VICTIM = "victim"
    WITNESS = "witness"
    EXPERT_WITNESS = "expert_witness"
    INTERVENOR = "intervenor"


class AttorneyType(str, Enum):
    """Type of attorney role."""
    DEFENSE = "defense"
    PROSECUTION = "prosecution"
    PLAINTIFF = "plaintiff"
    PUBLIC_DEFENDER = "public_defender"
    COURT_APPOINTED = "court_appointed"
    PRO_BONO = "pro_bono"


class Party(BaseModel):
    """
    Party to a legal case.
    """
    id: UUID = Field(default_factory=uuid4)

    # Identity
    party_type: PartyType
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization_name: Optional[str] = None
    is_organization: bool = False

    # Personal Information
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    race: Optional[str] = None  # For statistical analysis

    # Contact
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    # Legal Status
    custody_status: Optional[str] = None
    bail_amount: Optional[float] = None
    bail_posted: bool = False

    # History
    prior_cases: List[UUID] = Field(default_factory=list)
    prior_convictions: int = 0

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    @property
    def display_name(self) -> str:
        """Get display name for the party."""
        if self.is_organization and self.organization_name:
            return self.organization_name
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else "Unknown"


class Attorney(BaseModel):
    """
    Attorney/lawyer profile.
    """
    id: UUID = Field(default_factory=uuid4)

    # Identity
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    suffix: Optional[str] = None

    # Professional
    attorney_type: AttorneyType
    bar_number: str
    jurisdictions: List[UUID] = Field(default_factory=list)
    bar_admissions: List[str] = Field(default_factory=list)

    # Firm
    firm_name: Optional[str] = None
    firm_address: Optional[str] = None
    firm_city: Optional[str] = None
    firm_state: Optional[str] = None
    firm_postal_code: Optional[str] = None

    # Contact
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

    # Experience
    years_experience: Optional[int] = None
    specializations: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)

    # Performance Metrics
    total_cases: int = 0
    cases_won: int = 0
    cases_lost: int = 0
    acquittal_rate: float = 0.0
    dismissal_rate: float = 0.0
    plea_rate: float = 0.0
    avg_sentence_reduction: float = 0.0  # % below guidelines

    # By Case Type
    performance_by_type: Dict[str, Dict[str, float]] = Field(default_factory=dict)

    # Judge Relationships
    cases_before_judges: Dict[str, int] = Field(default_factory=dict)  # judge_id -> count
    win_rate_by_judge: Dict[str, float] = Field(default_factory=dict)

    # Status
    active: bool = True
    disciplinary_actions: List[str] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    @property
    def full_name(self) -> str:
        """Get the attorney's full name."""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)

    @property
    def win_rate(self) -> float:
        """Calculate overall win rate."""
        total = self.cases_won + self.cases_lost
        return self.cases_won / total if total > 0 else 0.0


class AttorneySearchCriteria(BaseModel):
    """Search criteria for finding attorneys."""
    jurisdiction_id: Optional[UUID] = None
    attorney_type: Optional[List[AttorneyType]] = None
    specializations: Optional[List[str]] = None
    name_search: Optional[str] = None
    min_experience_years: Optional[int] = None
    min_cases: Optional[int] = None
    min_win_rate: Optional[float] = None

    class Config:
        use_enum_values = True
