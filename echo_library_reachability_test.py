#!/usr/bin/env python3
"""
Echo Library - Network Reachability Test
Vatican-level institutional preservation standard

Comprehensive network probe across finance sector and global nexus.
Each test result becomes an immutable, hash-sealed Data Pod.
"""

import requests
import time
import json
import hashlib
import concurrent.futures
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
import sys

from data_pod_factory import DataPodFactory, DataPodCollection

class EchoLibraryReachabilityTest:
    def __init__(self, agent_id: str = "echo_probe_01", location: str = "sandbox"):
        self.agent_id = agent_id
        self.location = location
        self.pod_collection = DataPodCollection()
        self.start_time = datetime.now(timezone.utc)
        
        # Calculate engine hash (hash of this script)
        with open(__file__, 'r') as f:
            script_content = f.read()
        self.engine_hash = DataPodFactory.create_engine_hash(script_content)
        
        print(f"🔍 Echo Library Reachability Test")
        print(f"   Agent ID: {self.agent_id}")
        print(f"   Location: {self.location}")
        print(f"   Engine Hash: {self.engine_hash[:16]}...")
        print(f"   Start Time: {self.start_time.isoformat()}")
        
    def test_endpoint(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Test a single endpoint and return raw results.
        
        Args:
            url: URL to test
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with test results
        """
        result = {
            'url': url,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'success': False,
            'status_code': None,
            'latency_ms': None,
            'payload_data': b'',
            'error': None
        }
        
        start_time = time.time()
        
        try:
            headers = {
                'User-Agent': 'Echo-Library-Probe/1.0',
                'Accept': 'application/json,text/html'
            }
            
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True,
                verify=True
            )
            
            result['status_code'] = response.status_code
            result['latency_ms'] = round((time.time() - start_time) * 1000, 2)
            result['payload_data'] = response.content[:10000]  # First 10KB
            
            if 200 <= response.status_code < 400:
                result['success'] = True
            
        except requests.exceptions.Timeout:
            result['error'] = 'timeout'
            result['latency_ms'] = timeout * 1000
        except requests.exceptions.ConnectionError as e:
            result['error'] = f'connection_error'
            result['latency_ms'] = round((time.time() - start_time) * 1000, 2)
        except Exception as e:
            result['error'] = f'unexpected_error: {type(e).__name__}'
            result['latency_ms'] = round((time.time() - start_time) * 1000, 2)
        
        return result
    
    def create_data_pod_from_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert test result into a hash-sealed Data Pod.
        
        Args:
            result: Test result dictionary
            
        Returns:
            Data Pod dictionary
        """
        # Parse URL to get protocol and port
        from urllib.parse import urlparse
        parsed = urlparse(result['url'])
        protocol = parsed.scheme
        port = parsed.port or (443 if protocol == 'https' else 80)
        target_uri = parsed.netloc
        
        # Determine status
        if result['success']:
            status = "success"
        elif result['error']:
            status = result['error']
        else:
            status = f"http_{result['status_code']}"
        
        # Create falsification condition
        falsification_condition = (
            f"latency_ms > {result['latency_ms'] * 2} OR "
            f"status != {status} OR "
            f"consecutive_failures > 3"
        )
        
        # Create Data Pod
        pod = DataPodFactory.create_data_pod(
            target_uri=target_uri,
            protocol=protocol,
            port=port,
            agent_id=self.agent_id,
            location=self.location,
            engine_hash=self.engine_hash,
            status=status,
            latency_ms=result['latency_ms'] or 0,
            payload_data=result['payload_data'],
            falsification_condition=falsification_condition,
            retest_interval_sec=3600
        )
        
        return pod
    
    def run_sector_test(self, sector_name: str, endpoints: List[str]) -> Dict[str, Any]:
        """
        Test an entire sector and generate Data Pods for each endpoint.
        
        Args:
            sector_name: Name of the sector
            endpoints: List of URLs to test
            
        Returns:
            Sector results dictionary
        """
        print(f"\n{'='*60}")
        print(f"Testing: {sector_name}")
        print(f"Endpoints: {len(endpoints)}")
        print('='*60)
        
        sector_results = {
            'sector': sector_name,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'endpoints_tested': len(endpoints),
            'successful': 0,
            'failed': 0,
            'pods_created': 0,
            'details': []
        }
        
        # Run tests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {
                executor.submit(self.test_endpoint, url): url
                for url in endpoints
            }
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result(timeout=15)
                    
                    # Create Data Pod from result
                    pod = self.create_data_pod_from_result(result)
                    self.pod_collection.add_pod(pod)
                    sector_results['pods_created'] += 1
                    
                    if result['success']:
                        sector_results['successful'] += 1
                        status_icon = "✅"
                    else:
                        sector_results['failed'] += 1
                        status_icon = "❌"
                    
                    print(f"{status_icon} {url[:50]:50} | {result['latency_ms']:6.0f}ms | Pod: {pod['id'][:8]}")
                    
                    sector_results['details'].append({
                        'url': url,
                        'success': result['success'],
                        'pod_id': pod['id'],
                        'pod_cid': pod['integrity_seal']
                    })
                    
                except Exception as e:
                    sector_results['failed'] += 1
                    print(f"❌ {url[:50]:50} | Error: {str(e)[:30]}")
        
        sector_results['end_time'] = datetime.now(timezone.utc).isoformat()
        
        return sector_results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive test report.
        
        Args:
            results: List of sector results
            
        Returns:
            Report dictionary
        """
        total_tested = sum(r['endpoints_tested'] for r in results)
        total_successful = sum(r['successful'] for r in results)
        total_failed = sum(r['failed'] for r in results)
        total_pods = sum(r['pods_created'] for r in results)
        
        success_rate = (total_successful / total_tested * 100) if total_tested > 0 else 0
        
        report = {
            'test_id': hashlib.sha256(self.start_time.isoformat().encode()).hexdigest()[:16],
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now(timezone.utc).isoformat(),
            'duration_seconds': (datetime.now(timezone.utc) - self.start_time).total_seconds(),
            'agent_id': self.agent_id,
            'location': self.location,
            'engine_hash': self.engine_hash,
            'total_endpoints_tested': total_tested,
            'total_successful': total_successful,
            'total_failed': total_failed,
            'success_rate': round(success_rate, 1),
            'total_pods_created': total_pods,
            'collection_hash': self.pod_collection.collection_hash,
            'collection_verified': self.pod_collection.verify_collection(),
            'sector_results': results
        }
        
        return report


def main():
    """Run the complete Echo Library reachability test."""
    
    # Define test endpoints
    FINANCE_SECTOR = [
        "https://www.jpmorganchase.com",
        "https://www.bankofamerica.com",
        "https://www.wellsfargo.com",
        "https://www.goldmansachs.com",
        "https://www.paypal.com",
        "https://stripe.com",
        "https://www.coinbase.com",
        "https://www.kraken.com",
        "https://www.federalreserve.gov",
        "https://www.nyse.com",
        "https://www.nasdaq.com",
        "https://www.fidelity.com",
    ]
    
    GLOBAL_NEXUS = [
        "https://www.google.com",
        "https://www.amazon.com",
        "https://www.microsoft.com",
        "https://www.apple.com",
        "https://www.github.com",
        "https://www.twitter.com",
        "https://www.linkedin.com",
        "https://www.bbc.com",
        "https://www.cnn.com",
        "https://www.wikipedia.org",
        "https://www.cloudflare.com",
        "https://aws.amazon.com",
    ]
    
    try:
        # Initialize test
        tester = EchoLibraryReachabilityTest(
            agent_id="echo_probe_01",
            location="sandbox_us_east"
        )
        
        # Run sector tests
        results = []
        results.append(tester.run_sector_test("Finance Sector", FINANCE_SECTOR))
        results.append(tester.run_sector_test("Global Nexus", GLOBAL_NEXUS))
        
        # Generate report
        report = tester.generate_report(results)
        
        # Print summary
        print(f"\n{'='*60}")
        print("ECHO LIBRARY REACHABILITY REPORT")
        print('='*60)
        print(f"Test ID: {report['test_id']}")
        print(f"Duration: {report['duration_seconds']:.1f}s")
        print(f"Endpoints Tested: {report['total_endpoints_tested']}")
        print(f"Success Rate: {report['success_rate']}%")
        print(f"Data Pods Created: {report['total_pods_created']}")
        print(f"Collection Hash: {report['collection_hash'][:16]}...")
        print(f"Collection Verified: {'✓ VALID' if report['collection_verified'] else '✗ INVALID'}")
        
        # Save report
        report_file = f"echo_library_report_{report['test_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📁 Report saved: {report_file}")
        
        # Save Data Pod collection
        pods_file = f"echo_library_pods_{report['test_id']}.json"
        tester.pod_collection.save_collection(pods_file)
        print(f"📦 Data Pods saved: {pods_file}")
        
        print(f"\n✅ Echo Library test complete")
        print(f"   Ready for Tier 2 (IPFS pinning)")
        print(f"   Collection CID: {report['collection_hash']}")
        
        return report
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
