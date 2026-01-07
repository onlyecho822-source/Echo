# GSA Auctions Scanner

## Overview

This tool scans GSAAuctions.gov for newly listed items that meet specific investment criteria, focusing on electronics, vehicles, and equipment that can be resold for profit.

## Criteria

The scanner identifies items with:
- **Estimated Value**: Greater than $1,000
- **Current Bid**: Less than 50% of estimated value
- **Categories**: Electronics, Vehicles, Equipment

## Files

- `scan_gsa_auctions.py` - Main scanner script using Selenium for browser automation
- `data/gsa_auctions.json` - Output file containing scan results
- `data/gsa_page_source.html` - Debug file with page source

## Requirements

```bash
# Python packages
pip3 install selenium beautifulsoup4 requests

# System packages
sudo apt-get install chromium-browser chromium-chromedriver
```

## Usage

```bash
cd /home/ubuntu/Echo/art-of-proof/phoenix
python3 scan_gsa_auctions.py
```

## Output Format

The scanner generates a JSON file with the following structure:

```json
{
  "scan_date": "2026-01-07T05:05:47.415780",
  "total_items": 0,
  "criteria": {
    "min_estimated_value": 1000,
    "max_bid_percentage": 50,
    "categories": ["electronics", "vehicles", "equipment"]
  },
  "items": [
    {
      "description": "Item description",
      "current_bid": 500.00,
      "estimated_value": 2000.00,
      "auction_end_time": "2026-01-15 14:00:00",
      "location": "City, State",
      "item_url": "https://gsaauctions.gov/...",
      "category": "electronics"
    }
  ]
}
```

## Technical Challenges

GSAAuctions.gov is a React-based single-page application that loads content dynamically via JavaScript. The current implementation:

1. **Uses Selenium** for browser automation to handle JavaScript-rendered content
2. **Waits for page load** to allow React components to render
3. **Searches for common selectors** used in auction listing sites
4. **Extracts data** from identified elements using XPath and CSS selectors

### Known Limitations

- The site structure may change, requiring selector updates
- Some auction data may be behind additional navigation or search forms
- Rate limiting may affect large-scale scans
- The site may implement anti-scraping measures

## Alternative Approaches

If the automated scanner doesn't find items, consider:

1. **Manual Search**: Visit GSAAuctions.gov directly and use their search filters
2. **API Access**: Check if GSA provides an official API for auction data
3. **RSS Feeds**: Look for RSS feeds or email alerts for new listings
4. **Browser Extension**: Develop a browser extension for real-time monitoring

## Automation

To run this scanner on a schedule:

```bash
# Add to crontab for daily scans at 9 AM
0 9 * * * cd /home/ubuntu/Echo/art-of-proof/phoenix && python3 scan_gsa_auctions.py
```

## Data Analysis

After collecting data over time, you can analyze:

- **Best categories** for resale opportunities
- **Optimal bid timing** based on auction end patterns
- **Geographic trends** in item availability
- **Price patterns** and seasonal variations

## Legal & Ethical Considerations

- **Respect robots.txt**: Check GSA's robots.txt file for scraping policies
- **Rate limiting**: Implement delays between requests to avoid overloading servers
- **Terms of Service**: Review GSAAuctions.gov terms before automated access
- **Data usage**: Use scraped data responsibly and in compliance with regulations

## Support

For issues or improvements:
1. Check the debug file `data/gsa_page_source.html` to inspect page structure
2. Update selectors in the script based on current site structure
3. Increase wait times if content isn't loading properly
4. Review Selenium logs for browser automation errors

## Future Enhancements

- [ ] Add support for more categories
- [ ] Implement email notifications for matching items
- [ ] Create dashboard for visualizing opportunities
- [ ] Add historical price tracking
- [ ] Integrate with resale price estimation APIs
- [ ] Support for saved searches and custom criteria
- [ ] Export to CSV/Excel for analysis
