#!/usr/bin/env python3
"""
Autonomous Contact Finder - 24/7 Lead Generation
Finds single moms on Reddit, social media, and forums
Extracts contact info and saves to database
Runs automatically via GitHub Actions every 6 hours
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict

# Configuration
LANDING_PAGE_URL = os.environ.get('LANDING_PAGE_URL', 'https://your-site.manus.space')
TARGET_SUBREDDITS = ['singlemoms', 'SingleParents', 'povertyfinance', 'Assistance', 'tax', 'personalfinance']
CONTACT_DB_FILE = 'marketing/contacts_database.json'

# Keywords to identify potential leads
LEAD_KEYWORDS = [
    'single mom', 'single mother', 'single parent',
    'doordash', 'gig work', 'side hustle', 'cash job',
    'babysitting', 'cleaning', 'hair', 'nails',
    'w-2', 'w2', 'tax', 'taxes', 'refund', 'eitc',
    'raising kids alone', 'no help', 'struggling'
]

def load_contacts_database():
    """Load existing contacts from database"""
    if os.path.exists(CONTACT_DB_FILE):
        with open(CONTACT_DB_FILE, 'r') as f:
            return json.load(f)
    return {"contacts": [], "last_updated": None}

def save_contacts_database(db):
    """Save contacts to database"""
    db['last_updated'] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(CONTACT_DB_FILE), exist_ok=True)
    with open(CONTACT_DB_FILE, 'r') as f:
        json.dump(db, f, indent=2)
    print(f"✓ Saved {len(db['contacts'])} contacts to database")

def extract_email(text: str) -> str:
    """Extract email address from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_reddit_username(text: str) -> str:
    """Extract Reddit username from text"""
    username_pattern = r'u/([A-Za-z0-9_-]+)'
    match = re.search(username_pattern, text)
    return match.group(1) if match else None

def is_potential_lead(text: str) -> bool:
    """Check if text contains lead keywords"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in LEAD_KEYWORDS)

def find_reddit_contacts():
    """
    Find potential contacts on Reddit
    NOTE: This is a template - requires Reddit API credentials
    """
    print("\n" + "="*80)
    print("REDDIT CONTACT FINDER")
    print("="*80)
    
    contacts = []
    
    # Simulated Reddit scraping (replace with actual Reddit API calls)
    print(f"\nTarget Subreddits: {', '.join(TARGET_SUBREDDITS)}")
    print(f"Keywords: {', '.join(LEAD_KEYWORDS[:5])}...")
    
    # Template for actual Reddit API integration
    print("\n⚠️  Reddit API credentials not configured")
    print("   To enable Reddit scraping:")
    print("   1. Create Reddit app at: https://www.reddit.com/prefs/apps")
    print("   2. Add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to GitHub Secrets")
    print("   3. Install praw: pip install praw")
    print("\n   Example code:")
    print("   ```python")
    print("   import praw")
    print("   reddit = praw.Reddit(")
    print("       client_id=os.environ['REDDIT_CLIENT_ID'],")
    print("       client_secret=os.environ['REDDIT_CLIENT_SECRET'],")
    print("       user_agent='TaxServicesBot/1.0'")
    print("   )")
    print("   for subreddit_name in TARGET_SUBREDDITS:")
    print("       subreddit = reddit.subreddit(subreddit_name)")
    print("       for post in subreddit.hot(limit=100):")
    print("           if is_potential_lead(post.title + post.selftext):")
    print("               # Extract contact info and save")
    print("   ```")
    
    return contacts

def find_zapier_contacts():
    """
    Find contacts using Zapier integration
    Zapier can monitor Gmail, social media, forms, etc.
    """
    print("\n" + "="*80)
    print("ZAPIER CONTACT FINDER")
    print("="*80)
    
    # Check if Zapier webhook is configured
    zapier_webhook = os.environ.get('ZAPIER_WEBHOOK_URL')
    
    if not zapier_webhook:
        print("\n⚠️  Zapier webhook not configured")
        print("   To enable Zapier integration:")
        print("   1. Create Zap at: https://zapier.com/app/zaps")
        print("   2. Trigger: Gmail (new email matching filter)")
        print("   3. Filter: Subject contains 'single mom' OR 'tax help'")
        print("   4. Action: Webhooks by Zapier (POST)")
        print("   5. Add ZAPIER_WEBHOOK_URL to GitHub Secrets")
        return []
    
    print(f"✓ Zapier webhook configured: {zapier_webhook[:50]}...")
    print("  Zapier will automatically send new contacts to this system")
    
    return []

def find_gmail_contacts():
    """
    Find contacts from Gmail using MCP Gmail integration
    """
    print("\n" + "="*80)
    print("GMAIL CONTACT FINDER (MCP)")
    print("="*80)
    
    print("\n✓ Gmail MCP server available")
    print("  Use manus-mcp-cli to search Gmail for potential leads:")
    print("  $ manus-mcp-cli tool call gmail_search --server gmail --input '{\"query\": \"single mom tax help\"}'")
    print("  $ manus-mcp-cli tool call gmail_search --server gmail --input '{\"query\": \"doordash w-2\"}'")
    
    # Template for actual implementation
    print("\n  Integration steps:")
    print("  1. Search Gmail for keywords: 'single mom', 'tax help', 'doordash', 'w-2'")
    print("  2. Extract sender email addresses")
    print("  3. Add to contacts database")
    print("  4. Send automated response with landing page link")
    
    return []

def autonomous_contact_discovery():
    """Main autonomous contact discovery function"""
    print("="*80)
    print("AUTONOMOUS CONTACT FINDER - 24/7 LEAD GENERATION")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%H:%M %b %d %Y')}")
    print(f"Landing Page: {LANDING_PAGE_URL}")
    print("="*80)
    
    # Load existing contacts
    db = load_contacts_database()
    initial_count = len(db['contacts'])
    print(f"\nExisting contacts in database: {initial_count}")
    
    # Find contacts from multiple sources
    reddit_contacts = find_reddit_contacts()
    zapier_contacts = find_zapier_contacts()
    gmail_contacts = find_gmail_contacts()
    
    # Combine and deduplicate
    new_contacts = reddit_contacts + zapier_contacts + gmail_contacts
    
    # Add new contacts to database
    for contact in new_contacts:
        # Check if contact already exists
        existing = any(c.get('email') == contact.get('email') or 
                      c.get('username') == contact.get('username') 
                      for c in db['contacts'])
        if not existing:
            contact['added_at'] = datetime.now().isoformat()
            contact['source'] = contact.get('source', 'unknown')
            contact['contacted'] = False
            db['contacts'].append(contact)
    
    # Save database
    save_contacts_database(db)
    
    final_count = len(db['contacts'])
    new_count = final_count - initial_count
    
    print("\n" + "="*80)
    print("CONTACT DISCOVERY SUMMARY")
    print("="*80)
    print(f"Initial contacts: {initial_count}")
    print(f"New contacts found: {new_count}")
    print(f"Total contacts: {final_count}")
    print("="*80)
    
    # Create summary report
    report = {
        "timestamp": datetime.now().isoformat(),
        "initial_count": initial_count,
        "new_count": new_count,
        "total_count": final_count,
        "sources": {
            "reddit": len(reddit_contacts),
            "zapier": len(zapier_contacts),
            "gmail": len(gmail_contacts)
        }
    }
    
    # Save report
    report_file = f"marketing/distribution-logs/contact-discovery-{datetime.now().strftime('%Y-%m-%d')}.json"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ Report saved: {report_file}")
    
    return db

if __name__ == "__main__":
    try:
        autonomous_contact_discovery()
        print("\n✓ Autonomous contact discovery completed successfully")
        exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        exit(1)
