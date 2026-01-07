#!/usr/bin/env python3
"""
GSA Auctions Scanner
Scans GSAAuctions.gov for newly listed items with:
- Estimated value > $1000
- Current bid < 50% of estimated value
- Focus: electronics, vehicles, equipment
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Optional
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class GSAAuctionScanner:
    def __init__(self):
        self.base_url = "https://gsaauctions.gov"
        
        # Setup Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def __del__(self):
        """Cleanup browser on exit"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def parse_currency(self, text: str) -> Optional[float]:
        """Parse currency string to float"""
        if not text:
            return None
        # Remove currency symbols, commas, and whitespace
        cleaned = re.sub(r'[^\d.]', '', text.strip())
        try:
            return float(cleaned) if cleaned else None
        except ValueError:
            return None
    
    def extract_item_from_card(self, element) -> Optional[Dict]:
        """Extract item information from a listing card element"""
        try:
            item_data = {}
            
            # Try to extract item description/title
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, "h3, h4, .title, .item-title, .auction-title")
                item_data['description'] = title_elem.text.strip()[:500]
            except NoSuchElementException:
                item_data['description'] = "Description not available"
            
            # Try to extract current bid
            try:
                bid_elem = element.find_element(By.XPATH, ".//*[contains(text(), 'Current Bid') or contains(text(), 'Bid') or contains(text(), 'Price')]")
                bid_text = bid_elem.text
                item_data['current_bid'] = self.parse_currency(bid_text)
            except NoSuchElementException:
                item_data['current_bid'] = 0.0
            
            # Try to extract estimated/fair market value
            try:
                value_elem = element.find_element(By.XPATH, ".//*[contains(text(), 'Fair Market Value') or contains(text(), 'Estimated') or contains(text(), 'Retail')]")
                value_text = value_elem.text
                item_data['estimated_value'] = self.parse_currency(value_text)
            except NoSuchElementException:
                item_data['estimated_value'] = None
            
            # Try to extract auction end time
            try:
                end_elem = element.find_element(By.XPATH, ".//*[contains(text(), 'End') or contains(text(), 'Closing')]")
                item_data['auction_end_time'] = end_elem.text.strip()
            except NoSuchElementException:
                item_data['auction_end_time'] = "Not specified"
            
            # Try to extract location
            try:
                loc_elem = element.find_element(By.XPATH, ".//*[contains(text(), 'Location') or contains(@class, 'location')]")
                item_data['location'] = loc_elem.text.strip()
            except NoSuchElementException:
                item_data['location'] = "Not specified"
            
            # Try to extract item URL
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "a[href*='auction'], a[href*='item']")
                href = link_elem.get_attribute('href')
                item_data['item_url'] = href if href.startswith('http') else self.base_url + href
            except NoSuchElementException:
                item_data['item_url'] = "Not available"
            
            return item_data if item_data.get('estimated_value') else None
            
        except Exception as e:
            print(f"  Error extracting item: {e}")
            return None
    
    def scan_category(self, category: str, search_url: str) -> List[Dict]:
        """Scan a specific category for items matching criteria"""
        items = []
        
        try:
            print(f"Scanning {category}...")
            self.driver.get(search_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Try to find auction item cards/listings
            # Common selectors for auction items
            selectors = [
                ".auction-item",
                ".item-card",
                ".listing-item",
                "[class*='auction']",
                "[class*='item-']",
                ".card"
            ]
            
            elements = []
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"  Found {len(elements)} elements with selector: {selector}")
                        break
                except:
                    continue
            
            if not elements:
                print(f"  No auction items found for {category}")
                return items
            
            # Process each item
            for idx, element in enumerate(elements[:30]):  # Limit to first 30
                try:
                    item_data = self.extract_item_from_card(element)
                    
                    if item_data:
                        item_data['category'] = category
                        
                        # Check if item meets criteria
                        estimated_value = item_data.get('estimated_value')
                        current_bid = item_data.get('current_bid', 0)
                        
                        if estimated_value and estimated_value > 1000:
                            if current_bid < (estimated_value * 0.5):
                                items.append(item_data)
                                print(f"  ✓ Found matching item: ${current_bid} / ${estimated_value}")
                
                except Exception as e:
                    print(f"  Error processing item {idx}: {e}")
                    continue
                
        except Exception as e:
            print(f"  Error scanning {category}: {e}")
        
        return items
    
    def scan_all_categories(self) -> List[Dict]:
        """Scan all target categories"""
        all_items = []
        
        # Updated category URLs based on actual site structure
        categories = {
            'electronics': f"{self.base_url}/gsaauctions/aucitsrh/?sl=ELEC",
            'vehicles': f"{self.base_url}/gsaauctions/aucitsrh/?sl=VEHI",
            'equipment': f"{self.base_url}/gsaauctions/aucitsrh/?sl=EQUI"
        }
        
        # First, try to navigate to main page and explore structure
        try:
            print("Navigating to GSA Auctions homepage...")
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Save page source for debugging
            with open('/home/ubuntu/Echo/art-of-proof/phoenix/data/gsa_page_source.html', 'w') as f:
                f.write(self.driver.page_source)
            print("  Page source saved for debugging")
            
        except Exception as e:
            print(f"Error accessing homepage: {e}")
        
        # Scan each category
        for category, url in categories.items():
            items = self.scan_category(category, url)
            all_items.extend(items)
            time.sleep(2)  # Be respectful to the server
        
        return all_items
    
    def save_results(self, items: List[Dict], output_path: str):
        """Save results to JSON file"""
        output_data = {
            'scan_date': datetime.now().isoformat(),
            'total_items': len(items),
            'criteria': {
                'min_estimated_value': 1000,
                'max_bid_percentage': 50,
                'categories': ['electronics', 'vehicles', 'equipment']
            },
            'items': items
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n✓ Saved {len(items)} items to {output_path}")


def main():
    print("=" * 60)
    print("GSA AUCTIONS SCANNER")
    print("=" * 60)
    print("Criteria:")
    print("  • Estimated value > $1,000")
    print("  • Current bid < 50% of estimated value")
    print("  • Categories: Electronics, Vehicles, Equipment")
    print("=" * 60)
    print()
    
    scanner = None
    try:
        scanner = GSAAuctionScanner()
        items = scanner.scan_all_categories()
        
        output_path = "/home/ubuntu/Echo/art-of-proof/phoenix/data/gsa_auctions.json"
        scanner.save_results(items, output_path)
        
        print()
        print("=" * 60)
        print(f"SCAN COMPLETE: Found {len(items)} matching items")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during scan: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scanner:
            del scanner


if __name__ == "__main__":
    main()
