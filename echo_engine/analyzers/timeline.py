"""Timeline reconstruction module."""

import re
from datetime import datetime
from typing import Optional
from echo_engine.core.models import (
    Source,
    Fact,
    Timeline,
    TimelineEvent,
    ConfidenceLevel,
)


class TimelineReconstructor:
    """
    Reconstructs timelines from facts and sources.

    Extracts temporal information and orders events chronologically
    to build a coherent narrative of what happened when.
    """

    # Month name mappings
    MONTHS = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12,
    }

    # Relative time expressions
    RELATIVE_PATTERNS = {
        'yesterday': -1,
        'today': 0,
        'tomorrow': 1,
        'last week': -7,
        'next week': 7,
        'last month': -30,
        'next month': 30,
        'last year': -365,
        'next year': 365,
    }

    def __init__(self, config: Optional[dict] = None):
        """Initialize the timeline reconstructor."""
        self.config = config or {}
        self.reference_date = self.config.get("reference_date", datetime.now())

    def reconstruct(
        self,
        name: str,
        facts: list[Fact],
        sources: list[Source],
        description: str = "",
    ) -> Timeline:
        """
        Reconstruct a timeline from facts and sources.

        Args:
            name: Name of the timeline
            facts: List of facts to analyze
            sources: List of sources
            description: Optional description

        Returns:
            A Timeline object with ordered events
        """
        timeline = Timeline(
            name=name,
            description=description,
        )

        # Extract events from facts
        for fact in facts:
            event = self._extract_event_from_fact(fact)
            if event:
                timeline.add_event(event)

        # Extract events directly from sources
        for source in sources:
            events = self._extract_events_from_source(source)
            for event in events:
                timeline.add_event(event)

        return timeline

    def _extract_event_from_fact(self, fact: Fact) -> Optional[TimelineEvent]:
        """Extract a timeline event from a fact."""
        timestamp, precision = self._parse_temporal_info(fact.statement)

        if not timestamp:
            return None

        return TimelineEvent(
            description=fact.statement,
            timestamp=timestamp,
            timestamp_precision=precision,
            source_ids=fact.source_ids,
            fact_ids=[fact.id],
            entities=fact.entities,
            confidence=fact.confidence,
        )

    def _extract_events_from_source(self, source: Source) -> list[TimelineEvent]:
        """Extract timeline events directly from source content."""
        events = []
        sentences = self._split_sentences(source.content)

        for sentence in sentences:
            timestamp, precision = self._parse_temporal_info(sentence)
            if timestamp:
                event = TimelineEvent(
                    description=sentence.strip(),
                    timestamp=timestamp,
                    timestamp_precision=precision,
                    source_ids=[source.id],
                    confidence=ConfidenceLevel.MEDIUM,
                )
                events.append(event)

        return events

    def _parse_temporal_info(self, text: str) -> tuple[Optional[datetime], str]:
        """
        Parse temporal information from text.

        Returns:
            Tuple of (datetime, precision) or (None, "")
        """
        text_lower = text.lower()

        # Try various date formats

        # Format: Month DD, YYYY or DD Month YYYY
        for month_name, month_num in self.MONTHS.items():
            # Month DD, YYYY
            pattern = rf'{month_name}\s+(\d{{1,2}}),?\s+(\d{{4}})'
            match = re.search(pattern, text_lower)
            if match:
                try:
                    day = int(match.group(1))
                    year = int(match.group(2))
                    return datetime(year, month_num, day), "exact"
                except ValueError:
                    continue

            # DD Month YYYY
            pattern = rf'(\d{{1,2}})\s+{month_name}\s+(\d{{4}})'
            match = re.search(pattern, text_lower)
            if match:
                try:
                    day = int(match.group(1))
                    year = int(match.group(2))
                    return datetime(year, month_num, day), "exact"
                except ValueError:
                    continue

            # Month YYYY (no day)
            pattern = rf'{month_name}\s+(\d{{4}})'
            match = re.search(pattern, text_lower)
            if match:
                try:
                    year = int(match.group(1))
                    return datetime(year, month_num, 1), "month"
                except ValueError:
                    continue

        # Format: MM/DD/YYYY or DD/MM/YYYY or YYYY-MM-DD
        date_patterns = [
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', 'ymd'),
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', 'mdy'),
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', 'mdy'),
        ]

        for pattern, fmt in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if fmt == 'ymd':
                        year, month, day = match.groups()
                    else:  # mdy
                        month, day, year = match.groups()
                    return datetime(int(year), int(month), int(day)), "exact"
                except ValueError:
                    continue

        # Format: Just year
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
        if year_match:
            year = int(year_match.group(1))
            return datetime(year, 1, 1), "year"

        # Relative expressions
        for expression, days_delta in self.RELATIVE_PATTERNS.items():
            if expression in text_lower:
                from datetime import timedelta
                target_date = self.reference_date + timedelta(days=days_delta)
                return target_date, "approximate"

        return None, ""

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def merge_timelines(self, timelines: list[Timeline], name: str) -> Timeline:
        """
        Merge multiple timelines into one.

        Args:
            timelines: List of timelines to merge
            name: Name for the merged timeline

        Returns:
            A merged Timeline
        """
        merged = Timeline(
            name=name,
            description=f"Merged from {len(timelines)} timelines",
        )

        for timeline in timelines:
            for event in timeline.events:
                merged.add_event(event)

        return merged

    def find_gaps(self, timeline: Timeline) -> list[dict]:
        """
        Find temporal gaps in a timeline.

        Args:
            timeline: The timeline to analyze

        Returns:
            List of gap descriptions
        """
        gaps = []

        if len(timeline.events) < 2:
            return gaps

        sorted_events = sorted(
            [e for e in timeline.events if e.timestamp],
            key=lambda e: e.timestamp
        )

        for i in range(len(sorted_events) - 1):
            current = sorted_events[i]
            next_event = sorted_events[i + 1]

            delta = next_event.timestamp - current.timestamp
            days = delta.days

            # Flag significant gaps
            if days > 30:  # More than a month
                gaps.append({
                    "start_date": current.timestamp.isoformat(),
                    "end_date": next_event.timestamp.isoformat(),
                    "days": days,
                    "before_event": current.description[:50],
                    "after_event": next_event.description[:50],
                })

        return gaps

    def get_timeline_summary(self, timeline: Timeline) -> dict:
        """
        Get a summary of a timeline.

        Args:
            timeline: The timeline to summarize

        Returns:
            Summary dictionary
        """
        dated_events = [e for e in timeline.events if e.timestamp]
        undated_events = [e for e in timeline.events if not e.timestamp]

        # Count entities
        all_entities = []
        for event in timeline.events:
            all_entities.extend(event.entities)

        entity_counts = {}
        for entity in all_entities:
            entity_counts[entity] = entity_counts.get(entity, 0) + 1

        top_entities = sorted(
            entity_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            "total_events": len(timeline.events),
            "dated_events": len(dated_events),
            "undated_events": len(undated_events),
            "date_range": {
                "start": timeline.start_date.isoformat() if timeline.start_date else None,
                "end": timeline.end_date.isoformat() if timeline.end_date else None,
            },
            "top_entities": top_entities,
            "gaps": self.find_gaps(timeline),
        }
