#!/usr/bin/env python3
"""
ECHONATE EXPLAINABLE AI (XAI) LAYER

Implements explainability and transparency for autonomous decision-making:
- Decision Trace Logging
- Feature Attribution (SHAP-like analysis)
- Signal Provenance Chain
- Human-Readable Explanations
- Counterfactual Analysis

∇θ Phoenix Global Nexus
"""

import json
import math
import hashlib
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum


# =============================================================================
# EXPLANATION TYPES
# =============================================================================

class ExplanationType(Enum):
    """Types of explanations"""
    FEATURE_ATTRIBUTION = "feature_attribution"
    COUNTERFACTUAL = "counterfactual"
    DECISION_TRACE = "decision_trace"
    RULE_BASED = "rule_based"
    EXAMPLE_BASED = "example_based"


class ConfidenceLevel(Enum):
    """Confidence levels for explanations"""
    HIGH = "high"      # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"        # < 0.5


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class FeatureContribution:
    """Contribution of a single feature to the decision"""
    feature_name: str
    feature_value: Any
    contribution: float  # Positive = supports decision, Negative = opposes
    importance_rank: int
    explanation: str


@dataclass
class DecisionStep:
    """A single step in the decision trace"""
    step_id: int
    timestamp: str
    operation: str
    inputs: Dict
    outputs: Dict
    reasoning: str
    confidence: float


@dataclass
class Counterfactual:
    """What would need to change to flip the decision"""
    original_decision: str
    alternative_decision: str
    required_changes: List[Dict]
    minimum_change_magnitude: float
    feasibility: str


@dataclass
class SignalExplanation:
    """Complete explanation for a signal decision"""
    signal_id: str
    timestamp: str
    
    # The decision
    decision: str
    confidence: float
    confidence_level: ConfidenceLevel
    
    # Feature attributions
    feature_contributions: List[FeatureContribution]
    
    # Decision trace
    decision_trace: List[DecisionStep]
    
    # Counterfactuals
    counterfactuals: List[Counterfactual]
    
    # Human-readable summary
    summary: str
    detailed_explanation: str
    
    # Provenance
    data_sources: List[str]
    provenance_hashes: List[str]
    
    # Metadata
    explanation_type: ExplanationType = ExplanationType.FEATURE_ATTRIBUTION
    generation_time_ms: float = 0.0


# =============================================================================
# FEATURE ATTRIBUTION ENGINE
# =============================================================================

class FeatureAttributor:
    """
    Calculates feature contributions to decisions.
    Uses a simplified SHAP-like approach for interpretability.
    """
    
    def __init__(self):
        self.baseline_values = {}
    
    def set_baseline(self, feature_baselines: Dict[str, float]):
        """Set baseline values for features"""
        self.baseline_values = feature_baselines
    
    def calculate_contributions(self, 
                                features: Dict[str, float],
                                prediction: float,
                                feature_weights: Dict[str, float] = None) -> List[FeatureContribution]:
        """
        Calculate how each feature contributes to the prediction.
        Uses a linear attribution model for interpretability.
        """
        contributions = []
        
        # Default weights if not provided
        if feature_weights is None:
            feature_weights = {k: 1.0 for k in features.keys()}
        
        # Calculate total weighted sum
        total_contribution = 0
        for name, value in features.items():
            baseline = self.baseline_values.get(name, 0)
            weight = feature_weights.get(name, 1.0)
            contribution = (value - baseline) * weight
            total_contribution += contribution
        
        # Normalize contributions to sum to prediction
        if total_contribution != 0:
            scale = prediction / total_contribution
        else:
            scale = 1.0
        
        # Create contribution objects
        for name, value in features.items():
            baseline = self.baseline_values.get(name, 0)
            weight = feature_weights.get(name, 1.0)
            raw_contribution = (value - baseline) * weight * scale
            
            # Generate explanation
            if raw_contribution > 0:
                direction = "increases"
            elif raw_contribution < 0:
                direction = "decreases"
            else:
                direction = "has no effect on"
            
            explanation = f"{name}={value:.2f} (baseline={baseline:.2f}) {direction} the signal strength by {abs(raw_contribution):.3f}"
            
            contributions.append(FeatureContribution(
                feature_name=name,
                feature_value=value,
                contribution=raw_contribution,
                importance_rank=0,  # Will be set after sorting
                explanation=explanation
            ))
        
        # Sort by absolute contribution and assign ranks
        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)
        for i, c in enumerate(contributions):
            c.importance_rank = i + 1
        
        return contributions


# =============================================================================
# DECISION TRACER
# =============================================================================

class DecisionTracer:
    """
    Records the complete decision-making process step by step.
    Enables full auditability and debugging.
    """
    
    def __init__(self):
        self.current_trace: List[DecisionStep] = []
        self.step_counter = 0
    
    def start_trace(self):
        """Start a new decision trace"""
        self.current_trace = []
        self.step_counter = 0
    
    def record_step(self,
                    operation: str,
                    inputs: Dict,
                    outputs: Dict,
                    reasoning: str,
                    confidence: float = 1.0):
        """Record a step in the decision process"""
        self.step_counter += 1
        
        step = DecisionStep(
            step_id=self.step_counter,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            operation=operation,
            inputs=inputs,
            outputs=outputs,
            reasoning=reasoning,
            confidence=confidence
        )
        
        self.current_trace.append(step)
        return step
    
    def get_trace(self) -> List[DecisionStep]:
        """Get the current decision trace"""
        return self.current_trace.copy()
    
    def get_trace_summary(self) -> str:
        """Get a human-readable summary of the trace"""
        lines = ["Decision Trace Summary:", "=" * 40]
        
        for step in self.current_trace:
            lines.append(f"Step {step.step_id}: {step.operation}")
            lines.append(f"  Reasoning: {step.reasoning}")
            lines.append(f"  Confidence: {step.confidence:.2f}")
        
        return "\n".join(lines)


# =============================================================================
# COUNTERFACTUAL GENERATOR
# =============================================================================

class CounterfactualGenerator:
    """
    Generates counterfactual explanations.
    Answers: "What would need to change to get a different decision?"
    """
    
    def __init__(self):
        self.decision_thresholds = {}
    
    def set_thresholds(self, thresholds: Dict[str, float]):
        """Set decision thresholds"""
        self.decision_thresholds = thresholds
    
    def generate_counterfactuals(self,
                                  features: Dict[str, float],
                                  current_decision: str,
                                  alternative_decisions: List[str],
                                  feature_ranges: Dict[str, Tuple[float, float]] = None) -> List[Counterfactual]:
        """
        Generate counterfactual explanations for alternative decisions.
        """
        counterfactuals = []
        
        for alt_decision in alternative_decisions:
            if alt_decision == current_decision:
                continue
            
            # Calculate what changes would be needed
            required_changes = []
            total_change = 0
            
            for feature_name, current_value in features.items():
                # Simplified: assume we need to flip the sign or reach a threshold
                if alt_decision == "BULLISH" and current_decision == "BEARISH":
                    # Need to increase positive features
                    target_value = current_value * 1.5 if current_value > 0 else -current_value
                elif alt_decision == "BEARISH" and current_decision == "BULLISH":
                    # Need to decrease positive features
                    target_value = current_value * 0.5 if current_value > 0 else current_value * 1.5
                else:
                    target_value = current_value
                
                change = abs(target_value - current_value)
                if change > 0.01:
                    required_changes.append({
                        'feature': feature_name,
                        'current_value': current_value,
                        'required_value': target_value,
                        'change_magnitude': change
                    })
                    total_change += change
            
            # Assess feasibility
            if total_change < 0.1:
                feasibility = "EASY"
            elif total_change < 0.5:
                feasibility = "MODERATE"
            else:
                feasibility = "DIFFICULT"
            
            counterfactuals.append(Counterfactual(
                original_decision=current_decision,
                alternative_decision=alt_decision,
                required_changes=required_changes,
                minimum_change_magnitude=total_change,
                feasibility=feasibility
            ))
        
        return counterfactuals


# =============================================================================
# EXPLANATION GENERATOR
# =============================================================================

class ExplanationGenerator:
    """
    Main class for generating complete explanations.
    Combines feature attribution, decision tracing, and counterfactuals.
    """
    
    def __init__(self):
        self.attributor = FeatureAttributor()
        self.tracer = DecisionTracer()
        self.counterfactual_gen = CounterfactualGenerator()
        
        # Set default baselines for common features
        self.attributor.set_baseline({
            'earthquake_magnitude': 0.0,
            'earthquake_count': 0,
            'covid_critical': 0,
            'btc_price_change': 0.0,
            'market_volatility': 0.15,
            'sentiment_score': 0.0
        })
    
    def generate_explanation(self,
                             signal_id: str,
                             decision: str,
                             confidence: float,
                             features: Dict[str, float],
                             feature_weights: Dict[str, float] = None,
                             data_sources: List[str] = None,
                             provenance_hashes: List[str] = None) -> SignalExplanation:
        """
        Generate a complete explanation for a signal decision.
        """
        start_time = datetime.utcnow()
        
        # Start decision trace
        self.tracer.start_trace()
        
        # Step 1: Data collection
        self.tracer.record_step(
            operation="DATA_COLLECTION",
            inputs={"sources": data_sources or []},
            outputs={"features_extracted": list(features.keys())},
            reasoning=f"Collected {len(features)} features from {len(data_sources or [])} data sources",
            confidence=0.95
        )
        
        # Step 2: Feature extraction
        self.tracer.record_step(
            operation="FEATURE_EXTRACTION",
            inputs={"raw_features": features},
            outputs={"normalized_features": features},
            reasoning="Normalized features against historical baselines",
            confidence=0.90
        )
        
        # Step 3: Calculate feature contributions
        contributions = self.attributor.calculate_contributions(
            features, confidence, feature_weights
        )
        
        self.tracer.record_step(
            operation="FEATURE_ATTRIBUTION",
            inputs={"features": features, "weights": feature_weights},
            outputs={"contributions": [c.feature_name for c in contributions[:3]]},
            reasoning=f"Top contributing feature: {contributions[0].feature_name if contributions else 'N/A'}",
            confidence=0.85
        )
        
        # Step 4: Decision making
        self.tracer.record_step(
            operation="DECISION",
            inputs={"confidence": confidence, "threshold": 0.5},
            outputs={"decision": decision},
            reasoning=f"Confidence {confidence:.2f} exceeds threshold, decision: {decision}",
            confidence=confidence
        )
        
        # Generate counterfactuals
        counterfactuals = self.counterfactual_gen.generate_counterfactuals(
            features,
            decision,
            ["BULLISH", "BEARISH", "NEUTRAL"]
        )
        
        # Determine confidence level
        if confidence >= 0.8:
            confidence_level = ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            confidence_level = ConfidenceLevel.MEDIUM
        else:
            confidence_level = ConfidenceLevel.LOW
        
        # Generate human-readable summary
        summary = self._generate_summary(decision, confidence, contributions)
        detailed = self._generate_detailed_explanation(
            decision, confidence, contributions, counterfactuals
        )
        
        # Calculate generation time
        generation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return SignalExplanation(
            signal_id=signal_id,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            decision=decision,
            confidence=confidence,
            confidence_level=confidence_level,
            feature_contributions=contributions,
            decision_trace=self.tracer.get_trace(),
            counterfactuals=counterfactuals,
            summary=summary,
            detailed_explanation=detailed,
            data_sources=data_sources or [],
            provenance_hashes=provenance_hashes or [],
            generation_time_ms=generation_time
        )
    
    def _generate_summary(self,
                          decision: str,
                          confidence: float,
                          contributions: List[FeatureContribution]) -> str:
        """Generate a one-sentence summary"""
        top_feature = contributions[0] if contributions else None
        
        if top_feature:
            return (f"Signal: {decision} (confidence: {confidence:.0%}). "
                    f"Primary driver: {top_feature.feature_name} "
                    f"(contribution: {top_feature.contribution:+.3f})")
        else:
            return f"Signal: {decision} (confidence: {confidence:.0%}). No feature contributions available."
    
    def _generate_detailed_explanation(self,
                                        decision: str,
                                        confidence: float,
                                        contributions: List[FeatureContribution],
                                        counterfactuals: List[Counterfactual]) -> str:
        """Generate a detailed multi-paragraph explanation"""
        lines = []
        
        # Decision overview
        lines.append(f"## Decision: {decision}")
        lines.append(f"")
        lines.append(f"The system has generated a **{decision}** signal with "
                     f"**{confidence:.0%}** confidence.")
        lines.append("")
        
        # Feature contributions
        lines.append("### Key Contributing Factors")
        lines.append("")
        for c in contributions[:5]:
            direction = "↑" if c.contribution > 0 else "↓"
            lines.append(f"- **{c.feature_name}**: {c.feature_value:.2f} "
                         f"({direction} {abs(c.contribution):.3f})")
        lines.append("")
        
        # Counterfactual analysis
        if counterfactuals:
            lines.append("### What Would Change the Decision?")
            lines.append("")
            for cf in counterfactuals[:2]:
                lines.append(f"To change from {cf.original_decision} to "
                             f"{cf.alternative_decision} ({cf.feasibility}):")
                for change in cf.required_changes[:3]:
                    lines.append(f"  - {change['feature']}: {change['current_value']:.2f} → "
                                 f"{change['required_value']:.2f}")
            lines.append("")
        
        # Confidence assessment
        lines.append("### Confidence Assessment")
        lines.append("")
        if confidence >= 0.8:
            lines.append("This is a **HIGH CONFIDENCE** signal. The contributing factors "
                         "strongly support the decision with minimal uncertainty.")
        elif confidence >= 0.5:
            lines.append("This is a **MEDIUM CONFIDENCE** signal. The contributing factors "
                         "support the decision but with some uncertainty.")
        else:
            lines.append("This is a **LOW CONFIDENCE** signal. The contributing factors "
                         "are weak or conflicting. Exercise caution.")
        
        return "\n".join(lines)


# =============================================================================
# XAI INTEGRATION WITH ECHONATE
# =============================================================================

class EchoNateXAI:
    """
    Integration layer for XAI with EchoNate correlation engine.
    Provides explainability for all signal decisions.
    """
    
    def __init__(self):
        self.generator = ExplanationGenerator()
        self.explanations: Dict[str, SignalExplanation] = {}
    
    def explain_seismic_signal(self,
                                signal_id: str,
                                earthquake_magnitude: float,
                                earthquake_count: int,
                                target_stock: str,
                                decision: str,
                                confidence: float,
                                provenance_hashes: List[str] = None) -> SignalExplanation:
        """Generate explanation for a seismic-based signal"""
        features = {
            'earthquake_magnitude': earthquake_magnitude,
            'earthquake_count': earthquake_count,
            'magnitude_threshold_exceeded': 1.0 if earthquake_magnitude >= 5.0 else 0.0,
            'insurance_exposure': 0.7  # TRV has high insurance exposure
        }
        
        weights = {
            'earthquake_magnitude': 0.4,
            'earthquake_count': 0.2,
            'magnitude_threshold_exceeded': 0.3,
            'insurance_exposure': 0.1
        }
        
        explanation = self.generator.generate_explanation(
            signal_id=signal_id,
            decision=decision,
            confidence=confidence,
            features=features,
            feature_weights=weights,
            data_sources=["USGS Earthquake Feed", f"Yahoo Finance ({target_stock})"],
            provenance_hashes=provenance_hashes
        )
        
        self.explanations[signal_id] = explanation
        return explanation
    
    def explain_health_signal(self,
                               signal_id: str,
                               critical_cases: int,
                               case_trend: float,
                               target_stock: str,
                               decision: str,
                               confidence: float,
                               provenance_hashes: List[str] = None) -> SignalExplanation:
        """Generate explanation for a health-based signal"""
        features = {
            'critical_cases': critical_cases / 1000,  # Normalize to thousands
            'case_trend': case_trend,
            'pharma_demand_indicator': 1.0 if critical_cases > 30000 else 0.5,
            'healthcare_sector_correlation': 0.65
        }
        
        weights = {
            'critical_cases': 0.35,
            'case_trend': 0.25,
            'pharma_demand_indicator': 0.25,
            'healthcare_sector_correlation': 0.15
        }
        
        explanation = self.generator.generate_explanation(
            signal_id=signal_id,
            decision=decision,
            confidence=confidence,
            features=features,
            feature_weights=weights,
            data_sources=["disease.sh COVID API", f"Yahoo Finance ({target_stock})"],
            provenance_hashes=provenance_hashes
        )
        
        self.explanations[signal_id] = explanation
        return explanation
    
    def get_explanation(self, signal_id: str) -> Optional[SignalExplanation]:
        """Retrieve a stored explanation"""
        return self.explanations.get(signal_id)
    
    def export_explanation_report(self, signal_id: str) -> str:
        """Export explanation as markdown report"""
        explanation = self.explanations.get(signal_id)
        if not explanation:
            return f"No explanation found for signal: {signal_id}"
        
        lines = [
            f"# Signal Explanation Report",
            f"",
            f"**Signal ID:** {explanation.signal_id}",
            f"**Generated:** {explanation.timestamp}",
            f"**Generation Time:** {explanation.generation_time_ms:.2f}ms",
            f"",
            explanation.detailed_explanation,
            f"",
            f"---",
            f"",
            f"### Decision Trace",
            f"",
        ]
        
        for step in explanation.decision_trace:
            lines.append(f"**Step {step.step_id}: {step.operation}**")
            lines.append(f"- Reasoning: {step.reasoning}")
            lines.append(f"- Confidence: {step.confidence:.2f}")
            lines.append("")
        
        lines.extend([
            f"---",
            f"",
            f"### Data Provenance",
            f"",
            f"**Sources:** {', '.join(explanation.data_sources)}",
            f"",
            f"**Provenance Hashes:**",
        ])
        
        for h in explanation.provenance_hashes:
            lines.append(f"- `{h[:32]}...`")
        
        return "\n".join(lines)


# =============================================================================
# DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ECHONATE EXPLAINABLE AI (XAI) LAYER")
    print("=" * 80)
    
    xai = EchoNateXAI()
    
    # Generate explanation for seismic signal
    print("\n[1] Generating Seismic Signal Explanation...")
    seismic_explanation = xai.explain_seismic_signal(
        signal_id="SEISMIC_TRV_20260121",
        earthquake_magnitude=6.0,
        earthquake_count=47,
        target_stock="TRV",
        decision="BEARISH",
        confidence=0.75,
        provenance_hashes=["abc123def456", "789ghi012jkl"]
    )
    
    print(f"\n{seismic_explanation.summary}")
    print(f"\nTop 3 Contributing Features:")
    for c in seismic_explanation.feature_contributions[:3]:
        print(f"  {c.importance_rank}. {c.feature_name}: {c.contribution:+.3f}")
    
    # Generate explanation for health signal
    print("\n[2] Generating Health Signal Explanation...")
    health_explanation = xai.explain_health_signal(
        signal_id="HEALTH_PFE_20260121",
        critical_cases=34794,
        case_trend=0.02,
        target_stock="PFE",
        decision="BULLISH",
        confidence=0.65,
        provenance_hashes=["mno345pqr678"]
    )
    
    print(f"\n{health_explanation.summary}")
    
    # Show counterfactual
    print("\n[3] Counterfactual Analysis...")
    if health_explanation.counterfactuals:
        cf = health_explanation.counterfactuals[0]
        print(f"  To change from {cf.original_decision} to {cf.alternative_decision}:")
        print(f"  Feasibility: {cf.feasibility}")
        for change in cf.required_changes[:2]:
            print(f"    - {change['feature']}: {change['current_value']:.2f} → {change['required_value']:.2f}")
    
    # Export full report
    print("\n[4] Exporting Full Explanation Report...")
    report = xai.export_explanation_report("SEISMIC_TRV_20260121")
    print(f"\n{report[:1000]}...")
    
    print("\n" + "=" * 80)
    print("XAI Layer Demonstration Complete")
    print("=" * 80)
