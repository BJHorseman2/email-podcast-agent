#!/usr/bin/env python3
"""
Just process the first unread email - no questions asked
"""

import imaplib
import ssl
import json
from enhanced_complete_automation import EnhancedPodcastAutomationAgent
import email

# Connect
with open('aol_complete_config.json', 'r') as f:
    config = json.load(f)

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
imap.login(config['email']['username'], config['email']['password'])

# Get first unread email
imap.select('INBOX')
_, data = imap.search(None, 'UNSEEN')

if not data[0]:
    print("No unread emails!")
    exit()

# Process the FIRST unread email
email_id = data[0].split()[0]
_, msg_data = imap.fetch(email_id, '(RFC822)')
email_message = email.message_from_bytes(msg_data[0][1])

subject = email_message.get('Subject', 'No Subject')
sender = email_message.get('From', 'Unknown')

print(f"Processing: {subject}")
print(f"From: {sender}")

# Get body and process
agent = EnhancedPodcastAutomationAgent()
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
print(f"\n✅ Podcast created: {len(script.split())} words")

# Save it
with open('podcasts/mando_processed.txt', 'w') as f:
    f.write(script)

print(f"\n⚠️  FIX YOUR CONFIG!")
print(f'Change "sender" to: "{sender}"')

imap.logout()
