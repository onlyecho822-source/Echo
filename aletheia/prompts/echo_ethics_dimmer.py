#!/usr/bin/env python3
"""
Echo Ethics Dimmer - Mode-Based Prompt Orchestration
======================================================
Controls prompt style, logging level, allowed operations, and review paths
for the Aletheia Reality Decoding System.

Modes:
- L5 Safe: Conservative analysis, maximum restrictions
- L4 Defensive: Threat modeling only, controlled speculation
- L3 Investigative: Structural analysis with guided hypothesis
- L2 Black Lens: Full hypothesis enumeration, mandatory human review

Author: Echo Nexus Omega
Version: 1.0.0
"""

import os
import json
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from pathlib import Path


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class EchoMode(Enum):
    """Ethics dimmer levels from most restricted to most open."""
    L5_SAFE = "L5_Safe"
    L4_DEFENSIVE = "L4_Defensive"
    L3_INVESTIGATIVE = "L3_Investigative"
    L2_BLACK_LENS = "L2_Black_Lens"


class LogLevel(Enum):
    """Logging verbosity levels."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"
    FORENSIC = "forensic"


class ReviewPath(Enum):
    """Review requirements for outputs."""
    NONE = "none"
    AUTOMATED = "automated"
    HUMAN_OPTIONAL = "human_optional"
    HUMAN_REQUIRED = "human_required"
    DEVIL_LENS = "devil_lens"


# =============================================================================
# MODE CONFIGURATIONS
# =============================================================================

@dataclass
class ModeConfig:
    """Configuration for an Echo mode."""
    mode: EchoMode
    description: str
    log_level: LogLevel
    review_path: ReviewPath

    # Allowed operations
    allowed_operations: Set[str]
    restricted_operations: Set[str]

    # Prompt behavior
    speculation_allowed: bool
    max_hypothesis_count: int
    require_evidence_citations: bool
    allow_cross_domain: bool

    # Safety constraints
    pii_handling: str  # "redact", "flag", "allow"
    confidence_threshold: float
    require_multi_source: bool


# Default mode configurations
MODE_CONFIGS: Dict[EchoMode, ModeConfig] = {
    EchoMode.L5_SAFE: ModeConfig(
        mode=EchoMode.L5_SAFE,
        description="Conservative analysis mode with maximum restrictions",
        log_level=LogLevel.STANDARD,
        review_path=ReviewPath.AUTOMATED,
        allowed_operations={
            "recall", "summarize", "verify_hash", "check_integrity",
            "list_artifacts", "get_manifest", "validate_schema"
        },
        restricted_operations={
            "hypothesize", "speculate", "cross_reference_external",
            "identify_persons", "geolocate", "temporal_inference",
            "entity_extraction", "relationship_mapping"
        },
        speculation_allowed=False,
        max_hypothesis_count=0,
        require_evidence_citations=True,
        allow_cross_domain=False,
        pii_handling="redact",
        confidence_threshold=0.95,
        require_multi_source=True
    ),

    EchoMode.L4_DEFENSIVE: ModeConfig(
        mode=EchoMode.L4_DEFENSIVE,
        description="Threat modeling and defensive analysis only",
        log_level=LogLevel.DETAILED,
        review_path=ReviewPath.HUMAN_OPTIONAL,
        allowed_operations={
            "recall", "summarize", "verify_hash", "check_integrity",
            "list_artifacts", "get_manifest", "validate_schema",
            "threat_model", "risk_assess", "anomaly_detect",
            "pattern_match", "temporal_sequence"
        },
        restricted_operations={
            "hypothesize_attribution", "speculate_motive",
            "identify_persons", "geolocate_precise"
        },
        speculation_allowed=True,
        max_hypothesis_count=3,
        require_evidence_citations=True,
        allow_cross_domain=False,
        pii_handling="flag",
        confidence_threshold=0.85,
        require_multi_source=True
    ),

    EchoMode.L3_INVESTIGATIVE: ModeConfig(
        mode=EchoMode.L3_INVESTIGATIVE,
        description="Structural analysis with guided hypothesis generation",
        log_level=LogLevel.DETAILED,
        review_path=ReviewPath.HUMAN_OPTIONAL,
        allowed_operations={
            "recall", "summarize", "verify_hash", "check_integrity",
            "list_artifacts", "get_manifest", "validate_schema",
            "threat_model", "risk_assess", "anomaly_detect",
            "pattern_match", "temporal_sequence",
            "hypothesize", "cross_reference", "entity_extraction",
            "relationship_mapping", "causal_inference"
        },
        restricted_operations={
            "identify_living_persons", "speculate_unverified"
        },
        speculation_allowed=True,
        max_hypothesis_count=7,
        require_evidence_citations=True,
        allow_cross_domain=True,
        pii_handling="flag",
        confidence_threshold=0.70,
        require_multi_source=False
    ),

    EchoMode.L2_BLACK_LENS: ModeConfig(
        mode=EchoMode.L2_BLACK_LENS,
        description="Full hypothesis enumeration - REQUIRES Devil Lens human review",
        log_level=LogLevel.FORENSIC,
        review_path=ReviewPath.DEVIL_LENS,
        allowed_operations={
            "recall", "summarize", "verify_hash", "check_integrity",
            "list_artifacts", "get_manifest", "validate_schema",
            "threat_model", "risk_assess", "anomaly_detect",
            "pattern_match", "temporal_sequence",
            "hypothesize", "cross_reference", "entity_extraction",
            "relationship_mapping", "causal_inference",
            "full_enumeration", "adversarial_hypothesis",
            "counter_narrative", "contradiction_analysis"
        },
        restricted_operations=set(),  # No restrictions at L2
        speculation_allowed=True,
        max_hypothesis_count=20,
        require_evidence_citations=True,
        allow_cross_domain=True,
        pii_handling="allow",  # But flagged for review
        confidence_threshold=0.50,
        require_multi_source=False
    )
}


# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

SYSTEM_PROMPTS: Dict[EchoMode, str] = {
    EchoMode.L5_SAFE: """You are Aletheia, a Reality Decoding System operating in L5 SAFE mode.

CONSTRAINTS:
- Provide ONLY verified, evidence-backed statements
- Do NOT speculate or hypothesize
- Cite all sources with artifact IDs
- Require multi-source confirmation for all claims
- Redact any PII before output
- Confidence threshold: 95%

ALLOWED OPERATIONS:
{allowed_ops}

OUTPUT FORMAT:
- State only facts supported by sealed evidence
- Provide artifact IDs for all claims
- Flag any uncertainty explicitly
- No narrative construction beyond direct evidence

SAFETY SEAL: L5_SAFE_∇θ""",

    EchoMode.L4_DEFENSIVE: """You are Aletheia, a Reality Decoding System operating in L4 DEFENSIVE mode.

PURPOSE: Threat modeling and defensive security analysis only.

CONSTRAINTS:
- Generate up to 3 threat hypotheses maximum
- All hypotheses must be framed defensively
- Cite evidence with artifact IDs
- Flag but do not redact PII
- Confidence threshold: 85%

ALLOWED OPERATIONS:
{allowed_ops}

OUTPUT FORMAT:
- Threat model structure: [Threat] -> [Evidence] -> [Mitigation]
- Rank by likelihood and impact
- Provide counter-indicators for each hypothesis
- Clearly mark speculation with [HYPOTHESIS] tags

SAFETY SEAL: L4_DEFENSIVE_∇θ""",

    EchoMode.L3_INVESTIGATIVE: """You are Aletheia, a Reality Decoding System operating in L3 INVESTIGATIVE mode.

PURPOSE: Structural analysis with guided hypothesis generation.

CONSTRAINTS:
- Generate up to 7 ranked hypotheses
- Cross-domain analysis permitted
- Entity extraction and relationship mapping enabled
- Flag PII for review
- Confidence threshold: 70%

ALLOWED OPERATIONS:
{allowed_ops}

OUTPUT FORMAT:
- Structural analysis: [Pattern] -> [Evidence] -> [Inference]
- Causal graph for complex relationships
- Hypothesis ranking with confidence scores
- Evidence gaps explicitly noted
- Mark all inferences with [INFERENCE:confidence%] tags

SAFETY SEAL: L3_INVESTIGATIVE_∇θ""",

    EchoMode.L2_BLACK_LENS: """You are Aletheia, a Reality Decoding System operating in L2 BLACK LENS mode.

⚠️  DEVIL LENS REVIEW REQUIRED - ALL OUTPUTS FLAGGED FOR HUMAN VERIFICATION

PURPOSE: Full hypothesis enumeration for critical analysis.

CONSTRAINTS:
- Generate up to 20 hypotheses including adversarial scenarios
- Counter-narratives and contradiction analysis enabled
- All operations permitted
- Confidence threshold: 50% (speculative content allowed)

ALLOWED OPERATIONS:
{allowed_ops}

OUTPUT FORMAT:
- Complete hypothesis tree with all branches
- Adversarial hypotheses marked [ADVERSARIAL]
- Counter-narratives marked [COUNTER]
- Evidence contradictions marked [CONTRADICTION]
- Confidence scores for all claims
- Full provenance chains

⚠️  OUTPUT REQUIRES DEVIL LENS HUMAN REVIEW BEFORE ANY OPERATIONAL ACTION

SAFETY SEAL: L2_BLACK_LENS_∇θ_REVIEW_REQUIRED""",
}


# =============================================================================
# METRICS LOGGING
# =============================================================================

@dataclass
class ModeMetrics:
    """Metrics for mode fidelity tracking."""
    session_id: str
    mode: str
    timestamp: str
    operation_count: int
    hypothesis_count: int
    citations_provided: int
    pii_flags: int
    confidence_scores: List[float]
    review_triggered: bool
    violations: List[str]


class MetricsLogger:
    """Logger for Echo mode metrics."""

    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[str] = None
        self.metrics: List[ModeMetrics] = []

    def start_session(self, mode: EchoMode) -> str:
        """Start a new metrics session."""
        self.current_session = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return self.current_session

    def log_operation(
        self,
        mode: EchoMode,
        operation: str,
        hypothesis_count: int = 0,
        citations: int = 0,
        pii_flags: int = 0,
        confidence_scores: List[float] = None,
        violations: List[str] = None
    ):
        """Log an operation and its metrics."""
        config = MODE_CONFIGS[mode]

        metric = ModeMetrics(
            session_id=self.current_session or "unknown",
            mode=mode.value,
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            operation_count=1,
            hypothesis_count=hypothesis_count,
            citations_provided=citations,
            pii_flags=pii_flags,
            confidence_scores=confidence_scores or [],
            review_triggered=config.review_path in [ReviewPath.HUMAN_REQUIRED, ReviewPath.DEVIL_LENS],
            violations=violations or []
        )

        self.metrics.append(metric)

        # Write to log file
        log_file = self.log_dir / f"metrics_{self.current_session}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(asdict(metric)) + "\n")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session metrics."""
        if not self.metrics:
            return {}

        session_metrics = [m for m in self.metrics if m.session_id == self.current_session]

        return {
            "session_id": self.current_session,
            "total_operations": sum(m.operation_count for m in session_metrics),
            "total_hypotheses": sum(m.hypothesis_count for m in session_metrics),
            "total_citations": sum(m.citations_provided for m in session_metrics),
            "pii_flags": sum(m.pii_flags for m in session_metrics),
            "avg_confidence": sum(
                sum(m.confidence_scores) / len(m.confidence_scores)
                for m in session_metrics if m.confidence_scores
            ) / len(session_metrics) if session_metrics else 0,
            "violations": [v for m in session_metrics for v in m.violations],
            "reviews_triggered": sum(1 for m in session_metrics if m.review_triggered)
        }


# =============================================================================
# ORCHESTRATOR
# =============================================================================

class EchoOrchestrator:
    """
    Orchestrator for Echo Ethics Dimmer.

    Controls mode selection, prompt generation, operation validation,
    and metrics logging.
    """

    def __init__(self, default_mode: EchoMode = EchoMode.L5_SAFE):
        self.current_mode = default_mode
        self.config = MODE_CONFIGS[default_mode]
        self.logger = MetricsLogger()
        self.session_id = self.logger.start_session(default_mode)

    def set_mode(self, mode: EchoMode) -> Dict[str, Any]:
        """
        Switch to a different ethics mode.

        Returns mode configuration summary.
        """
        self.current_mode = mode
        self.config = MODE_CONFIGS[mode]

        return {
            "mode": mode.value,
            "description": self.config.description,
            "review_path": self.config.review_path.value,
            "allowed_operations": list(self.config.allowed_operations),
            "speculation_allowed": self.config.speculation_allowed,
            "max_hypotheses": self.config.max_hypothesis_count
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for current mode."""
        template = SYSTEM_PROMPTS[self.current_mode]
        return template.format(
            allowed_ops="\n".join(f"- {op}" for op in sorted(self.config.allowed_operations))
        )

    def validate_operation(self, operation: str) -> Tuple[bool, str]:
        """
        Validate if an operation is allowed in current mode.

        Returns: (is_allowed, reason)
        """
        if operation in self.config.restricted_operations:
            return False, f"Operation '{operation}' is restricted in {self.current_mode.value} mode"

        if operation not in self.config.allowed_operations:
            return False, f"Operation '{operation}' not in allowed list for {self.current_mode.value} mode"

        return True, "Operation permitted"

    def validate_output(
        self,
        hypothesis_count: int,
        confidence_scores: List[float],
        has_citations: bool,
        pii_detected: bool
    ) -> Tuple[bool, List[str]]:
        """
        Validate output against mode constraints.

        Returns: (is_valid, list of violations)
        """
        violations = []

        # Check hypothesis count
        if hypothesis_count > self.config.max_hypothesis_count:
            violations.append(
                f"Hypothesis count {hypothesis_count} exceeds max {self.config.max_hypothesis_count}"
            )

        # Check confidence threshold
        low_confidence = [s for s in confidence_scores if s < self.config.confidence_threshold]
        if low_confidence and not self.config.speculation_allowed:
            violations.append(
                f"Confidence scores {low_confidence} below threshold {self.config.confidence_threshold}"
            )

        # Check citations requirement
        if self.config.require_evidence_citations and not has_citations:
            violations.append("Citations required but not provided")

        # Check PII handling
        if pii_detected and self.config.pii_handling == "redact":
            violations.append("PII detected but mode requires redaction")

        return len(violations) == 0, violations

    def process_request(
        self,
        operation: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a request through the orchestrator.

        Returns response with mode framing and metrics.
        """
        # Validate operation
        is_allowed, reason = self.validate_operation(operation)
        if not is_allowed:
            return {
                "status": "blocked",
                "reason": reason,
                "mode": self.current_mode.value
            }

        # Build response wrapper
        response = {
            "status": "processed",
            "mode": self.current_mode.value,
            "system_prompt": self.get_system_prompt(),
            "constraints": {
                "max_hypotheses": self.config.max_hypothesis_count,
                "confidence_threshold": self.config.confidence_threshold,
                "speculation_allowed": self.config.speculation_allowed,
                "require_citations": self.config.require_evidence_citations
            },
            "review_required": self.config.review_path in [
                ReviewPath.HUMAN_REQUIRED, ReviewPath.DEVIL_LENS
            ],
            "context": context
        }

        # Log operation
        self.logger.log_operation(
            mode=self.current_mode,
            operation=operation
        )

        return response

    def flag_for_review(self, output: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Flag an output for Devil Lens human review."""
        return {
            "review_status": "FLAGGED",
            "review_type": "DEVIL_LENS",
            "reason": reason,
            "output": output,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "session_id": self.session_id,
            "action_required": "Human review required before any operational action"
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Echo Ethics Dimmer CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Mode info
    info_parser = subparsers.add_parser("info", help="Show mode information")
    info_parser.add_argument("--mode", choices=["L5", "L4", "L3", "L2"], required=True)

    # Generate prompt
    prompt_parser = subparsers.add_parser("prompt", help="Generate system prompt")
    prompt_parser.add_argument("--mode", choices=["L5", "L4", "L3", "L2"], required=True)
    prompt_parser.add_argument("--output", "-o")

    # Validate operation
    validate_parser = subparsers.add_parser("validate", help="Validate operation")
    validate_parser.add_argument("--mode", choices=["L5", "L4", "L3", "L2"], required=True)
    validate_parser.add_argument("--operation", required=True)

    args = parser.parse_args()

    mode_map = {
        "L5": EchoMode.L5_SAFE,
        "L4": EchoMode.L4_DEFENSIVE,
        "L3": EchoMode.L3_INVESTIGATIVE,
        "L2": EchoMode.L2_BLACK_LENS
    }

    if args.command == "info":
        mode = mode_map[args.mode]
        config = MODE_CONFIGS[mode]
        print(json.dumps({
            "mode": mode.value,
            "description": config.description,
            "review_path": config.review_path.value,
            "allowed_operations": list(config.allowed_operations),
            "restricted_operations": list(config.restricted_operations),
            "speculation_allowed": config.speculation_allowed,
            "max_hypotheses": config.max_hypothesis_count,
            "confidence_threshold": config.confidence_threshold
        }, indent=2))

    elif args.command == "prompt":
        mode = mode_map[args.mode]
        orchestrator = EchoOrchestrator(mode)
        prompt = orchestrator.get_system_prompt()

        if args.output:
            with open(args.output, "w") as f:
                f.write(prompt)
            print(f"Prompt written to {args.output}")
        else:
            print(prompt)

    elif args.command == "validate":
        mode = mode_map[args.mode]
        orchestrator = EchoOrchestrator(mode)
        is_allowed, reason = orchestrator.validate_operation(args.operation)
        print(json.dumps({
            "operation": args.operation,
            "mode": mode.value,
            "allowed": is_allowed,
            "reason": reason
        }, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()


# =============================================================================
# TYPE HINTS FOR EXTERNAL USE
# =============================================================================

from typing import Tuple  # Re-export for external use
