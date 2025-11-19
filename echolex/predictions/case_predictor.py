"""
Case Outcome Predictor

Machine learning model for predicting case outcomes.

DISCLAIMER: Predictions are for RESEARCH PURPOSES ONLY.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import numpy as np
from dataclasses import dataclass

from echolex.models.case import Case, CaseType, CaseSeverity, CaseOutcome
from echolex.models.judge import JudgeScorecard


@dataclass
class PredictionResult:
    """Result of a case prediction."""
    case_id: Optional[UUID]
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    factors: List[Dict[str, Any]]
    generated_at: datetime
    model_version: str
    disclaimer: str = (
        "FOR RESEARCH PURPOSES ONLY. This prediction does not constitute "
        "legal advice. Consult a licensed attorney for legal matters."
    )


class CasePredictor:
    """
    Case outcome predictor using machine learning.

    Predicts likely case outcomes based on:
    - Case characteristics
    - Judge patterns
    - Jurisdiction trends
    - Historical similar cases
    """

    MODEL_VERSION = "1.0.0"

    def __init__(self):
        """Initialize the case predictor."""
        self._model = None
        self._feature_weights = self._initialize_weights()

    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize feature weights for the prediction model."""
        return {
            # Case factors
            "severity": 0.15,
            "charge_count": 0.08,
            "prior_record": 0.12,
            "evidence_strength": 0.18,

            # Judge factors
            "judge_conviction_rate": 0.15,
            "judge_case_type_rate": 0.10,
            "judge_severity_rate": 0.08,

            # Jurisdiction factors
            "jurisdiction_conviction_rate": 0.08,

            # Representation factors
            "defense_quality": 0.06
        }

    def predict(
        self,
        case: Case,
        judge_scorecard: Optional[JudgeScorecard] = None,
        jurisdiction_stats: Optional[Dict[str, float]] = None,
        similar_cases: Optional[List[Case]] = None
    ) -> PredictionResult:
        """
        Predict the outcome of a case.

        Args:
            case: The case to predict
            judge_scorecard: Scorecard for assigned judge
            jurisdiction_stats: Statistics for jurisdiction
            similar_cases: Similar historical cases

        Returns:
            PredictionResult with prediction and confidence
        """
        # Extract features
        features = self._extract_features(
            case, judge_scorecard, jurisdiction_stats, similar_cases
        )

        # Calculate base probabilities
        probabilities = self._calculate_probabilities(features)

        # Determine prediction and confidence
        prediction = max(probabilities, key=probabilities.get)
        confidence = probabilities[prediction]

        # Identify key factors
        factors = self._identify_factors(features, probabilities)

        return PredictionResult(
            case_id=case.id,
            prediction=prediction,
            confidence=confidence,
            probabilities=probabilities,
            factors=factors,
            generated_at=datetime.utcnow(),
            model_version=self.MODEL_VERSION
        )

    def predict_batch(
        self,
        cases: List[Case],
        judge_scorecards: Dict[UUID, JudgeScorecard],
        jurisdiction_stats: Optional[Dict[str, float]] = None
    ) -> List[PredictionResult]:
        """
        Predict outcomes for multiple cases.

        Args:
            cases: List of cases to predict
            judge_scorecards: Dict mapping judge ID to scorecard
            jurisdiction_stats: Statistics for jurisdiction

        Returns:
            List of PredictionResults
        """
        results = []
        for case in cases:
            scorecard = judge_scorecards.get(case.judge_id) if case.judge_id else None
            result = self.predict(case, scorecard, jurisdiction_stats)
            results.append(result)
        return results

    def _extract_features(
        self,
        case: Case,
        judge_scorecard: Optional[JudgeScorecard],
        jurisdiction_stats: Optional[Dict[str, float]],
        similar_cases: Optional[List[Case]]
    ) -> Dict[str, float]:
        """Extract features for prediction."""
        features = {}

        # Case severity (normalized 0-1)
        severity_scores = {
            CaseSeverity.INFRACTION: 0.05,
            CaseSeverity.PETTY_OFFENSE: 0.1,
            CaseSeverity.MISDEMEANOR: 0.2,
            CaseSeverity.GROSS_MISDEMEANOR: 0.3,
            CaseSeverity.FELONY_4: 0.5,
            CaseSeverity.FELONY_3: 0.6,
            CaseSeverity.FELONY_2: 0.75,
            CaseSeverity.FELONY_1: 0.9,
            CaseSeverity.CAPITAL: 1.0
        }
        features["severity"] = severity_scores.get(case.severity, 0.5)

        # Charge count (normalized)
        features["charge_count"] = min(len(case.charges) / 10, 1.0)

        # Evidence factor (would be NLP-analyzed in production)
        features["evidence_strength"] = 0.5  # Default neutral

        # Prior record (would come from defendant history)
        features["prior_record"] = 0.3  # Default moderate

        # Judge factors
        if judge_scorecard:
            features["judge_conviction_rate"] = judge_scorecard.overall_conviction_rate

            # Get case-type specific rate
            case_type_key = case.primary_type.value if hasattr(case.primary_type, 'value') else case.primary_type
            if case_type_key in judge_scorecard.conviction_rate_by_type:
                features["judge_case_type_rate"] = judge_scorecard.conviction_rate_by_type[case_type_key]
            else:
                features["judge_case_type_rate"] = features["judge_conviction_rate"]

            # Get severity-specific behavior
            severity_key = case.severity.value if hasattr(case.severity, 'value') else case.severity
            if severity_key in judge_scorecard.metrics_by_severity:
                metrics = judge_scorecard.metrics_by_severity[severity_key]
                # Higher follow rate = more predictable
                features["judge_severity_rate"] = metrics.sentencing_guidelines_follow_rate
            else:
                features["judge_severity_rate"] = 0.5
        else:
            features["judge_conviction_rate"] = 0.65  # National average
            features["judge_case_type_rate"] = 0.65
            features["judge_severity_rate"] = 0.5

        # Jurisdiction factors
        if jurisdiction_stats:
            features["jurisdiction_conviction_rate"] = jurisdiction_stats.get("conviction_rate", 0.65)
        else:
            features["jurisdiction_conviction_rate"] = 0.65

        # Similar cases analysis
        if similar_cases:
            resolved = [c for c in similar_cases if c.outcome != CaseOutcome.PENDING]
            if resolved:
                convicted = sum(1 for c in resolved
                               if c.outcome in [CaseOutcome.GUILTY_PLEA, CaseOutcome.CONVICTED])
                features["similar_cases_rate"] = convicted / len(resolved)
            else:
                features["similar_cases_rate"] = 0.5
        else:
            features["similar_cases_rate"] = 0.5

        # Defense quality (would come from attorney stats)
        features["defense_quality"] = 0.5  # Default neutral

        return features

    def _calculate_probabilities(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate outcome probabilities from features."""
        # Base conviction probability
        conviction_factors = [
            features["severity"] * self._feature_weights["severity"],
            features["charge_count"] * self._feature_weights["charge_count"],
            features["prior_record"] * self._feature_weights["prior_record"],
            features["evidence_strength"] * self._feature_weights["evidence_strength"],
            features["judge_conviction_rate"] * self._feature_weights["judge_conviction_rate"],
            features["judge_case_type_rate"] * self._feature_weights["judge_case_type_rate"],
            features["jurisdiction_conviction_rate"] * self._feature_weights["jurisdiction_conviction_rate"],
            (1 - features["defense_quality"]) * self._feature_weights["defense_quality"]
        ]

        base_conviction = sum(conviction_factors)

        # Normalize to probability
        # Higher severity cases more likely to end in plea
        plea_modifier = 0.6 + (features["severity"] * 0.3)

        # Calculate raw probabilities
        raw_convicted = base_conviction * 0.4
        raw_plea = base_conviction * plea_modifier
        raw_dismissed = (1 - base_conviction) * 0.4
        raw_acquitted = (1 - base_conviction) * 0.3
        raw_other = 0.1

        # Normalize
        total = raw_convicted + raw_plea + raw_dismissed + raw_acquitted + raw_other
        probabilities = {
            CaseOutcome.CONVICTED.value: raw_convicted / total,
            CaseOutcome.GUILTY_PLEA.value: raw_plea / total,
            CaseOutcome.DISMISSED.value: raw_dismissed / total,
            CaseOutcome.ACQUITTED.value: raw_acquitted / total,
            "other": raw_other / total
        }

        return probabilities

    def _identify_factors(
        self,
        features: Dict[str, float],
        probabilities: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify key factors influencing the prediction."""
        factors = []

        # Severity impact
        if features["severity"] > 0.7:
            factors.append({
                "factor": "case_severity",
                "impact": "high",
                "description": "High severity charges significantly impact likely outcome",
                "weight": self._feature_weights["severity"]
            })
        elif features["severity"] < 0.3:
            factors.append({
                "factor": "case_severity",
                "impact": "low",
                "description": "Minor charges favor dismissal or reduced outcomes",
                "weight": self._feature_weights["severity"]
            })

        # Judge patterns
        if features["judge_conviction_rate"] > 0.75:
            factors.append({
                "factor": "judge_pattern",
                "impact": "high",
                "description": "Assigned judge has high conviction rate history",
                "weight": self._feature_weights["judge_conviction_rate"]
            })
        elif features["judge_conviction_rate"] < 0.5:
            factors.append({
                "factor": "judge_pattern",
                "impact": "favorable",
                "description": "Assigned judge has lower than average conviction rate",
                "weight": self._feature_weights["judge_conviction_rate"]
            })

        # Multiple charges
        if features["charge_count"] > 0.5:
            factors.append({
                "factor": "charge_count",
                "impact": "high",
                "description": "Multiple charges increase leverage for plea negotiations",
                "weight": self._feature_weights["charge_count"]
            })

        # Prior record
        if features["prior_record"] > 0.6:
            factors.append({
                "factor": "prior_record",
                "impact": "negative",
                "description": "Prior criminal history may influence outcome",
                "weight": self._feature_weights["prior_record"]
            })

        return factors

    def get_confidence_factors(self, result: PredictionResult) -> Dict[str, Any]:
        """
        Get explanation of confidence level.

        Args:
            result: The prediction result

        Returns:
            Dict explaining the confidence factors
        """
        confidence = result.confidence

        if confidence >= 0.8:
            level = "high"
            explanation = "Strong historical patterns and clear case factors"
        elif confidence >= 0.6:
            level = "moderate"
            explanation = "Reasonable historical patterns with some variability"
        elif confidence >= 0.4:
            level = "low"
            explanation = "Limited historical data or mixed signals"
        else:
            level = "very_low"
            explanation = "Insufficient data or highly unusual case"

        return {
            "confidence_score": confidence,
            "confidence_level": level,
            "explanation": explanation,
            "top_factors": result.factors[:3],
            "recommendation": (
                "This prediction should be considered alongside professional "
                "legal analysis and advice."
            )
        }


class OutcomeExplainer:
    """Utility for explaining prediction outcomes to users."""

    @staticmethod
    def explain_prediction(result: PredictionResult) -> str:
        """
        Generate a human-readable explanation of a prediction.

        Args:
            result: The prediction result

        Returns:
            Human-readable explanation
        """
        explanation = []

        # Main prediction
        confidence_pct = result.confidence * 100
        explanation.append(
            f"Predicted Outcome: {result.prediction.replace('_', ' ').title()}"
        )
        explanation.append(f"Confidence: {confidence_pct:.1f}%")
        explanation.append("")

        # Probability breakdown
        explanation.append("Outcome Probabilities:")
        for outcome, prob in sorted(result.probabilities.items(),
                                   key=lambda x: x[1], reverse=True):
            if prob > 0.05:
                explanation.append(f"  - {outcome.replace('_', ' ').title()}: {prob*100:.1f}%")

        explanation.append("")

        # Key factors
        if result.factors:
            explanation.append("Key Factors:")
            for factor in result.factors[:5]:
                explanation.append(f"  - {factor['description']}")

        # Disclaimer
        explanation.append("")
        explanation.append("DISCLAIMER: " + result.disclaimer)

        return "\n".join(explanation)
