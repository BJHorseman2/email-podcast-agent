#!/usr/bin/env python3
"""
Process ANY unread email that looks like Mando Minutes
"""

import imaplib
import email
import ssl
import json
from datetime import datetime
from enhanced_complete_automation import EnhancedPodcastAutomationAgent

# Connect
with open('aol_complete_config.json', 'r') as f:
    config = json.load(f)

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
imap.login(config['email']['username'], config['email']['password'])

# Get ALL unread emails
imap.select('INBOX')
_, data = imap.search(None, 'UNSEEN')

if not data[0]:
    print("❌ No unread emails found!")
    imap.logout()
    exit()

email_ids = data[0].split()
print(f"📬 Checking {len(email_ids)} unread emails for Mando Minutes...\n")

# Check each unread email
for email_id in email_ids:
    _, msg_data = imap.fetch(email_id, '(RFC822)')
    email_message = email.message_from_bytes(msg_data[0][1])
    
    subject = email_message.get('Subject', '')
    sender = email_message.get('From', '')
    
    # Very flexible matching
    is_mando = False
    
    # Check various patterns
    if ('mando' in subject.lower() or 
        'minutes' in subject.lower() or
        'mando' in sender.lower() or
        'puck' in sender.lower() or
        'kelly' in sender.lower() or
        'jon' in sender.lower()):
        is_mando = True
    
    # Also check for common newsletter domains
    if any(domain in sender.lower() for domain in ['beehiiv', 'substack', 'puck.news']):
        if 'minutes' in subject.lower() or 'daily' in subject.lower():
            is_mando = True
    
    if is_mando:
        print(f"✅ FOUND MANDO MINUTES!")
        print(f"   From: {sender}")
        print(f"   Subject: {subject}")
        print(f"\n🚀 Processing with enhanced automation...\n")
        
        # Process it
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
        
        # Create enhanced podcast
        script = agent.create_podcast_script(subject, body, sender)
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"podcasts/mando_found_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(script)
        
        print(f"✅ Enhanced podcast created!")
        print(f"📝 Script: {filename}")
        print(f"📊 Length: {len(script.split())} words")
        
        # Update config with correct sender
        print(f"\n⚠️  UPDATE YOUR CONFIG!")
        print(f'   Change sender to: "{sender}"')
        
        imap.logout()
        exit()

print("❌ No Mando Minutes found in unread emails")
print("\nPossible issues:")
print("1. Email hasn't arrived yet")
print("2. Email was marked as read")
print("3. Email went to spam/another folder")

imap.logout()
