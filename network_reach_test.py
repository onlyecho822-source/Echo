#!/usr/bin/env python3
"""
Echo Network Reach Test - Financial Sector & Global Nexus
Live test of API connectivity and global reach
"""

import requests
import time
import json
import socket
import ssl
import concurrent.futures
from datetime import datetime
from urllib.parse import urlparse
import pandas as pd
from typing import Dict, List, Tuple
import sys

class NetworkReachTest:
    def __init__(self):
        self.results = {
            "test_date": datetime.utcnow().isoformat(),
            "financial_sector": [],
            "global_nexus": [],
            "statistics": {},
            "raw_responses": {}
        }
        
        # Financial Sector APIs - Real production endpoints
        self.financial_apis = {
            # Payment Processors
            "stripe_api": "https://api.stripe.com/healthcheck",
            "paypal_api": "https://www.paypal.com",
            "square_api": "https://squareup.com",
            
            # Banking APIs
            "plaid_sandbox": "https://plaid.com",
            "yahoo_finance": "https://query1.finance.yahoo.com/v8/finance/chart/AAPL",
            
            # Crypto Exchanges
            "coinbase_api": "https://api.coinbase.com/v2/time",
            "binance_api": "https://api.binance.com/api/v3/ping",
            "kraken_api": "https://api.kraken.com/0/public/SystemStatus",
            
            # Stock Markets
            "nasdaq_api": "https://www.nasdaq.com",
            "nyse_health": "https://www.nyse.com",
            
            # Government Financial
            "sec_edgar": "https://www.sec.gov/files/company_tickers.json",
            "federal_reserve": "https://www.federalreserve.gov",
        }
        
        # Global Nexus - Critical internet infrastructure
        self.global_nexus = {
            # DNS Infrastructure
            "google_dns": "https://dns.google/resolve?name=google.com&type=A",
            "cloudflare_dns": "https://cloudflare-dns.com/dns-query?name=cloudflare.com&type=A",
            
            # CDN Networks
            "cloudflare_api": "https://www.cloudflare.com",
            "fastly_health": "https://www.fastly.com",
            
            # Cloud Providers
            "aws_health": "https://status.aws.amazon.com",
            "azure_status": "https://status.azure.com",
            "google_cloud": "https://status.cloud.google.com",
            
            # Social/Platform
            "facebook_api": "https://www.facebook.com",
            "reddit_api": "https://www.reddit.com/r/all/.json?limit=1",
            "github_api": "https://api.github.com/zen",
            
            # Search Engines
            "google_search": "https://www.google.com",
            "bing_api": "https://www.bing.com",
            "duckduckgo": "https://api.duckduckgo.com/?q=test&format=json",
            
            # Messaging
            "slack_api": "https://slack.com",
            "discord_api": "https://discord.com/api/v9/gateway",
            
            # E-commerce
            "amazon_api": "https://www.amazon.com",
            "shopify_api": "https://www.shopify.com",
            
            # Mapping
            "google_maps": "https://maps.googleapis.com",
            "openstreetmap": "https://api.openstreetmap.org/api/0.6/capabilities",
        }

    def test_endpoint(self, name: str, url: str, category: str) -> Dict:
        """Test a single endpoint with comprehensive metrics"""
        result = {
            "name": name,
            "url": url,
            "category": category,
            "timestamp": datetime.utcnow().isoformat(),
            "success": False,
            "status_code": None,
            "response_time_ms": None,
            "content_length": 0,
            "error": None,
            "geo_info": None
        }
        
        try:
            # HTTP Request with headers
            headers = {
                'User-Agent': 'EchoNetworkTest/1.0',
                'Accept': 'application/json,text/html',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            start_request = time.time()
            response = requests.get(
                url, 
                headers=headers,
                timeout=10,  # 10 second timeout
                allow_redirects=True,
                verify=True  # Verify SSL
            )
            result["response_time_ms"] = (time.time() - start_request) * 1000
            result["status_code"] = response.status_code
            result["content_length"] = len(response.content)
            
            # Success criteria
            if 200 <= response.status_code < 400:
                result["success"] = True
                
                # Try to get geo info from response headers
                result["geo_info"] = {
                    "server": response.headers.get('Server', 'Unknown'),
                    "date": response.headers.get('Date', 'Unknown'),
                    "content_type": response.headers.get('Content-Type', 'Unknown')
                }
                
        except Exception as e:
            result["error"] = str(e)
            
        return result

    def run_financial_sector_test(self):
        """Test all financial sector APIs"""
        print("\n" + "="*60)
        print("FINANCIAL SECTOR REACH TEST")
        print("="*60)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_api = {
                executor.submit(self.test_endpoint, name, url, "financial"): name
                for name, url in self.financial_apis.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_api):
                name = future_to_api[future]
                try:
                    result = future.result(timeout=15)
                    self.results["financial_sector"].append(result)
                    
                    status = "✅" if result["success"] else "❌"
                    time_str = f"{result['response_time_ms']:.0f}ms" if result['response_time_ms'] else "Timeout"
                    print(f"{status} {name:20} | Status: {result['status_code'] or 'N/A':4} | Time: {time_str:8}")
                    
                except Exception as e:
                    print(f"❌ {name:20} | Error: {str(e)[:40]}")

    def run_global_nexus_test(self):
        """Test global internet infrastructure"""
        print("\n" + "="*60)
        print("GLOBAL NEXUS REACH TEST")
        print("="*60)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_api = {
                executor.submit(self.test_endpoint, name, url, "global"): name
                for name, url in self.global_nexus.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_api):
                name = future_to_api[future]
                try:
                    result = future.result(timeout=15)
                    self.results["global_nexus"].append(result)
                    
                    status = "✅" if result["success"] else "❌"
                    time_str = f"{result['response_time_ms']:.0f}ms" if result['response_time_ms'] else "Timeout"
                    print(f"{status} {name:25} | Status: {result['status_code'] or 'N/A':4} | Time: {time_str:8}")
                    
                except Exception as e:
                    print(f"❌ {name:25} | Error: {str(e)[:30]}")

    def calculate_statistics(self):
        """Calculate comprehensive statistics"""
        all_results = self.results["financial_sector"] + self.results["global_nexus"]
        
        successful = [r for r in all_results if r["success"]]
        failed = [r for r in all_results if not r["success"]]
        
        response_times = [r["response_time_ms"] for r in successful if r["response_time_ms"]]
        
        self.results["statistics"] = {
            "total_endpoints_tested": len(all_results),
            "financial_endpoints": len(self.financial_apis),
            "global_endpoints": len(self.global_nexus),
            "successful_connections": len(successful),
            "failed_connections": len(failed),
            "success_rate": (len(successful) / len(all_results)) * 100 if all_results else 0,
            "avg_response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "total_data_received_bytes": sum([r.get("content_length", 0) for r in all_results]),
            "test_duration_seconds": None  # Will be set after complete run
        }

    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE NETWORK REACH REPORT")
        print("="*60)
        
        stats = self.results["statistics"]
        
        print(f"\n📊 SUMMARY STATISTICS")
        print(f"   Total endpoints tested: {stats['total_endpoints_tested']}")
        print(f"   Successful connections: {stats['successful_connections']}")
        print(f"   Failed connections: {stats['failed_connections']}")
        print(f"   Overall success rate: {stats['success_rate']:.1f}%")
        print(f"   Average response time: {stats['avg_response_time_ms']:.0f}ms")
        print(f"   Total data received: {stats['total_data_received_bytes']:,} bytes")
        
        print(f"\n🏦 FINANCIAL SECTOR ({len(self.results['financial_sector'])} endpoints)")
        financial_success = len([r for r in self.results["financial_sector"] if r["success"]])
        print(f"   Success rate: {(financial_success/len(self.results['financial_sector'])*100):.1f}%")
        
        print(f"\n🌐 GLOBAL NEXUS ({len(self.results['global_nexus'])} endpoints)")
        global_success = len([r for r in self.results["global_nexus"] if r["success"]])
        print(f"   Success rate: {(global_success/len(self.results['global_nexus'])*100):.1f}%")
        
        print(f"\n📈 PERFORMANCE ANALYSIS")
        print(f"   Fastest response: {stats['min_response_time_ms']:.0f}ms")
        print(f"   Slowest response: {stats['max_response_time_ms']:.0f}ms")

    def save_results(self):
        """Save detailed results to file"""
        filename = f"network_reach_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📁 Detailed results saved to: {filename}")
        
        # Also create CSV summary
        df_data = []
        for result in self.results["financial_sector"] + self.results["global_nexus"]:
            df_data.append({
                "Category": result["category"],
                "Name": result["name"],
                "URL": result["url"],
                "Success": result["success"],
                "Status Code": result["status_code"],
                "Response Time (ms)": result["response_time_ms"],
                "Error": result.get("error", "")
            })
        
        df = pd.DataFrame(df_data)
        csv_filename = filename.replace('.json', '.csv')
        df.to_csv(csv_filename, index=False)
        print(f"📊 CSV summary saved to: {csv_filename}")
        
        return filename

def main():
    """Run the complete network reach test"""
    print("🔍 ECHO NETWORK REACH VALIDATION TEST")
    print("Testing connectivity to financial sector and global infrastructure")
    print(f"Start time: {datetime.utcnow().isoformat()}")
    
    try:
        tester = NetworkReachTest()
        start_time = time.time()
        
        # Run tests
        tester.run_financial_sector_test()
        tester.run_global_nexus_test()
        
        # Calculate statistics
        tester.calculate_statistics()
        tester.results["statistics"]["test_duration_seconds"] = time.time() - start_time
        
        # Generate report
        tester.generate_report()
        
        # Save results
        filename = tester.save_results()
        
        print(f"\n✅ Test completed in {tester.results['statistics']['test_duration_seconds']:.1f} seconds")
        
        # Return results for Echo belief creation
        return tester.results
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
