"""
Sentence Predictor

Machine learning model for predicting sentencing outcomes.

DISCLAIMER: Predictions are for RESEARCH PURPOSES ONLY.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import numpy as np
from dataclasses import dataclass

from echolex.models.case import Case, CaseType, CaseSeverity
from echolex.models.judge import JudgeScorecard


@dataclass
class SentencePrediction:
    """Predicted sentence details."""
    case_id: Optional[UUID]

    # Incarceration
    incarceration_months_low: float
    incarceration_months_mid: float
    incarceration_months_high: float
    incarceration_probability: float

    # Probation
    probation_months_low: float
    probation_months_mid: float
    probation_months_high: float
    probation_probability: float

    # Fines
    fine_amount_low: float
    fine_amount_mid: float
    fine_amount_high: float

    # Special outcomes
    death_penalty_probability: float
    life_without_parole_probability: float

    # Metadata
    confidence: float
    factors: List[Dict[str, Any]]
    generated_at: datetime
    model_version: str

    disclaimer: str = (
        "FOR RESEARCH PURPOSES ONLY. This prediction does not constitute "
        "legal advice. Actual sentences vary based on many factors. "
        "Consult a licensed attorney."
    )


class SentencePredictor:
    """
    Sentence predictor using machine learning.

    Predicts likely sentence ranges based on:
    - Charge severity and type
    - Sentencing guidelines
    - Judge sentencing patterns
    - Jurisdiction norms
    """

    MODEL_VERSION = "1.0.0"

    # Base sentencing ranges by severity (months)
    SEVERITY_RANGES = {
        CaseSeverity.INFRACTION: (0, 0, 0),
        CaseSeverity.PETTY_OFFENSE: (0, 0, 1),
        CaseSeverity.MISDEMEANOR: (0, 3, 12),
        CaseSeverity.GROSS_MISDEMEANOR: (0, 6, 18),
        CaseSeverity.FELONY_4: (6, 18, 36),
        CaseSeverity.FELONY_3: (12, 36, 60),
        CaseSeverity.FELONY_2: (24, 60, 120),
        CaseSeverity.FELONY_1: (60, 120, 240),
        CaseSeverity.CAPITAL: (120, 360, 600)  # Life = 600 months
    }

    def __init__(self):
        """Initialize the sentence predictor."""
        pass

    def predict(
        self,
        case: Case,
        judge_scorecard: Optional[JudgeScorecard] = None,
        jurisdiction_stats: Optional[Dict[str, float]] = None
    ) -> SentencePrediction:
        """
        Predict the sentence for a case.

        Args:
            case: The case to predict
            judge_scorecard: Scorecard for assigned judge
            jurisdiction_stats: Statistics for jurisdiction

        Returns:
            SentencePrediction with ranges and probabilities
        """
        # Get base ranges
        base_low, base_mid, base_high = self._get_base_range(case)

        # Apply judge modifier
        judge_modifier = self._get_judge_modifier(case, judge_scorecard)

        # Apply jurisdiction modifier
        jurisdiction_modifier = self._get_jurisdiction_modifier(jurisdiction_stats)

        # Apply charge enhancements
        enhancement_modifier = self._get_enhancement_modifier(case)

        # Calculate final ranges
        total_modifier = judge_modifier * jurisdiction_modifier * enhancement_modifier

        incarceration_low = base_low * total_modifier
        incarceration_mid = base_mid * total_modifier
        incarceration_high = base_high * total_modifier

        # Calculate probation ranges (inverse relationship with incarceration)
        probation_factor = 1.5  # Probation typically 1.5x incarceration
        probation_low = incarceration_low * probation_factor
        probation_mid = incarceration_mid * probation_factor
        probation_high = incarceration_high * probation_factor

        # Calculate incarceration vs probation probability
        incarceration_prob = self._calculate_incarceration_probability(
            case, judge_scorecard
        )

        # Calculate fine amounts
        fine_low, fine_mid, fine_high = self._calculate_fines(case)

        # Special outcomes for capital cases
        death_prob = 0.0
        lwop_prob = 0.0

        if case.severity == CaseSeverity.CAPITAL:
            death_prob = self._calculate_death_penalty_probability(
                case, judge_scorecard, jurisdiction_stats
            )
            lwop_prob = 0.7 - death_prob  # Life without parole alternative

        # Calculate confidence
        confidence = self._calculate_confidence(case, judge_scorecard)

        # Identify factors
        factors = self._identify_factors(case, judge_scorecard, total_modifier)

        return SentencePrediction(
            case_id=case.id,
            incarceration_months_low=round(incarceration_low, 1),
            incarceration_months_mid=round(incarceration_mid, 1),
            incarceration_months_high=round(incarceration_high, 1),
            incarceration_probability=incarceration_prob,
            probation_months_low=round(probation_low, 1),
            probation_months_mid=round(probation_mid, 1),
            probation_months_high=round(probation_high, 1),
            probation_probability=1 - incarceration_prob,
            fine_amount_low=fine_low,
            fine_amount_mid=fine_mid,
            fine_amount_high=fine_high,
            death_penalty_probability=death_prob,
            life_without_parole_probability=lwop_prob,
            confidence=confidence,
            factors=factors,
            generated_at=datetime.utcnow(),
            model_version=self.MODEL_VERSION
        )

    def _get_base_range(self, case: Case) -> tuple:
        """Get base sentencing range for case severity."""
        return self.SEVERITY_RANGES.get(
            case.severity,
            self.SEVERITY_RANGES[CaseSeverity.MISDEMEANOR]
        )

    def _get_judge_modifier(
        self,
        case: Case,
        scorecard: Optional[JudgeScorecard]
    ) -> float:
        """Calculate modifier based on judge patterns."""
        if not scorecard:
            return 1.0

        # Base modifier from overall sentencing deviation
        deviation = scorecard.bench_metrics.avg_sentence_vs_guidelines
        modifier = 1.0 + deviation

        # Adjust for case-type specific patterns
        case_type = case.primary_type.value if hasattr(case.primary_type, 'value') else case.primary_type
        if case_type in scorecard.metrics_by_case_type:
            type_metrics = scorecard.metrics_by_case_type[case_type]
            type_deviation = type_metrics.avg_sentence_vs_guidelines
            # Weight type-specific more heavily
            modifier = (modifier + type_deviation * 2) / 3

        # Clamp to reasonable range
        return max(0.5, min(2.0, modifier))

    def _get_jurisdiction_modifier(
        self,
        stats: Optional[Dict[str, float]]
    ) -> float:
        """Calculate modifier based on jurisdiction norms."""
        if not stats:
            return 1.0

        # Get average sentence comparison to national average
        avg_sentence = stats.get("avg_incarceration_months", 0)
        national_avg = 24  # Placeholder for national average

        if national_avg > 0:
            return avg_sentence / national_avg

        return 1.0

    def _get_enhancement_modifier(self, case: Case) -> float:
        """Calculate modifier for charge enhancements."""
        modifier = 1.0

        for charge in case.charges:
            if charge.enhanced:
                modifier *= 1.5  # Each enhancement increases 50%
            if charge.count > 1:
                modifier *= (1 + 0.1 * (charge.count - 1))  # Multiple counts

        return modifier

    def _calculate_incarceration_probability(
        self,
        case: Case,
        scorecard: Optional[JudgeScorecard]
    ) -> float:
        """Calculate probability of incarceration vs alternatives."""
        # Base probability by severity
        severity_prob = {
            CaseSeverity.INFRACTION: 0.0,
            CaseSeverity.PETTY_OFFENSE: 0.05,
            CaseSeverity.MISDEMEANOR: 0.2,
            CaseSeverity.GROSS_MISDEMEANOR: 0.4,
            CaseSeverity.FELONY_4: 0.6,
            CaseSeverity.FELONY_3: 0.75,
            CaseSeverity.FELONY_2: 0.85,
            CaseSeverity.FELONY_1: 0.95,
            CaseSeverity.CAPITAL: 1.0
        }

        base_prob = severity_prob.get(case.severity, 0.5)

        # Adjust for judge patterns
        if scorecard:
            judge_rate = scorecard.incarceration_rate
            # Weight judge pattern
            return (base_prob + judge_rate) / 2

        return base_prob

    def _calculate_fines(self, case: Case) -> tuple:
        """Calculate fine ranges."""
        # Base fines by severity
        fine_ranges = {
            CaseSeverity.INFRACTION: (50, 150, 500),
            CaseSeverity.PETTY_OFFENSE: (100, 300, 1000),
            CaseSeverity.MISDEMEANOR: (500, 1500, 5000),
            CaseSeverity.GROSS_MISDEMEANOR: (1000, 3000, 10000),
            CaseSeverity.FELONY_4: (2500, 7500, 25000),
            CaseSeverity.FELONY_3: (5000, 15000, 50000),
            CaseSeverity.FELONY_2: (10000, 50000, 100000),
            CaseSeverity.FELONY_1: (25000, 100000, 250000),
            CaseSeverity.CAPITAL: (50000, 250000, 500000)
        }

        return fine_ranges.get(
            case.severity,
            fine_ranges[CaseSeverity.MISDEMEANOR]
        )

    def _calculate_death_penalty_probability(
        self,
        case: Case,
        scorecard: Optional[JudgeScorecard],
        stats: Optional[Dict[str, float]]
    ) -> float:
        """Calculate probability of death penalty for capital cases."""
        if case.severity != CaseSeverity.CAPITAL:
            return 0.0

        # Base rate depends on jurisdiction having death penalty
        base_rate = 0.15  # National average for eligible cases

        # Adjust for aggravating factors
        if case.victim_count > 1:
            base_rate *= 1.5

        # Check for specific aggravating charge types
        for charge in case.charges:
            if charge.case_type == CaseType.CAPITAL_MURDER:
                base_rate *= 1.3

        # Cap at reasonable maximum
        return min(0.4, base_rate)

    def _calculate_confidence(
        self,
        case: Case,
        scorecard: Optional[JudgeScorecard]
    ) -> float:
        """Calculate confidence score for the prediction."""
        confidence = 0.5  # Base confidence

        # Boost if we have judge data
        if scorecard:
            confidence += 0.2
            if scorecard.data_confidence_score > 0.7:
                confidence += 0.1

        # Lower severity = more predictable
        if case.severity in [CaseSeverity.INFRACTION, CaseSeverity.PETTY_OFFENSE]:
            confidence += 0.15

        return min(0.95, confidence)

    def _identify_factors(
        self,
        case: Case,
        scorecard: Optional[JudgeScorecard],
        modifier: float
    ) -> List[Dict[str, Any]]:
        """Identify key factors affecting sentence prediction."""
        factors = []

        # Judge patterns
        if scorecard:
            if scorecard.bench_metrics.avg_sentence_vs_guidelines > 0.1:
                factors.append({
                    "factor": "judge_sentencing_pattern",
                    "impact": "increase",
                    "description": "Judge tends to sentence above guidelines"
                })
            elif scorecard.bench_metrics.avg_sentence_vs_guidelines < -0.1:
                factors.append({
                    "factor": "judge_sentencing_pattern",
                    "impact": "decrease",
                    "description": "Judge tends to sentence below guidelines"
                })

            if scorecard.bench_metrics.probation_preference_rate > 0.6:
                factors.append({
                    "factor": "probation_preference",
                    "impact": "favorable",
                    "description": "Judge shows preference for probation"
                })

        # Enhancements
        enhanced_charges = sum(1 for c in case.charges if c.enhanced)
        if enhanced_charges:
            factors.append({
                "factor": "charge_enhancements",
                "impact": "increase",
                "description": f"{enhanced_charges} charge(s) with enhancements"
            })

        # Multiple counts
        total_counts = sum(c.count for c in case.charges)
        if total_counts > len(case.charges):
            factors.append({
                "factor": "multiple_counts",
                "impact": "increase",
                "description": f"Multiple counts on charges"
            })

        return factors
