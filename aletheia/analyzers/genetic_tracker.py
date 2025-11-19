"""
Aletheia Truth Verification Engine - Genetic & Genealogical Tracker

Traces human migration patterns, verifies population histories,
and identifies genetic evidence that contradicts official narratives.
"""

from dataclasses import dataclass, field
from typing import Optional

import sys
sys.path.insert(0, '/home/user/Echo')

from aletheia.core.models import (
    GeneticMarker, Evidence, EvidenceType, TimePeriod, GeoLocation
)


@dataclass
class MigrationPath:
    """A traced migration path with genetic evidence."""
    population_name: str
    origin: GeoLocation
    waypoints: list[GeoLocation]
    destination: GeoLocation
    time_period: TimePeriod
    genetic_markers: list[GeneticMarker]
    confidence: float
    narrative_conflicts: list[str]


@dataclass
class PopulationAnalysis:
    """Analysis of a population's genetic history."""
    population_id: str
    haplogroups_present: dict[str, float]  # haplogroup -> frequency
    admixture_events: list[dict]
    migration_history: list[MigrationPath]
    anomalies: list[str]
    narrative_implications: list[str]
    confidence: float


@dataclass
class AncestryResult:
    """Result of ancestry analysis for remains or populations."""
    sample_id: str
    maternal_haplogroup: str
    paternal_haplogroup: Optional[str]
    population_affinities: dict[str, float]
    geographic_origin: GeoLocation
    time_depth_years: int
    conflicts_with_claimed: bool
    analysis: str
    confidence: float


class GeneticTracker:
    """
    Tracks genetic evidence for population history.

    Capabilities:
    - Haplogroup analysis and migration tracking
    - Population admixture detection
    - Identification of genetic evidence that contradicts narratives
    - Ancient DNA analysis interpretation
    """

    def __init__(self):
        # Major Y-DNA haplogroups and their origins
        self.y_haplogroups = {
            "A": {
                "origin": GeoLocation(-2.0, 30.0, "East Africa", "Africa", 500),
                "age_years": 275000,
                "modern_distribution": {"Africa": 0.95, "Arabia": 0.02}
            },
            "E": {
                "origin": GeoLocation(15.0, 30.0, "Northeast Africa", "Africa", 500),
                "age_years": 65000,
                "modern_distribution": {"Africa": 0.70, "Middle East": 0.15, "Europe": 0.10}
            },
            "J": {
                "origin": GeoLocation(33.0, 44.0, "Fertile Crescent", "Middle East", 300),
                "age_years": 45000,
                "modern_distribution": {"Middle East": 0.40, "North Africa": 0.25, "Europe": 0.15}
            },
            "R1b": {
                "origin": GeoLocation(50.0, 80.0, "Central Asia", "Asia", 500),
                "age_years": 22000,
                "modern_distribution": {"Western Europe": 0.60, "Central Asia": 0.15}
            },
            "R1a": {
                "origin": GeoLocation(55.0, 75.0, "Pontic Steppe", "Eurasia", 500),
                "age_years": 22000,
                "modern_distribution": {"Eastern Europe": 0.45, "South Asia": 0.35}
            },
            "Q": {
                "origin": GeoLocation(60.0, 100.0, "Central Asia", "Asia", 500),
                "age_years": 30000,
                "modern_distribution": {"Americas": 0.80, "Siberia": 0.15}
            }
        }

        # Major mtDNA haplogroups
        self.mt_haplogroups = {
            "L0": {
                "origin": GeoLocation(-25.0, 25.0, "Southern Africa", "Africa", 500),
                "age_years": 150000,
                "modern_distribution": {"Africa": 0.90}
            },
            "L3": {
                "origin": GeoLocation(10.0, 35.0, "East Africa", "Africa", 500),
                "age_years": 70000,
                "modern_distribution": {"Africa": 0.50, "Arabia": 0.20}
            },
            "M": {
                "origin": GeoLocation(25.0, 70.0, "South Asia", "Asia", 500),
                "age_years": 60000,
                "modern_distribution": {"South Asia": 0.60, "East Asia": 0.20}
            },
            "N": {
                "origin": GeoLocation(30.0, 50.0, "West Asia", "Middle East", 500),
                "age_years": 60000,
                "modern_distribution": {"Europe": 0.50, "West Asia": 0.30}
            },
            "H": {
                "origin": GeoLocation(40.0, 40.0, "Near East", "Middle East", 500),
                "age_years": 25000,
                "modern_distribution": {"Europe": 0.45, "Middle East": 0.20}
            }
        }

        # Historical population movements
        self.known_migrations = [
            {
                "name": "Out of Africa",
                "time_period": TimePeriod(-70000, -50000),
                "markers": ["L3", "M", "N"],
                "route": "East Africa -> Arabia -> Asia"
            },
            {
                "name": "Bantu Expansion",
                "time_period": TimePeriod(-1000, 500),
                "markers": ["E1b1a"],
                "route": "West Africa -> Central/East/Southern Africa"
            },
            {
                "name": "Indo-European Expansion",
                "time_period": TimePeriod(-4000, -1000),
                "markers": ["R1a", "R1b"],
                "route": "Pontic Steppe -> Europe, South Asia"
            },
            {
                "name": "Peopling of Americas",
                "time_period": TimePeriod(-20000, -10000),
                "markers": ["Q", "C"],
                "route": "Siberia -> Beringia -> Americas"
            },
            {
                "name": "Austronesian Expansion",
                "time_period": TimePeriod(-3000, 1000),
                "markers": ["O", "B4a1a"],
                "route": "Taiwan -> Philippines -> Polynesia"
            }
        ]

    def analyze_ancestry(self, sample_id: str, genetic_data: dict,
                        claimed_origin: Optional[GeoLocation] = None) -> AncestryResult:
        """
        Analyze ancestry from genetic data.

        Args:
            sample_id: Identifier for the sample
            genetic_data: Genetic data including haplogroups
            claimed_origin: The officially claimed origin (to check for conflicts)

        Returns:
            Detailed ancestry analysis
        """
        maternal = genetic_data.get("mtdna_haplogroup", "")
        paternal = genetic_data.get("y_haplogroup", "")

        # Determine geographic origin
        origin = self._determine_origin(maternal, paternal)

        # Calculate population affinities
        affinities = self._calculate_affinities(maternal, paternal)

        # Check for conflicts with claimed origin
        conflict = False
        analysis = ""

        if claimed_origin and origin:
            distance = claimed_origin.distance_to(origin)
            if distance > 1000:  # More than 1000km discrepancy
                conflict = True
                analysis = (
                    f"DISCREPANCY: Genetic origin ({origin.region}) differs significantly "
                    f"from claimed origin ({claimed_origin.region}). Distance: {distance:.0f}km. "
                    f"This suggests the official narrative may be incorrect."
                )
            else:
                analysis = "Genetic evidence consistent with claimed origin."
        elif origin:
            analysis = f"Genetic origin determined as {origin.region}."

        return AncestryResult(
            sample_id=sample_id,
            maternal_haplogroup=maternal,
            paternal_haplogroup=paternal,
            population_affinities=affinities,
            geographic_origin=origin if origin else GeoLocation(0, 0, "Unknown", "Unknown", 0),
            time_depth_years=self._estimate_time_depth(maternal, paternal),
            conflicts_with_claimed=conflict,
            analysis=analysis,
            confidence=0.85 if maternal and paternal else 0.6
        )

    def _determine_origin(self, maternal: str, paternal: str) -> Optional[GeoLocation]:
        """Determine geographic origin from haplogroups."""
        origins = []

        # Get maternal origin
        for hg_name, hg_data in self.mt_haplogroups.items():
            if maternal.startswith(hg_name):
                origins.append(hg_data["origin"])
                break

        # Get paternal origin
        for hg_name, hg_data in self.y_haplogroups.items():
            if paternal.startswith(hg_name):
                origins.append(hg_data["origin"])
                break

        # Return first match or None
        return origins[0] if origins else None

    def _calculate_affinities(self, maternal: str, paternal: str) -> dict[str, float]:
        """Calculate population affinities based on haplogroups."""
        affinities = {}

        # Aggregate distributions from both lineages
        for hg_name, hg_data in self.mt_haplogroups.items():
            if maternal.startswith(hg_name):
                for region, freq in hg_data["modern_distribution"].items():
                    affinities[region] = affinities.get(region, 0) + freq * 0.5

        for hg_name, hg_data in self.y_haplogroups.items():
            if paternal.startswith(hg_name):
                for region, freq in hg_data["modern_distribution"].items():
                    affinities[region] = affinities.get(region, 0) + freq * 0.5

        return affinities

    def _estimate_time_depth(self, maternal: str, paternal: str) -> int:
        """Estimate time depth to most recent common ancestor."""
        ages = []

        for hg_name, hg_data in self.mt_haplogroups.items():
            if maternal.startswith(hg_name):
                ages.append(hg_data["age_years"])
                break

        for hg_name, hg_data in self.y_haplogroups.items():
            if paternal.startswith(hg_name):
                ages.append(hg_data["age_years"])
                break

        return min(ages) if ages else 0

    def trace_migration(self, population: str, genetic_markers: list[str]) -> MigrationPath:
        """
        Trace a population's migration history.

        Args:
            population: Population name or identifier
            genetic_markers: List of haplogroups present

        Returns:
            Reconstructed migration path
        """
        waypoints = []
        origin = None
        destination = None
        time_period = None
        narrative_conflicts = []

        # Find matching known migrations
        for migration in self.known_migrations:
            if any(marker in migration["markers"] for marker in genetic_markers):
                # Extract route waypoints
                route_parts = migration["route"].split(" -> ")
                if len(route_parts) >= 2:
                    # Create waypoints (simplified - would use actual coordinates)
                    for i, part in enumerate(route_parts):
                        loc = GeoLocation(0, 0, part, "Route", 100)
                        if i == 0:
                            origin = loc
                        elif i == len(route_parts) - 1:
                            destination = loc
                        else:
                            waypoints.append(loc)

                time_period = migration["time_period"]

        # Check for narrative conflicts
        # Example: finding unexpected genetic admixture that contradicts isolation claims
        if "R1b" in genetic_markers and "E" in genetic_markers:
            narrative_conflicts.append(
                "Presence of both R1b and E haplogroups suggests admixture "
                "that contradicts narratives of population isolation"
            )

        return MigrationPath(
            population_name=population,
            origin=origin if origin else GeoLocation(0, 0, "Unknown", "Unknown", 0),
            waypoints=waypoints,
            destination=destination if destination else GeoLocation(0, 0, "Unknown", "Unknown", 0),
            time_period=time_period if time_period else TimePeriod(0, 0),
            genetic_markers=[
                GeneticMarker(haplogroup=m) for m in genetic_markers
            ],
            confidence=0.7 if origin else 0.3,
            narrative_conflicts=narrative_conflicts
        )

    def detect_admixture_events(self, population_data: dict) -> list[dict]:
        """
        Detect historical admixture events from genetic data.

        These can reveal hidden historical contacts between populations
        that official histories deny or minimize.
        """
        events = []

        haplogroups = population_data.get("haplogroups", {})

        # Look for unexpected haplogroup combinations
        african_markers = ["E", "L"]
        european_markers = ["R1b", "R1a", "I", "J"]
        asian_markers = ["O", "N", "C"]
        american_markers = ["Q", "C"]

        found_african = any(hg.startswith(tuple(african_markers))
                          for hg in haplogroups.keys())
        found_european = any(hg.startswith(tuple(european_markers))
                           for hg in haplogroups.keys())
        found_asian = any(hg.startswith(tuple(asian_markers))
                        for hg in haplogroups.keys())

        # Detect significant admixture
        if found_african and found_european:
            events.append({
                "type": "African-European admixture",
                "markers": [hg for hg in haplogroups.keys()
                           if hg.startswith(tuple(african_markers + european_markers))],
                "implication": "Historical contact between African and European populations",
                "potential_period": "Could indicate ancient trade routes, migrations, or colonial-era mixing"
            })

        if found_asian and found_european:
            events.append({
                "type": "Asian-European admixture",
                "markers": [hg for hg in haplogroups.keys()
                           if hg.startswith(tuple(asian_markers + european_markers))],
                "implication": "Historical contact along Silk Road or earlier migrations",
                "potential_period": "Indo-European expansion or historical trade networks"
            })

        return events

    def analyze_ancient_dna(self, sample_id: str, adna_data: dict) -> dict:
        """
        Analyze ancient DNA to reconstruct historical populations.

        Can reveal true ancestral populations that differ from
        modern claims about ethnic or national continuity.
        """
        result = {
            "sample_id": sample_id,
            "sample_age_years": adna_data.get("age", 0),
            "population_assignment": "",
            "genetic_affinities": {},
            "surprising_findings": [],
            "narrative_implications": [],
            "confidence": 0.0
        }

        # Analyze haplogroups
        ancestry = self.analyze_ancestry(
            sample_id,
            adna_data,
            adna_data.get("claimed_origin")
        )

        result["genetic_affinities"] = ancestry.population_affinities

        # Look for surprises
        if ancestry.conflicts_with_claimed:
            result["surprising_findings"].append(ancestry.analysis)
            result["narrative_implications"].append(
                "This finding suggests the official historical narrative "
                "about this population or individual requires revision."
            )

        # Check for unexpectedly diverse ancestry in supposedly homogeneous samples
        if len(ancestry.population_affinities) > 2:
            regions = list(ancestry.population_affinities.keys())
            result["surprising_findings"].append(
                f"Sample shows affinities to multiple regions: {', '.join(regions)}. "
                f"This suggests more cosmopolitan origins than typically assumed."
            )

        result["confidence"] = ancestry.confidence

        return result

    def generate_genetic_evidence(self, analysis_results: list) -> list[Evidence]:
        """
        Generate evidence items from genetic analysis.
        """
        evidence_items = []

        for result in analysis_results:
            if isinstance(result, AncestryResult):
                evidence = Evidence(
                    evidence_type=EvidenceType.GENETIC,
                    description=f"Genetic ancestry analysis for {result.sample_id}",
                    source="Ancient DNA analysis",
                    content=result.analysis,
                    genetic_data=GeneticMarker(
                        haplogroup=f"{result.maternal_haplogroup}/{result.paternal_haplogroup}"
                    ),
                    confidence_score=result.confidence
                )

                if result.conflicts_with_claimed:
                    evidence.potential_biases = [
                        "Result conflicts with claimed origin - possible narrative falsification"
                    ]

                evidence_items.append(evidence)

        return evidence_items
