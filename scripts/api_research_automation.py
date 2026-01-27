#!/usr/bin/env python3
"""
API Research Automation Script
Automatically scrapes, tests, and catalogs APIs from public directories
"""

import requests
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
import os

class APIResearcher:
    def __init__(self, output_dir='./api_research_results'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Echo-API-Researcher/1.0'
        })
    
    def fetch_public_apis_repo(self) -> Optional[Dict]:
        """Fetch the public-apis repository README"""
        url = 'https://api.github.com/repos/public-apis/public-apis/readme'
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # GitHub API returns base64 encoded content
            import base64
            content = base64.b64decode(response.json()['content']).decode('utf-8')
            
            # Save raw content
            with open(f'{self.output_dir}/public_apis_readme.md', 'w') as f:
                f.write(content)
            
            print(f"✓ Fetched public-apis README ({len(content)} bytes)")
            return {'content': content}
            
        except Exception as e:
            print(f"✗ Error fetching public-apis: {e}")
            return None
    
    def fetch_public_apis_json(self) -> Optional[List[Dict]]:
        """Fetch the structured JSON data from public-apis"""
        url = 'https://api.publicapis.org/entries'
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            apis = data.get('entries', [])
            
            # Save to file
            with open(f'{self.output_dir}/public_apis_data.json', 'w') as f:
                json.dump(apis, f, indent=2)
            
            print(f"✓ Fetched {len(apis)} APIs from public-apis")
            return apis
            
        except Exception as e:
            print(f"✗ Error fetching public-apis JSON: {e}")
            return None
    
    def categorize_apis(self, apis: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize APIs by their category"""
        categories = {}
        
        for api in apis:
            category = api.get('Category', 'Uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(api)
        
        print(f"✓ Categorized into {len(categories)} categories")
        return categories
    
    def test_api(self, api: Dict) -> Dict:
        """Test if an API is accessible"""
        api_name = api.get('API', 'Unknown')
        api_url = api.get('Link', '')
        auth_type = api.get('Auth', 'None')
        https = api.get('HTTPS', False)
        cors = api.get('Cors', 'unknown')
        
        result = {
            'name': api_name,
            'url': api_url,
            'auth': auth_type,
            'https': https,
            'cors': cors,
            'tested': False,
            'accessible': False,
            'response_time': None,
            'error': None
        }
        
        # Skip if no URL
        if not api_url:
            result['error'] = 'No URL provided'
            return result
        
        # Try to access the API documentation page
        try:
            start_time = time.time()
            response = self.session.get(api_url, timeout=10)
            response_time = time.time() - start_time
            
            result['tested'] = True
            result['accessible'] = response.status_code == 200
            result['response_time'] = round(response_time, 2)
            
            if response.status_code != 200:
                result['error'] = f'HTTP {response.status_code}'
                
        except requests.exceptions.Timeout:
            result['tested'] = True
            result['error'] = 'Timeout'
        except requests.exceptions.ConnectionError:
            result['tested'] = True
            result['error'] = 'Connection error'
        except Exception as e:
            result['tested'] = True
            result['error'] = str(e)[:100]
        
        return result
    
    def test_apis_in_category(self, category: str, apis: List[Dict], max_tests: int = 5) -> List[Dict]:
        """Test a sample of APIs in a category"""
        print(f"\nTesting {category} APIs (max {max_tests})...")
        
        results = []
        tested = 0
        
        for api in apis[:max_tests]:
            result = self.test_api(api)
            results.append(result)
            tested += 1
            
            status = "✓" if result['accessible'] else "✗"
            print(f"  {status} {result['name']}: {result.get('error', 'OK')}")
            
            # Rate limiting
            time.sleep(0.5)
        
        return results
    
    def generate_category_report(self, category: str, apis: List[Dict], test_results: List[Dict]) -> str:
        """Generate markdown report for a category"""
        report = f"# {category} APIs\n\n"
        report += f"**Total APIs:** {len(apis)}\n"
        report += f"**Tested:** {len(test_results)}\n"
        
        accessible = sum(1 for r in test_results if r['accessible'])
        report += f"**Accessible:** {accessible}/{len(test_results)}\n\n"
        
        report += "## APIs in this category\n\n"
        
        for api in apis:
            name = api.get('API', 'Unknown')
            description = api.get('Description', 'No description')
            link = api.get('Link', '')
            auth = api.get('Auth', 'None')
            https = "✓" if api.get('HTTPS') else "✗"
            cors = api.get('Cors', 'unknown')
            
            report += f"### {name}\n\n"
            report += f"**Description:** {description}\n\n"
            report += f"**URL:** {link}\n\n"
            report += f"**Auth:** {auth} | **HTTPS:** {https} | **CORS:** {cors}\n\n"
            
            # Add test result if available
            test_result = next((r for r in test_results if r['name'] == name), None)
            if test_result:
                if test_result['accessible']:
                    report += f"**Status:** ✓ Accessible ({test_result['response_time']}s)\n\n"
                else:
                    report += f"**Status:** ✗ {test_result.get('error', 'Not accessible')}\n\n"
            
            report += "---\n\n"
        
        return report
    
    def run_full_research(self):
        """Run complete API research workflow"""
        print("=" * 60)
        print("Echo API Research Automation")
        print("=" * 60)
        
        # Step 1: Fetch APIs
        print("\n[1/5] Fetching API data...")
        apis = self.fetch_public_apis_json()
        
        if not apis:
            print("Failed to fetch APIs. Exiting.")
            return
        
        # Step 2: Categorize
        print("\n[2/5] Categorizing APIs...")
        categories = self.categorize_apis(apis)
        
        # Save category summary
        summary = {
            'total_apis': len(apis),
            'total_categories': len(categories),
            'categories': {cat: len(apis_list) for cat, apis_list in categories.items()},
            'timestamp': datetime.now().isoformat()
        }
        
        with open(f'{self.output_dir}/category_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Step 3: Test APIs (sample from each category)
        print("\n[3/5] Testing APIs...")
        all_test_results = {}
        
        # Priority categories for Echo products
        priority_categories = [
            'Finance',
            'Government',
            'Health',
            'Weather',
            'News',
            'Data Validation',
            'Documents & Productivity',
            'Cryptocurrency',
            'Science & Math',
            'Transportation'
        ]
        
        for category in priority_categories:
            if category in categories:
                test_results = self.test_apis_in_category(category, categories[category], max_tests=5)
                all_test_results[category] = test_results
        
        # Save test results
        with open(f'{self.output_dir}/test_results.json', 'w') as f:
            json.dump(all_test_results, f, indent=2)
        
        # Step 4: Generate reports
        print("\n[4/5] Generating category reports...")
        reports_dir = f'{self.output_dir}/category_reports'
        os.makedirs(reports_dir, exist_ok=True)
        
        for category, apis_list in categories.items():
            test_results = all_test_results.get(category, [])
            report = self.generate_category_report(category, apis_list, test_results)
            
            filename = category.lower().replace(' & ', '_').replace(' ', '_')
            with open(f'{reports_dir}/{filename}.md', 'w') as f:
                f.write(report)
        
        print(f"✓ Generated {len(categories)} category reports")
        
        # Step 5: Generate master index
        print("\n[5/5] Generating master index...")
        self.generate_master_index(categories, all_test_results)
        
        print("\n" + "=" * 60)
        print("Research Complete!")
        print(f"Results saved to: {self.output_dir}")
        print("=" * 60)
    
    def generate_master_index(self, categories: Dict, test_results: Dict):
        """Generate master index of all APIs"""
        index = "# API Research Master Index\n\n"
        index += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        index += f"**Total APIs:** {sum(len(apis) for apis in categories.values())}\n"
        index += f"**Total Categories:** {len(categories)}\n\n"
        
        index += "## Categories\n\n"
        
        for category in sorted(categories.keys()):
            apis_list = categories[category]
            tested = len(test_results.get(category, []))
            accessible = sum(1 for r in test_results.get(category, []) if r['accessible'])
            
            index += f"### {category}\n"
            index += f"- **Total APIs:** {len(apis_list)}\n"
            if tested > 0:
                index += f"- **Tested:** {tested} ({accessible} accessible)\n"
            index += f"- **Report:** [category_reports/{category.lower().replace(' & ', '_').replace(' ', '_')}.md](category_reports/{category.lower().replace(' & ', '_').replace(' ', '_')}.md)\n\n"
        
        with open(f'{self.output_dir}/INDEX.md', 'w') as f:
            f.write(index)
        
        print("✓ Generated master index")


if __name__ == '__main__':
    researcher = APIResearcher(output_dir='/home/ubuntu/api_research_results')
    researcher.run_full_research()
