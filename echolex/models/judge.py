"""
Judge Models with Scorecard and Bench Analytics

Comprehensive judge profiling with follow-rate metrics and bench patterns.
"""

from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class JudgeStatus(str, Enum):
    """Current status of a judge."""
    ACTIVE = "active"
    SENIOR = "senior"
    RETIRED = "retired"
    RECALLED = "recalled"
    SUSPENDED = "suspended"


class AppointmentType(str, Enum):
    """How the judge was appointed."""
    ELECTED = "elected"
    APPOINTED = "appointed"
    MERIT_SELECTION = "merit_selection"


class BenchMetrics(BaseModel):
    """
    Core bench performance metrics.

    Tracks how well a judge follows proformas and standard procedures.
    """
    # Proforma Follow Rates (0.0 to 1.0)
    sentencing_guidelines_follow_rate: float = 0.0
    plea_agreement_acceptance_rate: float = 0.0
    motion_grant_rate: float = 0.0
    continuance_grant_rate: float = 0.0
    bail_guidelines_follow_rate: float = 0.0
    evidence_admission_rate: float = 0.0

    # Sentencing Patterns
    avg_sentence_vs_guidelines: float = 0.0  # Negative = lenient, Positive = harsh
    probation_preference_rate: float = 0.0
    alternative_sentencing_rate: float = 0.0
    enhancement_application_rate: float = 0.0

    # Trial Behavior
    avg_trial_duration_days: float = 0.0
    jury_trial_rate: float = 0.0
    bench_trial_rate: float = 0.0
    mistrial_rate: float = 0.0

    # Appeal Metrics
    reversal_rate: float = 0.0
    partial_reversal_rate: float = 0.0
    affirmed_rate: float = 0.0

    # Efficiency
    cases_per_year: int = 0
    avg_time_to_disposition_days: float = 0.0
    backlog_count: int = 0

    # Sample sizes for statistical confidence
    total_cases_analyzed: int = 0
    sentencing_sample_size: int = 0
    motion_sample_size: int = 0


class JudgeScorecard(BaseModel):
    """
    Comprehensive judge scorecard with all metrics.

    Provides deep analytics on judicial behavior and patterns.
    """
    judge_id: UUID
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # Overall Bench Metrics
    bench_metrics: BenchMetrics = Field(default_factory=BenchMetrics)

    # By Case Type Performance
    metrics_by_case_type: Dict[str, BenchMetrics] = Field(default_factory=dict)

    # By Severity Level
    metrics_by_severity: Dict[str, BenchMetrics] = Field(default_factory=dict)

    # Temporal Trends
    yearly_metrics: Dict[int, BenchMetrics] = Field(default_factory=dict)

    # Conviction Rates
    overall_conviction_rate: float = 0.0
    conviction_rate_by_type: Dict[str, float] = Field(default_factory=dict)

    # Sentencing Distribution
    incarceration_rate: float = 0.0
    avg_incarceration_months: float = 0.0
    avg_fine_amount: float = 0.0
    avg_probation_months: float = 0.0

    # Comparison to Peers
    peer_comparison_percentile: float = 0.0  # Where they rank among peers
    jurisdiction_avg_comparison: Dict[str, float] = Field(default_factory=dict)

    # Notable Patterns
    known_biases: List[str] = Field(default_factory=list)  # Identified statistical patterns
    notable_rulings: List[UUID] = Field(default_factory=list)

    # Reliability Score
    data_confidence_score: float = 0.0  # Based on sample sizes


class Judge(BaseModel):
    """
    Complete judge profile with biographical and performance data.
    """
    id: UUID = Field(default_factory=uuid4)

    # Identity
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    suffix: Optional[str] = None  # Jr., Sr., III, etc.

    # Position
    title: str = "Judge"  # Judge, Justice, Magistrate, etc.
    court_id: UUID
    jurisdiction_id: UUID
    division: Optional[str] = None  # Criminal, Civil, Family, etc.
    department: Optional[str] = None

    # Status
    status: JudgeStatus = JudgeStatus.ACTIVE
    appointment_type: AppointmentType

    # Dates
    appointment_date: date
    term_expires: Optional[date] = None
    birth_date: Optional[date] = None

    # Background
    law_school: Optional[str] = None
    graduation_year: Optional[int] = None
    bar_admissions: List[str] = Field(default_factory=list)
    prior_experience: List[str] = Field(default_factory=list)

    # Contact
    chambers_phone: Optional[str] = None
    chambers_email: Optional[str] = None
    courtroom: Optional[str] = None

    # Clerk Information
    clerk_name: Optional[str] = None
    clerk_email: Optional[str] = None

    # Preferences (for attorneys)
    motion_format_preferences: Optional[str] = None
    scheduling_notes: Optional[str] = None
    courtroom_rules: Optional[str] = None

    # Current Scorecard (cached, updated periodically)
    current_scorecard: Optional[JudgeScorecard] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    @property
    def full_name(self) -> str:
        """Get the judge's full name."""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)

    @property
    def formal_name(self) -> str:
        """Get formal title and name."""
        return f"{self.title} {self.full_name}"


class JudgeSearchCriteria(BaseModel):
    """Search criteria for finding judges."""
    jurisdiction_id: Optional[UUID] = None
    court_id: Optional[UUID] = None
    status: Optional[List[JudgeStatus]] = None
    division: Optional[str] = None
    name_search: Optional[str] = None
    min_conviction_rate: Optional[float] = None
    max_conviction_rate: Optional[float] = None
    min_guidelines_follow_rate: Optional[float] = None
    max_reversal_rate: Optional[float] = None

    class Config:
        use_enum_values = True


class JudgeComparison(BaseModel):
    """Comparison of multiple judges for strategic analysis."""
    judges: List[UUID]
    comparison_metrics: List[str]
    results: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    recommendation: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
