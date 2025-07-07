#!/usr/bin/env python3
"""
Debug and process today's Mando Minutes
"""

import imaplib
import email
import ssl
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

# Load config
with open('aol_complete_config.json', 'r') as f:
    config = json.load(f)

# Connect to AOL
print("🔗 Connecting to AOL...")
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
imap.login(config['email']['username'], config['email']['password'])
print("✅ Connected to AOL!")

# Search for today's emails with various criteria
imap.select('INBOX')
today = datetime.now().strftime('%d-%b-%Y')

print(f"\n🔍 Searching for Mando Minutes emails from today ({today})...")

# Try multiple search patterns
search_patterns = [
    f'SINCE {today} FROM "puck.news"',
    f'SINCE {today} FROM "mandominutes"',
    f'SINCE {today} FROM "mando"',
    f'SINCE {today} SUBJECT "mando"',
    f'SINCE {today} SUBJECT "minutes"',
    f'SINCE {today} FROM "jon"',
    f'SINCE {today} FROM "kelly"',
    f'SINCE {today}'  # All emails from today
]

all_emails = []
for pattern in search_patterns:
    print(f"   Trying: {pattern}")
    _, data = imap.search(None, pattern)
    if data[0]:
        email_ids = data[0].split()
        print(f"   ✅ Found {len(email_ids)} emails")
        all_emails.extend(email_ids)

# Remove duplicates
all_emails = list(set(all_emails))
print(f"\n📧 Total unique emails found today: {len(all_emails)}")

# Check each email
mando_found = False
for email_id in all_emails:
    _, data = imap.fetch(email_id, '(RFC822)')
    raw_email = data[0][1]
    email_message = email.message_from_bytes(raw_email)
    
    subject = email_message.get('Subject', '')
    sender = email_message.get('From', '')
    
    print(f"\n📨 Email ID {email_id}:")
    print(f"   From: {sender}")
    print(f"   Subject: {subject}")
    
    # Check if this is Mando Minutes
    if ('mando' in subject.lower() or 'mando' in sender.lower() or 
        'puck' in sender.lower() or 'minutes' in subject.lower()):
        print("   ✅ THIS IS MANDO MINUTES!")
        mando_found = True
        
        # Process this email
        print("\n🚀 Processing this email with enhanced automation...")
        
        # Save the email details for processing
        with open('found_mando_email.json', 'w') as f:
            json.dump({
                'email_id': email_id.decode(),
                'subject': subject,
                'sender': sender,
                'found_at': datetime.now().isoformat()
            }, f, indent=2)
        
        # Now run the enhanced processing
        from enhanced_complete_automation import EnhancedPodcastAutomationAgent
        agent = EnhancedPodcastAutomationAgent()
        
        # Process the email
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        # Create enhanced podcast
        script = agent.create_podcast_script(subject, body, sender)
        print(f"\n📊 Created podcast script: {len(script.split())} words")
        
        # Save and process
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        script_file = f"podcasts/mando_fixed_{timestamp}.txt"
        with open(script_file, 'w') as f:
            f.write(script)
        
        print(f"✅ Script saved: {script_file}")
        
        # Generate audio and send email
        print("\n🎙️ Generating audio and sending email...")
        # This would call your complete automation
        
        break

if not mando_found:
    print("\n❌ No Mando Minutes email found today!")
    print("\n💡 Suggestions:")
    print("1. Check if the email arrived")
    print("2. The sender might be different than expected")
    print("3. Update the config with the correct sender")

# Show config for reference
print(f"\n📋 Current config looks for:")
print(f"   Sender: {config['target_email']['sender']}")
print(f"   Subject contains: {config['target_email']['subject_contains']}")

imap.logout()
