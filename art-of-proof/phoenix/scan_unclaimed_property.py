#!/usr/bin/env python3
"""
Illinois Unclaimed Property Scanner
Systematically searches the Illinois State Treasurer's ICash database
for properties over $1,000 in Cook County zip codes (60601-60699)
"""

import requests
import json
import time
from typing import List, Dict, Optional
from datetime import datetime

# Configuration
COOK_COUNTY_ZIP_CODES = list(range(60601, 60700))  # 60601-60699
MIN_PROPERTY_VALUE = 1000
ALERT_THRESHOLD = 10000
OUTPUT_FILE = "/home/ubuntu/Echo/art-of-proof/phoenix/data/unclaimed_property.json"

# Common surnames in Cook County for systematic searching
# Using most common surnames in Chicago/Cook County area
COMMON_SURNAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter",
    "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz",
    "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy", "Cook",
    "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey", "Reed",
    "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson", "Brooks",
    "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes", "Price",
    "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster", "Jimenez"
]


class ILUnclaimedPropertyScanner:
    """Scanner for Illinois unclaimed property database"""
    
    BASE_URL = "https://icash.illinoistreasurer.gov"
    SEARCH_API = f"{BASE_URL}/api/search"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.results = []
        self.high_value_alerts = []
        
    def search_properties(self, last_name: str, zip_code: str) -> List[Dict]:
        """
        Search for unclaimed properties by last name and zip code
        Returns list of properties found
        """
        try:
            # Try API endpoint first
            payload = {
                "lastName": last_name,
                "zipCode": zip_code
            }
            
            response = self.session.post(self.SEARCH_API, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_search_results(data)
            else:
                print(f"API search failed for {last_name} in {zip_code}: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error searching {last_name} in {zip_code}: {str(e)}")
            return []
    
    def _parse_search_results(self, data: Dict) -> List[Dict]:
        """Parse search results and extract property information"""
        properties = []
        
        # Handle different possible response formats
        results = data.get('results', data.get('properties', []))
        
        for item in results:
            try:
                # Extract property value
                amount_str = item.get('amount', item.get('value', '0'))
                amount = self._parse_amount(amount_str)
                
                # Only include properties over threshold
                if amount >= MIN_PROPERTY_VALUE:
                    property_info = {
                        'property_owner_name': item.get('ownerName', item.get('name', 'Unknown')),
                        'dollar_amount': amount,
                        'property_type': item.get('propertyType', item.get('type', 'Unknown')),
                        'claim_url': self._build_claim_url(item.get('propertyId', item.get('id'))),
                        'property_id': item.get('propertyId', item.get('id')),
                        'zip_code': item.get('zipCode', item.get('zip', '')),
                        'city': item.get('city', ''),
                        'last_reported_address': item.get('address', ''),
                        'holder_name': item.get('holderName', ''),
                        'date_reported': item.get('dateReported', ''),
                        'scan_date': datetime.now().isoformat()
                    }
                    
                    properties.append(property_info)
                    
                    # Check for high-value alert
                    if amount >= ALERT_THRESHOLD:
                        self.high_value_alerts.append(property_info)
                        
            except Exception as e:
                print(f"Error parsing property: {str(e)}")
                continue
        
        return properties
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        if isinstance(amount_str, (int, float)):
            return float(amount_str)
        
        # Remove currency symbols and commas
        amount_str = str(amount_str).replace('$', '').replace(',', '').strip()
        
        try:
            return float(amount_str)
        except:
            return 0.0
    
    def _build_claim_url(self, property_id: Optional[str]) -> str:
        """Build claim URL for property"""
        if property_id:
            return f"{self.BASE_URL}/app/claim-search?propertyId={property_id}"
        return f"{self.BASE_URL}/app/claim-search"
    
    def scan_cook_county(self, max_surnames: int = 20, max_zips: int = 10):
        """
        Systematically scan Cook County for unclaimed properties
        
        Args:
            max_surnames: Maximum number of surnames to search (for testing/limiting)
            max_zips: Maximum number of zip codes to search per surname
        """
        print(f"Starting scan of Illinois unclaimed property database...")
        print(f"Target: Cook County zip codes 60601-60699")
        print(f"Minimum value: ${MIN_PROPERTY_VALUE:,}")
        print(f"Alert threshold: ${ALERT_THRESHOLD:,}")
        print(f"Searching {max_surnames} surnames across {max_zips} zip codes")
        print("-" * 80)
        
        total_searches = 0
        total_properties = 0
        
        for surname in COMMON_SURNAMES[:max_surnames]:
            for zip_code in COOK_COUNTY_ZIP_CODES[:max_zips]:
                total_searches += 1
                
                print(f"Searching: {surname} in {zip_code} (Search #{total_searches})")
                
                properties = self.search_properties(surname, str(zip_code))
                
                if properties:
                    self.results.extend(properties)
                    total_properties += len(properties)
                    print(f"  ✓ Found {len(properties)} properties over ${MIN_PROPERTY_VALUE:,}")
                
                # Rate limiting - be respectful to the server
                time.sleep(1)
        
        print("-" * 80)
        print(f"Scan complete!")
        print(f"Total searches: {total_searches}")
        print(f"Total properties found: {total_properties}")
        print(f"High-value alerts (>${ALERT_THRESHOLD:,}): {len(self.high_value_alerts)}")
    
    def save_results(self):
        """Save results to JSON file"""
        output_data = {
            'scan_metadata': {
                'scan_date': datetime.now().isoformat(),
                'total_properties': len(self.results),
                'high_value_count': len(self.high_value_alerts),
                'min_value_threshold': MIN_PROPERTY_VALUE,
                'alert_threshold': ALERT_THRESHOLD,
                'zip_codes_scanned': f"60601-60699 (Cook County)"
            },
            'high_value_alerts': self.high_value_alerts,
            'all_properties': self.results
        }
        
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nResults saved to: {OUTPUT_FILE}")
        
        return output_data


def main():
    """Main execution function"""
    scanner = ILUnclaimedPropertyScanner()
    
    # Scan Cook County (start with limited search for testing)
    # Increase max_surnames and max_zips for more comprehensive search
    scanner.scan_cook_county(max_surnames=30, max_zips=20)
    
    # Save results
    results = scanner.save_results()
    
    # Display high-value alerts
    if scanner.high_value_alerts:
        print("\n" + "=" * 80)
        print(f"⚠️  HIGH VALUE ALERT: {len(scanner.high_value_alerts)} properties over ${ALERT_THRESHOLD:,} found!")
        print("=" * 80)
        
        for prop in scanner.high_value_alerts:
            print(f"\nOwner: {prop['property_owner_name']}")
            print(f"Amount: ${prop['dollar_amount']:,.2f}")
            print(f"Type: {prop['property_type']}")
            print(f"Claim URL: {prop['claim_url']}")
            print("-" * 80)
    else:
        print(f"\nNo properties over ${ALERT_THRESHOLD:,} found in this scan.")
    
    return results


if __name__ == "__main__":
    main()
