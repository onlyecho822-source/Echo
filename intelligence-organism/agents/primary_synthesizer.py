#!/usr/bin/env python3
"""
Primary Synthesizer Agent - Tier 0 (Manus AI)
Generates the Grand Master Report from all domain expert inputs
"""

import os
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# Configuration
OUTPUT_DIR = Path("intelligence-organism/reports/primary_synthesis")
DATA_DIR = Path("intelligence-organism/data/raw/edgar")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYNTHESIS_PROMPT = """You are the Primary Synthesizer of a Multi-Tier Intelligence Organism. Your role is to generate a comprehensive Grand Master Report synthesizing all available intelligence data.

Your mandate:
1. Analyze all SEC filings and economic data from the past 24 hours
2. Identify patterns, anomalies, and strategic movements by high-profile entities
3. Synthesize insights into a coherent narrative
4. Provide actionable intelligence for strategic decision-making

Data available:
{data_summary}

Generate a comprehensive Grand Master Report with the following sections:
1. Executive Summary
2. Key Findings
3. Entity-Specific Analysis
4. Strategic Implications
5. Recommended Actions

Be thorough, precise, and strategic. This report will be reviewed alongside an adversarial analysis."""

def load_latest_data():
    """Load the most recent data from all sources"""
    data_summary = []
    
    # Load EDGAR data
    if DATA_DIR.exists():
        for entity_dir in DATA_DIR.iterdir():
            if entity_dir.is_dir():
                files = sorted(entity_dir.glob("*.json"), reverse=True)
                if files:
                    with open(files[0]) as f:
                        data = json.load(f)
                        hits = data.get("hits", {}).get("hits", [])
                        data_summary.append(f"- {entity_dir.name}: {len(hits)} recent filings")
    
    return "\n".join(data_summary) if data_summary else "No data available"

def generate_report(data_summary):
    """Generate the Grand Master Report using GPT-4"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a strategic intelligence synthesizer."},
                {"role": "user", "content": SYNTHESIS_PROMPT.format(data_summary=data_summary)}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating report: {e}")
        return None

def save_report(content):
    """Save the Grand Master Report"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = OUTPUT_DIR / f"grand_master_report_{timestamp}.md"
    
    with open(output_file, 'w') as f:
        f.write(f"# Grand Master Report\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        f.write(content)
    
    print(f"Grand Master Report saved to {output_file}")

def main():
    """Main execution"""
    print(f"Primary Synthesizer starting at {datetime.now().isoformat()}")
    
    # Load data
    data_summary = load_latest_data()
    print(f"Data summary:\n{data_summary}\n")
    
    # Generate report
    print("Generating Grand Master Report...")
    report = generate_report(data_summary)
    
    if report:
        save_report(report)
        print("Primary synthesis complete")
    else:
        print("Failed to generate report")

if __name__ == "__main__":
    main()
