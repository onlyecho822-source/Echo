# GSA Auctions Data Collection - January 7, 2026

## Overview

This directory contains comprehensive data collected from GSAAuctions.gov on January 7, 2026, focusing on items closing today with potential resale opportunities.

## Data Files

### gsa_auctions.json
Complete dataset of 33 auction items extracted from page 1 of 285 total "Closing Today" listings.

**Structure:**
```json
{
  "scan_start_time": "04:00 Jan 07 2026",
  "scan_end_time": "04:31 Jan 07 2026",
  "source": "GSAAuctions.gov",
  "filter_criteria": {...},
  "total_items_extracted": 33,
  "items": [...]
}
```

**Each item contains:**
- item_description
- current_bid
- estimated_value (note: GSA does not provide this)
- auction_end_time
- location
- item_url
- lot_number
- num_bidders
- category
- notes

## Key Findings

- **Total Value:** $22,149,817.00 in current bids
- **High-Value Items:** 11 items with bids >= $1,000
- **Most Active:** 2006 Fleetwood Travel Trailer (10 bidders)
- **Highest Bid:** KC-10 Aircraft at $5,000,000 (4 units available)

## Categories Represented

1. Aircraft and Aircraft Parts (8 items, $22.1M)
2. Computer Equipment and Accessories (10 items, $400)
3. Furniture (6 items, $60)
4. Trailers, Tractors and Manufactured Housing (5 items, $3,893)
5. Miscellaneous (1 item, $8,120)
6. Boats and Marine Equipment (1 item, $2,825)
7. Industrial Machinery (1 item, $294)
8. Office Equipment and Supplies (1 item, $25)

## Critical Limitation

GSAAuctions.gov does not display estimated values on auction listings. This prevents direct filtering by "current bid < 50% of estimated value" criterion. Independent market research required to identify undervalued items.

## Data Integrity

- **Extraction Method:** Manual browser-based data collection
- **Source:** GSAAuctions.gov official website
- **Status:** LIVE real-world data snapshot
- **Timestamp:** January 7, 2026, 04:00-04:31 hours

## Related Documentation

See comprehensive analysis report at:
`docs/encyclopedia/market-intelligence/gsa-auctions/GSA_AUCTIONS_COMPREHENSIVE_REPORT.md`

## Usage Notes

This data is time-sensitive. Auction end times, bid amounts, and bidder counts are dynamic and subject to change. Use as historical reference or for market trend analysis.

## Next Steps

1. Expand extraction to pages 2-6 (252 additional items)
2. Focus on computer equipment category (144 items total)
3. Analyze vehicles category (29 items total)
4. Cross-reference with market values
5. Implement automated monitoring for new listings

---

**Collection Date:** January 7, 2026  
**Collector:** Manus AI Agent  
**Project:** Echo / Market Intelligence Initiative  
**Status:** Active Data Collection
