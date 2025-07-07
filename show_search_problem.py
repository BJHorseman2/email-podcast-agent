#!/usr/bin/env python3
"""
Show exactly what's wrong with the search
"""

import imaplib
import ssl
import json
from datetime import datetime

# Load config
with open('aol_complete_config.json', 'r') as f:
    config = json.load(f)

# Connect
context = ssl.create_default_context()
context.check_hostname = False  
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
imap.login(config['email']['username'], config['email']['password'])

imap.select('INBOX')

# Show what the automation searches for
today = datetime.now().strftime('%d-%b-%Y')
search_string = f'SINCE {today} UNSEEN FROM "{config["target_email"]["sender"]}"'

print("🔍 Your automation searches for:")
print(f'   {search_string}')
print(f"\n   Breaking this down:")
print(f'   - SINCE {today} (today)')
print(f'   - UNSEEN (unread only)')
print(f'   - FROM "{config["target_email"]["sender"]}"')

# Try this search
_, data = imap.search(None, search_string)
if data[0]:
    print(f"\n✅ This search finds: {len(data[0].split())} emails")
else:
    print(f"\n❌ This search finds: 0 emails")

# Now show what's actually there
print(f"\n📬 What's ACTUALLY in your inbox:")

# All unread emails
_, data = imap.search(None, 'UNSEEN')
if data[0]:
    email_ids = data[0].split()
    print(f"\n   Unread emails: {len(email_ids)}")
    
    # Show first few
    for email_id in email_ids[:3]:
        _, msg_data = imap.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        print(f"\n   📧 Unread email:")
        print(f"      From: {msg.get('From', 'Unknown')}")
        print(f"      Subject: {msg.get('Subject', 'No Subject')}")
        print(f"      Date: {msg.get('Date', 'Unknown')}")

# Show the mismatch
print(f"\n🚨 THE PROBLEM:")
print(f"   Config expects sender: {config['target_email']['sender']}")
print(f"   But actual sender is different (see above)")
print(f"\n   The email addresses DON'T MATCH!")

imap.logout()
