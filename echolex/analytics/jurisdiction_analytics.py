"""
Jurisdiction Analytics Engine

Analytics for comparing jurisdictions and understanding regional patterns.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import numpy as np
from collections import defaultdict

from echolex.models.jurisdiction import Jurisdiction, JurisdictionStats
from echolex.models.case import Case, CaseType, CaseSeverity, CaseOutcome


class JurisdictionAnalytics:
    """
    Jurisdiction analytics engine for regional legal pattern analysis.
    """

    def generate_stats(
        self,
        jurisdiction: Jurisdiction,
        cases: List[Case],
        period_start: datetime,
        period_end: datetime
    ) -> JurisdictionStats:
        """
        Generate comprehensive statistics for a jurisdiction.

        Args:
            jurisdiction: The jurisdiction to analyze
            cases: List of cases in this jurisdiction
            period_start: Start of analysis period
            period_end: End of analysis period

        Returns:
            JurisdictionStats with all metrics
        """
        stats = JurisdictionStats(
            jurisdiction_id=jurisdiction.id,
            period_start=period_start,
            period_end=period_end
        )

        if not cases:
            return stats

        # Case counts
        stats.total_cases_filed = len(cases)
        stats.total_cases_disposed = sum(
            1 for c in cases if c.outcome != CaseOutcome.PENDING
        )

        # By type
        for case in cases:
            case_type = case.primary_type.value if hasattr(case.primary_type, 'value') else case.primary_type
            stats.cases_by_type[case_type] = stats.cases_by_type.get(case_type, 0) + 1

        # By severity
        for case in cases:
            severity = case.severity.value if hasattr(case.severity, 'value') else case.severity
            stats.cases_by_severity[severity] = stats.cases_by_severity.get(severity, 0) + 1

        # Outcome rates
        resolved = [c for c in cases if c.outcome != CaseOutcome.PENDING]
        if resolved:
            convicted = sum(1 for c in resolved
                          if c.outcome in [CaseOutcome.GUILTY_PLEA, CaseOutcome.CONVICTED])
            dismissed = sum(1 for c in resolved if c.outcome == CaseOutcome.DISMISSED)
            pleas = sum(1 for c in resolved if c.outcome == CaseOutcome.GUILTY_PLEA)
            trials = sum(1 for c in resolved if c.outcome == CaseOutcome.CONVICTED)

            stats.conviction_rate = convicted / len(resolved)
            stats.dismissal_rate = dismissed / len(resolved)
            stats.plea_rate = pleas / len(resolved)
            stats.trial_rate = trials / len(resolved)

        # Timing
        disposition_days = []
        for case in cases:
            if case.disposition_date:
                days = (case.disposition_date - case.filing_date).days
                if days > 0:
                    disposition_days.append(days)

        if disposition_days:
            stats.avg_disposition_days = float(np.mean(disposition_days))
            stats.median_disposition_days = float(np.median(disposition_days))

        # Sentencing
        sentenced = [c for c in cases if c.sentences]
        if sentenced:
            incarceration_months = []
            fine_amounts = []

            for case in sentenced:
                total_months = sum(s.incarceration_months for s in case.sentences)
                if total_months > 0:
                    incarceration_months.append(total_months)

                total_fines = sum(s.fine_amount for s in case.sentences)
                if total_fines > 0:
                    fine_amounts.append(total_fines)

            if incarceration_months:
                stats.avg_incarceration_months = float(np.mean(incarceration_months))
                stats.incarceration_rate = len(incarceration_months) / len(sentenced)

            if fine_amounts:
                stats.avg_fine_amount = float(np.mean(fine_amounts))

        return stats

    def compare_jurisdictions(
        self,
        stats_list: List[JurisdictionStats],
        metrics: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare multiple jurisdictions across specified metrics.

        Args:
            stats_list: List of jurisdiction statistics
            metrics: List of metric names to compare

        Returns:
            Dict mapping metric name to jurisdiction values
        """
        comparison = {}

        for metric in metrics:
            comparison[metric] = {}
            for stats in stats_list:
                if hasattr(stats, metric):
                    value = getattr(stats, metric)
                    comparison[metric][str(stats.jurisdiction_id)] = value

        return comparison

    def identify_regional_patterns(
        self,
        stats_list: List[JurisdictionStats]
    ) -> List[Dict[str, Any]]:
        """
        Identify notable patterns across jurisdictions.

        Args:
            stats_list: List of jurisdiction statistics

        Returns:
            List of identified patterns
        """
        patterns = []

        if not stats_list:
            return patterns

        # Find highest and lowest conviction rates
        by_conviction = sorted(stats_list, key=lambda s: s.conviction_rate)
        if len(by_conviction) >= 2:
            lowest = by_conviction[0]
            highest = by_conviction[-1]

            if highest.conviction_rate - lowest.conviction_rate > 0.2:
                patterns.append({
                    "type": "conviction_variance",
                    "description": f"Significant conviction rate variance: {lowest.conviction_rate:.1%} to {highest.conviction_rate:.1%}",
                    "lowest_jurisdiction": str(lowest.jurisdiction_id),
                    "highest_jurisdiction": str(highest.jurisdiction_id)
                })

        # Find fastest and slowest disposition
        by_disposition = sorted(stats_list, key=lambda s: s.avg_disposition_days)
        if len(by_disposition) >= 2:
            fastest = by_disposition[0]
            slowest = by_disposition[-1]

            if slowest.avg_disposition_days > fastest.avg_disposition_days * 2:
                patterns.append({
                    "type": "disposition_variance",
                    "description": f"Case duration variance: {fastest.avg_disposition_days:.0f} to {slowest.avg_disposition_days:.0f} days",
                    "fastest_jurisdiction": str(fastest.jurisdiction_id),
                    "slowest_jurisdiction": str(slowest.jurisdiction_id)
                })

        # Find sentencing variations
        by_sentencing = sorted(stats_list, key=lambda s: s.avg_incarceration_months)
        if len(by_sentencing) >= 2:
            lenient = by_sentencing[0]
            harsh = by_sentencing[-1]

            if harsh.avg_incarceration_months > lenient.avg_incarceration_months * 1.5:
                patterns.append({
                    "type": "sentencing_variance",
                    "description": f"Sentencing variance: {lenient.avg_incarceration_months:.1f} to {harsh.avg_incarceration_months:.1f} months avg",
                    "lenient_jurisdiction": str(lenient.jurisdiction_id),
                    "harsh_jurisdiction": str(harsh.jurisdiction_id)
                })

        return patterns

    def benchmark_jurisdiction(
        self,
        target_stats: JurisdictionStats,
        peer_stats: List[JurisdictionStats]
    ) -> Dict[str, Any]:
        """
        Benchmark a jurisdiction against its peers.

        Args:
            target_stats: Statistics for the target jurisdiction
            peer_stats: Statistics for peer jurisdictions

        Returns:
            Dict with benchmark results
        """
        if not peer_stats:
            return {"error": "No peer jurisdictions provided"}

        metrics = [
            "conviction_rate",
            "dismissal_rate",
            "avg_disposition_days",
            "avg_incarceration_months",
            "avg_fine_amount"
        ]

        benchmarks = {}

        for metric in metrics:
            target_value = getattr(target_stats, metric, 0)
            peer_values = [getattr(s, metric, 0) for s in peer_stats]

            if not peer_values:
                continue

            peer_mean = float(np.mean(peer_values))
            peer_std = float(np.std(peer_values))

            # Calculate percentile
            below = sum(1 for v in peer_values if v < target_value)
            percentile = below / len(peer_values) * 100

            benchmarks[metric] = {
                "value": target_value,
                "peer_mean": peer_mean,
                "peer_std": peer_std,
                "percentile": percentile,
                "deviation": (target_value - peer_mean) / peer_std if peer_std else 0
            }

        return benchmarks
