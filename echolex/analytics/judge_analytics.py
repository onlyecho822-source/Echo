"""
Judge Analytics Engine

Comprehensive analytics for judicial behavior, patterns, and scorecard generation.
Tracks proforma follow rates and bench performance metrics.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import numpy as np
from collections import defaultdict

from echolex.models.judge import Judge, JudgeScorecard, BenchMetrics
from echolex.models.case import Case, CaseType, CaseSeverity, CaseOutcome


class JudgeAnalytics:
    """
    Judge analytics engine for generating scorecards and analyzing patterns.

    Provides comprehensive metrics on judicial behavior including:
    - Proforma/guidelines follow rates
    - Sentencing patterns
    - Motion grant rates
    - Appeal reversal rates
    - Temporal trends
    """

    def __init__(self):
        """Initialize the judge analytics engine."""
        self._cache: Dict[UUID, Tuple[JudgeScorecard, datetime]] = {}
        self._cache_ttl = timedelta(hours=1)

    def generate_scorecard(
        self,
        judge: Judge,
        cases: List[Case],
        include_temporal: bool = True
    ) -> JudgeScorecard:
        """
        Generate a comprehensive scorecard for a judge.

        Args:
            judge: The judge to analyze
            cases: List of cases handled by this judge
            include_temporal: Whether to include yearly breakdowns

        Returns:
            Complete JudgeScorecard with all metrics
        """
        scorecard = JudgeScorecard(judge_id=judge.id)

        if not cases:
            scorecard.data_confidence_score = 0.0
            return scorecard

        # Calculate overall bench metrics
        scorecard.bench_metrics = self._calculate_bench_metrics(cases)

        # Calculate metrics by case type
        cases_by_type = self._group_by_case_type(cases)
        for case_type, type_cases in cases_by_type.items():
            if len(type_cases) >= 5:  # Minimum sample size
                scorecard.metrics_by_case_type[case_type] = self._calculate_bench_metrics(type_cases)

        # Calculate metrics by severity
        cases_by_severity = self._group_by_severity(cases)
        for severity, sev_cases in cases_by_severity.items():
            if len(sev_cases) >= 5:
                scorecard.metrics_by_severity[severity] = self._calculate_bench_metrics(sev_cases)

        # Calculate temporal trends
        if include_temporal:
            cases_by_year = self._group_by_year(cases)
            for year, year_cases in cases_by_year.items():
                if len(year_cases) >= 10:
                    scorecard.yearly_metrics[year] = self._calculate_bench_metrics(year_cases)

        # Calculate conviction rates
        scorecard.overall_conviction_rate = self._calculate_conviction_rate(cases)
        for case_type, type_cases in cases_by_type.items():
            if len(type_cases) >= 5:
                scorecard.conviction_rate_by_type[case_type] = self._calculate_conviction_rate(type_cases)

        # Sentencing distribution
        sentencing_stats = self._calculate_sentencing_stats(cases)
        scorecard.incarceration_rate = sentencing_stats["incarceration_rate"]
        scorecard.avg_incarceration_months = sentencing_stats["avg_months"]
        scorecard.avg_fine_amount = sentencing_stats["avg_fine"]
        scorecard.avg_probation_months = sentencing_stats["avg_probation"]

        # Data confidence score based on sample sizes
        scorecard.data_confidence_score = self._calculate_confidence_score(cases)

        return scorecard

    def _calculate_bench_metrics(self, cases: List[Case]) -> BenchMetrics:
        """Calculate bench metrics from a set of cases."""
        metrics = BenchMetrics()

        if not cases:
            return metrics

        metrics.total_cases_analyzed = len(cases)

        # Sentencing guidelines follow rate
        sentenced_cases = [c for c in cases if c.sentences]
        if sentenced_cases:
            metrics.sentencing_sample_size = len(sentenced_cases)
            # Calculate deviation from guidelines (simulated)
            deviations = []
            for case in sentenced_cases:
                for sentence in case.sentences:
                    # In real implementation, compare to actual guidelines
                    deviations.append(self._calculate_guideline_deviation(case, sentence))
            if deviations:
                metrics.avg_sentence_vs_guidelines = float(np.mean(deviations))
                # Follow rate = cases within +/- 10% of guidelines
                within_guidelines = sum(1 for d in deviations if abs(d) <= 0.1)
                metrics.sentencing_guidelines_follow_rate = within_guidelines / len(deviations)

        # Outcome-based metrics
        outcomes = [c.outcome for c in cases if c.outcome != CaseOutcome.PENDING]
        if outcomes:
            guilty = sum(1 for o in outcomes if o in [CaseOutcome.GUILTY_PLEA, CaseOutcome.CONVICTED])
            plea = sum(1 for o in outcomes if o == CaseOutcome.GUILTY_PLEA)
            metrics.plea_agreement_acceptance_rate = plea / len(outcomes) if outcomes else 0.0

        # Calculate motion grant rates (simulated based on case events)
        motion_decisions = self._extract_motion_decisions(cases)
        if motion_decisions:
            metrics.motion_sample_size = len(motion_decisions)
            granted = sum(1 for m in motion_decisions if m["granted"])
            metrics.motion_grant_rate = granted / len(motion_decisions)

        # Continuance grant rate
        continuance_decisions = self._extract_continuance_decisions(cases)
        if continuance_decisions:
            granted = sum(1 for c in continuance_decisions if c["granted"])
            metrics.continuance_grant_rate = granted / len(continuance_decisions)

        # Trial metrics
        trial_cases = [c for c in cases if any(e.event_type == "trial" for e in c.events)]
        if trial_cases:
            jury = sum(1 for c in trial_cases if self._is_jury_trial(c))
            metrics.jury_trial_rate = jury / len(trial_cases)
            metrics.bench_trial_rate = 1 - metrics.jury_trial_rate
            mistrials = sum(1 for c in trial_cases if c.outcome == CaseOutcome.MISTRIAL)
            metrics.mistrial_rate = mistrials / len(trial_cases)

        # Calculate average trial duration
        durations = []
        for case in cases:
            if case.trial_date and case.disposition_date:
                duration = (case.disposition_date - case.trial_date).days
                if duration > 0:
                    durations.append(duration)
        if durations:
            metrics.avg_trial_duration_days = float(np.mean(durations))

        # Time to disposition
        disposition_times = []
        for case in cases:
            if case.disposition_date:
                time_to_disp = (case.disposition_date - case.filing_date).days
                if time_to_disp > 0:
                    disposition_times.append(time_to_disp)
        if disposition_times:
            metrics.avg_time_to_disposition_days = float(np.mean(disposition_times))

        # Cases per year (annualized)
        if cases:
            date_range = self._get_date_range(cases)
            if date_range > 0:
                metrics.cases_per_year = int(len(cases) / (date_range / 365))

        # Probation and alternative sentencing rates
        if sentenced_cases:
            probation_cases = sum(1 for c in sentenced_cases
                                  if any(s.probation_months > 0 for s in c.sentences))
            metrics.probation_preference_rate = probation_cases / len(sentenced_cases)

            alternative_cases = sum(1 for c in sentenced_cases
                                    if any(s.community_service_hours > 0 for s in c.sentences))
            metrics.alternative_sentencing_rate = alternative_cases / len(sentenced_cases)

            enhanced_cases = sum(1 for c in cases
                                 if any(ch.enhanced for ch in c.charges))
            metrics.enhancement_application_rate = enhanced_cases / len(cases)

        return metrics

    def _calculate_guideline_deviation(self, case: Case, sentence: Any) -> float:
        """
        Calculate how much a sentence deviates from guidelines.

        Returns:
            Deviation as a percentage (-1.0 to 1.0+)
            Negative = more lenient, Positive = more harsh
        """
        # This would connect to actual sentencing guidelines in production
        # For now, use a simplified calculation based on severity
        severity_base = {
            CaseSeverity.INFRACTION: 0,
            CaseSeverity.PETTY_OFFENSE: 0,
            CaseSeverity.MISDEMEANOR: 3,
            CaseSeverity.GROSS_MISDEMEANOR: 6,
            CaseSeverity.FELONY_4: 12,
            CaseSeverity.FELONY_3: 24,
            CaseSeverity.FELONY_2: 60,
            CaseSeverity.FELONY_1: 120,
            CaseSeverity.CAPITAL: 240,
        }

        expected = severity_base.get(case.severity, 0)
        if expected == 0:
            return 0.0

        actual = sentence.incarceration_months
        return (actual - expected) / expected

    def _extract_motion_decisions(self, cases: List[Case]) -> List[Dict[str, Any]]:
        """Extract motion decisions from case events."""
        decisions = []
        for case in cases:
            for event in case.events:
                if "motion" in event.event_type.lower():
                    decisions.append({
                        "case_id": case.id,
                        "event_id": event.id,
                        "granted": event.outcome == "granted" if event.outcome else False
                    })
        return decisions

    def _extract_continuance_decisions(self, cases: List[Case]) -> List[Dict[str, Any]]:
        """Extract continuance decisions from case events."""
        decisions = []
        for case in cases:
            for event in case.events:
                if "continuance" in event.event_type.lower():
                    decisions.append({
                        "case_id": case.id,
                        "event_id": event.id,
                        "granted": event.outcome == "granted" if event.outcome else False
                    })
        return decisions

    def _is_jury_trial(self, case: Case) -> bool:
        """Determine if a case was a jury trial."""
        for event in case.events:
            if "jury" in event.event_type.lower() or "jury" in event.description.lower():
                return True
        return False

    def _calculate_conviction_rate(self, cases: List[Case]) -> float:
        """Calculate conviction rate for a set of cases."""
        resolved = [c for c in cases if c.outcome != CaseOutcome.PENDING]
        if not resolved:
            return 0.0

        convicted = sum(1 for c in resolved
                        if c.outcome in [CaseOutcome.GUILTY_PLEA, CaseOutcome.CONVICTED])
        return convicted / len(resolved)

    def _calculate_sentencing_stats(self, cases: List[Case]) -> Dict[str, float]:
        """Calculate sentencing statistics."""
        stats = {
            "incarceration_rate": 0.0,
            "avg_months": 0.0,
            "avg_fine": 0.0,
            "avg_probation": 0.0
        }

        sentenced = [c for c in cases if c.sentences]
        if not sentenced:
            return stats

        incarceration_count = 0
        total_months = []
        total_fines = []
        total_probation = []

        for case in sentenced:
            case_incarceration = sum(s.incarceration_months for s in case.sentences)
            if case_incarceration > 0:
                incarceration_count += 1
                total_months.append(case_incarceration)

            case_fines = sum(s.fine_amount for s in case.sentences)
            if case_fines > 0:
                total_fines.append(case_fines)

            case_probation = sum(s.probation_months for s in case.sentences)
            if case_probation > 0:
                total_probation.append(case_probation)

        stats["incarceration_rate"] = incarceration_count / len(sentenced)
        stats["avg_months"] = float(np.mean(total_months)) if total_months else 0.0
        stats["avg_fine"] = float(np.mean(total_fines)) if total_fines else 0.0
        stats["avg_probation"] = float(np.mean(total_probation)) if total_probation else 0.0

        return stats

    def _calculate_confidence_score(self, cases: List[Case]) -> float:
        """Calculate data confidence score based on sample sizes."""
        if not cases:
            return 0.0

        # More cases = higher confidence, with diminishing returns
        case_score = min(1.0, len(cases) / 100)

        # Variety of case types improves confidence
        types = len(set(c.primary_type for c in cases))
        type_score = min(1.0, types / 10)

        # Recent cases weighted more
        now = datetime.utcnow().date()
        recent = sum(1 for c in cases
                     if c.filing_date and (now - c.filing_date).days < 365)
        recency_score = recent / len(cases) if cases else 0

        return (case_score * 0.5 + type_score * 0.2 + recency_score * 0.3)

    def _group_by_case_type(self, cases: List[Case]) -> Dict[str, List[Case]]:
        """Group cases by their primary type."""
        grouped = defaultdict(list)
        for case in cases:
            grouped[case.primary_type.value if hasattr(case.primary_type, 'value')
                    else case.primary_type].append(case)
        return dict(grouped)

    def _group_by_severity(self, cases: List[Case]) -> Dict[str, List[Case]]:
        """Group cases by severity level."""
        grouped = defaultdict(list)
        for case in cases:
            grouped[case.severity.value if hasattr(case.severity, 'value')
                    else case.severity].append(case)
        return dict(grouped)

    def _group_by_year(self, cases: List[Case]) -> Dict[int, List[Case]]:
        """Group cases by filing year."""
        grouped = defaultdict(list)
        for case in cases:
            if case.filing_date:
                grouped[case.filing_date.year].append(case)
        return dict(grouped)

    def _get_date_range(self, cases: List[Case]) -> int:
        """Get the date range in days covered by cases."""
        dates = [c.filing_date for c in cases if c.filing_date]
        if not dates:
            return 0
        return (max(dates) - min(dates)).days or 1

    def compare_judges(
        self,
        judges: List[Judge],
        cases_by_judge: Dict[UUID, List[Case]],
        metrics: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare multiple judges across specified metrics.

        Args:
            judges: List of judges to compare
            cases_by_judge: Dict mapping judge ID to their cases
            metrics: List of metric names to compare

        Returns:
            Dict mapping metric name to judge scores
        """
        comparison = {}

        scorecards = {}
        for judge in judges:
            cases = cases_by_judge.get(judge.id, [])
            scorecards[judge.id] = self.generate_scorecard(judge, cases)

        for metric in metrics:
            comparison[metric] = {}
            for judge in judges:
                scorecard = scorecards[judge.id]
                value = self._get_metric_value(scorecard, metric)
                comparison[metric][str(judge.id)] = value

        return comparison

    def _get_metric_value(self, scorecard: JudgeScorecard, metric: str) -> float:
        """Get a specific metric value from a scorecard."""
        if hasattr(scorecard.bench_metrics, metric):
            return getattr(scorecard.bench_metrics, metric)
        elif hasattr(scorecard, metric):
            return getattr(scorecard, metric)
        return 0.0

    def identify_patterns(self, scorecard: JudgeScorecard) -> List[str]:
        """
        Identify notable patterns in judicial behavior.

        Args:
            scorecard: The judge's scorecard

        Returns:
            List of identified patterns
        """
        patterns = []
        metrics = scorecard.bench_metrics

        # Sentencing patterns
        if metrics.avg_sentence_vs_guidelines < -0.2:
            patterns.append("Consistently lenient sentencing (20%+ below guidelines)")
        elif metrics.avg_sentence_vs_guidelines > 0.2:
            patterns.append("Consistently harsh sentencing (20%+ above guidelines)")

        # Motion patterns
        if metrics.motion_grant_rate > 0.7:
            patterns.append("High motion grant rate (70%+)")
        elif metrics.motion_grant_rate < 0.3:
            patterns.append("Low motion grant rate (below 30%)")

        # Trial patterns
        if metrics.jury_trial_rate > 0.8:
            patterns.append("Strong preference for jury trials")
        elif metrics.bench_trial_rate > 0.7:
            patterns.append("Strong preference for bench trials")

        # Reversal rate
        if metrics.reversal_rate > 0.3:
            patterns.append("High appeal reversal rate (30%+)")

        # Efficiency
        if metrics.avg_time_to_disposition_days > 180:
            patterns.append("Extended case duration (180+ days average)")
        elif metrics.avg_time_to_disposition_days < 60:
            patterns.append("Rapid case disposition (under 60 days)")

        # Probation preference
        if metrics.probation_preference_rate > 0.6:
            patterns.append("Strong preference for probation over incarceration")

        return patterns


class JudgeRanking:
    """Utility for ranking judges by various criteria."""

    @staticmethod
    def rank_by_metric(
        scorecards: List[JudgeScorecard],
        metric: str,
        ascending: bool = True
    ) -> List[Tuple[UUID, float]]:
        """
        Rank judges by a specific metric.

        Args:
            scorecards: List of judge scorecards
            metric: Metric to rank by
            ascending: Sort order

        Returns:
            List of (judge_id, value) tuples sorted by metric
        """
        rankings = []
        for sc in scorecards:
            if hasattr(sc.bench_metrics, metric):
                value = getattr(sc.bench_metrics, metric)
            elif hasattr(sc, metric):
                value = getattr(sc, metric)
            else:
                value = 0.0
            rankings.append((sc.judge_id, value))

        return sorted(rankings, key=lambda x: x[1], reverse=not ascending)
