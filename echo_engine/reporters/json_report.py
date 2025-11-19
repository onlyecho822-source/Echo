"""JSON report generator."""

import json
from datetime import datetime
from typing import Optional
from echo_engine.reporters.base import BaseReporter
from echo_engine.core.models import Investigation


class JSONReporter(BaseReporter):
    """Generates JSON-formatted investigation reports."""

    def generate(self, investigation: Investigation) -> str:
        """Generate a JSON report."""
        report = self._build_report(investigation)
        return json.dumps(report, indent=2)

    def save(self, investigation: Investigation, filepath: str) -> None:
        """Save report to file."""
        report = self.generate(investigation)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)

    def _build_report(self, investigation: Investigation) -> dict:
        """Build the report dictionary."""
        stats = self.get_summary_stats(investigation)

        return {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "engine_version": "0.1.0",
                "report_type": "investigation",
            },
            "investigation": {
                "id": investigation.id,
                "name": investigation.name,
                "query": investigation.query,
                "description": investigation.description,
                "status": investigation.status,
                "created_at": investigation.created_at.isoformat(),
                "updated_at": investigation.updated_at.isoformat(),
                "confidence": investigation.confidence.value,
            },
            "summary": stats,
            "analysis": {
                "sources": self._analyze_sources(investigation),
                "facts": self._analyze_facts(investigation),
                "timelines": self._analyze_timelines(investigation),
                "connections": self._analyze_connections(investigation),
                "provenance": self._analyze_provenance(investigation),
            },
            "conclusions": investigation.conclusions,
            "confidence_assessment": self._assess_confidence(investigation),
        }

    def _analyze_sources(self, investigation: Investigation) -> dict:
        """Analyze sources for the report."""
        sources = investigation.sources

        type_counts = {}
        for source in sources:
            t = source.source_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "total": len(sources),
            "by_type": type_counts,
            "sources": [
                {
                    "id": s.id,
                    "name": s.name,
                    "type": s.source_type.value,
                    "collected_at": s.collected_at.isoformat(),
                    "content_length": len(s.content),
                    "author": s.author,
                    "url": s.url,
                }
                for s in sources
            ],
        }

    def _analyze_facts(self, investigation: Investigation) -> dict:
        """Analyze facts for the report."""
        facts = investigation.facts

        status_counts = {}
        confidence_counts = {}

        for fact in facts:
            status = fact.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

            conf = fact.confidence.name
            confidence_counts[conf] = confidence_counts.get(conf, 0) + 1

        return {
            "total": len(facts),
            "by_status": status_counts,
            "by_confidence": confidence_counts,
            "facts": [
                {
                    "id": f.id,
                    "statement": f.statement,
                    "status": f.status.value,
                    "confidence": f.confidence.value,
                    "entities": f.entities,
                    "keywords": f.keywords[:5],
                    "supporting_evidence": len(f.supporting_evidence),
                    "contradicting_evidence": len(f.contradicting_evidence),
                }
                for f in facts
            ],
        }

    def _analyze_timelines(self, investigation: Investigation) -> dict:
        """Analyze timelines for the report."""
        timelines = investigation.timelines

        return {
            "total": len(timelines),
            "timelines": [
                {
                    "id": t.id,
                    "name": t.name,
                    "event_count": len(t.events),
                    "date_range": {
                        "start": t.start_date.isoformat() if t.start_date else None,
                        "end": t.end_date.isoformat() if t.end_date else None,
                    },
                }
                for t in timelines
            ],
        }

    def _analyze_connections(self, investigation: Investigation) -> dict:
        """Analyze connections for the report."""
        connections = investigation.connections

        type_counts = {}
        for conn in connections:
            t = conn.connection_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "total": len(connections),
            "by_type": type_counts,
            "average_strength": (
                sum(c.strength for c in connections) / len(connections)
                if connections else 0
            ),
        }

    def _analyze_provenance(self, investigation: Investigation) -> dict:
        """Analyze provenance chains for the report."""
        chains = investigation.provenance_chains

        return {
            "total_chains": len(chains),
            "chains": [
                {
                    "id": c.id,
                    "name": c.name,
                    "node_count": len(c.nodes),
                    "root_id": c.root_id,
                }
                for c in chains
            ],
        }

    def _assess_confidence(self, investigation: Investigation) -> dict:
        """Assess overall investigation confidence."""
        facts = investigation.facts

        if not facts:
            return {
                "level": "insufficient_data",
                "score": 0,
                "explanation": "No facts extracted",
            }

        verified = len(investigation.get_verified_facts())
        disputed = len(investigation.get_disputed_facts())
        total = len(facts)

        verification_rate = verified / total
        dispute_rate = disputed / total

        score = (verification_rate * 100) - (dispute_rate * 50)
        score = max(0, min(100, score))

        if score >= 80:
            level = "high"
        elif score >= 60:
            level = "medium"
        elif score >= 40:
            level = "low"
        else:
            level = "very_low"

        return {
            "level": level,
            "score": round(score, 2),
            "verification_rate": round(verification_rate * 100, 2),
            "dispute_rate": round(dispute_rate * 100, 2),
        }

    def get_compact_report(self, investigation: Investigation) -> str:
        """Generate a compact JSON report."""
        stats = self.get_summary_stats(investigation)

        compact = {
            "id": investigation.id,
            "name": investigation.name,
            "status": investigation.status,
            "summary": stats,
            "confidence": self._assess_confidence(investigation),
        }

        return json.dumps(compact)
