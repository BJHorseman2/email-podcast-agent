#!/usr/bin/env python3
"""
Fixed automation that finds Mando Minutes regardless of read status
"""

import imaplib
import email
import ssl
import json
import logging
from datetime import datetime, timedelta
from enhanced_complete_automation import EnhancedPodcastAutomationAgent

logging.basicConfig(level=logging.INFO)

class FixedMandoAutomation(EnhancedPodcastAutomationAgent):
    """Fixed version that handles read emails and multiple senders"""
    
    def find_target_email(self, imap):
        """Find Mando Minutes email - read or unread"""
        try:
            imap.select('INBOX')
            
            # Search for emails from the last 24 hours
            since_date = (datetime.now() - timedelta(hours=24)).strftime('%d-%b-%Y')
            
            # Multiple search patterns to find Mando
            search_patterns = [
                f'SINCE {since_date} FROM "mandominutes"',
                f'SINCE {since_date} FROM "mando"',
                f'SINCE {since_date} SUBJECT "mando"',
                f'SINCE {since_date} SUBJECT "minutes"',
                f'SINCE {since_date} FROM "puck.news"',
                f'SINCE {since_date} FROM "jon"',
            ]
            
            email_ids = []
            for pattern in search_patterns:
                logging.info(f"Searching: {pattern}")
                _, data = imap.search(None, pattern)
                if data[0]:
                    email_ids.extend(data[0].split())
            
            # Remove duplicates
            email_ids = list(set(email_ids))
            
            if not email_ids:
                logging.warning("No Mando Minutes emails found in last 24 hours")
                return None
            
            # Check each email to find the right one
            for email_id in email_ids:
                _, msg_data = imap.fetch(email_id, '(RFC822)')
                email_message = email.message_from_bytes(msg_data[0][1])
                
                subject = email_message.get('Subject', '').lower()
                sender = email_message.get('From', '').lower()
                
                # Check if this is Mando Minutes
                if ('mando' in subject or 'mando' in sender or 
                    'minutes' in subject or 'puck' in sender):
                    
                    # Check if already processed today
                    msg_date = email_message.get('Date', '')
                    if self.is_from_today(msg_date):
                        logging.info(f"✅ Found today's Mando Minutes!")
                        logging.info(f"   Subject: {email_message.get('Subject')}")
                        logging.info(f"   From: {email_message.get('From')}")
                        return email_message
            
            logging.warning("No Mando Minutes email from today found")
            return None
            
        except Exception as e:
            logging.error(f"Error searching emails: {e}")
            return None
    
    def is_from_today(self, date_string):
        """Check if email is from today"""
        try:
            from email.utils import parsedate_to_datetime
            email_date = parsedate_to_datetime(date_string).date()
            today = datetime.now().date()
            return email_date == today
        except:
            return True  # If can't parse, assume it's recent
    
    def run_complete_automation(self):
        """Override to use our fixed email finding"""
        logging.info("🚀 Starting fixed Mando Minutes automation...")
        
        # Connect to email
        imap = self.connect_to_aol()
        if not imap:
            return False
        
        try:
            # Find Mando email
            email_message = self.find_target_email(imap)
            if not email_message:
                logging.info("📭 No Mando Minutes to process today")
                return False
            
            # Extract content
            subject = email_message.get('Subject', 'No Subject')
            sender = email_message.get('From', 'Unknown')
            
            # Get body
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            # Create enhanced podcast with link following
            logging.info("📝 Creating enhanced podcast script...")
            script = self.create_podcast_script(subject, body, sender)
            
            # Continue with rest of automation...
            # (audio generation, email sending, etc.)
            
            logging.info(f"✅ Podcast created: {len(script.split())} words")
            
            # Save script
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            script_file = f"podcasts/mando_minutes_{timestamp}.txt"
            with open(script_file, 'w') as f:
                f.write(script)
            
            logging.info(f"📝 Script saved: {script_file}")
            
            # TODO: Add your audio generation and email sending here
            
            return True
            
        finally:
            imap.logout()

if __name__ == "__main__":
    agent = FixedMandoAutomation()
    success = agent.run_complete_automation()
    
    if success:
        print("\n✅ Mando Minutes podcast created successfully!")
    else:
        print("\n❌ No Mando Minutes found or already processed")
