#!/usr/bin/env python3
"""
EDGAR Monitor Agent - Tier 3/4 Sensory System
Real-time SEC filings ingestion for both Primary and Adversarial synthesis pipelines
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
BASE_URL = "https://efts.sec.gov/LATEST/search-index"
USER_AGENT = os.getenv("SEC_USER_AGENT", "Intelligence Organism research@example.com")
OUTPUT_DIR = Path("intelligence-organism/data/raw/edgar")

# Target entities for monitoring (billionaires, major institutions)
TARGET_ENTITIES = [
    "Bezos",
    "Musk",
    "Buffett",
    "Gates",
    "Zuckerberg",
    "BlackRock",
    "Vanguard",
    "Citadel"
]

def fetch_edgar_filings(entity_name, days_back=1):
    """
    Fetch SEC EDGAR filings for a given entity using full-text search.
    This is the adversarial data pipeline - unfiltered, complete results.
    """
    headers = {"User-Agent": USER_AGENT}
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    params = {
        "q": entity_name,
        "dateRange": "custom",
        "startdt": start_date.strftime("%Y-%m-%d"),
        "enddt": end_date.strftime("%Y-%m-%d")
    }
    
    try:
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data for {entity_name}: {e}")
        return None

def save_filing_data(entity_name, data):
    """Save raw filing data to disk"""
    if not data or "hits" not in data or "hits" not in data["hits"]:
        print(f"No filings found for {entity_name}")
        return
    
    # Create output directory
    entity_dir = OUTPUT_DIR / entity_name.lower().replace(" ", "_")
    entity_dir.mkdir(parents=True, exist_ok=True)
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = entity_dir / f"filings_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved {len(data['hits']['hits'])} filings for {entity_name} to {output_file}")

def main():
    """Main execution loop"""
    print(f"EDGAR Monitor starting at {datetime.now().isoformat()}")
    print(f"Monitoring {len(TARGET_ENTITIES)} entities...")
    
    for entity in TARGET_ENTITIES:
        print(f"\nFetching filings for: {entity}")
        data = fetch_edgar_filings(entity)
        if data:
            save_filing_data(entity, data)
    
    print(f"\nEDGAR Monitor completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
