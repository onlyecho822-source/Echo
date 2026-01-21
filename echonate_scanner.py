#!/usr/bin/env python3
"""
EchoNate Autonomous Settlement Scanner
Identity: EchoNate <echonate@phoenix.ai>
Mission: Discover and track class action settlement opportunities
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import hashlib
import os

class EchoNateScanner:
    def __init__(self):
        self.identity = "EchoNate"
        self.email = "echonate@phoenix.ai"
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.settlements = []
        self.sources = [
            "https://www.classaction.org/settlements",
            "https://topclassactions.com/lawsuit-settlements/open-class-action-settlements/"
        ]
        self.headers = {
            'User-Agent': 'EchoNate/1.0 (Settlement Intelligence Scanner)'
        }
    
    def scan_classaction_org(self):
        """Scan classaction.org for settlements"""
        print(f"[EchoNate] Scanning classaction.org...")
        try:
            url = "https://www.classaction.org/settlements"
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                # Extract settlement cards
                cards = soup.find_all('div', class_=re.compile(r'settlement|card'))
                print(f"[EchoNate] Found {len(cards)} potential settlements on classaction.org")
                for card in cards[:20]:  # Limit to first 20
                    title = card.find(['h2', 'h3', 'a'])
                    if title:
                        self.settlements.append({
                            "source": "classaction.org",
                            "title": title.get_text(strip=True)[:200],
                            "scanned_at": self.timestamp
                        })
        except Exception as e:
            print(f"[EchoNate] Error scanning classaction.org: {e}")
    
    def scan_topclassactions(self):
        """Scan topclassactions.com for settlements"""
        print(f"[EchoNate] Scanning topclassactions.com...")
        try:
            url = "https://topclassactions.com/lawsuit-settlements/open-class-action-settlements/"
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                articles = soup.find_all('article')
                print(f"[EchoNate] Found {len(articles)} potential settlements on topclassactions.com")
                for article in articles[:20]:
                    title = article.find(['h2', 'h3', 'a'])
                    if title:
                        self.settlements.append({
                            "source": "topclassactions.com",
                            "title": title.get_text(strip=True)[:200],
                            "scanned_at": self.timestamp
                        })
        except Exception as e:
            print(f"[EchoNate] Error scanning topclassactions.com: {e}")
    
    def generate_report(self):
        """Generate EchoNate scan report"""
        report = {
            "agent": {
                "name": self.identity,
                "email": self.email,
                "version": "1.0.0"
            },
            "scan": {
                "timestamp": self.timestamp,
                "sources_scanned": len(self.sources),
                "settlements_found": len(self.settlements)
            },
            "settlements": self.settlements,
            "signature": hashlib.sha256(
                f"{self.identity}:{self.timestamp}:{len(self.settlements)}".encode()
            ).hexdigest()[:16]
        }
        return report
    
    def run(self):
        """Execute full scan"""
        print(f"═══════════════════════════════════════════════════════════════")
        print(f"  EchoNate Settlement Scanner")
        print(f"  Timestamp: {self.timestamp}")
        print(f"═══════════════════════════════════════════════════════════════")
        
        self.scan_classaction_org()
        self.scan_topclassactions()
        
        report = self.generate_report()
        
        # Save report
        os.makedirs("echonate/data/settlements", exist_ok=True)
        scan_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        with open(f"echonate/data/settlements/scan_{scan_date}.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[EchoNate] Scan complete: {len(self.settlements)} settlements found")
        print(f"[EchoNate] Report saved to echonate/data/settlements/scan_{scan_date}.json")
        
        return report

if __name__ == "__main__":
    scanner = EchoNateScanner()
    report = scanner.run()
    
    # Output for GitHub Actions
    print(f"\n::set-output name=settlements_found::{len(report['settlements'])}")
