"""
Appeal Predictor

Machine learning model for predicting appeal outcomes.

DISCLAIMER: Predictions are for RESEARCH PURPOSES ONLY.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import numpy as np
from dataclasses import dataclass

from echolex.models.case import Case, CaseType, CaseSeverity, CaseOutcome
from echolex.models.judge import JudgeScorecard


@dataclass
class AppealPrediction:
    """Predicted appeal outcome."""
    case_id: Optional[UUID]

    # Appeal likelihood
    appeal_probability: float
    appeal_grounds: List[str]

    # Outcome probabilities
    affirmed_probability: float
    reversed_probability: float
    partial_reversal_probability: float
    remanded_probability: float

    # Impact if reversed
    likely_new_outcome: Optional[str]
    sentence_reduction_probability: float

    # Metadata
    confidence: float
    factors: List[Dict[str, Any]]
    generated_at: datetime
    model_version: str

    disclaimer: str = (
        "FOR RESEARCH PURPOSES ONLY. Appeal outcomes depend on many factors "
        "including the strength of legal arguments. Consult an appellate attorney."
    )


class AppealPredictor:
    """
    Appeal outcome predictor.

    Predicts:
    - Likelihood of appeal being filed
    - Probability of success
    - Likely grounds for appeal
    """

    MODEL_VERSION = "1.0.0"

    def __init__(self):
        """Initialize the appeal predictor."""
        pass

    def predict(
        self,
        case: Case,
        judge_scorecard: Optional[JudgeScorecard] = None,
        jurisdiction_stats: Optional[Dict[str, float]] = None
    ) -> AppealPrediction:
        """
        Predict appeal outcome for a case.

        Args:
            case: The case to analyze
            judge_scorecard: Scorecard for the trial judge
            jurisdiction_stats: Jurisdiction statistics

        Returns:
            AppealPrediction with probabilities and grounds
        """
        # Calculate appeal probability
        appeal_prob = self._calculate_appeal_probability(case, judge_scorecard)

        # Identify potential grounds
        grounds = self._identify_appeal_grounds(case, judge_scorecard)

        # Calculate outcome probabilities
        outcome_probs = self._calculate_outcome_probabilities(
            case, judge_scorecard, jurisdiction_stats
        )

        # Determine likely new outcome if reversed
        new_outcome = self._predict_new_outcome(case) if outcome_probs["reversed"] > 0.3 else None

        # Calculate sentence reduction probability
        sentence_reduction = self._calculate_sentence_reduction_probability(
            case, judge_scorecard
        )

        # Calculate confidence
        confidence = self._calculate_confidence(case, judge_scorecard)

        # Identify key factors
        factors = self._identify_factors(case, judge_scorecard, outcome_probs)

        return AppealPrediction(
            case_id=case.id,
            appeal_probability=appeal_prob,
            appeal_grounds=grounds,
            affirmed_probability=outcome_probs["affirmed"],
            reversed_probability=outcome_probs["reversed"],
            partial_reversal_probability=outcome_probs["partial"],
            remanded_probability=outcome_probs["remanded"],
            likely_new_outcome=new_outcome,
            sentence_reduction_probability=sentence_reduction,
            confidence=confidence,
            factors=factors,
            generated_at=datetime.utcnow(),
            model_version=self.MODEL_VERSION
        )

    def _calculate_appeal_probability(
        self,
        case: Case,
        scorecard: Optional[JudgeScorecard]
    ) -> float:
        """Calculate probability that an appeal will be filed."""
        # Base probability by outcome
        outcome_appeal_rates = {
            CaseOutcome.CONVICTED: 0.35,
            CaseOutcome.GUILTY_PLEA: 0.05,
            CaseOutcome.ACQUITTED: 0.02,  # Prosecution rarely appeals
            CaseOutcome.DISMISSED: 0.01,
        }

        base_rate = outcome_appeal_rates.get(case.outcome, 0.1)

        # Higher severity = more likely to appeal
        severity_modifier = {
            CaseSeverity.INFRACTION: 0.5,
            CaseSeverity.PETTY_OFFENSE: 0.7,
            CaseSeverity.MISDEMEANOR: 0.9,
            CaseSeverity.GROSS_MISDEMEANOR: 1.0,
            CaseSeverity.FELONY_4: 1.2,
            CaseSeverity.FELONY_3: 1.3,
            CaseSeverity.FELONY_2: 1.5,
            CaseSeverity.FELONY_1: 1.8,
            CaseSeverity.CAPITAL: 2.0  # Almost always appealed
        }

        modifier = severity_modifier.get(case.severity, 1.0)
        appeal_prob = base_rate * modifier

        # Adjust for judge reversal history
        if scorecard:
            if scorecard.bench_metrics.reversal_rate > 0.3:
                appeal_prob *= 1.3  # High reversal rate encourages appeals

        return min(0.95, appeal_prob)

    def _identify_appeal_grounds(
        self,
        case: Case,
        scorecard: Optional[JudgeScorecard]
    ) -> List[str]:
        """Identify potential grounds for appeal."""
        grounds = []

        # Sentencing issues
        if case.sentences:
            if scorecard and scorecard.bench_metrics.avg_sentence_vs_guidelines > 0.2:
                grounds.append("Excessive sentence - above guidelines")

            # Check for potential illegal sentences
            for sentence in case.sentences:
                if sentence.death_penalty and case.severity != CaseSeverity.CAPITAL:
                    grounds.append("Illegal sentence - death penalty for non-capital offense")

        # Evidence issues (would analyze case events in production)
        grounds.append("Evidentiary errors - admission/exclusion of evidence")

        # Procedural issues
        if scorecard:
            if scorecard.bench_metrics.motion_grant_rate < 0.2:
                grounds.append("Abuse of discretion - denial of motions")

        # Constitutional issues
        grounds.append("Ineffective assistance of counsel")
        grounds.append("Prosecutorial misconduct")

        # Jury issues (if applicable)
        jury_events = [e for e in case.events if "jury" in e.event_type.lower()]
        if jury_events:
            grounds.append("Jury instruction errors")
            grounds.append("Jury selection issues")

        return grounds[:5]  # Return top 5 most relevant

    def _calculate_outcome_probabilities(
        self,
        case: Case,
        scorecard: Optional[JudgeScorecard],
        jurisdiction_stats: Optional[Dict[str, float]]
    ) -> Dict[str, float]:
        """Calculate probabilities of different appeal outcomes."""
        # Base rates (national averages)
        base_affirmed = 0.70
        base_reversed = 0.12
        base_partial = 0.10
        base_remanded = 0.08

        # Adjust for judge reversal history
        if scorecard:
            reversal_rate = scorecard.bench_metrics.reversal_rate
            if reversal_rate > 0:
                # Shift probability based on historical rate
                base_reversed = (base_reversed + reversal_rate * 2) / 3
                base_partial = (base_partial + scorecard.bench_metrics.partial_reversal_rate) / 2
                base_affirmed = 1 - base_reversed - base_partial - base_remanded

        # Adjust for jurisdiction
        if jurisdiction_stats:
            jurisdiction_reversal = jurisdiction_stats.get("reversal_rate", 0.12)
            base_reversed = (base_reversed + jurisdiction_reversal) / 2
            base_affirmed = 1 - base_reversed - base_partial - base_remanded

        # Normalize
        total = base_affirmed + base_reversed + base_partial + base_remanded
        return {
            "affirmed": base_affirmed / total,
            "reversed": base_reversed / total,
            "partial": base_partial / total,
            "remanded": base_remanded / total
        }

    def _predict_new_outcome(self, case: Case) -> str:
        """Predict likely outcome if case is reversed."""
        # Most reversals lead to new trial or dismissal
        if case.severity in [CaseSeverity.INFRACTION, CaseSeverity.PETTY_OFFENSE]:
            return CaseOutcome.DISMISSED.value

        return "new_trial"

    def _calculate_sentence_reduction_probability(
        self,
        case: Case,
        scorecard: Optional[JudgeScorecard]
    ) -> float:
        """Calculate probability of sentence reduction on appeal."""
        if not case.sentences:
            return 0.0

        base_prob = 0.2  # Base probability

        # Higher if judge sentences above guidelines
        if scorecard:
            if scorecard.bench_metrics.avg_sentence_vs_guidelines > 0.2:
                base_prob = 0.4
            elif scorecard.bench_metrics.avg_sentence_vs_guidelines > 0.1:
                base_prob = 0.3

        return base_prob

    def _calculate_confidence(
        self,
        case: Case,
        scorecard: Optional[JudgeScorecard]
    ) -> float:
        """Calculate confidence in the prediction."""
        confidence = 0.5

        # More data = higher confidence
        if scorecard:
            confidence += 0.15
            if scorecard.bench_metrics.total_cases_analyzed > 100:
                confidence += 0.1

        # Resolved cases are more predictable
        if case.outcome != CaseOutcome.PENDING:
            confidence += 0.1

        return min(0.85, confidence)

    def _identify_factors(
        self,
        case: Case,
        scorecard: Optional[JudgeScorecard],
        outcome_probs: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify key factors affecting appeal prediction."""
        factors = []

        # Judge history
        if scorecard:
            if scorecard.bench_metrics.reversal_rate > 0.25:
                factors.append({
                    "factor": "judge_reversal_history",
                    "impact": "favorable",
                    "description": f"Judge has {scorecard.bench_metrics.reversal_rate*100:.0f}% reversal rate"
                })
            elif scorecard.bench_metrics.reversal_rate < 0.1:
                factors.append({
                    "factor": "judge_reversal_history",
                    "impact": "unfavorable",
                    "description": "Judge rarely reversed on appeal"
                })

        # Severity
        if case.severity in [CaseSeverity.FELONY_1, CaseSeverity.CAPITAL]:
            factors.append({
                "factor": "case_severity",
                "impact": "thorough_review",
                "description": "High severity cases receive more thorough appellate review"
            })

        # Outcome probabilities
        if outcome_probs["reversed"] > 0.25:
            factors.append({
                "factor": "reversal_likelihood",
                "impact": "favorable",
                "description": "Higher than average probability of reversal"
            })

        return factors
