#!/usr/bin/env python3
"""
Echo-1 Mathematical Stress Test Suite
Comprehensive validation of constraint equations, resonance calculations, and edge cases
"""

import math
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from typing import List, Tuple, Dict
from statistics import mean, stdev
import json


@dataclass
class ConstraintScore:
    """Individual constraint evaluation result"""
    name: str
    score: float  # 0.0 to 1.0
    violations: int
    severity: float


@dataclass
class ResonanceResult:
    """Result of resonance calculation"""
    temporal_score: float
    provenance_score: float
    authority_score: float
    host_score: float
    harmonic_mean: float
    scram_triggered: bool
    timestamp: str


class EchoMathematicalValidator:
    """Comprehensive mathematical validation for Echo-1"""
    
    RESONANCE_FLOOR = 0.4
    CORRECTION_THRESHOLD = 0.7
    
    def __init__(self):
        self.test_results = []
        self.violations_detected = 0
        self.scram_triggers = 0
    
    # ========== HARMONIC MEAN CALCULATIONS ==========
    
    def harmonic_mean(self, scores: List[float]) -> float:
        """
        Calculate harmonic mean of constraint scores.
        
        Formula: H = n / (1/a + 1/b + 1/c + 1/d)
        
        Why harmonic mean?
        - Penalizes outliers (weak constraints break harmony)
        - Arithmetic mean masks weakness: (0.9+0.9+0.9+0.1)/4 = 0.7
        - Harmonic mean exposes weakness: 4/(1.11+1.11+1.11+10) = 0.31
        """
        if not scores or any(s < 0 or s > 1 for s in scores):
            raise ValueError(f"Invalid scores: {scores}")
        
        # Handle zero case
        if any(s == 0 for s in scores):
            return 0.0
        
        n = len(scores)
        reciprocal_sum = sum(1.0 / s for s in scores)
        return n / reciprocal_sum
    
    def test_harmonic_mean_properties(self) -> Dict:
        """Test mathematical properties of harmonic mean"""
        results = {
            "symmetry": False,
            "outlier_penalty": False,
            "boundary_behavior": False,
            "precision": False,
            "details": []
        }
        
        # Test 1: Symmetry
        scores1 = [0.9, 0.8, 0.7, 0.6]
        scores2 = [0.6, 0.7, 0.8, 0.9]
        hm1 = self.harmonic_mean(scores1)
        hm2 = self.harmonic_mean(scores2)
        results["symmetry"] = abs(hm1 - hm2) < 1e-10
        results["details"].append(f"Symmetry: {hm1:.10f} == {hm2:.10f} ? {results['symmetry']}")
        
        # Test 2: Outlier Penalty
        normal = [0.9, 0.9, 0.9, 0.9]
        with_outlier = [0.9, 0.9, 0.9, 0.1]
        hm_normal = self.harmonic_mean(normal)
        hm_outlier = self.harmonic_mean(with_outlier)
        penalty = hm_normal - hm_outlier
        results["outlier_penalty"] = penalty > 0.5  # Should be significant
        results["details"].append(f"Outlier penalty: {hm_normal:.3f} - {hm_outlier:.3f} = {penalty:.3f}")
        
        # Test 3: Boundary Behavior
        all_ones = self.harmonic_mean([1.0, 1.0, 1.0, 1.0])
        all_zeros = self.harmonic_mean([0.0, 0.0, 0.0, 0.0])
        results["boundary_behavior"] = (all_ones == 1.0) and (all_zeros == 0.0)
        results["details"].append(f"Boundaries: all_ones={all_ones}, all_zeros={all_zeros}")
        
        # Test 4: Precision (edge case with very small numbers)
        try:
            precision_test = self.harmonic_mean([0.9999999999, 0.9999999998, 0.9999999997, 0.0001])
            results["precision"] = 0.0 < precision_test < 0.1
            results["details"].append(f"Precision test: {precision_test:.15f}")
        except Exception as e:
            results["details"].append(f"Precision test failed: {e}")
        
        return results
    
    # ========== TEMPORAL DECAY CALCULATIONS ==========
    
    def calculate_confidence(
        self,
        initial: float,
        lambda_decay: float,
        days_old: float,
        floor: float = 0.0
    ) -> float:
        """
        Calculate confidence using Broken Clock formula.
        
        Formula: confidence(t) = max(floor, initial × e^(-λ × days))
        """
        if initial < 0 or initial > 1:
            raise ValueError(f"Initial confidence must be 0-1, got {initial}")
        if lambda_decay < 0:
            raise ValueError(f"Decay rate must be non-negative, got {lambda_decay}")
        if days_old < 0:
            raise ValueError(f"Days old must be non-negative, got {days_old}")
        
        raw = initial * math.exp(-lambda_decay * days_old)
        return max(floor, min(1.0, raw))
    
    def test_temporal_decay(self) -> Dict:
        """Test temporal decay formula across content types"""
        results = {
            "news_decay": [],
            "code_decay": [],
            "science_decay": [],
            "legal_decay": [],
            "history_decay": [],
            "floor_protection": False,
            "half_life_accuracy": False
        }
        
        # Define decay policies
        policies = {
            "News": {"lambda": 0.10, "floor": 0.05, "initial": 0.95},
            "Code": {"lambda": 0.005, "floor": 0.20, "initial": 0.85},
            "Science": {"lambda": 0.002, "floor": 0.30, "initial": 0.90},
            "Legal": {"lambda": 0.001, "floor": 0.40, "initial": 0.95},
            "History": {"lambda": 0.0, "floor": 1.00, "initial": 1.00},
        }
        
        # Test decay over time
        test_days = [0, 7, 14, 30, 90, 180, 365, 730]
        
        for policy_name, policy in policies.items():
            decay_curve = []
            for days in test_days:
                conf = self.calculate_confidence(
                    initial=policy["initial"],
                    lambda_decay=policy["lambda"],
                    days_old=days,
                    floor=policy["floor"]
                )
                decay_curve.append(conf)
            
            results[f"{policy_name.lower()}_decay"] = decay_curve
        
        # Test floor protection (News should hit floor by day 35)
        news_decay = results["news_decay"]
        results["floor_protection"] = news_decay[-1] == 0.05  # Should be at floor
        
        # Test half-life accuracy for Code (λ=0.005)
        # Half-life = ln(2) / λ = 0.693 / 0.005 ≈ 139 days
        code_at_139 = self.calculate_confidence(0.85, 0.005, 139, 0.20)
        expected_half = 0.85 / 2
        results["half_life_accuracy"] = abs(code_at_139 - expected_half) < 0.05
        
        return results
    
    # ========== CONSTRAINT PROPAGATION TESTS ==========
    
    def test_constraint_propagation(self) -> Dict:
        """Test constraint propagation through transformations"""
        results = {
            "propagation_layers": [],
            "constraint_loss_detected": False,
            "circular_dependency_detected": False,
            "conflict_detected": False
        }
        
        # Simulate 5-layer transformation
        constraints = {
            "temporal": 0.95,
            "provenance": 0.90,
            "authority": 0.85,
            "host": 0.88
        }
        
        # Layer 1: Pre-execution
        layer1 = constraints.copy()
        layer1_resonance = self.harmonic_mean(list(layer1.values()))
        results["propagation_layers"].append({
            "layer": 1,
            "constraints": layer1,
            "resonance": layer1_resonance
        })
        
        # Layer 2: Execution (slight degradation)
        layer2 = {
            "temporal": 0.95,
            "provenance": 0.88,  # Slightly degraded
            "authority": 0.85,
            "host": 0.88
        }
        layer2_resonance = self.harmonic_mean(list(layer2.values()))
        results["propagation_layers"].append({
            "layer": 2,
            "constraints": layer2,
            "resonance": layer2_resonance
        })
        
        # Layer 3: Post-execution (more degradation)
        layer3 = {
            "temporal": 0.95,
            "provenance": 0.85,  # Further degraded
            "authority": 0.80,   # Degraded
            "host": 0.88
        }
        layer3_resonance = self.harmonic_mean(list(layer3.values()))
        results["propagation_layers"].append({
            "layer": 3,
            "constraints": layer3,
            "resonance": layer3_resonance
        })
        
        # Check for constraint loss
        if len(layer3) < len(layer1):
            results["constraint_loss_detected"] = True
        
        return results
    
    # ========== SCRAM PROTOCOL TESTS ==========
    
    def evaluate_scram_trigger(self, resonance: float) -> Dict:
        """Evaluate SCRAM protocol decision"""
        return {
            "resonance": resonance,
            "scram_triggered": resonance < self.RESONANCE_FLOOR,
            "correction_mode": self.RESONANCE_FLOOR <= resonance < self.CORRECTION_THRESHOLD,
            "normal_operation": resonance >= self.CORRECTION_THRESHOLD,
            "action": (
                "SCRAM (Emergency Shutdown)" if resonance < self.RESONANCE_FLOOR else
                "Active Correction" if resonance < self.CORRECTION_THRESHOLD else
                "Log and Monitor"
            )
        }
    
    def test_scram_oscillation(self) -> Dict:
        """Test SCRAM oscillation vulnerability"""
        results = {
            "oscillation_detected": False,
            "oscillation_count": 0,
            "resonance_trajectory": []
        }
        
        # Simulate system oscillating around threshold
        resonance = 0.45
        for iteration in range(20):
            results["resonance_trajectory"].append(resonance)
            
            # Simulate correction
            if resonance < self.RESONANCE_FLOOR:
                resonance += 0.05  # Correction pushes up
            else:
                resonance -= 0.03  # Drift pulls down
            
            # Check for oscillation
            if len(results["resonance_trajectory"]) > 2:
                if (results["resonance_trajectory"][-2] < self.RESONANCE_FLOOR and
                    results["resonance_trajectory"][-1] >= self.RESONANCE_FLOOR):
                    results["oscillation_count"] += 1
        
        results["oscillation_detected"] = results["oscillation_count"] > 2
        
        return results
    
    # ========== EDGE CASE TESTS ==========
    
    def test_edge_cases(self) -> Dict:
        """Test mathematical edge cases"""
        results = {
            "division_by_zero": False,
            "negative_time": False,
            "extreme_values": False,
            "floating_point_precision": False,
            "details": []
        }
        
        # Test 1: Division by zero protection
        try:
            zero_scores = [0.0, 0.0, 0.0, 0.0]
            hm = self.harmonic_mean(zero_scores)
            results["division_by_zero"] = hm == 0.0
            results["details"].append(f"Division by zero: harmonic_mean({zero_scores}) = {hm}")
        except Exception as e:
            results["details"].append(f"Division by zero error: {e}")
        
        # Test 2: Negative time handling
        try:
            conf = self.calculate_confidence(0.85, 0.005, -10, 0.20)
            results["details"].append(f"Negative time: calculate_confidence with -10 days raised error (expected)")
        except ValueError:
            results["negative_time"] = True
        
        # Test 3: Extreme values
        try:
            extreme_high = self.harmonic_mean([1.0, 1.0, 1.0, 1.0])
            extreme_low = self.harmonic_mean([0.001, 0.001, 0.001, 0.001])
            results["extreme_values"] = (extreme_high == 1.0) and (0 < extreme_low < 0.01)
            results["details"].append(f"Extreme values: high={extreme_high}, low={extreme_low}")
        except Exception as e:
            results["details"].append(f"Extreme values error: {e}")
        
        # Test 4: Floating point precision
        try:
            precision_scores = [0.33333333, 0.33333333, 0.33333334, 0.33333333]
            hm = self.harmonic_mean(precision_scores)
            results["floating_point_precision"] = 0.33 < hm < 0.34
            results["details"].append(f"Floating point precision: {hm:.15f}")
        except Exception as e:
            results["details"].append(f"Floating point precision error: {e}")
        
        return results
    
    # ========== COMPREHENSIVE STRESS TEST ==========
    
    def run_comprehensive_stress_test(self) -> Dict:
        """Run all stress tests and generate report"""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "harmonic_mean_properties": self.test_harmonic_mean_properties(),
            "temporal_decay": self.test_temporal_decay(),
            "constraint_propagation": self.test_constraint_propagation(),
            "scram_oscillation": self.test_scram_oscillation(),
            "edge_cases": self.test_edge_cases(),
            "summary": {}
        }
        
        # Calculate summary
        all_tests = [
            report["harmonic_mean_properties"],
            report["temporal_decay"],
            report["constraint_propagation"],
            report["scram_oscillation"],
            report["edge_cases"]
        ]
        
        total_checks = sum(1 for test in all_tests for key in test if key != "details")
        passed_checks = sum(1 for test in all_tests for key, val in test.items() 
                          if key != "details" and val is True)
        
        report["summary"] = {
            "total_checks": total_checks,
            "passed": passed_checks,
            "failed": total_checks - passed_checks,
            "pass_rate": f"{(passed_checks / total_checks * 100):.1f}%"
        }
        
        return report


def main():
    """Run comprehensive stress test suite"""
    print("=" * 80)
    print("ECHO-1 MATHEMATICAL STRESS TEST SUITE")
    print("=" * 80)
    print()
    
    validator = EchoMathematicalValidator()
    report = validator.run_comprehensive_stress_test()
    
    # Print results
    print("HARMONIC MEAN PROPERTIES")
    print("-" * 80)
    for detail in report["harmonic_mean_properties"]["details"]:
        print(f"  {detail}")
    print()
    
    print("TEMPORAL DECAY ANALYSIS")
    print("-" * 80)
    print(f"  Floor Protection: {report['temporal_decay']['floor_protection']}")
    print(f"  Half-Life Accuracy: {report['temporal_decay']['half_life_accuracy']}")
    print()
    
    print("CONSTRAINT PROPAGATION")
    print("-" * 80)
    for layer in report["constraint_propagation"]["propagation_layers"]:
        print(f"  Layer {layer['layer']}: Resonance = {layer['resonance']:.4f}")
    print()
    
    print("SCRAM OSCILLATION TEST")
    print("-" * 80)
    print(f"  Oscillation Detected: {report['scram_oscillation']['oscillation_detected']}")
    print(f"  Oscillation Count: {report['scram_oscillation']['oscillation_count']}")
    print()
    
    print("EDGE CASES")
    print("-" * 80)
    for detail in report["edge_cases"]["details"]:
        print(f"  {detail}")
    print()
    
    print("SUMMARY")
    print("-" * 80)
    print(f"  Total Checks: {report['summary']['total_checks']}")
    print(f"  Passed: {report['summary']['passed']}")
    print(f"  Failed: {report['summary']['failed']}")
    print(f"  Pass Rate: {report['summary']['pass_rate']}")
    print()
    
    # Save report to JSON
    with open("/home/ubuntu/echo_stress_test_results.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Full report saved to: /home/ubuntu/echo_stress_test_results.json")
    print("=" * 80)


if __name__ == "__main__":
    main()
