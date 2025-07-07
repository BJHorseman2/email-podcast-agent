#!/usr/bin/env python3
"""
Find the 7:34am Mando Minutes email and show why it's not being picked up
"""

import imaplib
import email
import ssl
import json
from datetime import datetime
from email.utils import parsedate_to_datetime

# Connect
with open('aol_complete_config.json', 'r') as f:
    config = json.load(f)

print("🔗 Connecting to AOL...")
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
imap.login(config['email']['username'], config['email']['password'])
print("✅ Connected!")

# Get ALL emails from today
imap.select('INBOX')
today = datetime.now().strftime('%d-%b-%Y')

print(f"\n🔍 Looking for ALL emails from today ({today})...")

# First, let's see what the automation is searching for
print(f"\n⚠️  Your config is searching for:")
print(f"   Sender: {config['target_email']['sender']}")
print(f"   This is probably WRONG!\n")

# Search for all emails from today
_, data = imap.search(None, f'SINCE {today}')
if not data[0]:
    print("❌ No emails from today found!")
    exit()

email_ids = data[0].split()
print(f"📬 Found {len(email_ids)} emails from today\n")

# Check each email
mando_found = False
for email_id in email_ids:
    _, msg_data = imap.fetch(email_id, '(RFC822)')
    email_message = email.message_from_bytes(msg_data[0][1])
    
    subject = email_message.get('Subject', 'No Subject')
    sender = email_message.get('From', 'Unknown')
    date_str = email_message.get('Date', '')
    
    # Parse time
    try:
        email_time = parsedate_to_datetime(date_str)
        time_str = email_time.strftime('%I:%M %p')
    except:
        time_str = "Unknown time"
    
    # Check if this is around 7:34am
    if '7:3' in time_str or '07:3' in time_str:
        print(f"📧 Email at {time_str}:")
        print(f"   From: {sender}")
        print(f"   Subject: {subject}")
        
        # Check if unread
        _, flags_data = imap.fetch(email_id, '(FLAGS)')
        flags_str = str(flags_data[0])
        is_unread = '\\Seen' not in flags_str
        print(f"   Status: {'UNREAD' if is_unread else 'Read'}")
        
        # This is probably Mando!
        if any(word in (subject + sender).lower() for word in ['mando', 'minutes', 'newsletter']):
            print(f"   ✅ THIS IS MANDO MINUTES!")
            mando_found = True
            
            print(f"\n🚨 FOUND THE PROBLEM!")
            print(f"   Your config searches for: {config['target_email']['sender']}")
            print(f"   But actual sender is: {sender}")
            print(f"   THEY DON'T MATCH!\n")
            
            # Process it now
            choice = input("Process this email now? (y/n): ")
            if choice.lower() == 'y':
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
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"podcasts/mando_7am_{timestamp}.txt"
                with open(filename, 'w') as f:
                    f.write(script)
                
                print(f"✅ Podcast created: {filename}")
                print(f"📊 Length: {len(script.split())} words")
                
                # Save correct sender
                with open('correct_mando_sender.txt', 'w') as f:
                    f.write(f"Update your aol_complete_config.json:\n")
                    f.write(f'"sender": "{sender}"\n')
                    f.write(f"\nOr use multiple senders:\n")
                    f.write(f'"sender": ["jonkelly@puck.news", "{sender}"]\n')
        
        print()

if not mando_found:
    print("\n🔍 Let me check UNREAD emails specifically...")
    _, data = imap.search(None, 'UNSEEN')
    if data[0]:
        email_ids = data[0].split()
        print(f"Found {len(email_ids)} unread emails:")
        
        for email_id in email_ids[:5]:  # First 5
            _, msg_data = imap.fetch(email_id, '(RFC822)')
            email_message = email.message_from_bytes(msg_data[0][1])
            
            print(f"\nUnread email:")
            print(f"  From: {email_message.get('From')}")
            print(f"  Subject: {email_message.get('Subject')}")
            print(f"  Date: {email_message.get('Date')}")

imap.logout()
