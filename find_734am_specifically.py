#!/usr/bin/env python3
"""
Find email from around 7:34 AM today
"""

import imaplib
import ssl
import json
from datetime import datetime
import email
from email.utils import parsedate_to_datetime

# Connect
with open('aol_complete_config.json', 'r') as f:
    config = json.load(f)

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
imap.login(config['email']['username'], config['email']['password'])

imap.select('INBOX')

# Search for emails from this morning
today = datetime.now().strftime('%d-%b-%Y')
print(f"🔍 Looking for emails from this morning ({today})...\n")

# Get emails from today
_, data = imap.search(None, f'SINCE {today}')
if not data[0]:
    print("No emails from today!")
    exit()

email_ids = data[0].split()
print(f"Found {len(email_ids)} emails from today\n")

# Check emails from around 7-8 AM
morning_emails = []
for email_id in email_ids:
    _, msg_data = imap.fetch(email_id, '(RFC822)')
    email_message = email.message_from_bytes(msg_data[0][1])
    
    # Check time
    date_str = email_message.get('Date', '')
    try:
        email_time = parsedate_to_datetime(date_str)
        if 7 <= email_time.hour <= 8:  # 7-8 AM
            morning_emails.append((email_id, email_message, email_time))
    except:
        pass

print(f"📬 Found {len(morning_emails)} emails between 7-8 AM:\n")

# Show each one
for email_id, email_message, email_time in morning_emails:
    subject = email_message.get('Subject', 'No Subject')
    sender = email_message.get('From', 'Unknown')
    time_str = email_time.strftime('%I:%M %p')
    
    # Check if unread
    _, flags_data = imap.fetch(email_id, '(FLAGS)')
    is_unread = '\\Seen' not in str(flags_data[0])
    
    print(f"Email at {time_str}:")
    print(f"  From: {sender}")
    print(f"  Subject: {subject}")
    print(f"  Status: {'UNREAD ✨' if is_unread else 'Read'}")
    
    # Is this Mando?
    if '7:3' in time_str and is_unread:
        print(f"  ✅ This looks like the 7:34 AM Mando Minutes!")
        
        choice = input("\nProcess this email? (y/n): ")
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
            script = agent.create_podcast_script(subject, body, sender)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"podcasts/mando_734am_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(script)
            
            print(f"\n✅ Enhanced podcast created!")
            print(f"📝 File: {filename}")
            print(f"📊 Length: {len(script.split())} words")
            print(f"\n🔧 FIX: Update config sender to: {sender}")
            break
    
    print()

imap.logout()
