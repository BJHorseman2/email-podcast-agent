#!/usr/bin/env python3
"""
Simple AOL Email to Podcast Agent
Reliable version that works with AOL's email system
"""

import imaplib
import smtplib
import email
import json
import os
import ssl
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class SimpleAOLAgent:
    def __init__(self):
        self.config = self.load_config()
        
    def load_config(self):
        """Load AOL configuration"""
        try:
            with open('aol_complete_config.json', 'r') as f:
                return json.load(f)
        except:
            print("❌ Config file not found")
            return None
    
    def test_aol_connection(self):
        """Test AOL email connection with better error handling"""
        print("🧪 Testing AOL Email Connection")
        print("=" * 40)
        
        try:
            print("1. Testing AOL IMAP...")
            
            # Create IMAP connection with custom SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
            imap.login(self.config['email']['username'], self.config['email']['password'])
            
            # Test inbox access
            imap.select('INBOX')
            _, messages = imap.search(None, 'ALL')
            total_emails = len(messages[0].split()) if messages[0] else 0
            
            print(f"   ✅ AOL IMAP connected successfully!")
            print(f"   📧 Found {total_emails} emails in inbox")
            
            imap.close()
            imap.logout()
            
        except Exception as e:
            print(f"   ❌ AOL IMAP failed: {e}")
            return False
        
        try:
            print("2. Testing AOL SMTP...")
            
            server = smtplib.SMTP('smtp.aol.com', 587)
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.quit()
            
            print("   ✅ AOL SMTP connected successfully!")
            
        except Exception as e:
            print(f"   ❌ AOL SMTP failed: {e}")
            return False
        
        print("\n🎉 AOL Connection Test: SUCCESS!")
        print("✅ Ready to process Puck News emails")
        return True
    
    def find_puck_email(self):
        """Find Jon Kelly / Puck News email"""
        try:
            print("🔍 Looking for Puck News email...")
            
            # Connect with relaxed SSL
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
            imap.login(self.config['email']['username'], self.config['email']['password'])
            imap.select('INBOX')
            
            # Search for Jon Kelly emails
            _, messages = imap.search(None, 'FROM "jonkelly@puck.news"')
            
            if not messages[0]:
                print("📭 No Puck News emails found")
                imap.close()
                imap.logout()
                return None
            
            # Get the most recent email
            email_ids = messages[0].split()
            latest_id = email_ids[-1]
            
            _, msg_data = imap.fetch(latest_id, '(RFC822)')
            email_message = email.message_from_bytes(msg_data[0][1])
            
            subject = email_message['Subject']
            sender = email_message['From']
            date = email_message['Date']
            
            print(f"📧 Found email: {subject}")
            print(f"📅 Date: {date}")
            
            # Extract body
            body = self.extract_body(email_message)
            
            imap.close()
            imap.logout()
            
            return {
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body[:500] + "..." if len(body) > 500 else body
            }
            
        except Exception as e:
            print(f"❌ Error finding email: {e}")
            return None
    
    def extract_body(self, email_message):
        """Extract email body text"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                        break
        else:
            payload = email_message.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
        
        # Clean up
        body = re.sub(r'\n\s*\n', '\n\n', body)
        body = body.strip()
        
        return body
    
    def create_simple_script(self, email_data):
        """Create a basic podcast script"""
        script = f"""
Good morning! Welcome to your Puck News podcast.

Today's update from Jon Kelly:

{email_data['subject']}

Here's what you need to know:

{email_data['body']}

That's your Puck News update for today. Stay informed!
        """.strip()
        
        return script
    
    def send_test_email(self, email_data, script):
        """Send test email via AOL"""
        try:
            print("📧 Sending test email...")
            
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = self.config['email']['username']
            msg['Subject'] = f"🎙️ Test Podcast - {email_data['subject']}"
            
            body = f"""
Good morning!

This is a test of your AOL email-to-podcast system.

Original email: {email_data['subject']}
From: {email_data['sender']}

Podcast Script:
{script}

🤖 Automated by your AOL Email-to-Podcast Agent
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.aol.com', 587)
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.sendmail(self.config['email']['username'], self.config['email']['username'], msg.as_string())
            server.quit()
            
            print("✅ Test email sent to your AOL inbox!")
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False
    
    def run_full_test(self):
        """Run complete system test"""
        print("🚀 AOL Email-to-Podcast Agent - Full Test")
        print("=" * 50)
        
        if not self.config:
            print("❌ Configuration not loaded")
            return
        
        # Step 1: Test connection
        if not self.test_aol_connection():
            print("❌ Connection test failed")
            return
        
        # Step 2: Find Puck email
        email_data = self.find_puck_email()
        if not email_data:
            print("📭 No Puck emails found - that's normal if none received recently")
            return
        
        # Step 3: Create script
        script = self.create_simple_script(email_data)
        
        # Step 4: Send test email
        if self.send_test_email(email_data, script):
            print("\n🎉 FULL TEST SUCCESSFUL!")
            print("📧 Check your AOL inbox for the test podcast email!")
        else:
            print("❌ Test email failed")

def main():
    agent = SimpleAOLAgent()
    agent.run_full_test()

if __name__ == "__main__":
    main()
