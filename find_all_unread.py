#!/usr/bin/env python3
"""
Find ALL unread emails to see what's there
"""

import imaplib
import email
import ssl
import json
from datetime import datetime

# Load config
with open('aol_complete_config.json', 'r') as f:
    config = json.load(f)

# Connect
print("🔗 Connecting to AOL...")
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
imap.login(config['email']['username'], config['email']['password'])
print("✅ Connected!")

# Get ALL UNSEEN emails
imap.select('INBOX')
print("\n🔍 Finding ALL unread emails...")

_, data = imap.search(None, 'UNSEEN')
if data[0]:
    email_ids = data[0].split()
    print(f"📬 Found {len(email_ids)} unread emails\n")
    
    # Show each one
    for i, email_id in enumerate(email_ids, 1):
        _, msg_data = imap.fetch(email_id, '(RFC822)')
        email_message = email.message_from_bytes(msg_data[0][1])
        
        subject = email_message.get('Subject', 'No Subject')
        sender = email_message.get('From', 'Unknown')
        date = email_message.get('Date', 'No Date')
        
        print(f"Email #{i}:")
        print(f"  📧 From: {sender}")
        print(f"  📋 Subject: {subject}")
        print(f"  📅 Date: {date}")
        
        # Check if this might be Mando
        if any(word in subject.lower() + sender.lower() for word in ['mando', 'minutes', 'puck', 'kelly']):
            print("  ✅ THIS LOOKS LIKE MANDO MINUTES!")
            
            # Save the actual sender
            with open('actual_mando_sender.txt', 'w') as f:
                f.write(f"Actual sender: {sender}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"Update your config to search for this sender!\n")
        
        print()
else:
    print("❌ No unread emails found!")
    print("\nLet's check recent emails (read or unread)...")
    
    # Search for all emails from today
    today = datetime.now().strftime('%d-%b-%Y')
    _, data = imap.search(None, f'SINCE {today}')
    
    if data[0]:
        email_ids = data[0].split()
        print(f"\n📬 Found {len(email_ids)} emails from today\n")
        
        for i, email_id in enumerate(email_ids[-5:], 1):  # Last 5 emails
            _, msg_data = imap.fetch(email_id, '(RFC822)')
            email_message = email.message_from_bytes(msg_data[0][1])
            
            subject = email_message.get('Subject', 'No Subject')
            sender = email_message.get('From', 'Unknown')
            
            print(f"Recent Email #{i}:")
            print(f"  📧 From: {sender}")
            print(f"  📋 Subject: {subject}")
            
            if any(word in subject.lower() + sender.lower() for word in ['mando', 'minutes', 'puck']):
                print("  ✅ THIS IS MANDO MINUTES!")
            print()

print("\n📌 Current config is looking for:")
print(f"   Sender: {config['target_email']['sender']}")
print("   ⚠️  This might be wrong! Check the actual sender above.")

imap.logout()
