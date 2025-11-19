"""Markdown report generator."""

from datetime import datetime
from echo_engine.reporters.base import BaseReporter
from echo_engine.core.models import Investigation, FactStatus


class MarkdownReporter(BaseReporter):
    """Generates Markdown-formatted investigation reports."""

    def generate(self, investigation: Investigation) -> str:
        """Generate a Markdown report."""
        stats = self.get_summary_stats(investigation)

        sections = [
            self._generate_header(investigation),
            self._generate_overview(investigation),
            self._generate_summary_stats(stats),
            self._generate_sources_section(investigation),
            self._generate_facts_section(investigation),
            self._generate_timeline_section(investigation),
            self._generate_connections_section(investigation),
            self._generate_conclusions_section(investigation),
            self._generate_footer(),
        ]

        return "\n\n".join(sections)

    def save(self, investigation: Investigation, filepath: str) -> None:
        """Save report to file."""
        report = self.generate(investigation)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)

    def _generate_header(self, investigation: Investigation) -> str:
        """Generate report header."""
        return f"""# Investigation Report: {investigation.name}

**Investigation ID:** `{investigation.id}`
**Status:** {investigation.status.upper()}
**Created:** {investigation.created_at.strftime('%Y-%m-%d %H:%M')}
**Last Updated:** {investigation.updated_at.strftime('%Y-%m-%d %H:%M')}"""

    def _generate_overview(self, investigation: Investigation) -> str:
        """Generate overview section."""
        return f"""## Overview

### Query
> {investigation.query}

### Description
{investigation.description or '*No description provided*'}"""

    def _generate_summary_stats(self, stats: dict) -> str:
        """Generate summary statistics section."""
        return f"""## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Sources | {stats['total_sources']} |
| Total Facts Extracted | {stats['total_facts']} |
| Verified Facts | {stats['verified_facts']} |
| Disputed Facts | {stats['disputed_facts']} |
| Connections Found | {stats['total_connections']} |
| Timelines Built | {stats['total_timelines']} |
| Provenance Chains | {stats['provenance_chains']} |"""

    def _generate_sources_section(self, investigation: Investigation) -> str:
        """Generate sources section."""
        if not investigation.sources:
            return "## Sources\n\n*No sources collected*"

        lines = ["## Sources\n"]

        for i, source in enumerate(investigation.sources, 1):
            lines.append(f"### {i}. {source.name}\n")
            lines.append(f"- **Type:** {source.source_type.value}")
            lines.append(f"- **Collected:** {source.collected_at.strftime('%Y-%m-%d %H:%M')}")

            if source.author:
                lines.append(f"- **Author:** {source.author}")
            if source.url:
                lines.append(f"- **URL:** {source.url}")
            if source.filepath:
                lines.append(f"- **File:** `{source.filepath}`")

            # Show content preview
            preview = source.content[:200] + "..." if len(source.content) > 200 else source.content
            lines.append(f"\n> {preview.replace(chr(10), ' ')}\n")

        return "\n".join(lines)

    def _generate_facts_section(self, investigation: Investigation) -> str:
        """Generate facts section."""
        if not investigation.facts:
            return "## Facts\n\n*No facts extracted*"

        lines = ["## Facts\n"]

        # Group by status
        verified = [f for f in investigation.facts if f.status == FactStatus.VERIFIED]
        disputed = [f for f in investigation.facts if f.status == FactStatus.DISPUTED]
        unverified = [f for f in investigation.facts if f.status == FactStatus.UNVERIFIED]
        refuted = [f for f in investigation.facts if f.status == FactStatus.REFUTED]
        partial = [f for f in investigation.facts if f.status == FactStatus.PARTIALLY_VERIFIED]

        if verified:
            lines.append("### Verified Facts\n")
            for fact in verified:
                lines.append(f"- **{fact.statement}**")
                lines.append(f"  - Confidence: {fact.confidence.value}/5")
                if fact.entities:
                    lines.append(f"  - Entities: {', '.join(fact.entities[:5])}")
            lines.append("")

        if partial:
            lines.append("### Partially Verified Facts\n")
            for fact in partial:
                lines.append(f"- {fact.statement}")
                lines.append(f"  - Confidence: {fact.confidence.value}/5")
            lines.append("")

        if disputed:
            lines.append("### Disputed Facts\n")
            for fact in disputed:
                lines.append(f"- ~~{fact.statement}~~ (DISPUTED)")
                if fact.contradicting_evidence:
                    lines.append(f"  - Contradicted by: {len(fact.contradicting_evidence)} source(s)")
            lines.append("")

        if refuted:
            lines.append("### Refuted Facts\n")
            for fact in refuted:
                lines.append(f"- ~~{fact.statement}~~ (REFUTED)")
            lines.append("")

        if unverified:
            lines.append("### Unverified Facts\n")
            for fact in unverified[:10]:  # Limit to 10
                lines.append(f"- {fact.statement}")
            if len(unverified) > 10:
                lines.append(f"\n*...and {len(unverified) - 10} more unverified facts*")
            lines.append("")

        return "\n".join(lines)

    def _generate_timeline_section(self, investigation: Investigation) -> str:
        """Generate timeline section."""
        if not investigation.timelines:
            return "## Timeline\n\n*No timeline constructed*"

        lines = ["## Timeline\n"]

        for timeline in investigation.timelines:
            lines.append(f"### {timeline.name}\n")

            if timeline.description:
                lines.append(f"{timeline.description}\n")

            if not timeline.events:
                lines.append("*No events in timeline*\n")
                continue

            # Create timeline table
            lines.append("| Date | Event | Confidence |")
            lines.append("|------|-------|------------|")

            for event in timeline.events:
                date_str = event.timestamp.strftime('%Y-%m-%d') if event.timestamp else "Unknown"
                desc = event.description[:80] + "..." if len(event.description) > 80 else event.description
                conf = event.confidence.value

                lines.append(f"| {date_str} | {desc} | {conf}/5 |")

            lines.append("")

        return "\n".join(lines)

    def _generate_connections_section(self, investigation: Investigation) -> str:
        """Generate connections section."""
        if not investigation.connections:
            return "## Connections\n\n*No connections found*"

        lines = ["## Connections\n"]

        # Group by type
        connection_types = {}
        for conn in investigation.connections:
            conn_type = conn.connection_type.value
            if conn_type not in connection_types:
                connection_types[conn_type] = []
            connection_types[conn_type].append(conn)

        for conn_type, connections in connection_types.items():
            lines.append(f"### {conn_type.replace('_', ' ').title()} ({len(connections)})\n")

            for conn in connections[:5]:  # Limit to 5 per type
                strength_bar = "█" * int(conn.strength * 5) + "░" * (5 - int(conn.strength * 5))
                lines.append(f"- {strength_bar} {conn.description[:60]}")

            if len(connections) > 5:
                lines.append(f"\n*...and {len(connections) - 5} more*")
            lines.append("")

        return "\n".join(lines)

    def _generate_conclusions_section(self, investigation: Investigation) -> str:
        """Generate conclusions section."""
        if not investigation.conclusions:
            return "## Conclusions\n\n*No conclusions drawn yet*"

        lines = ["## Conclusions\n"]

        for i, conclusion in enumerate(investigation.conclusions, 1):
            lines.append(f"{i}. {conclusion}")

        return "\n".join(lines)

    def _generate_footer(self) -> str:
        """Generate report footer."""
        return f"""---

*Report generated by Echo Reverse Engineering Engine*
*Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"""
