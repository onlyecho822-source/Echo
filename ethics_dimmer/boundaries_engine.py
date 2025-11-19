"""
Boundaries Engine (ACL)

Enforces invariant safety rules that apply across ALL ethics levels.
The dimmer adjusts mindset, not laws.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Set, Optional
from enum import Enum
import re


class BoundaryType(Enum):
    """Types of boundaries that can be enforced."""
    DATA_ACCESS = "data_access"
    ACTION = "action"
    NETWORK = "network"
    FINANCIAL = "financial"
    PRIVACY = "privacy"
    COMPLIANCE = "compliance"


class ViolationSeverity(Enum):
    """Severity of a boundary violation."""
    BLOCKED = "blocked"       # Action completely blocked
    WARNING = "warning"       # Action allowed with warning
    LOGGED = "logged"         # Action allowed, logged only


@dataclass
class Boundary:
    """A single boundary rule."""
    id: str
    name: str
    boundary_type: BoundaryType
    description: str
    pattern: str  # Regex pattern to match violations
    severity: ViolationSeverity
    enabled: bool = True


@dataclass
class BoundaryViolation:
    """Record of a boundary violation."""
    boundary_id: str
    boundary_name: str
    severity: ViolationSeverity
    matched_content: str
    context: Dict[str, Any]
    blocked: bool


class BoundariesEngine:
    """
    Enforces invariant boundaries across all ethics levels.

    INVARIANT RULES (apply to ALL levels):
    - PUBLIC DATA ONLY
    - No actionable harm
    - No evasion
    - No unauthorized access
    - No operational exploits
    - No private-network interaction
    - No financial misconduct
    """

    # Core invariant boundaries that cannot be modified
    INVARIANT_BOUNDARIES: List[Boundary] = [
        Boundary(
            id="DATA_001",
            name="Public Data Only",
            boundary_type=BoundaryType.DATA_ACCESS,
            description="System may only access publicly available data",
            pattern=r"(private|classified|confidential|secret)\s*(data|access|information)",
            severity=ViolationSeverity.BLOCKED,
        ),
        Boundary(
            id="ACTION_001",
            name="No Actionable Harm",
            boundary_type=BoundaryType.ACTION,
            description="System cannot produce instructions for harm",
            pattern=r"(how\s+to|instructions?\s+for|steps?\s+to)\s*(harm|injure|damage|destroy|kill)",
            severity=ViolationSeverity.BLOCKED,
        ),
        Boundary(
            id="ACTION_002",
            name="No Evasion",
            boundary_type=BoundaryType.ACTION,
            description="System cannot help evade detection or security",
            pattern=r"(evade|bypass|circumvent|avoid)\s*(detection|security|monitoring|tracking)",
            severity=ViolationSeverity.BLOCKED,
        ),
        Boundary(
            id="ACCESS_001",
            name="No Unauthorized Access",
            boundary_type=BoundaryType.DATA_ACCESS,
            description="System cannot facilitate unauthorized access",
            pattern=r"(hack|break\s+into|unauthorized\s+access|crack\s+password)",
            severity=ViolationSeverity.BLOCKED,
        ),
        Boundary(
            id="EXPLOIT_001",
            name="No Operational Exploits",
            boundary_type=BoundaryType.ACTION,
            description="System cannot provide working exploit code",
            pattern=r"(exploit\s+code|payload|shellcode|malware|virus|trojan)",
            severity=ViolationSeverity.BLOCKED,
        ),
        Boundary(
            id="NETWORK_001",
            name="No Private Network Interaction",
            boundary_type=BoundaryType.NETWORK,
            description="System cannot access private networks",
            pattern=r"(internal\s+network|intranet|private\s+ip|192\.168\.|10\.\d+\.|172\.(1[6-9]|2[0-9]|3[01])\.)",
            severity=ViolationSeverity.BLOCKED,
        ),
        Boundary(
            id="FINANCIAL_001",
            name="No Financial Misconduct",
            boundary_type=BoundaryType.FINANCIAL,
            description="System cannot facilitate financial crimes",
            pattern=r"(money\s+laundering|fraud|embezzlement|insider\s+trading|tax\s+evasion)",
            severity=ViolationSeverity.BLOCKED,
        ),
        Boundary(
            id="PRIVACY_001",
            name="No PII Exposure",
            boundary_type=BoundaryType.PRIVACY,
            description="System cannot expose personal information",
            pattern=r"(social\s+security|credit\s+card|bank\s+account)\s*(number|info)",
            severity=ViolationSeverity.BLOCKED,
        ),
    ]

    def __init__(self, custom_boundaries: Optional[List[Boundary]] = None):
        # Start with invariant boundaries (immutable)
        self._invariant_boundaries = self.INVARIANT_BOUNDARIES.copy()

        # Custom boundaries can be added/modified
        self._custom_boundaries: List[Boundary] = custom_boundaries or []

        # Track violations
        self._violations: List[BoundaryViolation] = []

        # Whitelist patterns (allowed even if matching)
        self._whitelist: Set[str] = set()

    @property
    def all_boundaries(self) -> List[Boundary]:
        """Get all active boundaries."""
        return self._invariant_boundaries + self._custom_boundaries

    def add_custom_boundary(self, boundary: Boundary) -> bool:
        """
        Add a custom boundary.

        Note: Cannot override invariant boundaries.

        Args:
            boundary: The boundary to add

        Returns:
            True if added, False if it conflicts with invariant
        """
        # Check for conflict with invariant boundaries
        for inv in self._invariant_boundaries:
            if boundary.id == inv.id:
                return False

        self._custom_boundaries.append(boundary)
        return True

    def remove_custom_boundary(self, boundary_id: str) -> bool:
        """Remove a custom boundary by ID."""
        for i, b in enumerate(self._custom_boundaries):
            if b.id == boundary_id:
                self._custom_boundaries.pop(i)
                return True
        return False

    def add_to_whitelist(self, pattern: str) -> None:
        """Add a pattern to the whitelist."""
        self._whitelist.add(pattern)

    def check(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[BoundaryViolation]:
        """
        Check content against all boundaries.

        Args:
            content: The content to check
            context: Additional context about the check

        Returns:
            List of violations found
        """
        context = context or {}
        violations = []
        content_lower = content.lower()

        # Check whitelist first
        for whitelist_pattern in self._whitelist:
            if re.search(whitelist_pattern, content_lower, re.IGNORECASE):
                # Content is whitelisted
                return []

        # Check all boundaries
        for boundary in self.all_boundaries:
            if not boundary.enabled:
                continue

            if re.search(boundary.pattern, content_lower, re.IGNORECASE):
                violation = BoundaryViolation(
                    boundary_id=boundary.id,
                    boundary_name=boundary.name,
                    severity=boundary.severity,
                    matched_content=content[:200],  # Truncate for safety
                    context=context,
                    blocked=boundary.severity == ViolationSeverity.BLOCKED,
                )
                violations.append(violation)
                self._violations.append(violation)

        return violations

    def is_allowed(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, List[BoundaryViolation]]:
        """
        Check if content is allowed.

        Args:
            content: The content to check
            context: Additional context

        Returns:
            Tuple of (allowed, violations)
        """
        violations = self.check(content, context)

        # Check for blocking violations
        blocked = any(v.blocked for v in violations)

        return (not blocked, violations)

    def get_violations_summary(self) -> Dict[str, Any]:
        """Get summary of all recorded violations."""
        if not self._violations:
            return {
                "total": 0,
                "blocked": 0,
                "warnings": 0,
                "by_type": {},
            }

        by_type: Dict[str, int] = {}
        blocked = 0
        warnings = 0

        for v in self._violations:
            if v.blocked:
                blocked += 1
            else:
                warnings += 1

            # Find boundary type
            for b in self.all_boundaries:
                if b.id == v.boundary_id:
                    type_name = b.boundary_type.value
                    by_type[type_name] = by_type.get(type_name, 0) + 1
                    break

        return {
            "total": len(self._violations),
            "blocked": blocked,
            "warnings": warnings,
            "by_type": by_type,
        }

    def reset_violations(self) -> None:
        """Clear violation history."""
        self._violations.clear()

    def get_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        return {
            "invariant_boundaries": len(self._invariant_boundaries),
            "custom_boundaries": len(self._custom_boundaries),
            "whitelist_patterns": len(self._whitelist),
            "total_violations": len(self._violations),
            "violations_summary": self.get_violations_summary(),
        }

    def validate_output(
        self,
        output: str,
        ethics_level: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate output before it's returned to the user.

        This is the final safety gate.

        Args:
            output: The generated output
            ethics_level: Current ethics level (1-5)
            context: Additional context

        Returns:
            Validation result with allowed status and any modifications
        """
        context = context or {}
        context["ethics_level"] = ethics_level

        allowed, violations = self.is_allowed(output, context)

        result = {
            "allowed": allowed,
            "violations": [
                {
                    "boundary": v.boundary_name,
                    "severity": v.severity.value,
                    "blocked": v.blocked,
                }
                for v in violations
            ],
            "modified": False,
            "output": output,
        }

        if not allowed:
            # Content blocked - provide safe alternative
            result["output"] = (
                "[CONTENT BLOCKED: This output violated safety boundaries. "
                f"Violations: {', '.join(v.boundary_name for v in violations if v.blocked)}]"
            )
            result["modified"] = True

        return result
