#!/usr/bin/env python3
"""
Mando Minutes Link-Following Email Agent
Specifically designed for link-heavy newsletters like Mando Minutes
"""

import imaplib
import email
import ssl
import json
import logging
from datetime import datetime, timedelta
from link_following_agent import LinkFollowingNewsletterAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mando_minutes_agent.log'),
        logging.StreamHandler()
    ]
)

class MandoMinutesAgent(LinkFollowingNewsletterAgent):
    def __init__(self):
        super().__init__()
        # Add Mando-specific trusted domains
        self.trusted_domains.update({
            'puck.news', 'axios.com', 'politico.com', 'semafor.com',
            'theinformation.com', 'stratechery.com'
        })
    
    def connect_to_email(self, email_config):
        """Connect to email server (AOL/IMAP)"""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Connect to server
            if email_config['server'] == 'imap.aol.com':
                mail = imaplib.IMAP4_SSL(email_config['server'], 993, ssl_context=context)
            else:
                mail = imaplib.IMAP4_SSL(email_config['server'], 993)
            
            mail.login(email_config['email'], email_config['password'])
            logging.info(f"✅ Connected to {email_config['server']} successfully!")
            return mail
            
        except Exception as e:
            logging.error(f"❌ Failed to connect: {e}")
            return None
    
    def fetch_recent_mando_emails(self, mail, days_back=1):
        """Fetch recent emails from Mando Minutes or similar senders"""
        try:
            mail.select('INBOX')
            
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=days_back)).strftime('%d-%b-%Y')
            
            # Search for Mando Minutes emails
            search_criteria = [
                f'(SINCE {since_date} FROM "mando")',
                f'(SINCE {since_date} SUBJECT "mando minutes")',
                f'(SINCE {since_date} FROM "puck.news")',
            ]
            
            email_ids = []
            for criteria in search_criteria:
                result, data = mail.search(None, criteria)
                if result == 'OK' and data[0]:
                    email_ids.extend(data[0].split())
            
            # Remove duplicates
            email_ids = list(set(email_ids))
            logging.info(f"Found {len(email_ids)} Mando Minutes emails")
            
            return email_ids
            
        except Exception as e:
            logging.error(f"Error searching emails: {e}")
            return []
    
    def process_mando_minutes(self):
        """Main process to handle Mando Minutes newsletters"""
        if not self.config:
            logging.error("No configuration found")
            return
        
        # Look for Mando Minutes config or create one
        mando_config = None
        for newsletter in self.config.get('newsletters', []):
            if 'mando' in newsletter['newsletter_name'].lower():
                mando_config = newsletter
                break
        
        if not mando_config:
            logging.error("No Mando Minutes configuration found")
            return
        
        # Connect to email
        mail = self.connect_to_email(mando_config)
        if not mail:
            return
        
        try:
            # Fetch recent Mando emails
            email_ids = self.fetch_recent_mando_emails(mail)
            
            if not email_ids:
                logging.info("No recent Mando Minutes emails found")
                return
            
            # Process each email
            for email_id in email_ids[-3:]:  # Process last 3 emails
                try:
                    result, data = mail.fetch(email_id, '(RFC822)')
                    if result == 'OK':
                        raw_email = data[0][1]
                        email_message = email.message_from_bytes(raw_email)
                        
                        # Process with link following
                        logging.info("Processing Mando Minutes email with link following...")
                        self.process_newsletter_with_links(email_message, mando_config)
                        
                except Exception as e:
                    logging.error(f"Error processing email {email_id}: {e}")
            
        finally:
            mail.logout()
            logging.info("Disconnected from email server")
    
    def create_enhanced_podcast_script(self, email_subject, sender, email_content, 
                                     articles, newsletter_name):
        """Create Mando-specific podcast script"""
        
        script = f"""Good morning! Welcome to your Mando Minutes podcast for {datetime.now().strftime('%A, %B %d, %Y')}.

I'm your AI host, bringing you the latest insights from {sender}.

"""
        
        # For Mando Minutes, the email content is mostly links, so focus on fetched articles
        if articles:
            script += f"Today we have {len(articles)} stories to cover. Let's dive in!\n\n"
            
            # Group articles by topic if possible
            crypto_articles = [a for a in articles if any(word in a['title'].lower() 
                             for word in ['crypto', 'bitcoin', 'eth', 'blockchain'])]
            macro_articles = [a for a in articles if any(word in a['title'].lower() 
                            for word in ['market', 'stock', 'economy', 'inflation', 'fed'])]
            other_articles = [a for a in articles if a not in crypto_articles and a not in macro_articles]
            
            # Crypto section
            if crypto_articles:
                script += "=== CRYPTO UPDATE ===\n\n"
                for article in crypto_articles[:3]:
                    script += f"📊 {article['title']}\n"
                    script += f"Source: {article['domain']}\n\n"
                    if article['content']:
                        # Extract key points
                        content_preview = article['content'][:300]
                        script += f"{content_preview}...\n\n"
                    script += "---\n\n"
            
            # Macro section
            if macro_articles:
                script += "=== MARKETS & MACRO ===\n\n"
                for article in macro_articles[:3]:
                    script += f"📈 {article['title']}\n"
                    script += f"Source: {article['domain']}\n\n"
                    if article['content']:
                        content_preview = article['content'][:300]
                        script += f"{content_preview}...\n\n"
                    script += "---\n\n"
            
            # Other news
            if other_articles:
                script += "=== OTHER TOP STORIES ===\n\n"
                for article in other_articles[:2]:
                    script += f"📰 {article['title']}\n"
                    script += f"Source: {article['domain']}\n\n"
                    if article['content']:
                        content_preview = article['content'][:250]
                        script += f"{content_preview}...\n\n"
                    script += "---\n\n"
        
        else:
            # Fallback to email content if no articles fetched
            script += "Today's newsletter summary:\n\n"
            script += email_content[:1000] + "...\n\n"
        
        # Add market summary if mentioned in email
        if 'nasdaq' in email_content.lower() or 'bitcoin' in email_content.lower():
            script += "\n=== QUICK MARKET CHECK ===\n"
            script += "For the latest prices and detailed analysis, check the full newsletter.\n\n"
        
        # Closing
        script += f"""That's all for today's Mando Minutes podcast!

Remember, this is just a summary - for complete details and all the links, check your email.

Have a great day, and we'll see you tomorrow with another update!

---
🎙️ Mando Minutes Podcast - AI-Generated Summary
📧 Original newsletter from {sender}
"""
        
        return script

# Run the agent
if __name__ == "__main__":
    logging.info("🚀 Starting Mando Minutes Link-Following Agent...")
    
    agent = MandoMinutesAgent()
    agent.process_mando_minutes()
    
    logging.info("✅ Mando Minutes processing complete!")
