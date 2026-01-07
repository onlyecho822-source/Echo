#!/usr/bin/env python3
"""
Archon Daily Report Generator
Automated daily intelligence reports for Echo Universe
Sends to: onlyecho822@gmail.com
"""

import os
import yaml
import json
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class ArchonReporter:
    """Archon - The Echo Curator's reporting system"""
    
    def __init__(self, repo_path="/home/ubuntu/Echo"):
        self.repo_path = Path(repo_path)
        self.curator_config = self.load_curator_config()
        self.index = self.load_master_index()
        self.report_date = datetime.utcnow()
        
    def load_curator_config(self):
        """Load Archon's configuration"""
        config_path = self.repo_path / "CURATOR.yaml"
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    def load_master_index(self):
        """Load master INDEX.yaml"""
        index_path = self.repo_path / "INDEX.yaml"
        with open(index_path) as f:
            return yaml.safe_load(f)
    
    def get_git_activity(self, since_hours=24):
        """Get Git activity in last 24 hours"""
        os.chdir(self.repo_path)
        
        since_time = (datetime.utcnow() - timedelta(hours=since_hours)).isoformat()
        
        # Get commits
        commits_cmd = f'git log --since="{since_time}" --pretty=format:"%h|%an|%s|%ai" --all'
        commits_output = subprocess.check_output(commits_cmd, shell=True, text=True)
        
        commits = []
        for line in commits_output.strip().split('\n'):
            if line:
                hash, author, subject, date = line.split('|')
                commits.append({
                    'hash': hash,
                    'author': author,
                    'subject': subject,
                    'date': date
                })
        
        # Get file changes
        files_cmd = f'git diff --name-status HEAD@{{{since_hours} hours ago}} HEAD 2>/dev/null || echo ""'
        files_output = subprocess.check_output(files_cmd, shell=True, text=True)
        
        files_changed = []
        for line in files_output.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    files_changed.append({
                        'status': parts[0],
                        'file': parts[1]
                    })
        
        # Get branch info
        branches_cmd = 'git branch -a'
        branches_output = subprocess.check_output(branches_cmd, shell=True, text=True)
        branches = [b.strip().replace('* ', '') for b in branches_output.split('\n') if b.strip()]
        
        return {
            'commits': commits,
            'files_changed': files_changed,
            'branches': branches,
            'commit_count': len(commits),
            'files_count': len(files_changed)
        }
    
    def detect_emergent_patterns(self, git_activity):
        """Detect emergent patterns from activity"""
        patterns = []
        
        # Pattern: Multiple related files changed together
        files = [f['file'] for f in git_activity['files_changed']]
        
        # Check for cross-directory connections
        directories = set([str(Path(f).parent) for f in files])
        if len(directories) > 3:
            patterns.append({
                'type': 'cross-project-connection',
                'description': f'Activity across {len(directories)} different areas',
                'significance': 'medium',
                'details': list(directories)
            })
        
        # Pattern: New directories created
        new_dirs = [f['file'] for f in git_activity['files_changed'] 
                   if f['status'] == 'A' and '/' in f['file']]
        if new_dirs:
            patterns.append({
                'type': 'structure-expansion',
                'description': f'{len(new_dirs)} new organizational units created',
                'significance': 'high',
                'details': new_dirs
            })
        
        # Pattern: High commit frequency
        if git_activity['commit_count'] > 10:
            patterns.append({
                'type': 'high-velocity-development',
                'description': f'{git_activity["commit_count"]} commits in 24 hours',
                'significance': 'high',
                'details': 'Rapid iteration and development'
            })
        
        return patterns
    
    def calculate_metrics(self, git_activity):
        """Calculate KPIs and metrics"""
        # Count lines of code added
        diff_cmd = 'git diff --shortstat HEAD@{24 hours ago} HEAD 2>/dev/null || echo "0 files changed, 0 insertions(+), 0 deletions(-)"'
        diff_output = subprocess.check_output(diff_cmd, shell=True, text=True, cwd=self.repo_path)
        
        # Parse diff output
        insertions = 0
        deletions = 0
        if 'insertion' in diff_output:
            parts = diff_output.split(',')
            for part in parts:
                if 'insertion' in part:
                    insertions = int(part.strip().split()[0])
                elif 'deletion' in part:
                    deletions = int(part.strip().split()[0])
        
        # Count files by type
        py_files = len([f for f in git_activity['files_changed'] if f['file'].endswith('.py')])
        md_files = len([f for f in git_activity['files_changed'] if f['file'].endswith('.md')])
        yaml_files = len([f for f in git_activity['files_changed'] if f['file'].endswith('.yaml')])
        
        return {
            'commits': git_activity['commit_count'],
            'files_changed': git_activity['files_count'],
            'lines_added': insertions,
            'lines_deleted': deletions,
            'net_lines': insertions - deletions,
            'python_files': py_files,
            'markdown_files': md_files,
            'yaml_files': yaml_files
        }
    
    def generate_report_html(self, git_activity, patterns, metrics):
        """Generate HTML email report"""
        
        # Format commits
        commits_html = ""
        for commit in git_activity['commits'][:10]:  # Show last 10
            commits_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee; font-family: monospace; font-size: 12px;">{commit['hash']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{commit['subject']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; font-size: 11px; color: #666;">{commit['date'][:16]}</td>
            </tr>
            """
        
        # Format patterns
        patterns_html = ""
        for pattern in patterns:
            significance_color = {
                'critical': '#dc3545',
                'high': '#fd7e14',
                'medium': '#ffc107',
                'low': '#28a745'
            }.get(pattern['significance'], '#6c757d')
            
            patterns_html += f"""
            <div style="margin-bottom: 15px; padding: 15px; background: #f8f9fa; border-left: 4px solid {significance_color};">
                <h4 style="margin: 0 0 10px 0; color: {significance_color};">
                    {pattern['type'].replace('-', ' ').title()}
                </h4>
                <p style="margin: 0 0 5px 0;">{pattern['description']}</p>
                <p style="margin: 0; font-size: 12px; color: #666;">
                    <strong>Significance:</strong> {pattern['significance'].upper()}
                </p>
            </div>
            """
        
        if not patterns_html:
            patterns_html = "<p>No significant patterns detected today.</p>"
        
        # Format files changed
        files_html = ""
        for file in git_activity['files_changed'][:20]:  # Show first 20
            status_icon = {
                'A': '➕',
                'M': '✏️',
                'D': '❌',
                'R': '🔄'
            }.get(file['status'], '📄')
            
            files_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">{status_icon}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; font-family: monospace; font-size: 12px;">{file['file']}</td>
            </tr>
            """
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Echo Universe Daily Master Report</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
    
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
        <h1 style="margin: 0 0 10px 0; font-size: 28px;">🏛️ Echo Universe Daily Master Report</h1>
        <p style="margin: 0; font-size: 16px; opacity: 0.9;">
            <strong>Date:</strong> {self.report_date.strftime('%B %d, %Y')} | 
            <strong>Curator:</strong> Archon
        </p>
    </div>
    
    <!-- Executive Summary -->
    <div style="margin-bottom: 30px;">
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">🎯 Executive Summary</h2>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
            <p><strong>Repository Activity:</strong> {metrics['commits']} commits, {metrics['files_changed']} files changed</p>
            <p><strong>Code Changes:</strong> +{metrics['lines_added']} / -{metrics['lines_deleted']} lines (net: {metrics['net_lines']:+d})</p>
            <p><strong>Patterns Detected:</strong> {len(patterns)} emergent patterns identified</p>
            <p><strong>System Status:</strong> ✅ Operational</p>
        </div>
    </div>
    
    <!-- Repository Activity -->
    <div style="margin-bottom: 30px;">
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">📊 Repository Activity</h2>
        
        <h3>Recent Commits ({metrics['commits']} total)</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f8f9fa;">
                    <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Hash</th>
                    <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Message</th>
                    <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Date</th>
                </tr>
            </thead>
            <tbody>
                {commits_html}
            </tbody>
        </table>
        
        <h3 style="margin-top: 25px;">Files Changed ({metrics['files_changed']} total)</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f8f9fa;">
                    <th style="padding: 10px; text-align: center; border-bottom: 2px solid #dee2e6; width: 60px;">Status</th>
                    <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">File</th>
                </tr>
            </thead>
            <tbody>
                {files_html}
            </tbody>
        </table>
    </div>
    
    <!-- Emergent Patterns -->
    <div style="margin-bottom: 30px;">
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">🌟 Emergent Patterns & Discoveries</h2>
        {patterns_html}
    </div>
    
    <!-- Metrics -->
    <div style="margin-bottom: 30px;">
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">📈 Metrics & KPIs</h2>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0; color: #667eea;">Code Activity</h4>
                <p style="margin: 5px 0;"><strong>Lines Added:</strong> {metrics['lines_added']}</p>
                <p style="margin: 5px 0;"><strong>Lines Deleted:</strong> {metrics['lines_deleted']}</p>
                <p style="margin: 5px 0;"><strong>Net Change:</strong> {metrics['net_lines']:+d}</p>
            </div>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0; color: #667eea;">File Types</h4>
                <p style="margin: 5px 0;"><strong>Python:</strong> {metrics['python_files']}</p>
                <p style="margin: 5px 0;"><strong>Markdown:</strong> {metrics['markdown_files']}</p>
                <p style="margin: 5px 0;"><strong>YAML:</strong> {metrics['yaml_files']}</p>
            </div>
        </div>
    </div>
    
    <!-- Next 24 Hours -->
    <div style="margin-bottom: 30px;">
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">⏭️ Next 24 Hours Priority</h2>
        <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">
            <p><strong>Archon will continue monitoring and organizing the repository.</strong></p>
            <p>Check INDEX.yaml for current priorities and next actions.</p>
        </div>
    </div>
    
    <!-- Footer -->
    <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #dee2e6; text-align: center; color: #666;">
        <p style="margin: 5px 0;">🏛️ <strong>Archon - The Echo Curator</strong></p>
        <p style="margin: 5px 0; font-style: italic;">Order maintained, intelligence delivered</p>
        <p style="margin: 15px 0 5px 0; font-size: 12px;">
            Next report: {(self.report_date + timedelta(days=1)).strftime('%B %d, %Y at 23:00 UTC')}
        </p>
        <p style="margin: 5px 0; font-size: 11px;">
            Repository: onlyecho822-source/Echo | Generated: {self.report_date.strftime('%Y-%m-%d %H:%M:%S UTC')}
        </p>
    </div>
    
</body>
</html>
        """
        
        return html
    
    def send_email(self, html_content):
        """Send email report"""
        # Email configuration
        sender = "archon@echo-universe.dev"
        recipient = "onlyecho822@gmail.com"
        subject = f"🏛️ Echo Universe Daily Master Report - {self.report_date.strftime('%B %d, %Y')}"
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Attach HTML
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Note: Actual SMTP sending requires credentials
        # For now, save to file for manual sending or GitHub Actions integration
        output_path = self.repo_path / "automation" / "latest_report.html"
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Report generated: {output_path}")
        print(f"📧 Ready to send to: {recipient}")
        print(f"📋 Subject: {subject}")
        
        return output_path
    
    def run(self):
        """Generate and send daily report"""
        print("🏛️ Archon Daily Report Generator")
        print(f"📅 Date: {self.report_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("="*60)
        
        # Collect data
        print("📊 Collecting Git activity...")
        git_activity = self.get_git_activity()
        
        print("🔍 Detecting emergent patterns...")
        patterns = self.detect_emergent_patterns(git_activity)
        
        print("📈 Calculating metrics...")
        metrics = self.calculate_metrics(git_activity)
        
        print("📝 Generating report...")
        html_content = self.generate_report_html(git_activity, patterns, metrics)
        
        print("📧 Preparing email...")
        report_path = self.send_email(html_content)
        
        print("="*60)
        print("✅ Daily report complete!")
        print(f"📄 Report saved to: {report_path}")
        print("\n🏛️ Archon - Order maintained, intelligence delivered")
        
        return report_path

def main():
    reporter = ArchonReporter()
    reporter.run()

if __name__ == "__main__":
    main()
