# ECP Enforcement Layer

## Overview

The Enforcement Layer transforms the Echo Coordination Protocol from an **optional governance framework** into a **mandatory, architecturally non-negotiable system**. No AI action can bypass the Event → Classification → Consensus → Human Authority flow.

## Core Components

### 1. Mandatory Ingress Gate (`enforcement/gate.py`)

The **HardGate** enforces ECP compliance at system ingress points. It acts as a decorator-based enforcement mechanism that intercepts all agentive actions.

#### Key Features

- **Context Validation**: Every function requires valid ECP context with required fields
- **Automatic Event Creation**: All agentive actions are automatically logged as events
- **Mandatory Classification**: Actions with `agency_present: true` generate automatic classifications
- **Consensus Triggering**: Multiple classifications trigger divergence scoring
- **Automatic Escalation**: High divergence automatically escalates to human review

#### Usage

```python
from ai_coordination.enforcement import initialize_global_gate, ecp_mandatory

# Initialize global gate
gate = initialize_global_gate(storage_backend, policy)

# Decorate functions to enforce ECP compliance
@ecp_mandatory
def make_decision(decision_data, context):
    """
    Context must include:
    - causation: "ai_decision" | "natural" | "human_directed"
    - agency_present: true | false
    - duty_of_care: "critical" | "high" | "medium" | "low"
    - knowledge_level: "full" | "partial" | "none"
    - control_level: "direct" | "indirect" | "none"
    """
    # Function body
    return result
```

#### Decorator Behavior

When a function decorated with `@ecp_mandatory` is called:

1. **Context Extraction**: Extracts ECP context from function parameters
2. **Validation**: Validates all required context fields are present
3. **Event Creation**: Creates immutable event record
4. **Function Execution**: Executes the wrapped function
5. **Classification**: If `agency_present: true`, creates automatic classification
6. **Consensus Check**: Triggers divergence scoring if multiple agents involved
7. **Escalation**: Escalates to human if divergence exceeds threshold

### 2. Storage Consistency Enforcer (`enforcement/consistency.py`)

The **ImmutabilityGuard** wraps storage backends to enforce ECP immutability guarantees at the storage layer.

#### Key Features

- **Hash Chain**: SHA-256 hash chain prevents tampering
- **Event Validation**: Enforces ECP event structure requirements
- **Immutability**: Prevents event overwriting or deletion
- **Chain Verification**: Detects any breaks in the hash chain
- **Archive Preservation**: Archives old versions when updating classifications

#### Usage

```python
from ai_coordination.enforcement import ImmutabilityGuard

# Wrap storage backend
guard = ImmutabilityGuard(storage_backend)

# Store events with immutability guarantees
event_hash = guard.store_event(event_data)

# Store classifications with referential integrity
class_hash = guard.store_classification(classification_data)

# Verify entire chain integrity
errors = guard.verify_chain()
if errors:
    print(f"Chain integrity issues detected: {errors}")
```

#### Consistency Checker

The **StorageConsistencyChecker** periodically verifies storage integrity:

```python
from ai_coordination.enforcement import StorageConsistencyChecker

checker = StorageConsistencyChecker(guard)
result = checker.run_check()

print(f"Status: {result['status']}")
print(f"Errors: {result['total_errors']}")
```

### 3. Violation Tracker (`enforcement/violation_tracker.py`)

The **ViolationTracker** records and escalates all ECP compliance violations.

#### Violation Types

- `missing_context`: Function called without required ECP context
- `incomplete_context`: Context missing required fields
- `unregistered_agent`: Agent not registered in system
- `immutability_breach`: Attempt to modify immutable data
- `chain_broken`: Hash chain integrity violation
- `invalid_reference`: Classification references non-existent event

#### Severity Levels

- **blocking**: Immediately halts execution and escalates
- **warning**: Logged and tracked but execution continues
- **audit**: Logged for audit trail only

#### Usage

```python
from ai_coordination.enforcement import ViolationTracker

tracker = ViolationTracker(storage_backend)

# Record a violation
violation_id = tracker.record_violation(
    violation_type="missing_context",
    severity="blocking",
    message="Function called without ECP context",
    agent_id="manus",
    function_name="analyze_data",
    stack_trace="..."
)

# Query violations
blocking = tracker.get_blocking_violations()
agent_violations = tracker.get_violations_by_agent("chatgpt")
recent = tracker.get_recent_violations(hours=24)

# Generate report
report = tracker.generate_violation_report()
print(f"Total violations: {report['total_violations']}")
print(f"Blocking: {report['blocking_violations']}")
```

## Integration Pattern

### Step 1: Initialize Enforcement

```python
from ai_coordination.enforcement import initialize_global_gate, ImmutabilityGuard, ViolationTracker

# Initialize gate
gate = initialize_global_gate(storage_backend, policy_config)

# Initialize consistency enforcer
guard = ImmutabilityGuard(storage_backend)

# Initialize violation tracker
tracker = ViolationTracker(storage_backend)
```

### Step 2: Decorate Critical Functions

```python
from ai_coordination.enforcement import ecp_mandatory

@ecp_mandatory
def critical_decision_function(data, context):
    # All agentive actions flow through ECP
    return result
```

### Step 3: Monitor Compliance

```python
# Periodic compliance check
errors = guard.verify_chain()
if errors:
    print("Chain integrity issues!")

# Violation reporting
report = tracker.generate_violation_report()
if report['blocking_violations'] > 0:
    print("Critical violations detected!")
```

## Enforcement Guarantees

✅ **No Bypass**: No action can skip Event → Classification → Consensus flow  
✅ **Immutable Logs**: SHA-256 hash chain prevents tampering  
✅ **Automatic Escalation**: High divergence automatically escalates  
✅ **Violation Tracking**: All compliance breaches are recorded  
✅ **Chain Integrity**: Detects any tampering or corruption  
✅ **Human Authority**: Final decisions remain with humans  

## Configuration

The enforcement layer respects the policy configuration in `config/policy.json`:

```json
{
  "divergence": {
    "threshold": 0.4,
    "weights": {
      "ethical_status": 0.4,
      "confidence": 0.3,
      "risk_estimate": 0.3
    }
  },
  "escalation": {
    "automatic_at_divergence": 0.4,
    "automatic_at_unethical": true,
    "notification_channels": ["github_issues", "log_file"],
    "timeout_hours": 72
  },
  "security": {
    "hash_algorithm": "sha256",
    "require_git_commit": true,
    "log_all_operations": true,
    "validate_json_schema": true
  }
}
```

## Best Practices

1. **Always Provide Context**: Every agentive action must include valid ECP context
2. **Use Decorators**: Apply `@ecp_mandatory` to all decision-making functions
3. **Monitor Violations**: Regularly check violation reports for compliance issues
4. **Verify Chain**: Periodically verify hash chain integrity
5. **Escalate Properly**: Let the system handle escalation automatically
6. **Archive History**: Preserve all versions for audit trail

## Security Properties

- **Tamper-Proof**: Hash chain prevents modification of events
- **Audit Trail**: Complete record of all decisions and violations
- **Non-Repudiation**: Agents cannot deny their actions
- **Referential Integrity**: Classifications must reference valid events
- **Automatic Escalation**: No human can suppress violations
- **Transparent Scoring**: Divergence calculation is explicit and auditable

## Troubleshooting

### Chain Integrity Errors

If `verify_chain()` returns errors, the storage may be corrupted:

```python
errors = guard.verify_chain()
for error in errors:
    print(f"Chain error at index {error['index']}: {error['message']}")
```

### Missing Context Violations

Ensure all decorated functions receive proper context:

```python
# ❌ Wrong - will raise violation
result = function(data)

# ✅ Correct - includes context
context = {
    "causation": "ai_decision",
    "agency_present": True,
    "duty_of_care": "high",
    "knowledge_level": "full",
    "control_level": "direct"
}
result = function(data, context=context)
```

### Unregistered Agent Violations

Register agents before they can perform actions:

```python
# Register agent
storage_backend.register_agent("manus")

# Now decorated functions work
@ecp_mandatory
def agent_function(data, context):
    return result
```

## Future Enhancements

- Real-time violation monitoring dashboard
- Automated remediation for certain violation types
- Machine learning-based anomaly detection
- Advanced consensus algorithms
- Multi-signature approval for critical decisions
