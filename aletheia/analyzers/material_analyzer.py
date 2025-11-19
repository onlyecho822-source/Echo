"""
Aletheia Truth Verification Engine - Material & Forensic Analyzer

Analyzes physical evidence: material composition, dating, origin determination,
and authentication of artifacts, paintings, and documents.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import sys
sys.path.insert(0, '/home/user/Echo')

from aletheia.core.models import (
    MaterialComposition, Evidence, EvidenceType, TimePeriod, GeoLocation,
    Artifact
)


@dataclass
class MaterialAnalysisResult:
    """Result of material composition analysis."""
    artifact_id: str
    materials_identified: list[str]
    composition: MaterialComposition
    origin_assessment: dict
    age_assessment: dict
    authenticity_assessment: dict
    anomalies: list[str]
    confidence: float


@dataclass
class DateAnalysisResult:
    """Result of dating analysis."""
    artifact_id: str
    method: str
    estimated_date: TimePeriod
    margin_of_error_years: int
    conflicts_with_claimed_date: bool
    analysis_notes: str
    confidence: float


@dataclass
class PigmentAnalysis:
    """Analysis of pigments in artwork."""
    pigment_name: str
    chemical_composition: str
    origin_region: str
    availability_period: TimePeriod
    synthetic: bool
    notes: str


class MaterialForensicAnalyzer:
    """
    Analyzes physical and material evidence.

    Capabilities:
    - Material composition analysis
    - Geographic origin determination via isotope analysis
    - Dating verification
    - Pigment and material authenticity checking
    - Detection of anachronistic materials
    """

    def __init__(self):
        # Material origin databases
        # Maps materials to their known geographic sources and time periods
        self.material_sources = {
            "lapis_lazuli": {
                "primary_sources": [
                    GeoLocation(36.5, 70.5, "Badakhshan", "Afghanistan", 50),
                    GeoLocation(38.0, 67.0, "Tajikistan", "Central Asia", 100)
                ],
                "availability": TimePeriod(-7000, 2025),
                "notes": "Primary ancient source was Afghanistan"
            },
            "obsidian": {
                "primary_sources": [
                    GeoLocation(38.5, 43.0, "Anatolia", "Turkey", 100),
                    GeoLocation(19.5, -99.0, "Mexico", "Mesoamerica", 200),
                    GeoLocation(-1.0, 37.0, "Kenya", "East Africa", 100)
                ],
                "availability": TimePeriod(-10000, 2025),
                "notes": "Isotope analysis can determine specific source"
            },
            "gold": {
                "primary_sources": [
                    GeoLocation(25.0, 33.0, "Nubia", "Sudan/Egypt", 200),
                    GeoLocation(12.0, -8.0, "West Africa", "Mali/Ghana", 300),
                    GeoLocation(-13.5, -72.0, "Andes", "Peru", 200)
                ],
                "availability": TimePeriod(-5000, 2025),
                "notes": "Trace element analysis reveals specific sources"
            },
            "tyrian_purple": {
                "primary_sources": [
                    GeoLocation(33.3, 35.2, "Tyre", "Lebanon", 50)
                ],
                "availability": TimePeriod(-1500, 1453),
                "notes": "Extracted from murex snails, extremely valuable"
            },
            "cochineal": {
                "primary_sources": [
                    GeoLocation(19.0, -99.0, "Mexico", "Mesoamerica", 200),
                    GeoLocation(-16.0, -68.0, "Andes", "Peru/Bolivia", 200)
                ],
                "availability": TimePeriod(-2000, 2025),
                "notes": "New World origin - presence in pre-Columbian Europe is anomalous"
            }
        }

        # Historical pigment database for artwork authentication
        self.pigment_database = {
            "ultramarine_natural": PigmentAnalysis(
                pigment_name="Natural Ultramarine",
                chemical_composition="Na8[Al6Si6O24]Sn",
                origin_region="Afghanistan",
                availability_period=TimePeriod(-3000, 2025),
                synthetic=False,
                notes="Made from lapis lazuli, very expensive historically"
            ),
            "ultramarine_synthetic": PigmentAnalysis(
                pigment_name="Synthetic Ultramarine",
                chemical_composition="Na8[Al6Si6O24]Sn",
                origin_region="Europe",
                availability_period=TimePeriod(1828, 2025),
                synthetic=True,
                notes="Invented 1828 - presence before this date proves forgery"
            ),
            "prussian_blue": PigmentAnalysis(
                pigment_name="Prussian Blue",
                chemical_composition="Fe4[Fe(CN)6]3",
                origin_region="Germany",
                availability_period=TimePeriod(1704, 2025),
                synthetic=True,
                notes="First synthetic blue - presence before 1704 proves forgery"
            ),
            "titanium_white": PigmentAnalysis(
                pigment_name="Titanium White",
                chemical_composition="TiO2",
                origin_region="Global",
                availability_period=TimePeriod(1921, 2025),
                synthetic=True,
                notes="Not available before 1921"
            ),
            "egyptian_blue": PigmentAnalysis(
                pigment_name="Egyptian Blue",
                chemical_composition="CaCuSi4O10",
                origin_region="Egypt/Mesopotamia",
                availability_period=TimePeriod(-3100, 800),
                synthetic=False,
                notes="One of first synthetic pigments, fell out of use"
            ),
            "mayan_blue": PigmentAnalysis(
                pigment_name="Maya Blue",
                chemical_composition="Indigo + Palygorskite",
                origin_region="Mesoamerica",
                availability_period=TimePeriod(300, 1520),
                synthetic=False,
                notes="Unique to Maya civilization"
            )
        }

        # Dating method capabilities
        self.dating_methods = {
            "radiocarbon": {
                "material_types": ["organic", "wood", "bone", "textile", "paper"],
                "range_years": (-50000, 0),
                "precision_years": 50
            },
            "thermoluminescence": {
                "material_types": ["ceramic", "burnt_stone", "glass"],
                "range_years": (-500000, 0),
                "precision_years": 100
            },
            "dendrochronology": {
                "material_types": ["wood"],
                "range_years": (-10000, 0),
                "precision_years": 1
            },
            "uranium_series": {
                "material_types": ["calcium_carbite", "bone", "coral"],
                "range_years": (-500000, 0),
                "precision_years": 1000
            }
        }

    def analyze_material_composition(self, artifact: Artifact,
                                    spectral_data: dict) -> MaterialAnalysisResult:
        """
        Analyze the material composition of an artifact.

        Args:
            artifact: The artifact to analyze
            spectral_data: Data from spectroscopic analysis (XRF, Raman, etc.)

        Returns:
            Comprehensive material analysis result
        """
        materials_found = []
        anomalies = []
        origin_candidates = []

        # Process spectral data to identify materials
        for material_name, concentration in spectral_data.get("elements", {}).items():
            materials_found.append(f"{material_name}: {concentration}%")

            # Check against known sources
            if material_name.lower() in self.material_sources:
                source_info = self.material_sources[material_name.lower()]
                origin_candidates.extend(source_info["primary_sources"])

        # Create composition object
        composition = MaterialComposition(
            primary_material=spectral_data.get("primary_material", "unknown"),
            secondary_materials=spectral_data.get("secondary_materials", []),
            trace_elements=spectral_data.get("trace_elements", {}),
            isotope_ratios=spectral_data.get("isotope_ratios", {}),
            analysis_method=spectral_data.get("method", "XRF"),
            analysis_date=datetime.now()
        )

        # Determine most likely origin
        if origin_candidates:
            # Would use isotope matching in production
            composition.probable_origin = origin_candidates[0]
            composition.origin_confidence = 0.7

        # Check for anachronisms
        anomalies = self._check_material_anachronisms(
            materials_found, artifact.claimed_date
        )

        # Assess authenticity
        authenticity = self._assess_authenticity(composition, artifact)

        return MaterialAnalysisResult(
            artifact_id=artifact.id,
            materials_identified=materials_found,
            composition=composition,
            origin_assessment={
                "probable_origin": composition.probable_origin,
                "confidence": composition.origin_confidence,
                "alternative_origins": origin_candidates[1:3] if len(origin_candidates) > 1 else []
            },
            age_assessment={
                "consistent_with_claimed": len(anomalies) == 0,
                "notes": "Material composition is period-appropriate" if not anomalies else "Anachronisms detected"
            },
            authenticity_assessment=authenticity,
            anomalies=anomalies,
            confidence=0.8 if not anomalies else 0.4
        )

    def _check_material_anachronisms(self, materials: list[str],
                                    claimed_date: Optional[TimePeriod]) -> list[str]:
        """Check if materials are anachronistic to claimed date."""
        anomalies = []

        if not claimed_date:
            return anomalies

        # Check synthetic pigments against dates
        for pigment_name, pigment_data in self.pigment_database.items():
            for material in materials:
                if pigment_name.replace("_", " ").lower() in material.lower():
                    if pigment_data.availability_period.start_year > claimed_date.end_year:
                        anomalies.append(
                            f"ANACHRONISM: {pigment_data.pigment_name} not available until "
                            f"{pigment_data.availability_period.start_year}, but artifact "
                            f"claims date of {claimed_date.end_year} or earlier"
                        )

        return anomalies

    def _assess_authenticity(self, composition: MaterialComposition,
                            artifact: Artifact) -> dict:
        """Assess overall authenticity based on material analysis."""
        assessment = {
            "authentic": True,
            "confidence": 0.5,
            "issues": [],
            "supporting_factors": []
        }

        # Check origin consistency
        if artifact.claimed_origin and composition.probable_origin:
            distance = artifact.claimed_origin.distance_to(composition.probable_origin)
            if distance > 500:  # More than 500km difference
                assessment["issues"].append(
                    f"Material origin ({composition.probable_origin.name}) differs from "
                    f"claimed origin ({artifact.claimed_origin.name}) by {distance:.0f}km"
                )
                assessment["authentic"] = False
                assessment["confidence"] = 0.3
            else:
                assessment["supporting_factors"].append("Material origin consistent with claimed origin")
                assessment["confidence"] = 0.8

        return assessment

    def analyze_pigments(self, artwork: Artifact,
                        pigment_data: list[dict]) -> dict:
        """
        Analyze pigments in an artwork for authentication.

        Args:
            artwork: The artwork artifact
            pigment_data: List of identified pigments with locations

        Returns:
            Pigment analysis with authenticity implications
        """
        result = {
            "artwork_id": artwork.id,
            "pigments_identified": [],
            "anachronisms": [],
            "origin_implications": [],
            "authenticity_verdict": "undetermined",
            "confidence": 0.0
        }

        for pigment_info in pigment_data:
            pigment_name = pigment_info.get("name", "").lower().replace(" ", "_")

            if pigment_name in self.pigment_database:
                pigment = self.pigment_database[pigment_name]
                result["pigments_identified"].append({
                    "name": pigment.pigment_name,
                    "location_in_artwork": pigment_info.get("location", "unknown"),
                    "period_appropriate": self._is_period_appropriate(
                        pigment.availability_period, artwork.claimed_date
                    )
                })

                # Check for anachronisms
                if artwork.claimed_date:
                    if pigment.availability_period.start_year > artwork.claimed_date.end_year:
                        result["anachronisms"].append({
                            "pigment": pigment.pigment_name,
                            "issue": f"Not available until {pigment.availability_period.start_year}",
                            "claimed_date": artwork.claimed_date.end_year,
                            "verdict": "FORGERY INDICATOR"
                        })

                # Origin implications
                if pigment.origin_region not in ["Europe", "Global"]:
                    result["origin_implications"].append({
                        "pigment": pigment.pigment_name,
                        "origin": pigment.origin_region,
                        "implication": f"Indicates trade contact with {pigment.origin_region}"
                    })

        # Determine verdict
        if result["anachronisms"]:
            result["authenticity_verdict"] = "LIKELY FORGERY OR LATER ALTERATION"
            result["confidence"] = 0.85
        elif result["pigments_identified"]:
            result["authenticity_verdict"] = "NO ANACHRONISMS DETECTED"
            result["confidence"] = 0.7
        else:
            result["confidence"] = 0.3

        return result

    def _is_period_appropriate(self, availability: TimePeriod,
                               claimed: Optional[TimePeriod]) -> bool:
        """Check if a material's availability overlaps with claimed date."""
        if not claimed:
            return True
        return availability.overlaps(claimed)

    def date_artifact(self, artifact: Artifact, material_type: str,
                     raw_data: dict) -> DateAnalysisResult:
        """
        Date an artifact using appropriate method.

        Args:
            artifact: The artifact to date
            material_type: Type of material (wood, ceramic, etc.)
            raw_data: Raw dating data (C14 measurements, etc.)

        Returns:
            Dating analysis result
        """
        # Select appropriate dating method
        selected_method = None
        for method_name, method_info in self.dating_methods.items():
            if material_type in method_info["material_types"]:
                selected_method = method_name
                break

        if not selected_method:
            return DateAnalysisResult(
                artifact_id=artifact.id,
                method="none",
                estimated_date=TimePeriod(0, 0),
                margin_of_error_years=0,
                conflicts_with_claimed_date=False,
                analysis_notes="No appropriate dating method for this material type",
                confidence=0.0
            )

        method_info = self.dating_methods[selected_method]

        # Process raw data to get date estimate
        # In production, this would involve proper calculations
        estimated_year = raw_data.get("estimated_year", 0)
        margin = method_info["precision_years"]

        estimated_period = TimePeriod(
            estimated_year - margin,
            estimated_year + margin
        )

        # Check conflict with claimed date
        conflict = False
        if artifact.claimed_date:
            conflict = not estimated_period.overlaps(artifact.claimed_date)

        return DateAnalysisResult(
            artifact_id=artifact.id,
            method=selected_method,
            estimated_date=estimated_period,
            margin_of_error_years=margin,
            conflicts_with_claimed_date=conflict,
            analysis_notes=f"Dated using {selected_method} method",
            confidence=0.8 if not conflict else 0.9
        )

    def trace_material_origin(self, composition: MaterialComposition) -> dict:
        """
        Trace the geographic origin of materials using isotope analysis.

        This can reveal the true source of materials that contradict
        official narratives about artifact origins.
        """
        result = {
            "primary_material": composition.primary_material,
            "isotope_matches": [],
            "probable_origin": None,
            "alternative_origins": [],
            "trade_route_implications": [],
            "confidence": 0.0
        }

        # Check isotope ratios against known sources
        if composition.isotope_ratios:
            # Simplified matching - production would use proper isotope databases
            if "pb206_204" in composition.isotope_ratios:
                # Lead isotope matching for metal artifacts
                result["isotope_matches"].append({
                    "element": "Lead",
                    "ratio": composition.isotope_ratios["pb206_204"],
                    "analysis": "Lead isotope ratio analysis performed"
                })

            if "sr87_86" in composition.isotope_ratios:
                # Strontium for biological origin
                result["isotope_matches"].append({
                    "element": "Strontium",
                    "ratio": composition.isotope_ratios["sr87_86"],
                    "analysis": "Strontium isotope ratio indicates geographic origin of organic material"
                })

        # Set origin from composition if available
        if composition.probable_origin:
            result["probable_origin"] = {
                "location": composition.probable_origin.name,
                "region": composition.probable_origin.region,
                "confidence": composition.origin_confidence
            }
            result["confidence"] = composition.origin_confidence

        return result

    def generate_forensic_evidence(self, artifact: Artifact,
                                  analysis_results: list) -> list[Evidence]:
        """
        Generate evidence items from forensic analysis.
        """
        evidence_items = []

        for result in analysis_results:
            if isinstance(result, MaterialAnalysisResult):
                evidence = Evidence(
                    evidence_type=EvidenceType.MATERIAL,
                    description=f"Material analysis of {artifact.name}",
                    source="Forensic material analysis",
                    content=str(result.materials_identified),
                    material_data=result.composition,
                    confidence_score=result.confidence
                )

                if result.anomalies:
                    evidence.potential_biases = result.anomalies

                evidence_items.append(evidence)

            elif isinstance(result, DateAnalysisResult):
                evidence = Evidence(
                    evidence_type=EvidenceType.ARCHAEOLOGICAL,
                    description=f"Dating analysis of {artifact.name}",
                    source=f"{result.method} dating",
                    time_period=result.estimated_date,
                    confidence_score=result.confidence
                )

                if result.conflicts_with_claimed_date:
                    evidence.potential_biases = [
                        f"Dating conflicts with claimed date: {result.analysis_notes}"
                    ]

                evidence_items.append(evidence)

        return evidence_items
