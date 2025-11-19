"""
Aletheia Truth Verification Engine - Symbolic & Linguistic Decoder

Analyzes ancient texts, symbols, and iconography across cultures and time periods.
Identifies patterns, tracks symbol migration, and detects meaning inversions.
"""

from dataclasses import dataclass, field
from typing import Optional
import re

import sys
sys.path.insert(0, '/home/user/Echo')

from aletheia.core.models import (
    Symbol, Evidence, EvidenceType, TimePeriod, GeoLocation,
    Artifact, ConfidenceLevel
)


@dataclass
class SymbolMatch:
    """Result of matching symbols across cultures."""
    symbol_a: Symbol
    symbol_b: Symbol
    similarity_score: float
    shared_meanings: list[str]
    divergent_meanings: list[str]
    potential_connection: str
    confidence: float


@dataclass
class LinguisticPattern:
    """A linguistic pattern found across texts."""
    pattern: str
    occurrences: list[dict]  # {text_id, location, context}
    cultures: list[str]
    time_range: Optional[TimePeriod] = None
    semantic_field: str = ""
    significance: str = ""


@dataclass
class TextAnalysis:
    """Analysis result for a text."""
    text_id: str
    language: str
    script: str
    symbols_identified: list[Symbol]
    semantic_themes: list[str]
    astronomical_references: list[str]
    mathematical_concepts: list[str]
    cosmological_concepts: list[str]
    potential_mistranslations: list[dict]
    suppressed_meanings: list[str]
    confidence: float


class SymbolicLinguisticDecoder:
    """
    Decodes and analyzes symbols and languages across cultures.

    Capabilities:
    - Cross-temporal NLP for ancient languages
    - Symbol pattern recognition and tracking
    - Semantic analysis beyond literal translation
    - Detection of meaning inversion by conquering cultures
    """

    def __init__(self):
        # Symbol database - would be loaded from persistent storage
        self.symbol_database: dict[str, Symbol] = {}
        self.linguistic_patterns: list[LinguisticPattern] = []

        # Known language families and scripts
        self.language_families = {
            "indo_european": ["sanskrit", "greek", "latin", "persian"],
            "afroasiatic": ["egyptian", "coptic", "aramaic", "hebrew", "arabic"],
            "sino_tibetan": ["chinese", "tibetan"],
            "mesoamerican": ["mayan", "nahuatl", "zapotec"],
            "niger_congo": ["dogon", "yoruba", "akan"],
            "austronesian": ["polynesian", "malay"],
            "isolates": ["sumerian", "elamite", "basque"]
        }

        # Script systems
        self.scripts = {
            "cuneiform": {"origin": "sumer", "period": TimePeriod(-3400, 100)},
            "hieroglyphic": {"origin": "egypt", "period": TimePeriod(-3200, 400)},
            "hieratic": {"origin": "egypt", "period": TimePeriod(-2600, 300)},
            "demotic": {"origin": "egypt", "period": TimePeriod(-650, 450)},
            "linear_a": {"origin": "minoan", "period": TimePeriod(-1800, -1450)},
            "linear_b": {"origin": "mycenaean", "period": TimePeriod(-1450, -1200)},
            "mayan_glyphs": {"origin": "maya", "period": TimePeriod(-300, 1500)},
            "rongorongo": {"origin": "rapa_nui", "period": TimePeriod(1200, 1860)}
        }

        # Universal symbolic archetypes found across cultures
        self.universal_archetypes = {
            "serpent": {
                "cultures": ["egyptian", "sumerian", "mayan", "hindu", "greek", "norse", "chinese"],
                "meanings": ["wisdom", "eternity", "transformation", "cosmic force", "knowledge"],
                "astronomical": "constellation patterns, ecliptic"
            },
            "world_tree": {
                "cultures": ["norse", "mayan", "siberian", "mesopotamian", "buddhist"],
                "meanings": ["axis_mundi", "connection_realms", "cosmic_structure"],
                "astronomical": "milky way, polar axis"
            },
            "eye": {
                "cultures": ["egyptian", "sumerian", "hindu", "celtic", "masonic"],
                "meanings": ["divine_sight", "protection", "consciousness", "sun"],
                "astronomical": "sun, specific stars"
            },
            "spiral": {
                "cultures": ["celtic", "polynesian", "pueblo", "greek", "chinese"],
                "meanings": ["evolution", "cycles", "cosmic_force", "energy"],
                "astronomical": "galaxy form, golden ratio"
            },
            "cross": {
                "cultures": ["egyptian", "celtic", "christian", "hindu", "mayan"],
                "meanings": ["four_directions", "intersection", "balance", "cosmic_order"],
                "astronomical": "solstices, equinoxes, cardinal points"
            }
        }

    def add_symbol(self, symbol: Symbol) -> None:
        """Add a symbol to the database."""
        self.symbol_database[symbol.id] = symbol

    def analyze_text(self, text: str, language: str, context: dict) -> TextAnalysis:
        """
        Perform deep analysis of a text.

        Args:
            text: The text content
            language: Source language
            context: Additional context (era, culture, document type)

        Returns:
            Comprehensive text analysis
        """
        analysis = TextAnalysis(
            text_id=context.get("text_id", "unknown"),
            language=language,
            script=context.get("script", "unknown"),
            symbols_identified=[],
            semantic_themes=[],
            astronomical_references=[],
            mathematical_concepts=[],
            cosmological_concepts=[],
            potential_mistranslations=[],
            suppressed_meanings=[],
            confidence=0.0
        )

        # Identify symbols in text
        analysis.symbols_identified = self._identify_symbols(text, language)

        # Extract semantic themes
        analysis.semantic_themes = self._extract_themes(text, language, context)

        # Find astronomical references
        analysis.astronomical_references = self._find_astronomical_refs(text, language)

        # Identify mathematical concepts
        analysis.mathematical_concepts = self._find_mathematical_concepts(text)

        # Detect cosmological concepts
        analysis.cosmological_concepts = self._find_cosmological_concepts(text, language)

        # Check for potential mistranslations
        analysis.potential_mistranslations = self._detect_mistranslations(
            text, language, context
        )

        # Identify suppressed meanings
        analysis.suppressed_meanings = self._find_suppressed_meanings(
            text, language, context
        )

        # Calculate confidence
        analysis.confidence = self._calculate_analysis_confidence(analysis)

        return analysis

    def _identify_symbols(self, text: str, language: str) -> list[Symbol]:
        """Identify symbolic elements in text."""
        found_symbols = []

        # Check against known archetypes
        for archetype_name, archetype_data in self.universal_archetypes.items():
            # Simple keyword matching - in production would use NLP
            keywords = [archetype_name] + archetype_data.get("meanings", [])
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    symbol = Symbol(
                        name=archetype_name,
                        description=f"Universal archetype: {archetype_name}",
                        cultures=archetype_data["cultures"],
                        astronomical_correlation=archetype_data.get("astronomical")
                    )
                    for culture in archetype_data["cultures"]:
                        symbol.meanings[culture] = ", ".join(archetype_data["meanings"])
                    found_symbols.append(symbol)
                    break

        return found_symbols

    def _extract_themes(self, text: str, language: str, context: dict) -> list[str]:
        """Extract major semantic themes from text."""
        themes = []

        # Theme keywords - would be much more sophisticated in production
        theme_indicators = {
            "creation": ["beginning", "first", "origin", "birth", "primordial"],
            "destruction": ["end", "death", "dissolution", "chaos"],
            "transformation": ["change", "become", "transmute", "evolve"],
            "cosmic_order": ["law", "truth", "justice", "balance", "maat", "dharma"],
            "divine_knowledge": ["wisdom", "secret", "hidden", "mystery", "revelation"],
            "afterlife": ["death", "judgment", "soul", "rebirth", "underworld"],
            "astronomical": ["star", "sun", "moon", "planet", "heaven", "sky"]
        }

        text_lower = text.lower()
        for theme, indicators in theme_indicators.items():
            if any(ind in text_lower for ind in indicators):
                themes.append(theme)

        return themes

    def _find_astronomical_refs(self, text: str, language: str) -> list[str]:
        """Find astronomical references in text."""
        refs = []

        astronomical_terms = [
            "sirius", "orion", "pleiades", "pole star", "north star",
            "sun", "moon", "venus", "mars", "jupiter", "saturn",
            "eclipse", "equinox", "solstice", "constellation",
            "milky way", "galaxy", "star"
        ]

        text_lower = text.lower()
        for term in astronomical_terms:
            if term in text_lower:
                refs.append(term)

        return refs

    def _find_mathematical_concepts(self, text: str) -> list[str]:
        """Identify mathematical concepts in text."""
        concepts = []

        math_indicators = {
            "geometry": ["circle", "square", "triangle", "proportion", "angle"],
            "numbers": ["sacred", "seven", "twelve", "forty", "108", "432"],
            "ratios": ["golden", "phi", "proportion", "ratio"],
            "astronomy_math": ["cycle", "precession", "period", "calculation"]
        }

        text_lower = text.lower()
        for concept, indicators in math_indicators.items():
            if any(ind in text_lower for ind in indicators):
                concepts.append(concept)

        return concepts

    def _find_cosmological_concepts(self, text: str, language: str) -> list[str]:
        """Detect cosmological/metaphysical concepts."""
        concepts = []

        cosmo_indicators = {
            "multiple_realms": ["realm", "world", "dimension", "plane", "loka"],
            "illusion_reality": ["maya", "illusion", "dream", "veil", "shadow"],
            "consciousness": ["mind", "awareness", "consciousness", "spirit", "soul"],
            "cycles": ["yuga", "age", "cycle", "return", "eternal"],
            "unity": ["one", "all", "unity", "brahman", "source"]
        }

        text_lower = text.lower()
        for concept, indicators in cosmo_indicators.items():
            if any(ind in text_lower for ind in indicators):
                concepts.append(concept)

        return concepts

    def _detect_mistranslations(self, text: str, language: str,
                                context: dict) -> list[dict]:
        """
        Detect potential mistranslations or misinterpretations.

        This is crucial for identifying where meaning was changed
        by translators with cultural biases.
        """
        mistranslations = []

        # Known problematic translations
        known_issues = {
            "god": {
                "original_nuance": "Often translated from words meaning 'powerful one' or 'shining one'",
                "lost_meaning": "Not necessarily supernatural deity"
            },
            "heaven": {
                "original_nuance": "Often literally 'sky' or 'space above'",
                "lost_meaning": "Physical celestial realm, not metaphysical afterlife"
            },
            "angel": {
                "original_nuance": "Greek 'angelos' means messenger",
                "lost_meaning": "Could refer to human messengers or natural phenomena"
            },
            "demon": {
                "original_nuance": "Greek 'daimon' meant spirit or divine power",
                "lost_meaning": "Originally neutral or positive, demonized later"
            }
        }

        text_lower = text.lower()
        for term, issue in known_issues.items():
            if term in text_lower:
                mistranslations.append({
                    "term": term,
                    "issue": issue["original_nuance"],
                    "lost_meaning": issue["lost_meaning"],
                    "recommendation": f"Re-examine '{term}' in original language context"
                })

        return mistranslations

    def _find_suppressed_meanings(self, text: str, language: str,
                                  context: dict) -> list[str]:
        """
        Identify meanings that may have been suppressed.

        Look for concepts that would have been controversial
        to the institutions that preserved/translated the text.
        """
        suppressed = []

        # Concepts often suppressed by religious/political authorities
        controversial_concepts = {
            "direct_divine_access": ["within", "inner light", "self-realization"],
            "reincarnation": ["return", "rebirth", "cycle of lives"],
            "goddess_worship": ["divine feminine", "mother", "queen of heaven"],
            "astronomical_religion": ["star worship", "celestial", "as above"],
            "entheogens": ["sacred plant", "vision", "divine drink", "soma"],
            "advanced_technology": ["flying", "weapon", "vimana", "thunderbolt"]
        }

        text_lower = text.lower()
        for concept, indicators in controversial_concepts.items():
            if any(ind in text_lower for ind in indicators):
                suppressed.append(f"Possible suppressed concept: {concept}")

        return suppressed

    def _calculate_analysis_confidence(self, analysis: TextAnalysis) -> float:
        """Calculate overall confidence in the analysis."""
        factors = []

        # More identified elements = higher confidence
        if analysis.symbols_identified:
            factors.append(min(len(analysis.symbols_identified) * 0.1, 0.3))

        if analysis.semantic_themes:
            factors.append(min(len(analysis.semantic_themes) * 0.1, 0.3))

        if analysis.astronomical_references:
            factors.append(0.2)  # Astronomical refs are strong evidence

        if analysis.cosmological_concepts:
            factors.append(0.2)

        return min(sum(factors), 1.0)

    def cross_reference_symbols(self, symbol_a: Symbol,
                                symbol_b: Symbol) -> SymbolMatch:
        """
        Cross-reference two symbols to find connections.

        Used to track symbol migration and meaning evolution across cultures.
        """
        # Calculate visual/structural similarity (simplified)
        visual_sim = 0.5 if symbol_a.visual_pattern and symbol_b.visual_pattern else 0.0

        # Calculate semantic similarity
        semantic_sim = symbol_a.shared_meaning_with(symbol_b)

        # Find shared meanings
        shared = []
        divergent = []

        for culture in set(symbol_a.meanings.keys()) & set(symbol_b.meanings.keys()):
            meaning_a = symbol_a.meanings[culture].lower()
            meaning_b = symbol_b.meanings[culture].lower()

            if meaning_a == meaning_b:
                shared.append(f"{culture}: {meaning_a}")
            else:
                divergent.append(f"{culture}: A='{meaning_a}', B='{meaning_b}'")

        # Determine potential connection
        similarity = (visual_sim + semantic_sim) / 2

        if similarity > 0.7:
            connection = "Strong connection - likely common origin or direct transmission"
        elif similarity > 0.4:
            connection = "Moderate connection - possible cultural exchange or parallel development"
        else:
            connection = "Weak connection - may be coincidental or very distant relationship"

        return SymbolMatch(
            symbol_a=symbol_a,
            symbol_b=symbol_b,
            similarity_score=similarity,
            shared_meanings=shared,
            divergent_meanings=divergent,
            potential_connection=connection,
            confidence=similarity
        )

    def trace_symbol_migration(self, symbol_name: str) -> list[dict]:
        """
        Trace how a symbol migrated across cultures and time.

        Returns a timeline of the symbol's journey and meaning evolution.
        """
        migration_path = []

        if symbol_name in self.universal_archetypes:
            archetype = self.universal_archetypes[symbol_name]

            # Create migration entries for each culture
            # In production, this would pull from historical data
            for culture in archetype["cultures"]:
                migration_path.append({
                    "culture": culture,
                    "meanings": archetype["meanings"],
                    "astronomical_connection": archetype.get("astronomical", ""),
                    "notes": f"Symbol '{symbol_name}' present in {culture} tradition"
                })

        return migration_path

    def detect_meaning_inversion(self, symbol: Symbol,
                                 conquering_culture: str,
                                 conquered_culture: str) -> dict:
        """
        Detect if a symbol's meaning was inverted by a conquering culture.

        This is key to understanding cultural suppression and narrative control.
        """
        result = {
            "symbol": symbol.name,
            "inversion_detected": False,
            "original_meaning": "",
            "inverted_meaning": "",
            "analysis": ""
        }

        if conquering_culture in symbol.meanings and conquered_culture in symbol.meanings:
            orig = symbol.meanings[conquered_culture].lower()
            inverted = symbol.meanings[conquering_culture].lower()

            # Check for common inversion patterns
            inversion_pairs = [
                ("wisdom", "evil"), ("divine", "demonic"),
                ("sacred", "profane"), ("powerful", "dangerous"),
                ("life", "death"), ("good", "bad")
            ]

            for pos, neg in inversion_pairs:
                if pos in orig and neg in inverted:
                    result["inversion_detected"] = True
                    result["original_meaning"] = symbol.meanings[conquered_culture]
                    result["inverted_meaning"] = symbol.meanings[conquering_culture]
                    result["analysis"] = (
                        f"Symbol '{symbol.name}' appears to have been inverted from "
                        f"'{pos}' ({conquered_culture}) to '{neg}' ({conquering_culture}). "
                        f"This is a common pattern of cultural suppression."
                    )
                    break

        return result

    def generate_linguistic_evidence(self, artifact: Artifact) -> list[Evidence]:
        """
        Generate linguistic evidence items from artifact analysis.
        """
        evidence_items = []

        for inscription in artifact.inscriptions:
            # Analyze each inscription
            for lang in artifact.languages_present:
                analysis = self.analyze_text(
                    inscription,
                    lang,
                    {"text_id": artifact.id, "artifact": artifact.name}
                )

                evidence = Evidence(
                    evidence_type=EvidenceType.LINGUISTIC,
                    description=f"Linguistic analysis of {artifact.name}",
                    source=f"Inscription in {lang}",
                    content=inscription,
                    symbols=analysis.symbols_identified,
                    confidence_score=analysis.confidence
                )

                if analysis.potential_mistranslations:
                    evidence.potential_biases = [
                        mt["issue"] for mt in analysis.potential_mistranslations
                    ]

                evidence_items.append(evidence)

        return evidence_items
