# Illinois Unclaimed Property Scanner

## Project Overview

This project contains automated tools for scanning the Illinois State Treasurer's unclaimed property database (ICash) for properties over $1,000 in Cook County zip codes (60601-60699).

## Challenge

The Illinois ICash database (https://icash.illinoistreasurer.gov) has significant limitations for automated bulk searching:

### Technical Barriers

1. **CloudFront Bot Protection**: The website uses AWS CloudFront with aggressive bot detection that blocks automated requests
2. **No Public API**: Illinois does not provide a public API for bulk unclaimed property searches
3. **Name-Required Search**: The search interface requires a last name or business name - cannot search by zip code alone
4. **No Bulk Export**: No option to download or export bulk data
5. **CAPTCHA/Turnstile**: The search button uses Cloudflare Turnstile (CAPTCHA-like protection)

### Search Constraints

- Must provide a last/business name to search
- Zip code is optional filter only
- No ability to filter by property value in the interface
- No wildcard searches supported
- Results are paginated and limited

## Current Solution Status

The automated Selenium-based scanner encounters 403 Forbidden errors due to CloudFront bot protection. The website successfully blocks:
- Direct HTTP requests
- Selenium WebDriver automation
- Headless browser access

## Alternative Approaches

### 1. Manual Search Strategy (Most Reliable)

Manually search the database using common surnames combined with Cook County zip codes:

**Top Surnames to Search:**
- Smith, Johnson, Williams, Brown, Jones
- Garcia, Rodriguez, Martinez, Hernandez, Lopez
- Gonzalez, Wilson, Anderson, Thomas, Taylor

**Cook County Zip Codes:** 60601-60699

**Process:**
1. Visit https://icash.illinoistreasurer.gov/app/claim-search
2. Enter surname + zip code
3. Review results for properties > $1,000
4. Record findings in `data/unclaimed_property.json`

### 2. FOIA Request (Official Channel)

File a Freedom of Information Act (FOIA) request with the Illinois State Treasurer's Office:

**Request Template:**
```
To: Illinois State Treasurer's Office
Subject: FOIA Request - Unclaimed Property Data

I am requesting access to records of unclaimed property held by the 
Illinois State Treasurer's Office for Cook County (zip codes 60601-60699) 
with values exceeding $1,000.

Requested format: CSV or JSON export including:
- Property owner name
- Dollar amount
- Property type
- Property ID/Claim reference
- Last known address

Contact: [Your contact information]
```

Submit via: https://illinoistreasurer.gov/foia/

### 3. Third-Party Services

Consider using services that aggregate unclaimed property data:
- MissingMoney.com (multi-state search)
- NAUPA (National Association of Unclaimed Property Administrators)

### 4. Browser Extension Approach

Develop a browser extension that:
- Runs in user's actual browser (not automated)
- Assists with systematic searching
- Extracts and saves results
- Avoids bot detection by using real user session

## Files in This Repository

### Scripts

- `scan_unclaimed_property.py` - Original API-based scanner (blocked by CloudFront)
- `scan_unclaimed_property_selenium.py` - Selenium-based scanner (blocked by bot protection)
- `test_selenium.py` - Selenium setup test script

### Data

- `data/unclaimed_property.json` - Output file for search results (currently empty)

### Documentation

- `README.md` - This file

## Data Format

When properties are found, they should be recorded in the following JSON format:

```json
{
  "scan_metadata": {
    "scan_date": "2026-01-07T10:00:00",
    "total_properties": 0,
    "high_value_count": 0,
    "min_value_threshold": 1000,
    "alert_threshold": 10000,
    "zip_codes_scanned": "60601-60699 (Cook County)"
  },
  "high_value_alerts": [],
  "all_properties": [
    {
      "property_owner_name": "John Doe",
      "dollar_amount": 5000.00,
      "property_type": "Cash",
      "claim_url": "https://icash.illinoistreasurer.gov/app/claim-search?propertyId=12345",
      "property_id": "12345",
      "zip_code": "60601",
      "scan_date": "2026-01-07T10:00:00"
    }
  ]
}
```

## High-Value Alert Threshold

Properties exceeding **$10,000** should be flagged as high-value alerts and prominently displayed.

## Legal and Ethical Considerations

### Compliance

- This tool is designed for legitimate research and public benefit purposes
- Unclaimed property data is public information
- Respect the website's terms of service and rate limits
- Do not use for unauthorized commercial purposes

### Privacy

- Unclaimed property owner names are public records
- Handle data responsibly and securely
- Do not share or publish personal information beyond what's publicly available

## Future Enhancements

1. **Browser Extension**: Create a Chrome/Firefox extension for user-assisted searching
2. **FOIA Automation**: Automate FOIA request submission and tracking
3. **Multi-State Expansion**: Extend to other state unclaimed property databases
4. **Data Analysis**: Add analytics and visualization of unclaimed property patterns
5. **Notification System**: Alert system for newly reported high-value properties

## Technical Requirements

### Python Dependencies

```bash
pip install selenium
```

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get install chromium-browser chromium-chromedriver

# Or use standalone Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

## Contributing

To contribute to this project:

1. Document any successful search strategies
2. Share findings in the data directory
3. Propose alternative technical approaches
4. Improve documentation and scripts

## Resources

- **Illinois State Treasurer**: https://illinoistreasurer.gov
- **ICash Search**: https://icash.illinoistreasurer.gov/app/claim-search
- **FOIA Portal**: https://illinoistreasurer.gov/foia/
- **MissingMoney.com**: https://www.missingmoney.com
- **NAUPA**: https://www.unclaimed.org

## Contact

For questions about this project or to report findings, please use the repository's issue tracker.

## License

This project is for research and public benefit purposes. Use responsibly and in compliance with applicable laws and terms of service.
