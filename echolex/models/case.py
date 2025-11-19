"""
Case Models - From Traffic Tickets to Capital Murder

Comprehensive case representation across all legal domains.
"""

from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class CaseSeverity(str, Enum):
    """Case severity levels from minor infractions to capital offenses."""
    INFRACTION = "infraction"           # Parking tickets, minor violations
    PETTY_OFFENSE = "petty_offense"     # Minor traffic violations
    MISDEMEANOR = "misdemeanor"         # Class A, B, C misdemeanors
    GROSS_MISDEMEANOR = "gross_misdemeanor"
    FELONY_4 = "felony_4"               # 4th degree felony
    FELONY_3 = "felony_3"               # 3rd degree felony
    FELONY_2 = "felony_2"               # 2nd degree felony
    FELONY_1 = "felony_1"               # 1st degree felony
    CAPITAL = "capital"                 # Capital murder, death penalty eligible


class CaseType(str, Enum):
    """Comprehensive case type classification."""
    # Traffic & Vehicle
    TRAFFIC_INFRACTION = "traffic_infraction"
    TRAFFIC_MISDEMEANOR = "traffic_misdemeanor"
    DUI_DWI = "dui_dwi"
    RECKLESS_DRIVING = "reckless_driving"
    VEHICULAR_MANSLAUGHTER = "vehicular_manslaughter"

    # Property Crimes
    PETTY_THEFT = "petty_theft"
    GRAND_THEFT = "grand_theft"
    BURGLARY = "burglary"
    ROBBERY = "robbery"
    ARMED_ROBBERY = "armed_robbery"
    ARSON = "arson"

    # Drug Offenses
    DRUG_POSSESSION = "drug_possession"
    DRUG_DISTRIBUTION = "drug_distribution"
    DRUG_TRAFFICKING = "drug_trafficking"
    DRUG_MANUFACTURING = "drug_manufacturing"

    # Violent Crimes
    SIMPLE_ASSAULT = "simple_assault"
    AGGRAVATED_ASSAULT = "aggravated_assault"
    BATTERY = "battery"
    DOMESTIC_VIOLENCE = "domestic_violence"
    KIDNAPPING = "kidnapping"

    # Homicide
    INVOLUNTARY_MANSLAUGHTER = "involuntary_manslaughter"
    VOLUNTARY_MANSLAUGHTER = "voluntary_manslaughter"
    MURDER_2 = "murder_2"
    MURDER_1 = "murder_1"
    CAPITAL_MURDER = "capital_murder"

    # White Collar
    FRAUD = "fraud"
    EMBEZZLEMENT = "embezzlement"
    TAX_EVASION = "tax_evasion"
    MONEY_LAUNDERING = "money_laundering"
    SECURITIES_FRAUD = "securities_fraud"

    # Sexual Offenses
    SEXUAL_ASSAULT = "sexual_assault"
    SEXUAL_BATTERY = "sexual_battery"

    # Other
    WEAPONS_CHARGE = "weapons_charge"
    CONSPIRACY = "conspiracy"
    CONTEMPT = "contempt"
    PROBATION_VIOLATION = "probation_violation"
    OTHER = "other"


class CaseStatus(str, Enum):
    """Current status of a case."""
    FILED = "filed"
    ARRAIGNMENT = "arraignment"
    PRELIMINARY_HEARING = "preliminary_hearing"
    PRETRIAL = "pretrial"
    PLEA_NEGOTIATIONS = "plea_negotiations"
    TRIAL = "trial"
    JURY_DELIBERATION = "jury_deliberation"
    SENTENCING = "sentencing"
    APPEAL = "appeal"
    CLOSED = "closed"
    DISMISSED = "dismissed"


class CaseOutcome(str, Enum):
    """Possible case outcomes."""
    PENDING = "pending"
    DISMISSED = "dismissed"
    ACQUITTED = "acquitted"
    GUILTY_PLEA = "guilty_plea"
    NO_CONTEST = "no_contest"
    CONVICTED = "convicted"
    HUNG_JURY = "hung_jury"
    MISTRIAL = "mistrial"
    DEFERRED = "deferred"
    DIVERTED = "diverted"


class Charge(BaseModel):
    """Individual charge within a case."""
    id: UUID = Field(default_factory=uuid4)
    statute_code: str
    statute_description: str
    case_type: CaseType
    severity: CaseSeverity
    count: int = 1
    enhanced: bool = False
    enhancement_reason: Optional[str] = None
    outcome: CaseOutcome = CaseOutcome.PENDING

    class Config:
        use_enum_values = True


class Sentence(BaseModel):
    """Sentence details for a charge."""
    charge_id: UUID
    incarceration_months: int = 0
    probation_months: int = 0
    fine_amount: float = 0.0
    restitution_amount: float = 0.0
    community_service_hours: int = 0
    suspended_sentence_months: int = 0
    conditions: List[str] = Field(default_factory=list)
    death_penalty: bool = False
    life_without_parole: bool = False


class CaseEvent(BaseModel):
    """Timeline event in a case."""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime
    event_type: str
    description: str
    judge_id: Optional[UUID] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None


class Case(BaseModel):
    """
    Comprehensive legal case model.

    Represents any case from traffic infractions to capital murder,
    with full tracking of charges, events, outcomes, and sentencing.
    """
    id: UUID = Field(default_factory=uuid4)
    case_number: str
    jurisdiction_id: UUID
    court_id: UUID

    # Classification
    primary_type: CaseType
    severity: CaseSeverity
    charges: List[Charge] = Field(default_factory=list)

    # Status
    status: CaseStatus = CaseStatus.FILED
    outcome: CaseOutcome = CaseOutcome.PENDING

    # Dates
    filing_date: date
    arrest_date: Optional[date] = None
    arraignment_date: Optional[date] = None
    trial_date: Optional[date] = None
    disposition_date: Optional[date] = None

    # Parties
    defendant_id: UUID
    prosecutor_id: Optional[UUID] = None
    defense_attorney_id: Optional[UUID] = None
    judge_id: Optional[UUID] = None

    # Details
    facts_summary: Optional[str] = None
    evidence_summary: Optional[str] = None
    victim_count: int = 0

    # Sentencing
    sentences: List[Sentence] = Field(default_factory=list)

    # Timeline
    events: List[CaseEvent] = Field(default_factory=list)

    # Metadata
    related_cases: List[UUID] = Field(default_factory=list)
    precedents_cited: List[UUID] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class CaseSearchCriteria(BaseModel):
    """Search criteria for finding cases."""
    case_types: Optional[List[CaseType]] = None
    severity_min: Optional[CaseSeverity] = None
    severity_max: Optional[CaseSeverity] = None
    jurisdiction_id: Optional[UUID] = None
    judge_id: Optional[UUID] = None
    status: Optional[List[CaseStatus]] = None
    outcome: Optional[List[CaseOutcome]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    keywords: Optional[str] = None
    statute_code: Optional[str] = None

    class Config:
        use_enum_values = True


class CaseSummary(BaseModel):
    """Brief case summary for search results and listings."""
    id: UUID
    case_number: str
    primary_type: CaseType
    severity: CaseSeverity
    status: CaseStatus
    outcome: CaseOutcome
    filing_date: date
    jurisdiction_name: str
    judge_name: Optional[str] = None
    charge_count: int

    class Config:
        use_enum_values = True
