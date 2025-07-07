#!/usr/bin/env python3
"""
Count the news items in today's Mando Minutes
Shows why 120 words is ridiculous for this much content
"""

import imaplib
import email
import ssl
import json

# Load config
with open('multi_newsletter_config.json', 'r') as f:
    config = json.load(f)

# Connect and find Mando
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
imap.login(config['email']['username'], config['email']['password'])

imap.select('INBOX')
_, data = imap.search(None, 'SUBJECT "Mando Minutes" SINCE 07-Jul-2025')

if data[0]:
    email_id = data[0].split()[0]
    _, msg_data = imap.fetch(email_id, '(RFC822)')
    email_message = email.message_from_bytes(msg_data[0][1])
    
    # Extract body
    body = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                break
    else:
        body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
    
    # Count items
    lines = body.split('\n')
    bullet_points = [l for l in lines if l.strip().startswith(('•', '-', '*'))]
    price_lines = [l for l in lines if any(x in l for x in ['BTC:', 'ETH:', 'NASDAQ:'])]
    
    total_items = len(bullet_points) + len(price_lines)
    
    print("📊 MANDO MINUTES CONTENT ANALYSIS")
    print("=" * 50)
    print(f"Email has:")
    print(f"  • {len(bullet_points)} news items")
    print(f"  • {len(price_lines)} price updates")
    print(f"  • {total_items} TOTAL items to cover")
    print()
    print(f"❌ Your 120-word podcast = {120/total_items:.1f} words per item")
    print(f"   That's less than a tweet per story!")
    print()
    print(f"✅ Comprehensive podcast = ~{1500/total_items:.0f} words per item")
    print(f"   That's actual analysis and insights!")
    print()
    print("Run this to get REAL coverage:")
    print("👉 python3 process_mando_comprehensive.py")

imap.logout()
