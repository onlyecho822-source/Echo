"""Command-line interface for Echo Universe.

This is the user-facing layer for Echo's memory prosthetic.

Design principles:
- Friction is intentional (make it harder, not easier)
- Falsification is mandatory
- Founder constraints are enforced
- Audit trail is always available
"""

import json
import sys
from typing import Optional

import click

from .models import BeliefStatus
from .storage import BeliefStorage


@click.group()
@click.version_option(version="0.1.0", prog_name="echo")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Echo Universe - Immutable belief tracking with mandatory falsification.

    Echo is a memory prosthetic that refuses to lie.

    Core principles:
    - Beliefs must have falsification criteria
    - All changes are logged immutably
    - Founder has no special privileges
    - Shadow decisions are detected
    """
    # Initialize storage in context
    ctx.ensure_object(dict)
    ctx.obj["storage"] = BeliefStorage()


@main.group()
@click.pass_context
def belief(ctx: click.Context) -> None:
    """Manage beliefs with falsification criteria."""
    pass


@belief.command()
@click.option("--statement", required=True, help="The belief statement")
@click.option(
    "--falsify",
    required=True,
    help="Falsification criteria (how you could be wrong) - MANDATORY",
)
@click.option(
    "--tier",
    type=click.Choice(["speculation", "hypothesis", "evidence", "conclusion", "truth"]),
    default="hypothesis",
    help="Verification Ladder tier",
)
@click.option(
    "--confidence",
    type=float,
    default=0.5,
    help="Confidence level (0.0-1.0)",
)
@click.option(
    "--created-by",
    default="",
    help="Your email (optional, for audit trail)",
)
@click.option(
    "--tags",
    multiple=True,
    help="Tags for organization (can specify multiple times)",
)
@click.pass_context
def create(
    ctx: click.Context,
    statement: str,
    falsify: str,
    tier: str,
    confidence: float,
    created_by: str,
    tags: tuple,
) -> None:
    """Create a new belief with falsification criteria.

    Falsification is MANDATORY. You must specify how you could be wrong.

    Example:
        echo belief create \\
          --statement "Our landing page converts at >5%" \\
          --falsify "If conversion <3% after 1000 visitors, belief is false" \\
          --tier hypothesis \\
          --confidence 0.7
    """
    storage: BeliefStorage = ctx.obj["storage"]

    try:
        belief = storage.create_belief(
            statement=statement,
            falsification=falsify,
            tier=tier,
            confidence=confidence,
            created_by=created_by,
            tags=list(tags),
        )

        click.echo(f"✓ Belief created: {belief.belief_id}")
        click.echo(f"  Statement: {belief.statement}")
        click.echo(f"  Falsification: {belief.falsification}")
        click.echo(f"  Tier: {belief.tier}")
        click.echo(f"  Confidence: {belief.confidence}")

        # Warn if founder
        if created_by and storage._is_founder(created_by):
            click.echo()
            click.echo("⚠️  FOUNDER ACTION LOGGED")
            click.echo("   You have no special privileges.")
            click.echo("   This action is in the public audit trail.")

    except ValueError as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@belief.command(name="list")
@click.option(
    "--status",
    type=click.Choice(["active", "falsified", "deprecated", "superseded"]),
    help="Filter by status",
)
@click.option(
    "--created-by",
    help="Filter by creator email",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output as JSON",
)
@click.pass_context
def list_beliefs(
    ctx: click.Context,
    status: Optional[str],
    created_by: Optional[str],
    output_json: bool,
) -> None:
    """List all beliefs."""
    storage: BeliefStorage = ctx.obj["storage"]

    # Convert status string to enum
    status_enum = BeliefStatus(status) if status else None

    beliefs = storage.list_beliefs(status=status_enum, created_by=created_by)

    if output_json:
        # Output as JSON
        beliefs_data = [
            {
                "belief_id": b.belief_id,
                "statement": b.statement,
                "falsification": b.falsification,
                "tier": b.tier,
                "confidence": b.confidence,
                "status": b.status,
                "created_at": b.created_at.isoformat(),
                "created_by": b.created_by,
                "evidence_count": len(b.evidence),
            }
            for b in beliefs
        ]
        click.echo(json.dumps(beliefs_data, indent=2))
    else:
        # Human-readable output
        if not beliefs:
            click.echo("No beliefs found.")
            return

        click.echo(f"Found {len(beliefs)} belief(s):\n")
        for b in beliefs:
            click.echo(f"[{b.belief_id[:8]}] {b.statement}")
            click.echo(f"  Falsification: {b.falsification}")
            click.echo(f"  Tier: {b.tier} | Confidence: {b.confidence} | Status: {b.status}")
            click.echo(f"  Created: {b.created_at.isoformat()}")
            if b.evidence:
                click.echo(f"  Evidence: {len(b.evidence)} item(s)")
            click.echo()


@belief.command()
@click.argument("belief_id")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def show(ctx: click.Context, belief_id: str, output_json: bool) -> None:
    """Show detailed information about a belief."""
    storage: BeliefStorage = ctx.obj["storage"]

    belief = storage.get_belief(belief_id)
    if belief is None:
        click.echo(f"✗ Belief {belief_id} not found", err=True)
        sys.exit(1)

    if output_json:
        click.echo(belief.model_dump_json(indent=2))
    else:
        click.echo(f"Belief: {belief.belief_id}")
        click.echo(f"Statement: {belief.statement}")
        click.echo(f"Falsification: {belief.falsification}")
        click.echo(f"Tier: {belief.tier}")
        click.echo(f"Confidence: {belief.confidence}")
        click.echo(f"Status: {belief.status}")
        click.echo(f"Created: {belief.created_at.isoformat()}")
        click.echo(f"Created by: {belief.created_by or '(anonymous)'}")

        if belief.evidence:
            click.echo(f"\nEvidence ({len(belief.evidence)} item(s)):")
            for e in belief.evidence:
                support_str = "✓ Supports" if e.supports else "✗ Refutes"
                click.echo(f"  [{support_str}] {e.description}")
                click.echo(f"    Source: {e.source}")
                click.echo(f"    Added: {e.added_at.isoformat()}")

        if belief.notes:
            click.echo(f"\nNotes: {belief.notes}")


@belief.command()
@click.argument("belief_id")
@click.option("--evidence", required=True, help="Evidence description")
@click.option("--source", required=True, help="Evidence source (URL, citation, etc.)")
@click.option(
    "--supports/--refutes",
    default=True,
    help="Does this evidence support or refute the belief?",
)
@click.option("--added-by", default="", help="Your email (for audit trail)")
@click.pass_context
def add_evidence(
    ctx: click.Context,
    belief_id: str,
    evidence: str,
    source: str,
    supports: bool,
    added_by: str,
) -> None:
    """Add evidence to a belief."""
    storage: BeliefStorage = ctx.obj["storage"]

    try:
        evidence_obj = storage.add_evidence(
            belief_id=belief_id,
            description=evidence,
            source=source,
            supports=supports,
            added_by=added_by,
        )

        support_str = "supports" if supports else "refutes"
        click.echo(f"✓ Evidence added ({support_str} belief)")
        click.echo(f"  Evidence ID: {evidence_obj.evidence_id}")

        # Warn if founder
        if added_by and storage._is_founder(added_by):
            click.echo()
            click.echo("⚠️  FOUNDER ACTION LOGGED")

    except ValueError as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@belief.command()
@click.argument("belief_id")
@click.option("--reason", required=True, help="Why falsification criteria were met")
@click.option("--falsified-by", default="", help="Your email (for audit trail)")
@click.pass_context
def falsify(
    ctx: click.Context,
    belief_id: str,
    reason: str,
    falsified_by: str,
) -> None:
    """Mark a belief as falsified (falsification criteria met)."""
    storage: BeliefStorage = ctx.obj["storage"]

    try:
        storage.falsify_belief(
            belief_id=belief_id,
            reason=reason,
            falsified_by=falsified_by,
        )

        click.echo(f"✓ Belief {belief_id} marked as FALSIFIED")
        click.echo(f"  Reason: {reason}")

    except ValueError as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.pass_context
def audit(ctx: click.Context) -> None:
    """Generate audit report with integrity verification."""
    storage: BeliefStorage = ctx.obj["storage"]

    report = storage.audit_report()

    click.echo("=== ECHO AUDIT REPORT ===\n")

    # Ledger integrity
    click.echo("Ledger Integrity:")
    if report["ledger"]["integrity_verified"]:
        click.echo("  ✓ VERIFIED - Hash chain intact")
    else:
        click.echo("  ✗ COMPROMISED - Hash chain broken!")

    click.echo(f"  Total entries: {report['ledger']['total_entries']}")
    click.echo(f"  First entry: {report['ledger']['first_entry']}")
    click.echo(f"  Last entry: {report['ledger']['last_entry']}")

    # Beliefs
    click.echo("\nBeliefs:")
    click.echo(f"  Total: {report['beliefs']['total']}")
    click.echo(f"  Active: {report['beliefs']['active']}")
    click.echo(f"  Falsified: {report['beliefs']['falsified']}")
    click.echo(f"  Deprecated: {report['beliefs']['deprecated']}")

    # Founder actions
    click.echo(f"\nFounder Actions: {report['founder_actions']}")
    if report['founder_actions'] > 0:
        click.echo("  (All founder actions are in public audit trail)")

    # Shadow decisions
    click.echo(f"\nShadow Decisions Detected: {report['shadow_decisions']}")
    if report['shadow_decisions'] > 0:
        click.echo("  ⚠️  WARNING: Retroactive beliefs detected")
        shadow_decisions = storage.detect_shadow_decisions()
        for sd in shadow_decisions:
            click.echo(f"    - Belief {sd['belief_id'][:8]}: {sd['decision_description']}")


@main.command()
@click.pass_context
def founder_audit(ctx: click.Context) -> None:
    """Show all founder actions (transparency requirement)."""
    storage: BeliefStorage = ctx.obj["storage"]

    actions = storage.audit_founder_actions()

    if not actions:
        click.echo("No founder actions recorded.")
        return

    click.echo(f"=== FOUNDER ACTIONS ({len(actions)}) ===\n")
    click.echo("All founder actions are logged for transparency.")
    click.echo("Founders have NO special privileges.\n")

    for action in actions:
        click.echo(f"[{action['timestamp']}] {action['action']}")
        click.echo(f"  Founder: {action['founder_email']}")
        click.echo(f"  Details: {action['details']}")
        click.echo()


if __name__ == "__main__":
    main()
