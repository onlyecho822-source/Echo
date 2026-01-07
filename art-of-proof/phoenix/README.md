# Phoenix - Class Action Settlement Tracker

**Project:** Art of Proof - Phoenix Initiative  
**Last Updated:** 04:06 Jan 07 2026

## Overview

Phoenix is an automated class action settlement monitoring system that scans major settlement websites for new opportunities with claim deadlines in the next 90 days.

## Data Files

### class_actions.json
**Format:** JSON  
**Size:** 91 KB  
**Last Scan:** 2026-01-07 00:00:00

Comprehensive database of 135 class action settlements with claim deadlines in the next 90 days.

**Data Structure:**
- `settlement_name` - Full name of the settlement
- `payout` - Dollar amount per claimant
- `deadline` - Claim deadline date (MM/DD/YY)
- `claim_url` - Direct URL guidance to file claim
- `eligibility` - Eligibility requirements
- `proof_required` - Whether proof is needed (Yes/No/N/A)
- `source` - Data source (classaction.org or topclassactions.com)

### settlement_scan_report.txt
**Format:** Plain text  
**Size:** 4.4 KB

Executive summary report highlighting:
- Total settlements found
- High-value settlements (>$1,000)
- Urgent deadlines (less than 7 days)
- Top 18 high-value opportunities

## Key Findings

**Total Settlements:** 135  
**High-Value Settlements (>$1,000):** 61

### Top High-Value Settlements

1. **Oklahoma Spine Hospital - Data Breach** - $100-$10,100 (Deadline: 1/7/26)
2. **Lyon Real Estate - Data Breach** - $250-$10,000 (Deadline: 2/5/26)
3. **23andMe - Data Breach** - $100-$10,000 (Deadline: 2/17/26)
4. **Hafetz - Data Breach** - $50-$10,000 (Deadline: 1/22/26)
5. **City of Hope - Data Breach** - $100-$5,250 (Deadline: 1/13/26)

### Urgent Deadlines (Less than 7 Days)

- Oklahoma Spine Hospital: $100-$10,100 by 1/7/26
- Nations Direct Mortgage: Up to $2,750 by 1/7/26
- Fathom Realty: $48 by 1/7/26

## Data Sources

- **classaction.org** - Primary source for settlement listings
- **topclassactions.com** - Secondary source for settlement listings

## Automation

This data is generated through automated scanning of class action settlement websites. The system:
1. Scans classaction.org and topclassactions.com
2. Extracts settlements with deadlines in next 90 days
3. Identifies high-value settlements (>$1,000)
4. Generates structured JSON data and summary report
5. Updates repository with latest findings

## Usage

To access settlement data programmatically:

```python
import json

with open('data/class_actions.json', 'r') as f:
    settlements = json.load(f)

# Get all high-value settlements
high_value = settlements['high_value_settlements']

# Filter by deadline
urgent = [s for s in settlements['settlements'] 
          if s['deadline'] in ['1/7/26', '1/8/26', '1/9/26']]
```

## Notes

- Many settlements require proof of purchase or documentation for higher payouts
- Some settlements offer alternative cash payments without proof
- Data breach settlements typically require notice of breach to claim
- Deadlines are firm - claims must be submitted by deadline date
- Some settlements are state-specific (e.g., California residents only)

## Security

This repository is **private** and contains sensitive financial opportunity data. Access is restricted to authorized personnel only.

---

**EchoNate** - Personal Representative  
Art of Proof Initiative
