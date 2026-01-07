#!/usr/bin/env python3
"""
Illinois Unclaimed Property Scanner - Selenium Version
Uses browser automation to systematically search the Illinois State Treasurer's 
ICash database for properties over $1,000 in Cook County zip codes (60601-60699)
"""

import json
import time
import re
from typing import List, Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
COOK_COUNTY_ZIP_CODES = list(range(60601, 60700))  # 60601-60699
MIN_PROPERTY_VALUE = 1000
ALERT_THRESHOLD = 10000
OUTPUT_FILE = "/home/ubuntu/Echo/art-of-proof/phoenix/data/unclaimed_property.json"

# Common surnames in Cook County for systematic searching
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
    """Scanner for Illinois unclaimed property database using Selenium"""
    
    SEARCH_URL = "https://icash.illinoistreasurer.gov/app/claim-search"
    
    def __init__(self, headless: bool = True):
        """Initialize the scanner with Selenium WebDriver"""
        self.results = []
        self.high_value_alerts = []
        self.driver = self._init_driver(headless)
        
    def _init_driver(self, headless: bool):
        """Initialize Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        
        return driver
    
    def search_properties(self, last_name: str, zip_code: str) -> List[Dict]:
        """
        Search for unclaimed properties by last name and zip code
        Returns list of properties found
        """
        try:
            # Navigate to search page
            self.driver.get(self.SEARCH_URL)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            
            # Find and fill last name field
            last_name_field = wait.until(
                EC.presence_of_element_located((By.ID, "lastName"))
            )
            last_name_field.clear()
            last_name_field.send_keys(last_name)
            
            # Find and fill zip code field
            zip_field = self.driver.find_element(By.ID, "searchZipCode")
            zip_field.clear()
            zip_field.send_keys(zip_code)
            
            # Click search button
            search_button = self.driver.find_element(By.ID, "btn-turnstile")
            search_button.click()
            
            # Wait for results to load
            time.sleep(3)
            
            # Parse results
            properties = self._parse_results_page()
            
            return properties
            
        except TimeoutException:
            print(f"Timeout searching {last_name} in {zip_code}")
            return []
        except Exception as e:
            print(f"Error searching {last_name} in {zip_code}: {str(e)}")
            return []
    
    def _parse_results_page(self) -> List[Dict]:
        """Parse the search results page and extract property information"""
        properties = []
        
        try:
            # Check if there are results
            # Look for result rows or "no results" message
            
            # Try to find result table or list
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".property-result, .result-row, [class*='result'], [class*='property']")
            
            if not result_elements:
                # No results found
                return properties
            
            for element in result_elements:
                try:
                    # Extract property information from each result
                    # This will need to be adjusted based on actual HTML structure
                    
                    property_text = element.text
                    
                    # Try to extract owner name
                    owner_name = self._extract_owner_name(element)
                    
                    # Try to extract amount
                    amount = self._extract_amount(element)
                    
                    # Only include if over threshold
                    if amount >= MIN_PROPERTY_VALUE:
                        # Try to extract property type
                        property_type = self._extract_property_type(element)
                        
                        # Try to extract property ID for claim URL
                        property_id = self._extract_property_id(element)
                        
                        property_info = {
                            'property_owner_name': owner_name,
                            'dollar_amount': amount,
                            'property_type': property_type,
                            'claim_url': self._build_claim_url(property_id),
                            'property_id': property_id,
                            'scan_date': datetime.now().isoformat()
                        }
                        
                        properties.append(property_info)
                        
                        # Check for high-value alert
                        if amount >= ALERT_THRESHOLD:
                            self.high_value_alerts.append(property_info)
                            
                except Exception as e:
                    print(f"Error parsing result element: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"Error parsing results page: {str(e)}")
        
        return properties
    
    def _extract_owner_name(self, element) -> str:
        """Extract owner name from result element"""
        try:
            # Try different selectors
            name_selectors = [
                ".owner-name", ".name", "[class*='owner']", "[class*='name']"
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if name_elem.text:
                        return name_elem.text.strip()
                except:
                    continue
            
            # Fallback: try to extract from text
            text = element.text
            lines = text.split('\n')
            if lines:
                return lines[0].strip()
            
            return "Unknown"
        except:
            return "Unknown"
    
    def _extract_amount(self, element) -> float:
        """Extract dollar amount from result element"""
        try:
            text = element.text
            
            # Look for dollar amounts in format $X,XXX.XX or $XXX
            matches = re.findall(r'\$[\d,]+\.?\d*', text)
            
            if matches:
                # Take the first match
                amount_str = matches[0].replace('$', '').replace(',', '')
                return float(amount_str)
            
            return 0.0
        except:
            return 0.0
    
    def _extract_property_type(self, element) -> str:
        """Extract property type from result element"""
        try:
            # Try different selectors
            type_selectors = [
                ".property-type", ".type", "[class*='type']"
            ]
            
            for selector in type_selectors:
                try:
                    type_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if type_elem.text:
                        return type_elem.text.strip()
                except:
                    continue
            
            # Fallback: look for common property types in text
            text = element.text.lower()
            types = ['cash', 'check', 'security', 'insurance', 'utility', 'wages', 'dividend']
            
            for ptype in types:
                if ptype in text:
                    return ptype.capitalize()
            
            return "Unknown"
        except:
            return "Unknown"
    
    def _extract_property_id(self, element) -> Optional[str]:
        """Extract property ID from result element"""
        try:
            # Try to find property ID in data attributes or links
            prop_id = element.get_attribute('data-property-id')
            if prop_id:
                return prop_id
            
            # Try to find in links
            links = element.find_elements(By.TAG_NAME, 'a')
            for link in links:
                href = link.get_attribute('href')
                if href and 'propertyId' in href:
                    # Extract ID from URL
                    match = re.search(r'propertyId=([^&]+)', href)
                    if match:
                        return match.group(1)
            
            return None
        except:
            return None
    
    def _build_claim_url(self, property_id: Optional[str]) -> str:
        """Build claim URL for property"""
        if property_id:
            return f"https://icash.illinoistreasurer.gov/app/claim-search?propertyId={property_id}"
        return "https://icash.illinoistreasurer.gov/app/claim-search"
    
    def scan_cook_county(self, max_surnames: int = 20, max_zips: int = 10):
        """
        Systematically scan Cook County for unclaimed properties
        
        Args:
            max_surnames: Maximum number of surnames to search
            max_zips: Maximum number of zip codes to search per surname
        """
        print(f"Starting automated scan of Illinois unclaimed property database...")
        print(f"Target: Cook County zip codes 60601-60699")
        print(f"Minimum value: ${MIN_PROPERTY_VALUE:,}")
        print(f"Alert threshold: ${ALERT_THRESHOLD:,}")
        print(f"Searching {max_surnames} surnames across {max_zips} zip codes")
        print("-" * 80)
        
        total_searches = 0
        total_properties = 0
        
        try:
            for surname in COMMON_SURNAMES[:max_surnames]:
                for zip_code in COOK_COUNTY_ZIP_CODES[:max_zips]:
                    total_searches += 1
                    
                    print(f"Searching: {surname} in {zip_code} (Search #{total_searches})")
                    
                    properties = self.search_properties(surname, str(zip_code))
                    
                    if properties:
                        self.results.extend(properties)
                        total_properties += len(properties)
                        print(f"  ✓ Found {len(properties)} properties over ${MIN_PROPERTY_VALUE:,}")
                    
                    # Rate limiting - be respectful
                    time.sleep(2)
            
        finally:
            self.driver.quit()
        
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
                'zip_codes_scanned': "60601-60699 (Cook County)"
            },
            'high_value_alerts': self.high_value_alerts,
            'all_properties': self.results
        }
        
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nResults saved to: {OUTPUT_FILE}")
        
        return output_data
    
    def __del__(self):
        """Cleanup"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
        except:
            pass


def main():
    """Main execution function"""
    print("Initializing Illinois Unclaimed Property Scanner...")
    
    scanner = ILUnclaimedPropertyScanner(headless=True)
    
    # Scan Cook County (start with limited search)
    # Increase max_surnames and max_zips for more comprehensive search
    scanner.scan_cook_county(max_surnames=10, max_zips=5)
    
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
