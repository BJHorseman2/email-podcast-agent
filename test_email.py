#!/usr/bin/env python3
"""
Check why email isn't working
"""

import smtplib
import json
from email.mime.text import MIMEText

# Load config
with open('multi_newsletter_config.json', 'r') as f:
    config = json.load(f)

print("🔍 Testing email configuration...")
print(f"Email: {config['email']['username']}")
print(f"Server: smtp.aol.com:587")

# Test connection
try:
    print("\n📧 Testing SMTP connection...")
    server = smtplib.SMTP('smtp.aol.com', 587)
    server.set_debuglevel(1)
    server.starttls()
    server.login(config['email']['username'], config['email']['password'])
    
    # Send test email
    msg = MIMEText("This is a test email from your Mando Minutes system.")
    msg['Subject'] = "Test: Mando Minutes System"
    msg['From'] = config['email']['username']
    msg['To'] = config['email']['username']
    
    server.send_message(msg)
    server.quit()
    
    print("\n✅ Email test successful! Check your inbox for test message.")
    
except Exception as e:
    print(f"\n❌ Email test failed: {e}")
    print("\nPossible issues:")
    print("1. Password might be wrong")
    print("2. Need app-specific password for AOL")
    print("3. Internet connection issue")
