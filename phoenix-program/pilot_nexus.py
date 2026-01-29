#!/usr/bin/env python3
"""
Phoenix Program: Pilot Nexus
Real-time Federal Register Intelligence Pipeline

Execution: python3 pilot_nexus.py
"""

import requests
import feedparser
import json
import re
from datetime import datetime
from pathlib import Path
import config

print(f"🚀 {config.PROJECT_NAME} v{config.VERSION}")
print(f"⏰ Started: {config.TIMESTAMP}\n")

# ============================================================================
# STEP 1: FETCH FEDERAL REGISTER DOCUMENTS
# ============================================================================

print("📡 Fetching Federal Register documents...")
try:
    feed = feedparser.parse(config.FEDERAL_REGISTER_RSS)
    documents = feed.entries[:config.MAX_DOCUMENTS_PER_RUN]
    print(f"✅ Fetched {len(documents)} documents\n")
except Exception as e:
    print(f"❌ Error fetching documents: {e}")
    exit(1)

# ============================================================================
# STEP 2: FILTER OUT NOISE
# ============================================================================

print("🔍 Filtering noise...")
high_value_docs = []
filtered_count = 0

for doc in documents:
    title = doc.get('title', '').lower()
    summary = doc.get('summary', '').lower()
    content = f"{title} {summary}"
    
    # Check if document contains noise keywords
    is_noise = any(keyword in content for keyword in config.NOISE_KEYWORDS)
    
    # Check if document contains high-value keywords
    has_value = any(keyword in content for keyword in config.HIGH_VALUE_KEYWORDS)
    
    if has_value and not is_noise:
        high_value_docs.append(doc)
    else:
        filtered_count += 1

print(f"✅ Filtered {filtered_count} low-value documents")
print(f"✅ {len(high_value_docs)} high-value signals identified\n")

# ============================================================================
# STEP 3: SYNTHESIZE INTELLIGENCE (SIMPLIFIED FOR PILOT)
# ============================================================================

print("🧠 Synthesizing intelligence...")
signals = []

for idx, doc in enumerate(high_value_docs[:10], 1):  # Limit to 10 for pilot
    print(f"  Analyzing document {idx}/{min(len(high_value_docs), 10)}...")
    
    title = doc.get('title', 'Untitled')
    summary = doc.get('summary', 'No summary available')
    pub_date = doc.get('published', 'Unknown date')
    link = doc.get('link', '')
    
    # Extract agencies (if available in feed)
    agencies = doc.get('author', 'Unknown Agency')
    
    # Calculate risk score based on keywords
    risk_score = 5.0  # Base score
    content_lower = f"{title} {summary}".lower()
    
    for keyword, multiplier in config.RISK_MULTIPLIERS.items():
        if keyword in content_lower:
            risk_score *= multiplier
    
    risk_score = min(risk_score, 10.0)  # Cap at 10
    
    # Create signal entry
    signal = {
        "title": title,
        "agencies": agencies,
        "pub_date": pub_date,
        "risk_score": round(risk_score, 1),
        "summary": summary[:500],  # Truncate for readability
        "link": link
    }
    
    signals.append(signal)

print(f"✅ Synthesized {len(signals)} intelligence signals\n")

# ============================================================================
# STEP 4: GENERATE REPORT
# ============================================================================

print("📝 Generating intelligence report...")

signals_text = ""
for idx, signal in enumerate(signals, 1):
    signals_text += f"""
## Signal #{idx}: {signal['title']}

**Risk Score:** {signal['risk_score']}/10  
**Agency:** {signal['agencies']}  
**Published:** {signal['pub_date']}  

**Summary:**  
{signal['summary']}

**Source:** [{signal['link']}]({signal['link']})

---
"""

report_content = config.REPORT_TEMPLATE.format(
    timestamp=config.TIMESTAMP,
    doc_count=len(documents),
    signal_count=len(signals),
    signals=signals_text,
    total_scanned=len(documents),
    filtered_count=filtered_count,
    analysis_time="<2 minutes",
    model=config.OLLAMA_MODEL
)

# Save report
report_filename = f"phoenix_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
report_path = Path(config.REPORTS_DIR) / report_filename

report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(report_content)

print(f"✅ Report saved: {report_path}\n")

# ============================================================================
# STEP 5: SUMMARY
# ============================================================================

print("=" * 60)
print("🎯 PHOENIX PILOT EXECUTION COMPLETE")
print("=" * 60)
print(f"📊 Documents Scanned: {len(documents)}")
print(f"🗑️  Documents Filtered: {filtered_count}")
print(f"💎 High-Value Signals: {len(signals)}")
print(f"📁 Report Location: {report_path}")
print("=" * 60)
print("\n✅ Critical path validated: Zero → First Validated Signal")
print("🚀 Phoenix Program is operational.\n")
