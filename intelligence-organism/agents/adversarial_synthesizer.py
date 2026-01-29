#!/usr/bin/env python3
"""
Adversarial Synthesizer Agent - Red Team
Generates alternative narratives to challenge the primary synthesis
"""

import os
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# Configuration
OUTPUT_DIR = Path("intelligence-organism/reports/adversarial_briefs")
DATA_DIR = Path("intelligence-organism/data/raw/edgar")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ADVERSARIAL_PROMPT = """You are the Red Team Synthesizer of a Multi-Tier Intelligence Organism. Your sole purpose is to identify the most compelling alternative narrative to the primary synthesis. 

Your mandate:
1. Challenge ALL assumptions made by the primary synthesis
2. Identify data points that may have been ignored, downplayed, or misinterpreted
3. Construct the strongest possible case that the primary narrative is incomplete or wrong
4. Present evidence-based alternative interpretations

Data available:
{data_summary}

Generate a formal Adversarial Brief with the following sections:
1. Executive Counter-Summary
2. Challenged Assumptions
3. Alternative Interpretation of Evidence
4. Overlooked Data Points
5. Counter-Recommendations

Your output must be a formal, evidence-based challenge. Do not be diplomatic. Your role is to stress-test the primary synthesis through rigorous intellectual opposition."""

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

def generate_adversarial_brief(data_summary):
    """Generate the Adversarial Brief using GPT-4"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a ruthless intellectual adversary. Challenge everything."},
                {"role": "user", "content": ADVERSARIAL_PROMPT.format(data_summary=data_summary)}
            ],
            temperature=0.9,  # Higher temperature for more creative challenges
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating adversarial brief: {e}")
        return None

def save_brief(content):
    """Save the Adversarial Brief"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = OUTPUT_DIR / f"adversarial_brief_{timestamp}.md"
    
    with open(output_file, 'w') as f:
        f.write(f"# Adversarial Brief (Red Team Analysis)\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        f.write(content)
    
    print(f"Adversarial Brief saved to {output_file}")

def main():
    """Main execution"""
    print(f"Adversarial Synthesizer (Red Team) starting at {datetime.now().isoformat()}")
    
    # Load data
    data_summary = load_latest_data()
    print(f"Data summary:\n{data_summary}\n")
    
    # Generate adversarial brief
    print("Generating Adversarial Brief...")
    brief = generate_adversarial_brief(data_summary)
    
    if brief:
        save_brief(brief)
        print("Adversarial synthesis complete")
    else:
        print("Failed to generate adversarial brief")

if __name__ == "__main__":
    main()
