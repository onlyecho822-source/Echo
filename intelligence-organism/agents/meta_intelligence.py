#!/usr/bin/env python3
"""
Meta-Intelligence Substrate Agent - Tier 5
Historical pattern recognition and Priority Interrupt generation
"""

import os
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np

# Configuration
FRED_DATA_DIR = Path("intelligence-organism/data/meta_intelligence/fred")
ALERT_DIR = Path("intelligence-organism/alerts/meta_intelligence")
PATTERN_THRESHOLD = 0.90  # 90% correlation triggers Priority Interrupt

# Historical failure patterns (2008 Financial Crisis signature)
CRISIS_2008_PATTERN = {
    "name": "2008 Credit Crisis Signature",
    "indicators": {
        "TOTCI": {"type": "contraction", "threshold": -0.20},  # 20% decline in commercial paper
        "WALCL": {"type": "expansion", "threshold": 0.50},     # 50% increase in Fed balance sheet
        "DGS10": {"type": "volatility", "threshold": 2.0}      # High volatility in 10Y treasury
    },
    "description": "Pattern matching the 2008 financial crisis: credit market freeze + Fed intervention"
}

def load_fred_series(series_id):
    """Load a FRED time series from disk"""
    csv_file = FRED_DATA_DIR / f"{series_id}.csv"
    if not csv_file.exists():
        return None
    
    df = pd.read_csv(csv_file)
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df.dropna()

def calculate_change(series, days=30):
    """Calculate percentage change over the last N days"""
    if series is None or len(series) < days:
        return None
    
    recent = series.tail(days)
    if len(recent) < 2:
        return None
    
    start_value = recent.iloc[0]['value']
    end_value = recent.iloc[-1]['value']
    
    if start_value == 0:
        return None
    
    return (end_value - start_value) / start_value

def check_pattern_match(pattern):
    """Check if current data matches a historical failure pattern"""
    matches = {}
    
    for series_id, criteria in pattern["indicators"].items():
        series = load_fred_series(series_id)
        if series is None:
            continue
        
        change = calculate_change(series, days=30)
        if change is None:
            continue
        
        # Check if the change matches the pattern criteria
        if criteria["type"] == "contraction":
            matches[series_id] = change <= criteria["threshold"]
        elif criteria["type"] == "expansion":
            matches[series_id] = change >= criteria["threshold"]
        elif criteria["type"] == "volatility":
            # Calculate volatility (standard deviation of recent changes)
            recent = series.tail(30)
            volatility = recent['value'].std()
            matches[series_id] = volatility >= criteria["threshold"]
    
    # Calculate overall match score
    if not matches:
        return 0.0
    
    return sum(matches.values()) / len(pattern["indicators"])

def generate_priority_interrupt(pattern, match_score):
    """Generate a Priority Interrupt alert"""
    ALERT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    alert_file = ALERT_DIR / f"priority_interrupt_{timestamp}.json"
    
    alert = {
        "timestamp": datetime.now().isoformat(),
        "alert_type": "PRIORITY_INTERRUPT",
        "pattern_name": pattern["name"],
        "match_score": match_score,
        "description": pattern["description"],
        "recommendation": "IMMEDIATE REVIEW REQUIRED: Historical pattern detected with high probability of systemic risk",
        "severity": "CRITICAL" if match_score >= 0.95 else "HIGH"
    }
    
    with open(alert_file, 'w') as f:
        json.dump(alert, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"🚨 PRIORITY INTERRUPT GENERATED 🚨")
    print(f"{'='*80}")
    print(f"Pattern: {pattern['name']}")
    print(f"Match Score: {match_score:.2%}")
    print(f"Severity: {alert['severity']}")
    print(f"Alert saved to: {alert_file}")
    print(f"{'='*80}\n")

def main():
    """Main execution loop"""
    print(f"Meta-Intelligence Substrate starting at {datetime.now().isoformat()}")
    print("Monitoring for historical failure patterns...\n")
    
    # Check the 2008 crisis pattern
    match_score = check_pattern_match(CRISIS_2008_PATTERN)
    print(f"Pattern: {CRISIS_2008_PATTERN['name']}")
    print(f"Match Score: {match_score:.2%}")
    
    if match_score >= PATTERN_THRESHOLD:
        generate_priority_interrupt(CRISIS_2008_PATTERN, match_score)
    else:
        print("No Priority Interrupt triggered (below threshold)")
    
    print(f"\nMeta-Intelligence Substrate completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
