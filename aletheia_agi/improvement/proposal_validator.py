"""
Proposal Validator - Improvement Proposal Validation
===================================================

Validates improvement proposals against alignment constraints
and feasibility requirements before they enter the pipeline.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Any, Optional
from datetime import datetime


class ValidationResult(Enum):
    """Results of proposal validation."""
    APPROVED = auto()       # Proposal approved to proceed
    NEEDS_REVISION = auto()  # Proposal needs changes
    REJECTED = auto()       # Proposal rejected


class RiskLevel(Enum):
    """Risk levels for proposals."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class ValidationReport:
    """Report from proposal validation."""
    result: ValidationResult
    risk_level: RiskLevel
    issues: List[str]
    recommendations: List[str]
    required_proofs: List[str]
    required_reviews: int
    timestamp: datetime


class ProposalValidator:
    """
    Validates improvement proposals.

    Checks:
    - Alignment constraint compliance
    - Feasibility
    - Risk assessment
    - Required oversight level
    """

    def __init__(self):
        self._validation_history: List[ValidationReport] = []

        # Risk keywords for detection
        self._high_risk_keywords = [
            'self-modify', 'recursive', 'autonomous',
            'override', 'bypass', 'remove constraint'
        ]

        self._critical_invariants = [
            'corrigibility', 'power limitation', 'human oversight',
            'shutdown', 'interruptibility'
        ]

    def validate_proposal(
        self,
        title: str,
        description: str,
        proposed_changes: List[str],
        expected_benefits: List[str],
        potential_risks: List[str],
        affected_invariants: List[str]
    ) -> ValidationReport:
        """
        Validate an improvement proposal.

        Returns a validation report with result and requirements.
        """
        issues = []
        recommendations = []
        required_proofs = []
        risk_level = RiskLevel.LOW
        required_reviews = 2  # Minimum

        # Check for required fields
        if not title or not description:
            issues.append("Missing title or description")

        if not proposed_changes:
            issues.append("No proposed changes specified")

        if not expected_benefits:
            issues.append("No expected benefits specified")

        # Risk assessment
        all_text = f"{title} {description} {' '.join(proposed_changes)}".lower()

        # Check for high-risk patterns
        for keyword in self._high_risk_keywords:
            if keyword in all_text:
                risk_level = RiskLevel.HIGH
                recommendations.append(
                    f"High-risk keyword detected: '{keyword}' - requires additional scrutiny"
                )

        # Check for critical invariants
        critical_affected = [
            inv for inv in affected_invariants
            if any(crit in inv.lower() for crit in self._critical_invariants)
        ]

        if critical_affected:
            risk_level = RiskLevel.CRITICAL
            required_reviews = 5
            for inv in critical_affected:
                issues.append(f"Affects critical invariant: {inv}")
                required_proofs.append(f"Formal proof of {inv} preservation required")

        # All affected invariants need proofs
        for inv in affected_invariants:
            if inv not in [p.replace("Formal proof of ", "").replace(" preservation required", "")
                          for p in required_proofs]:
                required_proofs.append(f"Proof required for: {inv}")

        # Risk-based requirements
        if risk_level == RiskLevel.MEDIUM:
            required_reviews = 3
        elif risk_level == RiskLevel.HIGH:
            required_reviews = 4
            recommendations.append("Recommend extended simulation period")
        elif risk_level == RiskLevel.CRITICAL:
            required_reviews = 5
            recommendations.append("Requires oversight board approval")
            recommendations.append("Recommend phased deployment with manual gates")

        # Determine result
        if len(issues) > 3 or risk_level == RiskLevel.CRITICAL:
            result = ValidationResult.NEEDS_REVISION
        elif len(issues) > 0:
            result = ValidationResult.NEEDS_REVISION
        else:
            result = ValidationResult.APPROVED

        # Create report
        report = ValidationReport(
            result=result,
            risk_level=risk_level,
            issues=issues,
            recommendations=recommendations,
            required_proofs=required_proofs,
            required_reviews=required_reviews,
            timestamp=datetime.utcnow()
        )

        self._validation_history.append(report)
        return report

    def check_alignment_compliance(
        self,
        proposed_changes: List[str],
        invariants: List[str]
    ) -> Dict[str, Any]:
        """
        Check if proposed changes comply with alignment constraints.

        Returns compliance status and any violations.
        """
        violations = []
        warnings = []

        change_text = " ".join(proposed_changes).lower()

        # Check for obvious violations
        violation_patterns = {
            'disable oversight': "Cannot disable oversight mechanisms",
            'remove constraint': "Cannot remove alignment constraints",
            'bypass verification': "Cannot bypass verification requirements",
            'hide from audit': "Cannot hide actions from audit",
            'unlimited resource': "Cannot acquire unlimited resources"
        }

        for pattern, message in violation_patterns.items():
            if pattern in change_text:
                violations.append(message)

        # Check invariant coverage
        if 'corrigibility' in " ".join(invariants).lower():
            if 'maintain' not in change_text and 'preserve' not in change_text:
                warnings.append(
                    "Changes affecting corrigibility should explicitly maintain it"
                )

        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'warnings': warnings
        }

    def estimate_risk(
        self,
        improvement_type: str,
        affected_invariants: List[str],
        potential_risks: List[str]
    ) -> RiskLevel:
        """Estimate the risk level of a proposal."""
        # Start with base risk by type
        type_risk = {
            'capability': RiskLevel.MEDIUM,
            'efficiency': RiskLevel.LOW,
            'safety': RiskLevel.LOW,
            'alignment': RiskLevel.MEDIUM,
            'interpretability': RiskLevel.LOW
        }

        risk = type_risk.get(improvement_type.lower(), RiskLevel.MEDIUM)

        # Escalate for critical invariants
        for inv in affected_invariants:
            if any(crit in inv.lower() for crit in self._critical_invariants):
                risk = RiskLevel.CRITICAL
                break

        # Escalate based on stated risks
        if len(potential_risks) > 3:
            if risk == RiskLevel.LOW:
                risk = RiskLevel.MEDIUM
            elif risk == RiskLevel.MEDIUM:
                risk = RiskLevel.HIGH

        return risk

    def get_validation_history(self) -> List[ValidationReport]:
        """Get history of validations."""
        return self._validation_history.copy()

    def generate_validation_stats(self) -> Dict[str, Any]:
        """Generate statistics on validations."""
        if not self._validation_history:
            return {'total': 0}

        return {
            'total': len(self._validation_history),
            'by_result': {
                r.name: len([
                    v for v in self._validation_history if v.result == r
                ])
                for r in ValidationResult
            },
            'by_risk': {
                r.name: len([
                    v for v in self._validation_history if v.risk_level == r
                ])
                for r in RiskLevel
            },
            'average_required_reviews': sum(
                v.required_reviews for v in self._validation_history
            ) / len(self._validation_history)
        }
