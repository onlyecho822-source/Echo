# Art of Proof - Phoenix: Class Action Settlement Scanner

**Version:** 1.0  
**Last Updated:** January 8, 2026  
**Status:** ✅ Active

---

## Overview

The Class Action Settlement Scanner is an automated monitoring system designed to identify valuable class action settlements with approaching deadlines. This project scans major settlement tracking websites, extracts relevant data, and alerts users to high-value opportunities.

### Key Features

- **Automated Scanning:** Monitors classaction.org and topclassactions.com
- **Smart Filtering:** Identifies settlements with deadlines within 90 days
- **High-Value Alerts:** Flags settlements offering >$1,000 per claimant
- **Structured Data:** Exports machine-readable JSON for integration
- **Comprehensive Reports:** Generates human-readable reports with recommendations

---

## Quick Start

### View Results

1. **Quick Reference:** See `data/INDEX.md` for settlement table
2. **Full Analysis:** Read `MASTER_REPORT.md` for comprehensive details
3. **Raw Data:** Access `data/class_actions.json` for structured data
4. **Text Report:** Review `data/settlement_scan_report.txt` for detailed findings

### Current Scan Results

- **Total Settlements:** 25 with deadlines in next 90 days
- **High-Value Settlements:** 15 offering >$1,000 per claimant
- **Urgent Deadlines:** 8 settlements with <7 days remaining
- **Maximum Payout:** $10,000 (23andMe Data Breach)

---

## Project Structure

```
art-of-proof/phoenix/
├── README.md                       # This file
├── MASTER_REPORT.md                # Comprehensive analysis report
├── data/
│   ├── class_actions.json          # Structured settlement database
│   ├── settlement_scan_report.txt  # Detailed text report
│   └── INDEX.md                    # Quick reference index
└── scripts/
    └── extract_settlements.py      # Data extraction script
```

---

## Data Files

### class_actions.json

Structured JSON database containing all settlement information.

**Fields:**
- `name` - Settlement name
- `payout` - Dollar amount or range per claimant
- `deadline` - Claim deadline (MM/DD/YY format)
- `proof_required` - Whether proof of eligibility is required
- `claim_url` - Direct URL to file claim
- `eligibility` - Eligibility requirements description
- `source` - Website source (classaction.org or topclassactions.com)
- `deadline_date` - Parsed deadline (YYYY-MM-DD format)
- `days_until_deadline` - Days remaining to file
- `max_payout_amount` - Maximum dollar amount (integer)

**Example Record:**
```json
{
  "name": "23andMe - Data Breach Class Action Settlement",
  "payout": "$100 - $10,000",
  "deadline": "2/17/26",
  "proof_required": "No",
  "claim_url": "https://www.classaction.org/settlements",
  "eligibility": "Were a 23andMe customer between May 1, 2023 and October 1, 2023...",
  "source": "classaction.org",
  "deadline_date": "2026-02-17",
  "days_until_deadline": 40,
  "max_payout_amount": 10000
}
```

### INDEX.md

Quick reference table with all settlements sorted by deadline, including:
- Settlement names and maximum payouts
- Deadlines and days remaining
- Status indicators (🔴 Critical, 🟡 Urgent, 🟢 Active)
- Category breakdowns
- Action priority matrix

### MASTER_REPORT.md

Comprehensive report including:
- Executive summary and key findings
- Detailed analysis of high-value settlements
- Urgent deadline alerts
- Complete settlement listings
- Recommendations and action items
- Technical details and methodology
- Future enhancement suggestions

---

## Scan Methodology

### Data Sources

**Primary Sources:**
1. **classaction.org** - Comprehensive settlement database
   - 156 total settlements reviewed
   - Detailed eligibility and payout information
   - Direct claim links where available

2. **topclassactions.com** - Curated open settlements
   - Featured high-value settlements
   - Settlement news and updates
   - Community-focused content

### Collection Process

1. **Website Navigation**
   - Access settlement listing pages
   - Extract visible settlement information
   - Capture deadline and payout data

2. **Data Extraction**
   - Parse settlement names and descriptions
   - Extract payout amounts and ranges
   - Identify claim deadlines
   - Capture claim URLs and eligibility requirements

3. **Data Processing**
   - Filter by 90-day deadline window
   - Parse dates into standardized format
   - Calculate days until deadline
   - Extract maximum payout amounts
   - Identify high-value settlements (>$1,000)

4. **Quality Assurance**
   - Verify data completeness
   - Validate claim URLs
   - Cross-reference duplicate settlements

### Filtering Criteria

- **Time Window:** Deadlines between Jan 8, 2026 and Apr 8, 2026 (90 days)
- **High-Value Threshold:** Maximum payout >$1,000 per claimant
- **Urgent Threshold:** Deadline within 7 days

---

## Key Findings

### High-Value Settlements Alert

**15 settlements** identified offering more than $1,000 per claimant:

**Top 5 by Maximum Payout:**
1. 23andMe Data Breach - $10,000 (40 days remaining)
2. City of Hope Data Breach - $5,250 (5 days remaining)
3. Therapeutic Health Services - $5,100 (5 days remaining)
4. Multiple settlements at $5,000 maximum

**Total Potential Value:** Over $60,000 across all high-value settlements

### Urgent Deadlines

**8 settlements** require immediate action (<7 days):
- Restek Corporation - 1 day (CRITICAL)
- 4 settlements - 4 days remaining
- 3 settlements - 5-6 days remaining

**Combined Potential Value:** Up to $37,250

### Settlement Categories

**Data Breach Settlements:** 18 (72% of total)
- Typical payouts: $45-$100 base, up to $5,000-$10,000 with documentation
- Common requirement: Received breach notification

**Consumer Product Settlements:** 5
- Typical payouts: $100-$200
- Common requirement: Proof of purchase

**Privacy/Technology:** 2
- Payouts: TBD or varies

---

## Usage Recommendations

### For Individual Claimants

1. **Review INDEX.md** for quick overview of all settlements
2. **Check eligibility** for high-value and urgent settlements first
3. **Gather documentation** (breach notifications, receipts, loss records)
4. **File claims immediately** for settlements with <7 days remaining
5. **Set reminders** for settlements with longer deadlines
6. **Track filed claims** and follow up on payment status

### For Automation/Integration

1. **Parse class_actions.json** for structured settlement data
2. **Filter by eligibility criteria** relevant to your use case
3. **Set up alerts** for new high-value settlements
4. **Schedule regular scans** (weekly or bi-weekly recommended)
5. **Integrate with calendar** for deadline reminders
6. **Build dashboard** for visual tracking

### For Legal Professionals

1. **Review MASTER_REPORT.md** for comprehensive analysis
2. **Identify patterns** in settlement types and payouts
3. **Track settlement trends** over time
4. **Monitor client eligibility** across multiple settlements
5. **Advise clients** on highest-value opportunities
6. **Document filing strategies** for maximum recovery

---

## Technical Details

### System Requirements

- Python 3.11+
- Internet access for website scanning
- Browser automation tools (Chromium)
- File system access for data storage

### Dependencies

- Standard Python libraries (json, re, datetime)
- No external packages required for core functionality

### Performance

- **Scan Time:** ~5-10 minutes for full scan
- **Data Size:** ~21KB JSON output
- **Coverage:** 156+ settlements reviewed
- **Accuracy:** High (direct extraction from official sources)

---

## Limitations

1. **Coverage:** Limited to two major settlement websites; other settlements may exist on regional or specialized sites

2. **Detail Level:** Some settlements require visiting individual pages for complete information

3. **Payout Accuracy:** "Varies" and "TBD" amounts cannot be precisely quantified until settlement administrators provide details

4. **Eligibility Verification:** Users must verify individual eligibility; this system provides general requirements only

5. **Claim URL Completeness:** Some URLs point to category pages rather than specific settlement claim sites

6. **Real-Time Updates:** Data is current as of scan date; settlement terms may change

---

## Future Enhancements

### Planned Improvements

1. **Automated Scheduling**
   - Weekly automated scans
   - Email alerts for new settlements
   - Deadline reminder notifications

2. **Enhanced Data Collection**
   - Individual settlement page scraping
   - Claim form downloads
   - Settlement administrator contact extraction

3. **Expanded Coverage**
   - Additional settlement websites
   - State-specific databases
   - Industry-specific settlements

4. **Advanced Features**
   - Eligibility matching algorithms
   - Historical trend analysis
   - Payment tracking
   - ROI calculations

5. **User Interface**
   - Web dashboard
   - Mobile app
   - Personalized alerts
   - Claim management system

---

## Data Backup & Storage

### Local Storage
- **Primary Location:** `/home/ubuntu/art-of-proof/phoenix/`
- **Data Directory:** `/home/ubuntu/art-of-proof/phoenix/data/`

### GitHub Repository
- **Repository:** onlyecho822-source/Echo
- **Branch:** main
- **Sync Status:** Automated push on completion

### Google Drive
- **Sync Method:** rclone
- **Remote Name:** manus_google_drive
- **Sync Status:** Automated upload on completion

---

## Maintenance Schedule

### Regular Tasks

**Weekly:**
- Run settlement scan
- Update JSON database
- Review new high-value settlements
- Check for expired deadlines

**Monthly:**
- Generate trend analysis
- Update documentation
- Review and refine filtering criteria
- Archive old settlement data

**Quarterly:**
- Evaluate new data sources
- Implement feature enhancements
- Review system performance
- Update technical documentation

---

## Support & Contact

### Documentation
- **Master Report:** See `MASTER_REPORT.md` for comprehensive details
- **Index:** See `data/INDEX.md` for quick reference
- **This README:** Project overview and usage guide

### Data Access
- **JSON Database:** `data/class_actions.json`
- **Text Report:** `data/settlement_scan_report.txt`

### Legal Disclaimer

This system is provided for informational purposes only and does not constitute legal advice. Users should:
- Verify all information with official settlement websites
- Consult with legal counsel for specific questions
- Review settlement terms and conditions carefully
- Understand that eligibility and payouts may vary

---

## Version History

### Version 1.0 (January 8, 2026)
- Initial release
- Implemented scanning for classaction.org and topclassactions.com
- Created JSON database structure
- Generated comprehensive reports
- Established 90-day filtering window
- Implemented high-value alert threshold ($1,000)

---

## License & Usage

This project is part of the Art of Proof initiative. All data is sourced from publicly available settlement websites. Users are responsible for verifying information accuracy and eligibility before filing claims.

---

**Project:** Art of Proof - Phoenix  
**Component:** Class Action Settlement Scanner  
**Version:** 1.0  
**Last Scan:** January 8, 2026  
**Next Scan:** January 15, 2026 (recommended)
