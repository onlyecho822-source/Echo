"""
Phoenix Program Configuration
Real-time Federal Register Intelligence Pipeline
"""

import os
from datetime import datetime

# ============================================================================
# CORE CONFIGURATION
# ============================================================================

PROJECT_NAME = "Phoenix Intelligence Pipeline"
VERSION = "1.0.0"
TIMESTAMP = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

# ============================================================================
# DATA SOURCES
# ============================================================================

FEDERAL_REGISTER_RSS = "https://www.federalregister.gov/api/v1/documents.rss"
FEDERAL_REGISTER_API = "https://www.federalregister.gov/api/v1/documents.json"

# ============================================================================
# FILTERING CONFIGURATION
# ============================================================================

# High-value keywords (strategic intelligence signals)
HIGH_VALUE_KEYWORDS = [
    # Regulatory & Policy
    "proposed rule", "final rule", "emergency", "immediate effect",
    "national security", "critical infrastructure", "cybersecurity",
    
    # Economic & Financial
    "tariff", "trade agreement", "sanctions", "export control",
    "antitrust", "merger", "acquisition", "divestiture",
    
    # Technology & Innovation
    "artificial intelligence", "quantum", "semiconductor", "5G",
    "data privacy", "encryption", "surveillance",
    
    # Energy & Environment
    "renewable energy", "carbon", "emissions", "climate",
    "oil", "gas", "nuclear", "grid",
    
    # Healthcare & Pharma
    "drug approval", "clinical trial", "FDA", "vaccine",
    "medical device", "healthcare", "medicare", "medicaid",
    
    # Defense & Intelligence
    "defense", "military", "intelligence", "classified",
    "foreign adversary", "espionage", "counterintelligence"
]

# Noise keywords (filter out low-value content)
NOISE_KEYWORDS = [
    "meeting notice", "sunshine act", "advisory committee",
    "public comment", "extension of comment period",
    "correction", "withdrawal", "technical amendment"
]

# ============================================================================
# OLLAMA CONFIGURATION
# ============================================================================

OLLAMA_MODEL = "qwen2.5:7b"
OLLAMA_BASE_URL = "http://localhost:11434"

# Synthesis prompt template
SYNTHESIS_PROMPT = """You are an elite intelligence analyst for a sovereign wealth fund. Analyze this Federal Register document and provide strategic intelligence.

DOCUMENT TITLE: {title}
DOCUMENT TYPE: {doc_type}
AGENCIES: {agencies}
PUBLICATION DATE: {pub_date}

DOCUMENT SUMMARY:
{abstract}

ANALYSIS REQUIRED:
1. STRATEGIC IMPLICATIONS: What does this mean for capital markets, geopolitics, or technology trends?
2. RISK ASSESSMENT: What risks or opportunities does this create? (Score 1-10)
3. TIME HORIZON: When will this impact be felt? (Immediate / 6 months / 12+ months)
4. ACTIONABLE INSIGHT: What should a strategic decision-maker do with this information?

Provide your analysis in a concise, high-signal format. No fluff."""

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

REPORTS_DIR = "/home/ubuntu/phoenix-program/reports"
DATA_DIR = "/home/ubuntu/phoenix-program/data"

# Report template
REPORT_TEMPLATE = """
# Phoenix Intelligence Report
**Generated:** {timestamp}
**Source:** Federal Register
**Documents Analyzed:** {doc_count}
**High-Value Signals:** {signal_count}

---

{signals}

---

**Audit Trail:**
- Total documents scanned: {total_scanned}
- Documents filtered (noise): {filtered_count}
- High-value signals identified: {signal_count}
- Analysis time: {analysis_time}

**Methodology:**
- Source: Federal Register RSS feed
- Filtering: Keyword-based noise removal
- Synthesis: Ollama {model} local LLM
- Risk scoring: Automated heuristic analysis
"""

# ============================================================================
# RISK SCORING CONFIGURATION
# ============================================================================

RISK_MULTIPLIERS = {
    "emergency": 2.0,
    "immediate effect": 1.8,
    "national security": 1.7,
    "sanctions": 1.6,
    "tariff": 1.5,
    "antitrust": 1.4,
    "critical infrastructure": 1.5,
    "cybersecurity": 1.3
}

# ============================================================================
# EXECUTION CONFIGURATION
# ============================================================================

MAX_DOCUMENTS_PER_RUN = 50  # Limit for micro-pilot
CHUNK_SIZE = 5  # Process in chunks to avoid memory issues
TIMEOUT_SECONDS = 120  # Max time for Ollama synthesis per document

# ============================================================================
# GITHUB INTEGRATION
# ============================================================================

GITHUB_REPO = "onlyecho822-source/Echo"
GITHUB_REPORTS_PATH = "phoenix-program/reports"
AUTO_COMMIT = True  # Automatically commit reports to GitHub

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
