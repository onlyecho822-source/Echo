#!/usr/bin/env python3
"""
Traffic Governance Engine v2 - Validation Test Suite

Tests all Devil's Eye corrections:
1. Contract matching (route templates)
2. Tier enforcement (OBSERVE_ONLY vs CONTROL)
3. Ledger integrity (chain verification)
4. Risk assessment (comprehensive factors)
5. Decision pipeline (deterministic)
6. Policy artifact verification
7. Cross-platform drift detection
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from traffic_governance_engine_v2 import (
    TrafficGovernanceEngine,
    GovernancePolicy,
    ServiceContract,
    RequestEvent,
    PlatformTier,
    Decision,
    CircuitState,
    PolicyArtifactVerifier
)


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def record(self, name: str, passed: bool, message: str = ""):
        self.tests.append((name, passed, message))
        if passed:
            self.passed += 1
            print(f"✅ {name}")
        else:
            self.failed += 1
            print(f"❌ {name}: {message}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} passed")
        print(f"{'='*60}")
        if self.failed > 0:
            print("\nFailed tests:")
            for name, passed, message in self.tests:
                if not passed:
                    print(f"  - {name}: {message}")
        return self.failed == 0


def setup_engine(platform_tier: PlatformTier):
    """Setup test engine"""
    policy = GovernancePolicy(version="1.0.0")
    
    contracts = {
        "GET /api/v1/status": ServiceContract(
            contract_id="status_v1",
            endpoint_pattern="GET /api/v1/status",
            allowed_methods=["GET"],
            max_latency_ms=100.0,
            rate_limit_rpm=1000.0,
            circuit_threshold=0.5
        ),
        "POST /api/v1/deployments": ServiceContract(
            contract_id="deploy_v1",
            endpoint_pattern="POST /api/v1/deployments",
            allowed_methods=["POST"],
            max_latency_ms=5000.0,
            rate_limit_rpm=10.0,
            circuit_threshold=0.3
        ),
        "GET /api/v1/deployments/{id}": ServiceContract(
            contract_id="deploy_get_v1",
            endpoint_pattern="GET /api/v1/deployments/{id}",
            allowed_methods=["GET"],
            max_latency_ms=500.0,
            rate_limit_rpm=100.0,
            circuit_threshold=0.5
        )
    }
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as f:
        ledger_path = f.name
    
    engine = TrafficGovernanceEngine(
        policy=policy,
        contracts=contracts,
        platform_tier=platform_tier,
        ledger_path=ledger_path
    )
    
    return engine, policy


def test_contract_matching(results: TestResults):
    """Test 1: Contract matching with route templates"""
    print("\n--- Test 1: Contract Matching ---")
    
    engine, _ = setup_engine(PlatformTier.OBSERVE_ONLY)
    
    # Test exact match
    event1 = RequestEvent(
        url="https://api.example.com/api/v1/status",
        method="GET",
        status_code=200,
        latency_ms=50.0
    )
    record1 = engine.process_request(event1)
    results.record(
        "Contract exact match",
        record1.contract_id == "status_v1",
        f"Expected status_v1, got {record1.contract_id}"
    )
    
    # Test template match with parameter
    event2 = RequestEvent(
        url="https://api.example.com/api/v1/deployments/abc123",
        method="GET",
        status_code=200,
        latency_ms=100.0
    )
    record2 = engine.process_request(event2)
    results.record(
        "Contract template match",
        record2.contract_id == "deploy_get_v1",
        f"Expected deploy_get_v1, got {record2.contract_id}"
    )
    
    # Test no match (unknown endpoint)
    event3 = RequestEvent(
        url="https://api.example.com/api/v1/unknown",
        method="GET",
        status_code=200,
        latency_ms=50.0
    )
    record3 = engine.process_request(event3)
    results.record(
        "Unknown endpoint detection",
        record3.contract_id is None and record3.risk_factors.unknown_endpoint,
        f"Expected None contract_id and unknown_endpoint=True"
    )
    
    # Test method disallowed
    event4 = RequestEvent(
        url="https://api.example.com/api/v1/status",
        method="POST",  # Not allowed by contract
        status_code=405,
        latency_ms=10.0
    )
    record4 = engine.process_request(event4)
    results.record(
        "Method disallowed detection",
        record4.risk_factors.method_disallowed,
        f"Expected method_disallowed=True"
    )


def test_tier_enforcement(results: TestResults):
    """Test 2: Platform tier enforcement"""
    print("\n--- Test 2: Tier Enforcement ---")
    
    # OBSERVE_ONLY tier
    engine_observe, _ = setup_engine(PlatformTier.OBSERVE_ONLY)
    event = RequestEvent(
        url="https://api.example.com/api/v1/status",
        method="GET",
        status_code=500,  # Error
        latency_ms=5000.0,  # High latency
        error_count=1
    )
    record_observe = engine_observe.process_request(event)
    
    results.record(
        "OBSERVE_ONLY allows only logging",
        set(record_observe.actions_taken) == {"log"},
        f"Expected only 'log', got {record_observe.actions_taken}"
    )
    
    results.record(
        "OBSERVE_ONLY recommends enforcement actions",
        len(record_observe.recommended_actions) > 1,
        f"Expected multiple recommended actions, got {record_observe.recommended_actions}"
    )
    
    # CONTROL tier
    engine_control, _ = setup_engine(PlatformTier.CONTROL)
    record_control = engine_control.process_request(event)
    
    results.record(
        "CONTROL tier takes enforcement actions",
        len(record_control.actions_taken) > 1,
        f"Expected multiple actions, got {record_control.actions_taken}"
    )
    
    results.record(
        "CONTROL tier enforces throttle/quarantine",
        any(action in record_control.actions_taken for action in ["throttle", "quarantine", "drop"]),
        f"Expected enforcement action, got {record_control.actions_taken}"
    )


def test_ledger_integrity(results: TestResults):
    """Test 3: Ledger chain integrity"""
    print("\n--- Test 3: Ledger Integrity ---")
    
    engine, _ = setup_engine(PlatformTier.OBSERVE_ONLY)
    
    # Process multiple requests to build chain
    for i in range(5):
        event = RequestEvent(
            url=f"https://api.example.com/api/v1/status",
            method="GET",
            status_code=200,
            latency_ms=50.0 + i * 10
        )
        engine.process_request(event)
    
    # Verify chain integrity
    is_valid, failed_index = engine.verify_ledger_integrity()
    results.record(
        "Ledger chain integrity",
        is_valid,
        f"Chain broken at index {failed_index}" if not is_valid else ""
    )
    
    # Test hash chaining
    ledger_path = engine.ledger.ledger_path
    with open(ledger_path, 'r') as f:
        lines = f.readlines()
    
    import json
    records = [json.loads(line) for line in lines[1:]]  # Skip genesis
    
    chain_valid = True
    for i in range(1, len(records)):
        if records[i].get("previous_hash") != records[i-1].get("record_hash"):
            chain_valid = False
            break
    
    results.record(
        "Hash chain continuity",
        chain_valid,
        "Previous hash doesn't match record hash"
    )


def test_risk_assessment(results: TestResults):
    """Test 4: Comprehensive risk assessment"""
    print("\n--- Test 4: Risk Assessment ---")
    
    engine, _ = setup_engine(PlatformTier.CONTROL)
    
    # Test latency score
    event_slow = RequestEvent(
        url="https://api.example.com/api/v1/status",
        method="GET",
        status_code=200,
        latency_ms=500.0  # 5x over contract limit
    )
    record_slow = engine.process_request(event_slow)
    results.record(
        "Latency score calculated",
        record_slow.risk_factors.latency_score > 1.0,
        f"Expected latency_score > 1.0, got {record_slow.risk_factors.latency_score}"
    )
    
    # Test error rate tracking
    for i in range(10):
        event_error = RequestEvent(
            url="https://api.example.com/api/v1/status",
            method="GET",
            status_code=500 if i < 5 else 200,
            latency_ms=50.0,
            error_count=1 if i < 5 else 0
        )
        engine.process_request(event_error)
    
    # Check baseline error rate
    baseline = engine.baselines.get("GET /api/v1/status")
    results.record(
        "Error rate tracked",
        baseline and baseline.error_count > 0,
        f"Expected error_count > 0, got {baseline.error_count if baseline else 'None'}"
    )
    
    # Test circuit breaker
    circuit = engine.circuits.get("GET /api/v1/status")
    results.record(
        "Circuit breaker state tracked",
        circuit is not None,
        "Circuit breaker not created"
    )
    
    # Test unknown endpoint risk
    event_unknown = RequestEvent(
        url="https://api.example.com/api/v1/unknown",
        method="GET",
        status_code=404,
        latency_ms=50.0
    )
    record_unknown = engine.process_request(event_unknown)
    results.record(
        "Unknown endpoint increases risk",
        record_unknown.risk_score > 0.5,
        f"Expected risk_score > 0.5, got {record_unknown.risk_score}"
    )


def test_decision_pipeline(results: TestResults):
    """Test 5: Deterministic decision pipeline"""
    print("\n--- Test 5: Decision Pipeline ---")
    
    engine, _ = setup_engine(PlatformTier.CONTROL)
    
    # Test ALLOW decision
    event_good = RequestEvent(
        url="https://api.example.com/api/v1/status",
        method="GET",
        status_code=200,
        latency_ms=50.0
    )
    record_good = engine.process_request(event_good)
    results.record(
        "Low risk → ALLOW decision",
        record_good.decision == Decision.ALLOW,
        f"Expected ALLOW, got {record_good.decision}"
    )
    
    # Test THROTTLE decision (medium risk)
    event_medium = RequestEvent(
        url="https://api.example.com/api/v1/status",
        method="GET",
        status_code=200,
        latency_ms=150.0,  # Over limit
        retry_count=4  # Retry storm
    )
    record_medium = engine.process_request(event_medium)
    results.record(
        "Medium risk → THROTTLE decision",
        record_medium.decision in (Decision.THROTTLE, Decision.QUARANTINE),
        f"Expected THROTTLE/QUARANTINE, got {record_medium.decision}"
    )
    
    # Test DROP decision (critical)
    event_critical = RequestEvent(
        url="https://api.example.com/api/v1/status",
        method="DELETE",  # Not allowed
        status_code=405,
        latency_ms=50.0
    )
    record_critical = engine.process_request(event_critical)
    results.record(
        "Method disallowed → DROP decision",
        record_critical.decision == Decision.DROP,
        f"Expected DROP, got {record_critical.decision}"
    )
    
    # Test reason codes
    results.record(
        "Reason codes provided",
        len(record_critical.reason_codes) > 0,
        "No reason codes provided"
    )


def test_policy_artifact_verification(results: TestResults):
    """Test 6: Policy artifact verification"""
    print("\n--- Test 6: Policy Artifact Verification ---")
    
    _, policy = setup_engine(PlatformTier.OBSERVE_ONLY)
    
    # Generate artifact
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w') as f:
        artifact_path = f.name
    
    PolicyArtifactVerifier.generate_policy_artifact(policy, artifact_path)
    
    # Verify artifact
    is_valid = PolicyArtifactVerifier.verify_policy_artifact(artifact_path, policy.policy_hash)
    results.record(
        "Policy artifact verification",
        is_valid,
        "Policy hash mismatch"
    )
    
    # Test tampered artifact
    import json
    with open(artifact_path, 'r') as f:
        artifact = json.load(f)
    
    artifact['policy']['version'] = "2.0.0"  # Tamper
    
    with open(artifact_path, 'w') as f:
        json.dump(artifact, f)
    
    is_valid_tampered = PolicyArtifactVerifier.verify_policy_artifact(artifact_path, policy.policy_hash)
    results.record(
        "Tampered artifact detected",
        not is_valid_tampered,
        "Tampered artifact passed verification"
    )


def test_cross_platform_consistency(results: TestResults):
    """Test 7: Cross-platform policy consistency"""
    print("\n--- Test 7: Cross-Platform Consistency ---")
    
    # Create two engines (GitHub OBSERVE_ONLY, GitLab CONTROL)
    engine_github, policy = setup_engine(PlatformTier.OBSERVE_ONLY)
    engine_gitlab, _ = setup_engine(PlatformTier.CONTROL)
    
    # Same request, different platforms
    event = RequestEvent(
        url="https://api.example.com/api/v1/status",
        method="GET",
        status_code=500,
        latency_ms=200.0,
        error_count=1
    )
    
    record_github = engine_github.process_request(event)
    record_gitlab = engine_gitlab.process_request(event)
    
    # Same policy version
    results.record(
        "Policy version consistent",
        record_github.policy_version == record_gitlab.policy_version,
        f"GitHub: {record_github.policy_version}, GitLab: {record_gitlab.policy_version}"
    )
    
    # Same policy hash
    results.record(
        "Policy hash consistent",
        record_github.policy_hash == record_gitlab.policy_hash,
        f"GitHub: {record_github.policy_hash}, GitLab: {record_gitlab.policy_hash}"
    )
    
    # Same risk assessment
    results.record(
        "Risk score consistent",
        abs(record_github.risk_score - record_gitlab.risk_score) < 0.01,
        f"GitHub: {record_github.risk_score}, GitLab: {record_gitlab.risk_score}"
    )
    
    # Same decision
    results.record(
        "Decision consistent",
        record_github.decision == record_gitlab.decision,
        f"GitHub: {record_github.decision}, GitLab: {record_gitlab.decision}"
    )
    
    # Different actions (tier enforcement)
    results.record(
        "Actions differ by tier",
        record_github.actions_taken != record_gitlab.actions_taken,
        "Actions should differ between OBSERVE_ONLY and CONTROL tiers"
    )


def run_all_tests():
    """Run all validation tests"""
    print("="*60)
    print("TRAFFIC GOVERNANCE ENGINE V2 - VALIDATION TEST SUITE")
    print("="*60)
    
    results = TestResults()
    
    test_contract_matching(results)
    test_tier_enforcement(results)
    test_ledger_integrity(results)
    test_risk_assessment(results)
    test_decision_pipeline(results)
    test_policy_artifact_verification(results)
    test_cross_platform_consistency(results)
    
    success = results.summary()
    
    if success:
        print("\n✅ ALL TESTS PASSED - PRODUCTION READY")
        print("∇θ — chain sealed, truth preserved.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - REVIEW REQUIRED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
