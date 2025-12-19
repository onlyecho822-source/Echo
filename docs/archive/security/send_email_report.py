#!/usr/bin/env python3
"""
Email Report Sender
Sends vulnerability reports via email using GitHub Actions secrets
"""

import json
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime

class EmailReportSender:
    """Send vulnerability reports via email"""
    
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        """
        Initialize email sender
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            sender_email: Email address to send from
            sender_password: Email password or app token
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_report(self, recipient_email: str, report_dict: dict, html_content: str = None):
        """
        Send vulnerability report via email
        
        Args:
            recipient_email: Email address to send to
            report_dict: Report data as dictionary
            html_content: HTML version of the report
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[Echo Universe] Daily Security Report - {report_dict.get('timestamp', 'N/A')}"
            msg["From"] = self.sender_email
            msg["To"] = recipient_email
            
            # Generate text content
            text_content = self._generate_text_content(report_dict)
            
            # Attach text version
            msg.attach(MIMEText(text_content, "plain"))
            
            # Attach HTML version if provided
            if html_content:
                msg.attach(MIMEText(html_content, "html"))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, msg.as_string())
            
            print(f"✅ Report sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}", file=sys.stderr)
            return False
    
    def _generate_text_content(self, report_dict: dict) -> str:
        """Generate plain text email content"""
        summary = report_dict.get("summary", {})
        
        text = f"""
Echo Universe - Daily Security Report
Generated: {report_dict.get('timestamp', 'N/A')}

VULNERABILITY SUMMARY
─────────────────────
Critical:  {summary.get('critical', 0)}
High:      {summary.get('high', 0)}
Moderate:  {summary.get('moderate', 0)}
Low:       {summary.get('low', 0)}
─────────────────────
Total:     {summary.get('total', 0)}

RECOMMENDATIONS
───────────────
"""
        
        for rec in report_dict.get("recommendations", []):
            text += f"\n[{rec['priority']}] {rec['action']}\n{rec['details']}\n"
        
        text += """

SCAN RESULTS
────────────
"""
        
        for scan_name, scan_data in report_dict.get("scans", {}).items():
            text += f"\n{scan_name}\n"
            text += "=" * len(scan_name) + "\n"
            
            scan_summary = scan_data.get("summary", {})
            text += f"Critical: {scan_summary.get('critical', 0)} | "
            text += f"High: {scan_summary.get('high', 0)} | "
            text += f"Moderate: {scan_summary.get('moderate', 0)} | "
            text += f"Low: {scan_summary.get('low', 0)}\n"
        
        text += """

For detailed information, visit:
https://github.com/onlyecho822-source/Echo/security

---
Echo Universe Security Monitoring System
"""
        
        return text

def main():
    # Get parameters from command line or environment
    if len(sys.argv) < 3:
        print("Usage: send_email_report.py <report_json_file> <recipient_email> [html_report_file]")
        print("\nEnvironment variables required:")
        print("  SMTP_SERVER - SMTP server address (default: smtp.gmail.com)")
        print("  SMTP_PORT - SMTP port (default: 587)")
        print("  SENDER_EMAIL - Email address to send from")
        print("  SENDER_PASSWORD - Email password or app token")
        sys.exit(1)
    
    report_file = sys.argv[1]
    recipient_email = sys.argv[2]
    html_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Load report
    try:
        with open(report_file, 'r') as f:
            report_dict = json.load(f)
    except Exception as e:
        print(f"Error loading report: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load HTML if provided
    html_content = None
    if html_file and Path(html_file).exists():
        try:
            with open(html_file, 'r') as f:
                html_content = f.read()
        except Exception as e:
            print(f"Warning: Could not load HTML file: {e}", file=sys.stderr)
    
    # Get email credentials from environment
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Error: SENDER_EMAIL and SENDER_PASSWORD environment variables required", file=sys.stderr)
        sys.exit(1)
    
    # Send report
    sender = EmailReportSender(smtp_server, smtp_port, sender_email, sender_password)
    success = sender.send_report(recipient_email, report_dict, html_content)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
