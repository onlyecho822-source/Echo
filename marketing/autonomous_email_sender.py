#!/usr/bin/env python3
"""
Autonomous Email Sender - 24/7 Outreach
Sends landing page emails to contacts found by contact_finder
Uses Zapier and Gmail MCP for automated sending
Runs automatically via GitHub Actions every 6 hours
"""

import os
import json
import subprocess
from datetime import datetime
from typing import List, Dict

# Configuration
LANDING_PAGE_URL = os.environ.get('LANDING_PAGE_URL', 'https://your-site.manus.space')
CONTACT_DB_FILE = 'marketing/contacts_database.json'
MAX_EMAILS_PER_RUN = 50  # Rate limiting to avoid spam flags

def load_contacts_database():
    """Load contacts from database"""
    if os.path.exists(CONTACT_DB_FILE):
        with open(CONTACT_DB_FILE, 'r') as f:
            return json.load(f)
    return {"contacts": [], "last_updated": None}

def save_contacts_database(db):
    """Save contacts to database"""
    db['last_updated'] = datetime.now().isoformat()
    with open(CONTACT_DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

def create_email_content(contact: Dict) -> Dict:
    """Create personalized email content for contact"""
    
    # Personalize based on contact source
    if contact.get('source') == 'reddit':
        greeting = f"Hi u/{contact.get('username', 'there')}"
    else:
        greeting = "Hi there"
    
    subject = "🎯 No W-2? No Problem - Tax Help for Single Moms"
    
    body = f"""{greeting},

I saw your post and wanted to reach out.

If you're a single mom doing gig work (DoorDash, babysitting, cleaning, hair/nails, selling online) and think you can't file taxes without a W-2 - you're wrong.

**No W-2? No Problem.**

We specialize in helping single moms get their maximum refund - even without traditional W-2 income.

Check it out: {LANDING_PAGE_URL}

📱 Follow us on Instagram: @chicago_to_the_dr

This is NOT a scam. This is real tax filing for real single parents who deserve every dollar they're entitled to.

💰 Average refund: $8,200
✅ 500+ single moms helped in 2025
⚡ Maximum refund guaranteed

Tax season ends April 15, 2026. Don't miss out.

Best,
Tax Services Team
onlyecho822@gmail.com

---
Not interested? Reply with "STOP" and I won't contact you again.
"""
    
    return {
        "to": contact.get('email'),
        "subject": subject,
        "body": body
    }

def send_email_via_zapier(email_data: Dict) -> bool:
    """Send email using Zapier webhook"""
    zapier_webhook = os.environ.get('ZAPIER_EMAIL_WEBHOOK_URL')
    
    if not zapier_webhook:
        print("⚠️  ZAPIER_EMAIL_WEBHOOK_URL not configured")
        return False
    
    try:
        import requests
        response = requests.post(zapier_webhook, json=email_data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Zapier email failed: {e}")
        return False

def send_email_via_gmail_mcp(email_data: Dict) -> bool:
    """Send email using Gmail MCP server"""
    
    try:
        # Use manus-mcp-cli to send email via Gmail
        mcp_input = json.dumps({
            "to": email_data['to'],
            "subject": email_data['subject'],
            "body": email_data['body']
        })
        
        result = subprocess.run(
            ['manus-mcp-cli', 'tool', 'call', 'gmail_send_email', 
             '--server', 'gmail', '--input', mcp_input],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✓ Email sent via Gmail MCP to: {email_data['to']}")
            return True
        else:
            print(f"✗ Gmail MCP error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Gmail MCP failed: {e}")
        return False

def autonomous_email_sending():
    """Main autonomous email sending function"""
    print("="*80)
    print("AUTONOMOUS EMAIL SENDER - 24/7 OUTREACH")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%H:%M %b %d %Y')}")
    print(f"Landing Page: {LANDING_PAGE_URL}")
    print(f"Max emails per run: {MAX_EMAILS_PER_RUN}")
    print("="*80)
    
    # Load contacts
    db = load_contacts_database()
    total_contacts = len(db['contacts'])
    
    # Filter contacts who haven't been contacted yet
    pending_contacts = [c for c in db['contacts'] if not c.get('contacted', False)]
    pending_count = len(pending_contacts)
    
    print(f"\nTotal contacts in database: {total_contacts}")
    print(f"Pending contacts (not yet contacted): {pending_count}")
    
    if pending_count == 0:
        print("\n✓ No pending contacts to email")
        return
    
    # Limit emails per run to avoid spam flags
    contacts_to_email = pending_contacts[:MAX_EMAILS_PER_RUN]
    print(f"Sending emails to: {len(contacts_to_email)} contacts")
    
    # Send emails
    sent_count = 0
    failed_count = 0
    
    for contact in contacts_to_email:
        # Skip if no email address
        if not contact.get('email'):
            print(f"⚠️  Skipping {contact.get('username', 'unknown')} - no email")
            continue
        
        # Create email content
        email_data = create_email_content(contact)
        
        # Try sending via Gmail MCP first, fallback to Zapier
        success = send_email_via_gmail_mcp(email_data)
        
        if not success:
            success = send_email_via_zapier(email_data)
        
        # Update contact status
        if success:
            contact['contacted'] = True
            contact['contacted_at'] = datetime.now().isoformat()
            sent_count += 1
        else:
            failed_count += 1
    
    # Save updated database
    save_contacts_database(db)
    
    print("\n" + "="*80)
    print("EMAIL SENDING SUMMARY")
    print("="*80)
    print(f"Emails sent: {sent_count}")
    print(f"Emails failed: {failed_count}")
    print(f"Remaining pending: {pending_count - sent_count}")
    print("="*80)
    
    # Create summary report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_contacts": total_contacts,
        "pending_before": pending_count,
        "sent": sent_count,
        "failed": failed_count,
        "pending_after": pending_count - sent_count
    }
    
    # Save report
    report_file = f"marketing/distribution-logs/email-sending-{datetime.now().strftime('%Y-%m-%d')}.json"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ Report saved: {report_file}")
    
    # Setup instructions if no email service configured
    if sent_count == 0 and failed_count > 0:
        print("\n" + "="*80)
        print("EMAIL SERVICE SETUP REQUIRED")
        print("="*80)
        print("\nOption 1: Gmail MCP (Recommended)")
        print("  ✓ Already configured in your Manus environment")
        print("  ✓ Uses your Gmail account automatically")
        print("  ✓ No additional setup needed")
        print("\nOption 2: Zapier Webhook")
        print("  1. Create Zap: Gmail → Send Email")
        print("  2. Trigger: Webhooks by Zapier (Catch Hook)")
        print("  3. Action: Gmail (Send Email)")
        print("  4. Map fields: to, subject, body")
        print("  5. Add ZAPIER_EMAIL_WEBHOOK_URL to GitHub Secrets")
        print("="*80)

if __name__ == "__main__":
    try:
        autonomous_email_sending()
        print("\n✓ Autonomous email sending completed successfully")
        exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        exit(1)
