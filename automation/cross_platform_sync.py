#!/usr/bin/env python3
"""
Cross-Platform Git Sync Automation
Synchronizes Echo repository across GitHub, GitLab, and extended platforms
"""

import subprocess
import json
import yaml
from datetime import datetime
from pathlib import Path

class CrossPlatformSync:
    """Manages synchronization across multiple git platforms"""
    
    def __init__(self, config_path=".git-sync-config.yml"):
        self.config = self.load_config(config_path)
        self.platforms = self.config.get('platforms', {})
        self.sync_strategy = self.config.get('sync_strategy', {})
    
    def load_config(self, path):
        """Load sync configuration"""
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def get_current_branch(self):
        """Get current git branch"""
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    def should_sync_branch(self, branch, platform_name):
        """Determine if branch should sync to platform"""
        if platform_name == 'github':
            patterns = self.sync_strategy.get('github_to_gitlab', [])
        else:
            patterns = self.sync_strategy.get('gitlab_to_github', [])
        
        for pattern in patterns:
            if pattern == branch or pattern.endswith('*') and branch.startswith(pattern[:-1]):
                return True
        return False
    
    def sync_to_platform(self, platform_name, branch):
        """Sync current branch to specified platform"""
        platform = self.platforms.get(platform_name)
        if not platform:
            print(f"❌ Platform {platform_name} not configured")
            return False
        
        url = platform['url']
        
        # Check if remote exists
        result = subprocess.run(
            ['git', 'remote', 'get-url', platform_name],
            capture_output=True
        )
        
        if result.returncode != 0:
            # Add remote
            subprocess.run(['git', 'remote', 'add', platform_name, url])
            print(f"✅ Added remote: {platform_name}")
        
        # Push to platform
        print(f"🔄 Syncing {branch} to {platform_name}...")
        result = subprocess.run(
            ['git', 'push', platform_name, f'{branch}:{branch}'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Synced to {platform_name}")
            return True
        else:
            print(f"❌ Sync failed: {result.stderr}")
            return False
    
    def sync_all(self):
        """Sync to all configured platforms based on strategy"""
        branch = self.get_current_branch()
        print(f"📊 Current branch: {branch}")
        print("")
        
        results = {}
        for platform_name in self.platforms.keys():
            if self.should_sync_branch(branch, platform_name):
                results[platform_name] = self.sync_to_platform(platform_name, branch)
            else:
                print(f"⏭️  Skipping {platform_name} (branch not in sync strategy)")
                results[platform_name] = None
        
        return results
    
    def generate_sync_report(self):
        """Generate cross-platform sync status report"""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'platforms': {}
        }
        
        for platform_name, platform in self.platforms.items():
            # Check if remote exists
            result = subprocess.run(
                ['git', 'remote', 'get-url', platform_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Get last sync info
                result = subprocess.run(
                    ['git', 'log', f'{platform_name}/main', '-1', '--format=%H|%s|%ci'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0 and result.stdout:
                    commit_hash, subject, date = result.stdout.strip().split('|')
                    report['platforms'][platform_name] = {
                        'status': 'synced',
                        'last_commit': commit_hash[:7],
                        'last_message': subject,
                        'last_sync': date,
                        'url': platform['url']
                    }
                else:
                    report['platforms'][platform_name] = {
                        'status': 'not_synced',
                        'url': platform['url']
                    }
            else:
                report['platforms'][platform_name] = {
                    'status': 'not_configured',
                    'url': platform['url']
                }
        
        return report

def main():
    """Main execution"""
    print("=" * 60)
    print("CROSS-PLATFORM GIT SYNC")
    print("=" * 60)
    print("")
    
    sync = CrossPlatformSync()
    
    # Generate report
    print("📊 Generating sync status report...")
    report = sync.generate_sync_report()
    print(json.dumps(report, indent=2))
    print("")
    
    # Perform sync
    print("🔄 Starting cross-platform sync...")
    print("")
    results = sync.sync_all()
    print("")
    
    # Summary
    print("=" * 60)
    print("SYNC SUMMARY")
    print("=" * 60)
    for platform, result in results.items():
        if result is True:
            print(f"✅ {platform}: Success")
        elif result is False:
            print(f"❌ {platform}: Failed")
        else:
            print(f"⏭️  {platform}: Skipped")
    print("")
    print("∇θ — Cross-platform sync complete")

if __name__ == '__main__':
    main()
