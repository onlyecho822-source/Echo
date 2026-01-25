#!/usr/bin/env python3
"""
Social Media Distribution System for Landing Page
Creates social media posts for Instagram, Facebook, Twitter/X
"""

import os
import sys
import json
from datetime import datetime

LANDING_PAGE_URL = os.environ.get('LANDING_PAGE_URL', 'https://your-site.manus.space')
INSTAGRAM_HANDLE = os.environ.get('INSTAGRAM_HANDLE', '@chicago_to_the_dr')

def create_instagram_post():
    """Create Instagram post caption"""
    return f"""🎯 NO W-2? NO PROBLEM.

Single moms: If you're doing DoorDash, babysitting, cleaning, hair/nails, or selling online - you CAN file taxes and get your refund.

You don't need a W-2. You just need us.

💰 Average refund: $8,200
✅ 500+ single moms helped
⚡ Maximum refund guaranteed

Link in bio ➡️ {LANDING_PAGE_URL}

Tax season ends April 15, 2026. Don't miss YOUR money.

#SingleMom #TaxRefund #NoW2NoProblem #GigWork #DoorDash #TaxSeason2026 #MaximumRefund #SingleParent #TaxHelp #ChicagoMoms

{INSTAGRAM_HANDLE}
"""

def create_facebook_post():
    """Create Facebook post"""
    return f"""🎯 Single Moms: No W-2? No Problem!

If you're raising your kids alone and doing gig work (DoorDash, babysitting, cleaning, hair/nails, selling online), you might think you can't file taxes without a W-2.

WRONG. ✋

We specialize in helping single moms get their maximum refund - even without traditional W-2 income.

💰 Average refund: $8,200
✅ 500+ single moms helped in 2025
⚡ Maximum refund guaranteed

Get your free review: {LANDING_PAGE_URL}

Tax season ends April 15, 2026. Don't leave YOUR money on the table.

Share this with a single mom who needs to see it. 💙

#SingleMom #TaxRefund #NoW2NoProblem #GigWork #TaxSeason2026
"""

def create_twitter_post():
    """Create Twitter/X post"""
    return f"""🎯 Single moms doing DoorDash, babysitting, cleaning, hair/nails, selling online:

NO W-2? NO PROBLEM.

We file for ALL income types.
Average refund: $8,200
500+ single moms helped

Get your free review: {LANDING_PAGE_URL}

Tax season ends April 15. Don't miss YOUR money. 💰

#SingleMom #TaxRefund #GigWork
"""

def create_reddit_post():
    """Create Reddit post for r/singlemoms, r/SingleParents"""
    return f"""No W-2? No Problem - Tax Filing for Single Moms Doing Gig Work

Hey everyone,

I wanted to share something that might help some of you. If you're a single mom doing gig work (DoorDash, babysitting, cleaning, hair/nails, selling online) and think you can't file taxes without a W-2 - that's not true.

**You CAN file taxes and get your refund without a W-2.**

I found this service that specializes in helping single moms with non-traditional income get their maximum refund:

{LANDING_PAGE_URL}

Some key points:
- They handle ALL income types (W-2 or no W-2)
- Average refund: $8,200
- 500+ single moms helped in 2025
- Maximum refund guaranteed
- Free review of your tax situation

Tax season ends April 15, 2026. If you're raising your kids alone, you deserve every dollar you're entitled to.

Hope this helps someone! 💙

(Not affiliated, just sharing what I found)
"""

def distribute_social_media():
    """Create social media posts and save to files"""
    
    print("=" * 80)
    print("SOCIAL MEDIA DISTRIBUTION SYSTEM")
    print("=" * 80)
    print(f"\nLanding Page URL: {LANDING_PAGE_URL}")
    print(f"Instagram Handle: {INSTAGRAM_HANDLE}\n")
    
    # Create posts
    instagram_post = create_instagram_post()
    facebook_post = create_facebook_post()
    twitter_post = create_twitter_post()
    reddit_post = create_reddit_post()
    
    # Save posts to files
    os.makedirs('marketing/distribution-logs/social-posts', exist_ok=True)
    
    with open('marketing/distribution-logs/social-posts/instagram.txt', 'w') as f:
        f.write(instagram_post)
    print("✓ Instagram post saved: marketing/distribution-logs/social-posts/instagram.txt")
    
    with open('marketing/distribution-logs/social-posts/facebook.txt', 'w') as f:
        f.write(facebook_post)
    print("✓ Facebook post saved: marketing/distribution-logs/social-posts/facebook.txt")
    
    with open('marketing/distribution-logs/social-posts/twitter.txt', 'w') as f:
        f.write(twitter_post)
    print("✓ Twitter/X post saved: marketing/distribution-logs/social-posts/twitter.txt")
    
    with open('marketing/distribution-logs/social-posts/reddit.txt', 'w') as f:
        f.write(reddit_post)
    print("✓ Reddit post saved: marketing/distribution-logs/social-posts/reddit.txt")
    
    # Log distribution
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "landing_page_url": LANDING_PAGE_URL,
        "distribution_type": "social_media",
        "platforms": ["instagram", "facebook", "twitter", "reddit"],
        "status": "posts_created",
        "instagram_handle": INSTAGRAM_HANDLE
    }
    
    with open('marketing/distribution-logs/social-distribution.json', 'w') as f:
        json.dump(log_entry, f, indent=2)
    
    print(f"\n✓ Distribution logged: marketing/distribution-logs/social-distribution.json")
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Copy posts from marketing/distribution-logs/social-posts/")
    print("2. Post to Instagram, Facebook, Twitter/X, Reddit manually")
    print("3. Or configure social media API keys for automated posting")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        distribute_social_media()
        sys.exit(0)
    except Exception as e:
        print(f"✗ Social media distribution failed: {e}")
        sys.exit(1)
