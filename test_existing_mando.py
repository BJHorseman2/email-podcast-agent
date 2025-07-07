#!/usr/bin/env python3
"""
Test the enhanced agent with existing Mando Minutes emails
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_complete_automation import EnhancedPodcastAutomationAgent
import imaplib
import email
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

def test_with_existing_email():
    """Process existing Mando Minutes emails (including already seen ones)"""
    
    agent = EnhancedPodcastAutomationAgent()
    
    # Connect to AOL
    imap = agent.connect_to_aol()
    if not imap:
        return
    
    try:
        imap.select('INBOX')
        
        # Search for ANY Mando Minutes email from the last 7 days
        # Remove UNSEEN filter to get all emails
        since_date = (datetime.now() - timedelta(days=7)).strftime('%d-%b-%Y')
        
        # Try multiple search criteria
        search_queries = [
            f'SINCE {since_date} FROM "puck.news"',
            f'SINCE {since_date} SUBJECT "mando"',
            f'SINCE {since_date} FROM "jon kelly"',
            f'SINCE {since_date} SUBJECT "minutes"'
        ]
        
        email_ids = []
        for query in search_queries:
            logging.info(f"Searching: {query}")
            _, data = imap.search(None, query)
            if data[0]:
                email_ids.extend(data[0].split())
        
        # Remove duplicates
        email_ids = list(set(email_ids))
        logging.info(f"Found {len(email_ids)} Mando emails (including already read)")
        
        if not email_ids:
            logging.error("No Mando Minutes emails found in the last 7 days")
            return
        
        # Process the most recent one
        latest_id = email_ids[-1]
        logging.info(f"Processing email ID: {latest_id}")
        
        _, data = imap.fetch(latest_id, '(RFC822)')
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)
        
        # Extract email details
        subject = email_message.get('Subject', 'No Subject')
        sender = email_message.get('From', 'Unknown')
        
        logging.info(f"📧 Subject: {subject}")
        logging.info(f"👤 From: {sender}")
        
        # Get email body
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        # Create enhanced podcast script
        logging.info("Creating enhanced podcast with link following...")
        script = agent.create_podcast_script(subject, body, sender)
        
        # Save the enhanced script
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"podcasts/mando_enhanced_test_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(script)
        
        logging.info(f"✅ Enhanced script saved: {filename}")
        logging.info(f"📊 Script stats: {len(script.split())} words, {len(script)} characters")
        
        # Show preview
        print("\n" + "="*60)
        print("ENHANCED PODCAST PREVIEW:")
        print("="*60)
        print(script[:500] + "...")
        print("="*60)
        
    finally:
        imap.logout()

if __name__ == "__main__":
    print("🧪 Testing enhanced Mando Minutes with existing emails...\n")
    test_with_existing_email()
