# Class Action Settlement Scan - Master Index

## Executive Summary

This directory contains comprehensive data from a systematic scan of class action settlement websites conducted on **January 8, 2026**. The scan identified **35 settlements** with claim deadlines within 90 days, including **17 high-value settlements** offering over $1,000 per claimant.

---

## 📋 Contents

### Primary Data Files

| File | Description | Size | Format |
|------|-------------|------|--------|
| `class_actions.json` | Complete structured dataset of all 35 settlements | 29KB | JSON |
| `high_value_settlements_alert.txt` | Detailed alert report for settlements >$1,000 | - | Plain Text |
| `README.md` | Master index and documentation (this file) | - | Markdown |

---

## 🎯 Key Findings

### Statistics
- **Total Settlements Scanned**: 35
- **High-Value Settlements (>$1,000)**: 17
- **Highest Single Payout**: $10,000 (23andMe Data Breach)
- **Average Max Payout (high-value)**: ~$4,500
- **Settlements with Imminent Deadlines (<7 days)**: 11

### Settlement Categories
- **Data Breach Settlements**: 27 (77%)
- **Consumer Protection**: 4 (11%)
- **Other**: 4 (11%)

### Urgent Action Required
- **1 Day Remaining**: 1 settlement ($3,500 max)
- **4 Days Remaining**: 5 settlements ($4,500-$5,000 max)
- **5 Days Remaining**: 5 settlements ($2,500-$5,250 max)

---

## 🚨 Top Priority Settlements

### Highest Value Available

**1. 23andMe Data Breach Settlement**
- **Maximum Payout**: $10,000
- **Claim Deadline**: February 17, 2026 (40 days)
- **Direct URL**: https://23andmedatasettlement.com/
- **Eligibility**: 23andMe customers between May 1-Oct 1, 2023 who received data breach notice
- **Benefits**: 
  - Up to $10,000 for Extraordinary Claims
  - Up to $165 for Health Information Claims
  - ~$100 for Statutory Cash Claims
  - 5 years Privacy & Medical Shield + Genetic Monitoring

### Most Urgent (Deadline: Jan 9, 2026)

**2. Restek Corporation Data Breach**
- **Maximum Payout**: $3,500
- **Days Remaining**: 1
- **Eligibility**: Personal information exposed in June 2023 Restek data breach

---

## 📊 Data Structure

### JSON Schema Overview

```json
{
  "metadata": {
    "scan_timestamp": "ISO 8601 timestamp",
    "scan_date": "YYYY-MM-DD",
    "sources": ["URL array"],
    "criteria": "Selection criteria",
    "total_settlements": "integer",
    "high_value_settlements_over_1000": "integer"
  },
  "settlements": [
    {
      "id": "unique identifier",
      "name": "settlement name",
      "source": "data source",
      "dollar_amount_per_claimant": "payout range",
      "min_payout": "minimum amount or null",
      "max_payout": "maximum amount or null",
      "claim_deadline": "YYYY-MM-DD",
      "days_until_deadline": "integer",
      "claim_url": "URL to file claim",
      "direct_settlement_url": "direct settlement website",
      "eligibility_requirements": "detailed requirements",
      "proof_required": "boolean",
      "exceeds_1000": "boolean"
    }
  ],
  "high_value_alerts": [
    {
      "settlement_id": "reference to settlement",
      "name": "settlement name",
      "max_payout": "amount",
      "claim_deadline": "YYYY-MM-DD",
      "alert_reason": "explanation"
    }
  ]
}
```

---

## 🔍 Data Sources

### Primary Sources
1. **ClassAction.org**: https://www.classaction.org/settlements
   - Comprehensive settlement database
   - Real-time deadline tracking
   - Direct links to official settlement websites

2. **TopClassActions.com**: https://topclassactions.com/category/lawsuit-settlements/open-lawsuit-settlements/
   - Curated settlement listings
   - Detailed eligibility information
   - Settlement amount estimates

### Scan Methodology
- **Scan Date**: January 8, 2026
- **Scan Timestamp**: 2026-01-08T15:06:52Z (UTC)
- **Time Window**: 90 days from scan date (through April 8, 2026)
- **Verification**: Cross-referenced between both sources where available
- **Direct URLs**: Captured for major settlements (23andMe, Toyota, Multnomah County)

---

## 📈 Settlement Trends

### By Category
- **Healthcare Data Breaches**: 16 settlements (majority of high-value)
- **Financial Services**: 3 settlements
- **Consumer Products**: 4 settlements
- **Technology/Privacy**: 5 settlements
- **Other**: 7 settlements

### By Payout Range
- **$0-$100**: 8 settlements
- **$100-$1,000**: 10 settlements
- **$1,000-$5,000**: 14 settlements
- **$5,000+**: 3 settlements

### Geographic Distribution
- **Nationwide**: 28 settlements
- **State-Specific**: 7 settlements
  - California: 3
  - Oregon: 1
  - Montana: 1
  - Rhode Island: 1
  - Washington: 1

---

## ⚠️ Important Notes

### Deadlines
- All deadlines are as of January 8, 2026
- **2 settlements have already passed their deadlines** (included for completeness)
- Days remaining calculated from scan date
- Always verify current deadline on official settlement website

### Eligibility
- Most settlements require **no proof of purchase**
- Data breach settlements typically require **receipt of breach notification**
- Some settlements have **geographic restrictions**
- Review full eligibility requirements before filing claims

### Payout Amounts
- Amounts shown are **maximum potential payouts**
- Actual payments may be **pro rata** based on total claims
- "Varies" indicates amount depends on individual circumstances
- Some settlements offer **alternative benefits** (credit monitoring, injunctive relief)

---

## 🔐 Data Integrity

### Timestamp Verification
- **Scan Start**: 2026-01-08T15:02:52Z
- **Scan Complete**: 2026-01-08T15:06:52Z
- **Data Compilation**: 2026-01-08T15:08:00Z
- **Total Execution Time**: ~6 minutes

### Quality Assurance
- ✓ All settlements verified from primary sources
- ✓ Deadlines cross-referenced where possible
- ✓ Direct URLs captured for major settlements
- ✓ Eligibility requirements extracted verbatim
- ✓ Payout ranges validated against source data

---

## 📞 Settlement Resources

### Key Direct URLs Captured
1. **23andMe Settlement**: https://23andmedatasettlement.com/
2. **Toyota Echo Settlement**: https://www.toyotaechosettlement.com/
3. **Multnomah County Settlement**: https://www.MultnomahTaxForeclosureSettlement.com

### General Resources
- **ClassAction.org Newsletter**: Free weekly settlement updates
- **Settlement Administrator Contact**: Typically Kroll Settlement Administration LLC
- **Legal Assistance**: Contact information available on individual settlement websites

---

## 📝 Usage Guidelines

### For Claimants
1. Review the `class_actions.json` file for complete settlement details
2. Check the `high_value_settlements_alert.txt` for priority settlements
3. Verify current deadlines on official settlement websites
4. File claims before deadlines (allow processing time)
5. Keep confirmation numbers and documentation

### For Researchers/Analysts
- JSON file is machine-readable and structured for analysis
- All timestamps in ISO 8601 format (UTC)
- Monetary values stored as integers (null for unknown)
- Boolean flags for key attributes (proof_required, exceeds_1000)

### For Developers
```python
# Example: Load and analyze the data
import json
from datetime import datetime

with open('class_actions.json', 'r') as f:
    data = json.load(f)

# Filter high-value settlements with imminent deadlines
urgent = [s for s in data['settlements'] 
          if s['exceeds_1000'] and s['days_until_deadline'] <= 7]

print(f"Found {len(urgent)} urgent high-value settlements")
```

---

## 🔄 Update History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-08 | Initial scan and data compilation |

---

## 📧 Disclaimer

This data is provided for informational purposes only and does not constitute legal advice. Settlement terms, deadlines, and eligibility requirements may change. Always verify information directly with settlement administrators before filing claims. The creators of this dataset are not responsible for any decisions made based on this information.

---

## 📄 License & Attribution

**Data Collection Date**: January 8, 2026  
**Sources**: ClassAction.org, TopClassActions.com  
**Compiled by**: Automated settlement monitoring system  
**Purpose**: Consumer awareness and protection

---

**Last Updated**: 2026-01-08T15:08:00Z
