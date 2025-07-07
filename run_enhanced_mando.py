#!/usr/bin/env python3
"""
Enhanced Mando Minutes Agent with Link Following
This replaces the standard processing with link-aware content extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from link_following_agent import LinkFollowingNewsletterAgent
import imaplib
import email
import ssl
import json
import logging
from datetime import datetime, timedelta
from email.header import decode_header
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EnhancedMandoAgent(LinkFollowingNewsletterAgent):
    def __init__(self):
        super().__init__()
        # Add Mando-specific configurations
        self.trusted_domains.update({
            'puck.news', 'axios.com', 'politico.com', 'semafor.com',
            'theinformation.com', 'stratechery.com', 'protocol.com'
        })
        
    def connect_to_aol(self, config):
        """Connect to AOL with proper SSL handling"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            mail = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
            mail.login(config['email'], config['password'])
            logging.info("✅ Connected to AOL successfully!")
            return mail
        except Exception as e:
            logging.error(f"❌ Failed to connect: {e}")
            return None
    
    def process_mando_email(self, email_message):
        """Process a Mando Minutes email with link following"""
        try:
            # Extract basic info
            subject = self.decode_email_header(email_message.get('Subject', 'No Subject'))
            sender = self.decode_email_header(email_message.get('From', 'Unknown'))
            
            logging.info(f"📧 Processing: {subject}")
            
            # Extract content
            text_content, html_content = self.extract_email_content(email_message)
            
            # Extract and follow links
            links = self.extract_links_from_content(text_content, html_content)
            logging.info(f"🔗 Found {len(links)} links")
            
            articles = []
            if links:
                logging.info("📰 Fetching article content...")
                # Prioritize crypto and market news links
                crypto_links = [l for l in links if any(word in l.lower() 
                               for word in ['crypto', 'bitcoin', 'coindesk', 'block'])]
                other_links = [l for l in links if l not in crypto_links]
                
                # Fetch crypto articles first
                all_links = crypto_links + other_links
                articles = self.fetch_multiple_articles(all_links[:8])  # Limit to 8 articles
                logging.info(f"✅ Fetched {len(articles)} articles successfully")
            
            # Create enhanced podcast script
            podcast_script = self.create_mando_podcast_script(
                subject, sender, text_content, articles
            )
            
            # Save the enhanced script
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            script_file = f"podcasts/mando_minutes_enhanced_{timestamp}.txt"
            
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(podcast_script)
            
            logging.info(f"📝 Enhanced script saved: {script_file}")
            logging.info(f"📊 Script length: {len(podcast_script)} characters, {len(podcast_script.split())} words")
            
            # Generate audio using your existing TTS
            audio_file = self.generate_audio(podcast_script, timestamp)
            
            return {
                'success': True,
                'script_file': script_file,
                'audio_file': audio_file,
                'articles_count': len(articles),
                'word_count': len(podcast_script.split())
            }
            
        except Exception as e:
            logging.error(f"Error processing email: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_mando_podcast_script(self, subject, sender, email_content, articles):
        """Create an engaging podcast script with fetched article content"""
        
        date_str = datetime.now().strftime('%A, %B %d, %Y')
        
        script = f"""Good morning! This is your Mando Minutes podcast for {date_str}.

I'm your AI assistant, bringing you the latest insights from today's newsletter.

"""
        
        if articles:
            # Group articles by category
            crypto_articles = [a for a in articles if any(word in a.get('title', '').lower() 
                             for word in ['crypto', 'bitcoin', 'eth', 'blockchain', 'defi'])]
            market_articles = [a for a in articles if any(word in a.get('title', '').lower() 
                             for word in ['market', 'stock', 'nasdaq', 'inflation', 'fed', 'economy'])]
            other_articles = [a for a in articles if a not in crypto_articles and a not in market_articles]
            
            # Crypto section
            if crypto_articles:
                script += "Let's start with crypto news.\n\n"
                for i, article in enumerate(crypto_articles[:3], 1):
                    script += f"Our {self._ordinal(i)} crypto story: {article['title']}\n\n"
                    if article['content']:
                        # Extract key points from content
                        words = article['content'].split()[:150]  # First 150 words
                        content = ' '.join(words)
                        script += f"{content}...\n\n"
                    script += f"That's from {article['domain']}.\n\n"
            
            # Markets section  
            if market_articles:
                script += "Now for markets and macro news.\n\n"
                for i, article in enumerate(market_articles[:3], 1):
                    script += f"{article['title']}\n\n"
                    if article['content']:
                        words = article['content'].split()[:150]
                        content = ' '.join(words)
                        script += f"{content}...\n\n"
                    script += f"Source: {article['domain']}.\n\n"
            
            # Other news
            if other_articles:
                script += "In other news today:\n\n"
                for article in other_articles[:2]:
                    script += f"{article['title']}\n\n"
                    if article['content']:
                        words = article['content'].split()[:100]  # Shorter for other news
                        content = ' '.join(words)
                        script += f"{content}...\n\n"
            
            script += f"""That wraps up today's Mando Minutes with {len(articles)} stories covered.

"""
        else:
            # Fallback to email content if no articles fetched
            script += "Here's today's summary:\n\n"
            # Clean up the email content
            lines = email_content.split('\n')
            for line in lines[:20]:  # First 20 lines
                line = line.strip()
                if line and len(line) > 10:
                    script += f"{line}\n"
            script += "\n"
        
        script += """For all the links and complete details, check your email.

Have a great day, and I'll see you tomorrow with another Mando Minutes update!"""
        
        return script
    
    def _ordinal(self, n):
        """Convert number to ordinal (1st, 2nd, 3rd, etc)"""
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"
    
    def generate_audio(self, script, timestamp):
        """Generate audio file (integrate with your existing TTS)"""
        # This is a placeholder - integrate with your actual TTS system
        audio_file = f"podcasts/mando_minutes_enhanced_{timestamp}.mp3"
        
        # You would call your TTS service here
        # For now, we'll just save the script
        logging.info(f"🎙️ Audio generation would happen here: {audio_file}")
        
        return audio_file
    
    def run(self):
        """Main execution function"""
        # Load config
        with open('multi_email_config.json', 'r') as f:
            config = json.load(f)
        
        # Find Mando config
        mando_config = None
        for newsletter in config.get('newsletters', []):
            if 'mando' in newsletter['newsletter_name'].lower():
                mando_config = newsletter
                break
        
        if not mando_config:
            logging.error("No Mando Minutes configuration found")
            return
        
        # Connect to email
        mail = self.connect_to_aol(mando_config)
        if not mail:
            return
        
        try:
            # Search for recent Mando emails
            mail.select('INBOX')
            since_date = (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y')
            
            # Search criteria
            search_queries = [
                f'(SINCE {since_date} FROM "puck.news")',
                f'(SINCE {since_date} SUBJECT "mando")',
                f'(SINCE {since_date} FROM "jon kelly")'
            ]
            
            email_ids = []
            for query in search_queries:
                result, data = mail.search(None, query)
                if result == 'OK' and data[0]:
                    email_ids.extend(data[0].split())
            
            # Remove duplicates
            email_ids = list(set(email_ids))
            
            if not email_ids:
                logging.info("No recent Mando Minutes emails found")
                return
            
            logging.info(f"Found {len(email_ids)} Mando emails")
            
            # Process the most recent email
            latest_id = email_ids[-1]
            result, data = mail.fetch(latest_id, '(RFC822)')
            
            if result == 'OK':
                raw_email = data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Process with link following
                result = self.process_mando_email(email_message)
                
                if result['success']:
                    logging.info(f"✅ ENHANCED MANDO MINUTES CREATED!")
                    logging.info(f"📊 Stats: {result['articles_count']} articles, {result['word_count']} words")
                    logging.info(f"📝 Script: {result['script_file']}")
                    
                    # Send email with enhanced podcast
                    if mando_config.get('send_email', True):
                        self.send_podcast_email(result, mando_config)
                
        finally:
            mail.logout()
            logging.info("Disconnected from email server")
    
    def send_podcast_email(self, result, config):
        """Send the enhanced podcast via email"""
        # Integrate with your existing email sending logic
        logging.info(f"📧 Would send enhanced podcast to {config.get('send_to_email', 'you')}")

if __name__ == "__main__":
    logging.info("🚀 Starting Enhanced Mando Minutes Agent with Link Following...")
    
    agent = EnhancedMandoAgent()
    agent.run()
    
    logging.info("✅ Enhanced processing complete!")
