#!/usr/bin/env python3
"""
Process the most recent Mando Minutes email - whether seen or unseen
"""

import imaplib
import email
import ssl
import json
import logging
from datetime import datetime
from enhanced_complete_automation import EnhancedPodcastAutomationAgent

logging.basicConfig(level=logging.INFO)

# Load config
with open('aol_complete_config.json', 'r') as f:
    config = json.load(f)

# Create agent
agent = EnhancedPodcastAutomationAgent()

# Connect to AOL
print("🔗 Connecting to AOL...")
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
imap.login(config['email']['username'], config['email']['password'])
print("✅ Connected!")

# Get the MOST RECENT email (seen or unseen)
imap.select('INBOX')

# Search for ALL recent emails (remove UNSEEN requirement)
_, data = imap.search(None, 'ALL')
email_ids = data[0].split()

if not email_ids:
    print("❌ No emails found in inbox")
    exit()

# Get the last email
latest_id = email_ids[-1]
print(f"📧 Processing most recent email (ID: {latest_id})")

# Fetch and process
_, data = imap.fetch(latest_id, '(RFC822)')
raw_email = data[0][1]
email_message = email.message_from_bytes(raw_email)

# Get email details
subject = email_message.get('Subject', 'No Subject')
sender = email_message.get('From', 'Unknown')
print(f"📋 Subject: {subject}")
print(f"👤 From: {sender}")

# Check if it's Mando Minutes
if 'mando' not in subject.lower() and 'puck' not in sender.lower():
    print("⚠️  This doesn't look like Mando Minutes. Processing anyway...")

# Run the complete automation process
print("\n🚀 Running enhanced automation...")
agent.email_message = email_message  # Pass the email to agent

# Process it
result = agent.run_complete_automation()

print("\n✅ Done! Check your email for the enhanced podcast")

imap.logout()
