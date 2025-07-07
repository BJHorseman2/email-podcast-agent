#!/usr/bin/env python3
"""
Find Mando in 8827 emails - search smartly!
"""

import imaplib
import ssl
import json
from datetime import datetime
import email

# Connect
with open('aol_complete_config.json', 'r') as f:
    config = json.load(f)

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
imap.login(config['email']['username'], config['email']['password'])
print("✅ Connected to AOL")

imap.select('INBOX')

# Search ONLY for today's unread emails
today = datetime.now().strftime('%d-%b-%Y')
print(f"\n🔍 Searching for UNREAD emails from TODAY ({today}) only...")

# Multiple search strategies for today's emails
searches = [
    f'UNSEEN SINCE {today} SUBJECT "mando"',
    f'UNSEEN SINCE {today} SUBJECT "minutes"',
    f'UNSEEN SINCE {today} FROM "mando"',
    f'UNSEEN SINCE {today} FROM "minutes"',
    f'UNSEEN SINCE {today} FROM "beehiiv"',
    f'UNSEEN SINCE {today} FROM "puck"',
    f'UNSEEN SINCE {today}'  # All unread from today
]

found_emails = []
for search in searches:
    print(f"   Trying: {search}")
    _, data = imap.search(None, search)
    if data[0]:
        count = len(data[0].split())
        print(f"   Found: {count} emails")
        
        if count < 50:  # Only process if reasonable number
            for email_id in data[0].split():
                if email_id not in found_emails:
                    found_emails.append(email_id)

print(f"\n📬 Found {len(found_emails)} potential emails from today")

# Check each one
mando_found = False
for email_id in found_emails:
    _, msg_data = imap.fetch(email_id, '(RFC822)')
    email_message = email.message_from_bytes(msg_data[0][1])
    
    subject = email_message.get('Subject', '')
    sender = email_message.get('From', '')
    date = email_message.get('Date', '')
    
    # Quick check for Mando
    if any(word in (subject + sender).lower() for word in ['mando', 'minutes', 'jon', 'kelly']):
        print(f"\n✅ FOUND MANDO MINUTES!")
        print(f"   From: {sender}")
        print(f"   Subject: {subject}")
        print(f"   Date: {date}")
        
        # Process immediately
        from enhanced_complete_automation import EnhancedPodcastAutomationAgent
        agent = EnhancedPodcastAutomationAgent()
        
        # Get body
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        # Create podcast
        print("\n🚀 Creating enhanced podcast...")
        script = agent.create_podcast_script(subject, body, sender)
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"podcasts/mando_found_in_8k_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(script)
        
        print(f"✅ Podcast created: {filename}")
        print(f"📊 Length: {len(script.split())} words")
        
        print(f"\n⚠️  UPDATE YOUR CONFIG!")
        print(f'Change sender from: {config["target_email"]["sender"]}')
        print(f'To actual sender: {sender}')
        
        # Generate audio if you want
        choice = input("\nGenerate audio file? (y/n): ")
        if choice.lower() == 'y':
            # Add your audio generation here
            print("Audio generation would happen here...")
        
        mando_found = True
        break

if not mando_found:
    print("\n❌ No Mando Minutes found in today's emails")
    print("\n💡 With 8,827 unread emails, consider:")
    print("1. Cleaning up your inbox")
    print("2. Creating a filter/folder for Mando Minutes")
    print("3. Using a dedicated email address for newsletters")

imap.logout()
