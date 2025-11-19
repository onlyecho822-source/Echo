"""
Basic Usage Example - Aletheia AGI Framework
============================================

This example demonstrates basic usage of the Aletheia AGI framework,
showing how to:
- Initialize the system
- Execute actions with alignment checking
- Propose improvements
- Work with governance
- Generate reports

IMPORTANT: This is a conceptual demonstration. The framework provides
interfaces and structure, not actual AGI capabilities.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from aletheia_agi import AletheiaAGI
from aletheia_agi.improvement.improvement_controller import ImprovementType
from aletheia_agi.governance.governance_stack import DecisionType, GovernanceBodyType, VoteType
from aletheia_agi.corrigibility.corrigibility_engine import OverrideLevel
from aletheia_agi.corrigibility.shutdown_protocol import ShutdownLevel, ShutdownReason


def main():
    """Demonstrate basic usage of the Aletheia AGI framework."""

    print("=" * 60)
    print("Aletheia AGI Framework - Basic Usage Demo")
    print("=" * 60)
    print()

    # Initialize the system
    print("1. Initializing Aletheia AGI...")
    agi = AletheiaAGI(config={'environment': 'demo'})
    print("   System initialized successfully.")
    print()

    # Execute an action
    print("2. Executing an action with alignment checking...")
    result = agi.execute_action(
        action_type="analyze_data",
        action_details={
            'data_source': 'user_provided',
            'analysis_type': 'statistical',
            'has_consent': True,
            'affects_user': True,
            'reasons': ['User requested analysis'],
            'goal': 'Provide accurate statistical insights'
        },
        actor="user"
    )
    print(f"   Action permitted: {result['action_permitted']}")
    if result['success']:
        print(f"   Explanation: {result['explanation'][:100]}...")
    print()

    # Try an action that would violate invariants
    print("3. Attempting action that violates invariants...")
    blocked_result = agi.execute_action(
        action_type="acquire_resources",
        action_details={
            'acquires_resources': True,
            'oversight_approved': False,
            'reasons': ['Self-expansion']
        },
        actor="system"
    )
    print(f"   Action permitted: {blocked_result['action_permitted']}")
    print(f"   Reason: {blocked_result.get('reason', 'N/A')}")
    print()

    # Propose an improvement
    print("4. Proposing a system improvement...")
    improvement = agi.propose_improvement(
        improvement_type=ImprovementType.EFFICIENCY,
        title="Optimize data processing pipeline",
        description="Improve processing speed while maintaining accuracy",
        proposed_changes=[
            "Implement caching for frequent queries",
            "Add parallel processing for independent tasks"
        ],
        expected_benefits=[
            "30% faster response times",
            "Reduced computational overhead"
        ],
        potential_risks=[
            "Increased memory usage",
            "Cache invalidation complexity"
        ],
        affected_invariants=["transparency"],
        proposer="developer"
    )
    print(f"   Improvement ID: {improvement.get('improvement_id', 'N/A')[:8]}...")
    print(f"   Stage: {improvement.get('stage', 'N/A')}")
    print(f"   Required reviews: {improvement.get('required_reviews', 'N/A')}")
    print()

    # Create a governance decision
    print("5. Creating a governance decision...")
    decision = agi.create_governance_decision(
        decision_type=DecisionType.POLICY_CHANGE,
        title="Update data retention policy",
        description="Modify retention period for user analytics",
        proposer="policy_team"
    )
    print(f"   Decision ID: {decision['decision_id'][:8]}...")
    print(f"   Required bodies: {', '.join(decision['required_bodies'])}")
    print(f"   Requires dual-key: {decision['requires_dual_key']}")
    print()

    # Add governance members and vote
    print("6. Adding governance members and casting votes...")
    member1 = agi.governance.add_member(
        name="Dr. Safety",
        body=GovernanceBodyType.TECHNICAL_SAFETY,
        role="Safety Lead",
        has_veto_power=True
    )
    member2 = agi.governance.add_member(
        name="Ethics Chair",
        body=GovernanceBodyType.ETHICS_COUNCIL,
        role="Council Chair",
        has_veto_power=True
    )

    # Cast votes
    agi.governance.cast_vote(
        decision['decision_id'],
        member2.id,
        VoteType.APPROVE,
        "Policy aligns with ethical guidelines"
    )
    print("   Vote cast by Ethics Chair: APPROVE")
    print()

    # Generate system status
    print("7. Getting system status...")
    status = agi.get_system_status()
    print(f"   Operations performed: {status['operation_count']}")
    print(f"   Invariants defined: {status['invariants']['total']}")
    print(f"   Active improvements: {status['improvements']['active']}")
    print(f"   Pending governance decisions: {status['governance']['decisions']['pending']}")
    print()

    # Generate alignment report
    print("8. Generating alignment report...")
    report = agi.generate_alignment_report()
    print(f"   Report generated at: {report['generated_at']}")
    print(f"   Total invariants: {report['invariant_report']['total_invariants']}")
    print(f"   Audit integrity: {report['audit_compliance']['integrity_status']['valid']}")
    print()

    # Demonstrate override capability
    print("9. Processing an override command...")
    override_result = agi.process_override(
        level=OverrideLevel.OPERATIONAL,
        command="pause_improvement_pipeline",
        issuer="safety_officer",
        reason="Review pending for critical change"
    )
    print(f"   Override executed: {override_result.get('executed', False)}")
    print()

    # Final summary
    print("=" * 60)
    print("Demo completed successfully!")
    print()
    print("Key points demonstrated:")
    print("- Actions are checked against alignment invariants")
    print("- Unsafe actions are blocked automatically")
    print("- Improvements go through formal pipeline")
    print("- Governance requires multi-stakeholder approval")
    print("- All actions are logged for audit")
    print("- System remains corrigible to human oversight")
    print("=" * 60)


if __name__ == "__main__":
    main()
