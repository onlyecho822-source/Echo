"""
Jurisdiction and Court Models

Global jurisdiction support from local courts to international tribunals.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class JurisdictionLevel(str, Enum):
    """Level of jurisdiction."""
    MUNICIPAL = "municipal"
    COUNTY = "county"
    STATE = "state"
    FEDERAL = "federal"
    MILITARY = "military"
    TRIBAL = "tribal"
    INTERNATIONAL = "international"


class CourtType(str, Enum):
    """Type of court."""
    # Trial Courts
    TRAFFIC = "traffic"
    MUNICIPAL = "municipal"
    MAGISTRATE = "magistrate"
    DISTRICT = "district"
    SUPERIOR = "superior"
    CIRCUIT = "circuit"

    # Specialized
    FAMILY = "family"
    JUVENILE = "juvenile"
    PROBATE = "probate"
    TAX = "tax"
    BANKRUPTCY = "bankruptcy"
    DRUG = "drug"
    MENTAL_HEALTH = "mental_health"
    VETERANS = "veterans"

    # Appellate
    APPEALS = "appeals"
    SUPREME = "supreme"

    # Federal
    FEDERAL_DISTRICT = "federal_district"
    FEDERAL_CIRCUIT = "federal_circuit"
    FEDERAL_SUPREME = "federal_supreme"

    # Military
    COURT_MARTIAL = "court_martial"
    MILITARY_APPEALS = "military_appeals"

    # International
    INTERNATIONAL_CRIMINAL = "international_criminal"
    INTERNATIONAL_JUSTICE = "international_justice"


class LegalSystem(str, Enum):
    """Type of legal system."""
    COMMON_LAW = "common_law"
    CIVIL_LAW = "civil_law"
    RELIGIOUS = "religious"
    CUSTOMARY = "customary"
    MIXED = "mixed"


class Jurisdiction(BaseModel):
    """
    Legal jurisdiction representing a geographic/governmental area.
    """
    id: UUID = Field(default_factory=uuid4)

    # Identity
    name: str
    code: str  # e.g., "US-CA", "US-TX-HARRIS"
    level: JurisdictionLevel
    legal_system: LegalSystem = LegalSystem.COMMON_LAW

    # Geography
    country: str
    state_province: Optional[str] = None
    county_region: Optional[str] = None
    city: Optional[str] = None

    # Hierarchy
    parent_jurisdiction_id: Optional[UUID] = None
    child_jurisdictions: List[UUID] = Field(default_factory=list)

    # Legal Framework
    constitution: Optional[str] = None  # Reference to constitution
    primary_statutes: List[str] = Field(default_factory=list)

    # Contact
    bar_association: Optional[str] = None
    bar_website: Optional[str] = None
    court_website: Optional[str] = None

    # Statistics
    population: Optional[int] = None
    annual_case_filings: Optional[int] = None
    judge_count: Optional[int] = None

    # Metadata
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class Court(BaseModel):
    """
    Specific court within a jurisdiction.
    """
    id: UUID = Field(default_factory=uuid4)

    # Identity
    name: str
    code: str  # Court identifier
    court_type: CourtType
    jurisdiction_id: UUID

    # Location
    address: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: str

    # Contact
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

    # Structure
    divisions: List[str] = Field(default_factory=list)
    departments: List[str] = Field(default_factory=list)

    # Judges
    chief_judge_id: Optional[UUID] = None
    judge_ids: List[UUID] = Field(default_factory=list)

    # Procedures
    local_rules_url: Optional[str] = None
    efiling_url: Optional[str] = None
    efiling_required: bool = False

    # Schedule
    business_hours: Optional[str] = None
    holiday_schedule: Optional[str] = None

    # Statistics
    annual_filings: Optional[int] = None
    avg_disposition_days: Optional[float] = None

    # Metadata
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class CourtRule(BaseModel):
    """Local court rule or procedure."""
    id: UUID = Field(default_factory=uuid4)
    court_id: UUID
    rule_number: str
    title: str
    text: str
    effective_date: Optional[datetime] = None
    categories: List[str] = Field(default_factory=list)


class CourtFee(BaseModel):
    """Court fee schedule entry."""
    id: UUID = Field(default_factory=uuid4)
    court_id: UUID
    fee_type: str
    description: str
    amount: float
    waiver_available: bool = False
    effective_date: Optional[datetime] = None


class JurisdictionStats(BaseModel):
    """Aggregated statistics for a jurisdiction."""
    jurisdiction_id: UUID
    period_start: datetime
    period_end: datetime

    # Case Statistics
    total_cases_filed: int = 0
    total_cases_disposed: int = 0
    cases_by_type: Dict[str, int] = Field(default_factory=dict)
    cases_by_severity: Dict[str, int] = Field(default_factory=dict)

    # Outcome Statistics
    conviction_rate: float = 0.0
    dismissal_rate: float = 0.0
    plea_rate: float = 0.0
    trial_rate: float = 0.0

    # Timing
    avg_disposition_days: float = 0.0
    median_disposition_days: float = 0.0

    # Sentencing
    avg_incarceration_months: float = 0.0
    avg_fine_amount: float = 0.0
    incarceration_rate: float = 0.0

    # Appeal Statistics
    appeal_rate: float = 0.0
    reversal_rate: float = 0.0
