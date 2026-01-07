# GSA Auctions Scan Summary

**Scan Date:** January 7, 2026 03:15 UTC  
**Output File:** `/home/ubuntu/art-of-proof/phoenix/data/gsa_auctions.json`

---

## Important Finding

**GSA Auctions does NOT provide estimated values** on their auction listings. The website only displays:
- Current bid amount
- Number of bidders  
- Auction closing time
- Item description and location

Therefore, the original requirement to filter by "estimated value >$1000 and current bid <50% of value" **cannot be fulfilled** as estimated values are not available.

---

## Adjusted Criteria

Instead, I filtered auctions by:
- **Current bid ≥ $1,000** (indicating high-value items)
- **Focus categories:** Vehicles, Electronics, Computer Equipment, Construction Equipment, Industrial Machinery, Aircraft
- **Items suitable for resale**

---

## Scan Results

### Summary Statistics
- **Total items found:** 14 auctions
- **Total current bid value:** $102,924.00
- **Average current bid:** $7,351.71
- **Categories scanned:** 6 (Vehicles, Computer Equipment, Electronics, Construction Equipment, Industrial Machinery, Aircraft)
- **Primary category:** Vehicles (100% of results)

### Top 5 Highest Bid Items

| Rank | Item | Current Bid | Bidders | Location | Closes |
|------|------|-------------|---------|----------|--------|
| 1 | 2019 Ford F250 4X4 | $18,040 | 20 | Oklahoma City, OK | 01/07/2026 04:07 PM CT |
| 2 | 2018 Chevrolet Silverado | $16,670 | 10 | Provo, UT | 01/09/2026 04:23 PM CT |
| 3 | 2017 Dodge Ram 1500 ST Quad Cab 4X4 | $16,670 | 4 | Salt Lake City, UT | 01/09/2026 04:42 PM CT |
| 4 | 2009 Ford Ranger | $9,516 | 12 | Fort Collins, CO | 01/07/2026 03:47 PM CT |
| 5 | 2018 Ram 1500 | $8,016 | 6 | Avondale, AZ | 01/07/2026 03:37 PM CT |

---

## Resale Potential Analysis

### High-Value Opportunities (Current Bid >$15,000)
1. **2019 Ford F250 4X4** - $18,040 (20 bidders)
   - Heavy competition indicates strong market demand
   - 4X4 trucks typically have excellent resale value
   - Commercial/work vehicle appeal

2. **2018 Chevrolet Silverado** - $16,670 (10 bidders)
   - Popular model with strong aftermarket
   - Good condition implied by bid level

3. **2017 Dodge Ram 1500 ST Quad Cab 4X4** - $16,670 (4 bidders)
   - Lower competition than similar-priced items
   - Quad cab configuration increases utility value

### Mid-Range Opportunities ($5,000-$10,000)
- **2009 Ford Ranger** - $9,516 (12 bidders) - High interest, compact truck segment
- **2018 Ram 1500** - $8,016 (6 bidders) - Recent model year
- **2018 Ford Fusion** - $6,780 (7 bidders) - Sedan market, good fuel economy
- **2011 Ford Flex** - $6,520 (12 bidders) - High competition for SUV
- **2017 Chevrolet Trax** - $6,073 (7 bidders) - Compact SUV, newer model

### Specialty/Niche Opportunities
- **1997 Stewart & Stevenson M-1088 Military Truck** - $4,050 (5 bidders)
  - Unique military surplus vehicle
  - Collector/commercial appeal
  - Heavy-duty capabilities

### Bargain/Repair Opportunities
- **2019 Ford Escape (Accident Damage)** - $1,825 & $1,775
  - Two similar units available
  - Repair and flip potential
  - Parts value if not repairable

---

## Data Structure

Each auction record contains:
- `item_description` - Full item name/description
- `current_bid` - Current highest bid amount (USD)
- `estimated_value` - "Not provided by GSA" (field included for reference)
- `auction_end_time` - Closing date and time (Central Time)
- `location` - City, State, ZIP code
- `item_url` - Direct link to auction page
- `category` - Item category
- `num_bidders` - Number of active bidders
- `lot_number` - GSA lot identification number

---

## Recommendations

1. **Monitor high-bidder items** - The 2019 Ford F250 and similar trucks show strong market demand
2. **Consider lower-competition items** - The Dodge Ram 1500 has fewer bidders but similar value
3. **Watch auction timing** - Several items close today (01/07/2026), requiring immediate action
4. **Evaluate repair opportunities** - Accident-damaged Ford Escapes may offer arbitrage potential
5. **Expand to other categories** - Computer equipment and electronics categories had 204+ items but mostly under $1,000 current bid

---

## Limitations

- **No estimated values available** from GSA Auctions website
- **Cannot calculate bid-to-value ratios** without estimated values
- **Vehicles dominate results** - Other categories (electronics, equipment) had lower current bids
- **Snapshot in time** - Bids change rapidly as auctions near closing
- **No condition reports** - Would need to inspect items or review detailed descriptions

---

## Next Steps

To find better deals matching the original criteria:
1. **Check other auction platforms** that provide estimated values (e.g., GovDeals, PropertyRoom)
2. **Monitor new listings** on GSA Auctions as they're posted
3. **Research market values** independently for items of interest
4. **Set up alerts** for specific categories or price ranges
5. **Expand search** to industrial equipment and electronics with detailed specifications

---

**File Location:** `/home/ubuntu/art-of-proof/phoenix/data/gsa_auctions.json`  
**Format:** JSON with metadata and structured auction records
