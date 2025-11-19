"""
Case Analytics Engine

Analytics for case patterns, outcomes, and trends.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
import numpy as np
from collections import defaultdict

from echolex.models.case import Case, CaseType, CaseSeverity, CaseOutcome, CaseStatus


class CaseAnalytics:
    """
    Case analytics engine for analyzing case patterns and trends.
    """

    def analyze_outcomes(
        self,
        cases: List[Case],
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze case outcomes.

        Args:
            cases: List of cases to analyze
            group_by: Optional grouping (type, severity, year)

        Returns:
            Dict with outcome statistics
        """
        if not cases:
            return {"total": 0, "outcomes": {}}

        resolved = [c for c in cases if c.outcome != CaseOutcome.PENDING]

        outcome_counts = defaultdict(int)
        for case in resolved:
            outcome = case.outcome.value if hasattr(case.outcome, 'value') else case.outcome
            outcome_counts[outcome] += 1

        total = len(resolved)
        outcome_rates = {k: v / total for k, v in outcome_counts.items()}

        result = {
            "total": len(cases),
            "resolved": total,
            "pending": len(cases) - total,
            "outcomes": dict(outcome_counts),
            "rates": outcome_rates
        }

        if group_by:
            grouped_analysis = self._analyze_by_group(resolved, group_by)
            result["by_group"] = grouped_analysis

        return result

    def analyze_sentencing(self, cases: List[Case]) -> Dict[str, Any]:
        """
        Analyze sentencing patterns.

        Args:
            cases: List of cases to analyze

        Returns:
            Dict with sentencing statistics
        """
        sentenced = [c for c in cases if c.sentences]

        if not sentenced:
            return {
                "total_sentenced": 0,
                "incarceration": {},
                "fines": {},
                "probation": {}
            }

        # Incarceration analysis
        incarceration_months = []
        fine_amounts = []
        probation_months = []

        for case in sentenced:
            case_incarceration = sum(s.incarceration_months for s in case.sentences)
            if case_incarceration > 0:
                incarceration_months.append(case_incarceration)

            case_fines = sum(s.fine_amount for s in case.sentences)
            if case_fines > 0:
                fine_amounts.append(case_fines)

            case_probation = sum(s.probation_months for s in case.sentences)
            if case_probation > 0:
                probation_months.append(case_probation)

        return {
            "total_sentenced": len(sentenced),
            "incarceration": self._calculate_stats(incarceration_months, "months"),
            "fines": self._calculate_stats(fine_amounts, "amount"),
            "probation": self._calculate_stats(probation_months, "months")
        }

    def analyze_timeline(self, cases: List[Case]) -> Dict[str, Any]:
        """
        Analyze case timelines and durations.

        Args:
            cases: List of cases to analyze

        Returns:
            Dict with timeline statistics
        """
        durations = {
            "filing_to_arraignment": [],
            "filing_to_trial": [],
            "filing_to_disposition": [],
            "trial_to_disposition": []
        }

        for case in cases:
            if case.arraignment_date:
                days = (case.arraignment_date - case.filing_date).days
                if days > 0:
                    durations["filing_to_arraignment"].append(days)

            if case.trial_date:
                days = (case.trial_date - case.filing_date).days
                if days > 0:
                    durations["filing_to_trial"].append(days)

            if case.disposition_date:
                days = (case.disposition_date - case.filing_date).days
                if days > 0:
                    durations["filing_to_disposition"].append(days)

                if case.trial_date:
                    days = (case.disposition_date - case.trial_date).days
                    if days > 0:
                        durations["trial_to_disposition"].append(days)

        return {
            "filing_to_arraignment": self._calculate_stats(durations["filing_to_arraignment"], "days"),
            "filing_to_trial": self._calculate_stats(durations["filing_to_trial"], "days"),
            "filing_to_disposition": self._calculate_stats(durations["filing_to_disposition"], "days"),
            "trial_to_disposition": self._calculate_stats(durations["trial_to_disposition"], "days")
        }

    def analyze_trends(
        self,
        cases: List[Case],
        period: str = "year"
    ) -> Dict[str, Any]:
        """
        Analyze trends over time.

        Args:
            cases: List of cases to analyze
            period: Time period (year, quarter, month)

        Returns:
            Dict with trend data
        """
        grouped = defaultdict(list)

        for case in cases:
            if not case.filing_date:
                continue

            if period == "year":
                key = case.filing_date.year
            elif period == "quarter":
                q = (case.filing_date.month - 1) // 3 + 1
                key = f"{case.filing_date.year}-Q{q}"
            else:  # month
                key = f"{case.filing_date.year}-{case.filing_date.month:02d}"

            grouped[key].append(case)

        trends = {}
        for period_key, period_cases in sorted(grouped.items()):
            resolved = [c for c in period_cases if c.outcome != CaseOutcome.PENDING]
            convicted = sum(1 for c in resolved
                           if c.outcome in [CaseOutcome.GUILTY_PLEA, CaseOutcome.CONVICTED])

            trends[period_key] = {
                "total": len(period_cases),
                "resolved": len(resolved),
                "conviction_rate": convicted / len(resolved) if resolved else 0,
                "by_severity": self._count_by_severity(period_cases)
            }

        return trends

    def analyze_charges(self, cases: List[Case]) -> Dict[str, Any]:
        """
        Analyze charge patterns.

        Args:
            cases: List of cases to analyze

        Returns:
            Dict with charge statistics
        """
        total_charges = 0
        charges_per_case = []
        charge_types = defaultdict(int)
        enhancement_count = 0

        for case in cases:
            num_charges = len(case.charges)
            total_charges += num_charges
            charges_per_case.append(num_charges)

            for charge in case.charges:
                charge_type = charge.case_type.value if hasattr(charge.case_type, 'value') else charge.case_type
                charge_types[charge_type] += 1
                if charge.enhanced:
                    enhancement_count += 1

        return {
            "total_charges": total_charges,
            "avg_charges_per_case": float(np.mean(charges_per_case)) if charges_per_case else 0,
            "max_charges": max(charges_per_case) if charges_per_case else 0,
            "charge_distribution": dict(charge_types),
            "enhancement_rate": enhancement_count / total_charges if total_charges else 0
        }

    def _analyze_by_group(self, cases: List[Case], group_by: str) -> Dict[str, Dict[str, Any]]:
        """Analyze cases grouped by a specific field."""
        grouped = defaultdict(list)

        for case in cases:
            if group_by == "type":
                key = case.primary_type.value if hasattr(case.primary_type, 'value') else case.primary_type
            elif group_by == "severity":
                key = case.severity.value if hasattr(case.severity, 'value') else case.severity
            elif group_by == "year":
                key = str(case.filing_date.year) if case.filing_date else "unknown"
            else:
                key = "all"

            grouped[key].append(case)

        result = {}
        for key, group_cases in grouped.items():
            outcome_counts = defaultdict(int)
            for case in group_cases:
                outcome = case.outcome.value if hasattr(case.outcome, 'value') else case.outcome
                outcome_counts[outcome] += 1

            total = len(group_cases)
            result[key] = {
                "count": total,
                "outcomes": dict(outcome_counts),
                "rates": {k: v / total for k, v in outcome_counts.items()}
            }

        return result

    def _calculate_stats(self, values: List[float], unit: str) -> Dict[str, Any]:
        """Calculate statistical summary for a list of values."""
        if not values:
            return {
                "count": 0,
                "unit": unit
            }

        return {
            "count": len(values),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std": float(np.std(values)),
            "min": float(min(values)),
            "max": float(max(values)),
            "unit": unit
        }

    def _count_by_severity(self, cases: List[Case]) -> Dict[str, int]:
        """Count cases by severity level."""
        counts = defaultdict(int)
        for case in cases:
            severity = case.severity.value if hasattr(case.severity, 'value') else case.severity
            counts[severity] += 1
        return dict(counts)
