#!/usr/bin/env python3
"""
FRED Monitor Agent - Meta-Intelligence Economic Data Feed
Fetches critical economic time series for historical pattern matching
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

# Configuration
FRED_API_KEY = os.getenv("FRED_API_KEY")
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
OUTPUT_DIR = Path("intelligence-organism/data/meta_intelligence/fred")

# Critical economic indicators for Meta-Intelligence Substrate
SERIES_IDS = {
    "WALCL": "Fed Balance Sheet (Total Assets)",
    "TOTCI": "Commercial Paper Outstanding",
    "MSI": "Money Supply (M1)",
    "DGS10": "10-Year Treasury Rate",
    "UNRATE": "Unemployment Rate",
    "CPIAUCSL": "Consumer Price Index",
    "DEXCHUS": "China/US Exchange Rate"
}

def fetch_series_data(series_id, days_back=365):
    """Fetch historical data for a given FRED series"""
    if not FRED_API_KEY:
        print("ERROR: FRED_API_KEY not set")
        return None
    
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching {series_id}: {e}")
        return None

def save_series_data(series_id, series_name, data):
    """Save time series data to disk"""
    if not data or "observations" not in data:
        print(f"No data for {series_id}")
        return
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(data["observations"])
    
    # Save as CSV for time-series analysis
    output_file = OUTPUT_DIR / f"{series_id}.csv"
    df.to_csv(output_file, index=False)
    
    # Also save raw JSON
    json_file = OUTPUT_DIR / f"{series_id}.json"
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved {len(df)} observations for {series_name} ({series_id})")

def main():
    """Main execution loop"""
    print(f"FRED Monitor starting at {datetime.now().isoformat()}")
    print(f"Fetching {len(SERIES_IDS)} economic time series...")
    
    for series_id, series_name in SERIES_IDS.items():
        print(f"\nFetching: {series_name} ({series_id})")
        data = fetch_series_data(series_id)
        if data:
            save_series_data(series_id, series_name, data)
    
    print(f"\nFRED Monitor completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
