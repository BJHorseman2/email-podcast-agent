#!/usr/bin/env python3
"""
Find Mando Minutes by exact subject: "Mando Minutes: 7 July"
"""

import imaplib
import ssl
import json
import email
from datetime import datetime

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

# Search for exact subject we can see in your screenshot
print("\n🔍 Searching for 'Mando Minutes: 7 July'...")

# Try different search approaches
searches = [
    'SUBJECT "Mando Minutes: 7 July"',
    'SUBJECT "Mando Minutes"',
    'BODY "BTC ATH weekly"',  # From the preview text
    f'SINCE 07-Jul-2025 BEFORE 08-Jul-2025'  # All emails from July 7
]

found = False
for search in searches:
    print(f"\nTrying: {search}")
    _, data = imap.search(None, search)
    
    if data[0]:
        email_ids = data[0].split()
        print(f"Found {len(email_ids)} emails")
        
        # Check each one
        for email_id in email_ids:
            _, msg_data = imap.fetch(email_id, '(RFC822)')
            email_message = email.message_from_bytes(msg_data[0][1])
            
            subject = email_message.get('Subject', '')
            sender = email_message.get('From', '')
            date = email_message.get('Date', '')
            
            print(f"\n📧 Email found:")
            print(f"   Subject: {subject}")
            print(f"   From: {sender}")
            print(f"   Date: {date}")
            
            # Is this the Mando email?
            if "Mando Minutes" in subject or "7 July" in subject:
                print(f"\n✅ FOUND IT! This is Mando Minutes!")
                print(f"\n🚨 THE ACTUAL SENDER IS: {sender}")
                print(f"🚨 Your config expects: {config['target_email']['sender']}")
                print(f"🚨 THEY DON'T MATCH!\n")
                
                # Save the correct sender
                with open('CORRECT_MANDO_SENDER.txt', 'w') as f:
                    f.write(f"CORRECT MANDO MINUTES SENDER:\n")
                    f.write(f"{sender}\n\n")
                    f.write(f"Update your aol_complete_config.json file:\n")
                    f.write(f'"sender": "{sender}"\n')
                
                # Process it
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
                print("\n🚀 Creating enhanced podcast with link following...")
                script = agent.create_podcast_script(subject, body, sender)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"podcasts/mando_july7_{timestamp}.txt"
                with open(filename, 'w') as f:
                    f.write(script)
                
                print(f"\n✅ ENHANCED PODCAST CREATED!")
                print(f"📝 File: {filename}")
                print(f"📊 Length: {len(script.split())} words")
                print(f"⏱️ Duration: ~{len(script.split()) / 150:.1f} minutes")
                
                found = True
                break
        
        if found:
            break

if not found:
    print("\n❌ Could not find the Mando Minutes email")
    print("This is strange since we can see it in your inbox!")
    print("\nTrying one more approach - get ALL emails from this morning...")
    
    # Get all morning emails
    _, data = imap.search(None, 'SINCE 07-Jul-2025')
    if data[0]:
        email_ids = data[0].split()
        print(f"\nFound {len(email_ids)} emails from today")
        print("Showing first 10:\n")
        
        for email_id in email_ids[:10]:
            _, msg_data = imap.fetch(email_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            print(f"- {msg.get('Subject', 'No Subject')[:50]}")
            print(f"  From: {msg.get('From', 'Unknown')}")

imap.logout()
