#!/usr/bin/env python3
"""
Dual Newsletter Automation
Processes BOTH Mando Minutes and Puck News as separate podcasts
They arrive at different times and are completely independent
"""

import imaplib
import email
import ssl
import json
import logging
import requests
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import schedule
import time

from comprehensive_mando_processor import ComprehensiveMandoProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dual_newsletter.log'),
        logging.StreamHandler()
    ]
)

class DualNewsletterAutomation:
    def __init__(self, config_file='multi_newsletter_config.json'):
        """Initialize with support for multiple newsletters"""
        self.config = self.load_config(config_file)
        self.podcasts_dir = "./podcasts"
        os.makedirs(self.podcasts_dir, exist_ok=True)
        
        # Initialize comprehensive processor for Mando
        self.mando_processor = ComprehensiveMandoProcessor()
    
    def load_config(self, config_file):
        """Load configuration"""
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def connect_to_aol(self):
        """Connect to AOL email"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            imap = imaplib.IMAP4_SSL(
                self.config['email']['imap_server'],
                self.config['email']['imap_port'],
                ssl_context=context
            )
            
            imap.login(
                self.config['email']['username'],
                self.config['email']['password']
            )
            
            logging.info("✅ Connected to AOL")
            return imap
            
        except Exception as e:
            logging.error(f"❌ Connection failed: {e}")
            return None
    
    def find_newsletter_email(self, imap, newsletter_config):
        """Find emails for a specific newsletter"""
        try:
            imap.select('INBOX')
            
            # Search based on newsletter config
            newsletter_name = newsletter_config['name']
            senders = newsletter_config['sender'] if isinstance(newsletter_config['sender'], list) else [newsletter_config['sender']]
            subjects = newsletter_config['subject_contains']
            
            # Search for recent emails
            since_date = (datetime.now() - timedelta(hours=24)).strftime('%d-%b-%Y')
            
            email_ids = []
            
            # Try each sender
            for sender in senders:
                search_query = f'SINCE {since_date} FROM "{sender}"'
                logging.info(f"🔍 Searching {newsletter_name}: {search_query}")
                
                _, data = imap.search(None, search_query)
                if data[0]:
                    email_ids.extend(data[0].split())
            
            # Also search by subject
            for subject in subjects:
                search_query = f'SINCE {since_date} SUBJECT "{subject}"'
                _, data = imap.search(None, search_query)
                if data[0]:
                    email_ids.extend(data[0].split())
            
            # Remove duplicates
            email_ids = list(set(email_ids))
            
            if not email_ids:
                logging.info(f"📭 No new {newsletter_name} emails found")
                return None
            
            # Get the most recent email
            latest_id = email_ids[-1]
            _, msg_data = imap.fetch(latest_id, '(RFC822)')
            email_message = email.message_from_bytes(msg_data[0][1])
            
            subject = email_message.get('Subject', 'No Subject')
            sender = email_message.get('From', 'Unknown')
            
            logging.info(f"✅ Found {newsletter_name}: {subject}")
            logging.info(f"   From: {sender}")
            
            return email_message
            
        except Exception as e:
            logging.error(f"Error finding {newsletter_name}: {e}")
            return None
    
    def create_podcast_script(self, email_message, newsletter_config):
        """Create podcast script based on newsletter type"""
        subject = email_message.get('Subject', 'No Subject')
        sender = email_message.get('From', 'Unknown')
        newsletter_name = newsletter_config['name']
        
        # Extract email body
        body = self.extract_email_body(email_message)
        
        # For Mando Minutes - use smart processor
        if newsletter_name == 'mando_minutes':
            logging.info("🧠 Using comprehensive processor for Mando Minutes")
            
            # Use the smart processor to create rich content
            script, word_count, duration = self.mando_processor.process_mando_email(body)
            logging.info(f"📊 Created {word_count} words of analysis")
            
            return script
            
        else:
            # For Puck or if link following not available
            script = self.create_standard_script(subject, sender, body, newsletter_config)
        
        return script
    
    def create_mando_script(self, subject, sender, body, articles):
        """Create Mando Minutes script with fetched articles"""
        date_str = datetime.now().strftime('%A, %B %d, %Y')
        
        script = f"""Good morning! This is your Mando Minutes podcast for {date_str}.

I'm your AI assistant with today's crypto and market updates.

"""
        
        if articles:
            # Group by topic
            crypto_articles = [a for a in articles if any(word in a.get('title', '').lower() 
                             for word in ['crypto', 'bitcoin', 'eth', 'blockchain'])]
            market_articles = [a for a in articles if any(word in a.get('title', '').lower() 
                             for word in ['market', 'stock', 'fed', 'inflation'])]
            other_articles = [a for a in articles if a not in crypto_articles and a not in market_articles]
            
            # Add sections
            if crypto_articles:
                script += "Let's start with crypto news.\n\n"
                for article in crypto_articles[:3]:
                    script += f"{article['title']}\n\n"
                    if article['content']:
                        content = ' '.join(article['content'].split()[:150])
                        script += f"{content}...\n\n"
            
            if market_articles:
                script += "Now for markets and macro.\n\n"
                for article in market_articles[:3]:
                    script += f"{article['title']}\n\n"
                    if article['content']:
                        content = ' '.join(article['content'].split()[:150])
                        script += f"{content}...\n\n"
        
        else:
            # Fallback to email content
            script += f"Today's updates:\n\n{body[:1500]}\n\n"
        
        script += """That's all for today's Mando Minutes.

Check your email for all the links. Have a great day!"""
        
        return script
    
    def create_standard_script(self, subject, sender, body, newsletter_config):
        """Create standard podcast script"""
        date_str = datetime.now().strftime('%A, %B %d, %Y')
        newsletter_name = newsletter_config['name'].replace('_', ' ').title()
        
        script = f"""Welcome to your {newsletter_name} podcast for {date_str}.

Today's newsletter: {subject}

{body[:3000]}

That concludes today's {newsletter_name} podcast. 

For the complete newsletter with all links and details, check your email.

Thank you for listening!"""
        
        return script
    
    def extract_email_body(self, email_message):
        """Extract email body"""
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
        
        return body
    
    def generate_audio(self, script, newsletter_name):
        """Generate audio using ElevenLabs"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_file = f"{self.podcasts_dir}/{newsletter_name}_{timestamp}.mp3"
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.config['voice_generation']['voice_id']}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.config['voice_generation']['api_key']
            }
            
            data = {
                "text": script,
                "model_id": self.config['voice_generation']['model'],
                "voice_settings": self.config['voice_generation']['voice_settings']
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open(audio_file, 'wb') as f:
                    f.write(response.content)
                
                file_size = os.path.getsize(audio_file)
                duration = file_size / (128000 / 8) / 60
                
                logging.info(f"✅ Audio generated: {duration:.1f} minutes")
                return audio_file, duration
            else:
                logging.error(f"ElevenLabs error: {response.status_code}")
                return None, 0
                
        except Exception as e:
            logging.error(f"Audio generation failed: {e}")
            return None, 0
    
    def send_podcast_email(self, audio_file, duration, newsletter_config, subject):
        """Send podcast via email"""
        try:
            newsletter_name = newsletter_config['name'].replace('_', ' ').title()
            
            msg = MIMEMultipart()
            msg['From'] = self.config['email_delivery']['sender_email']
            msg['To'] = self.config['email_delivery']['recipient_email']
            
            # Use newsletter-specific subject
            if newsletter_config['name'] == 'mando_minutes':
                msg['Subject'] = self.config['email_delivery']['mando_subject'].format(
                    date=datetime.now().strftime('%B %d, %Y')
                )
            else:
                msg['Subject'] = self.config['email_delivery']['puck_subject'].format(
                    date=datetime.now().strftime('%B %d, %Y')
                )
            
            # Email body
            body = f"""Good morning!

Your {newsletter_name} has been converted to a podcast.

📰 Original: {subject}
🎙️ Duration: {duration:.1f} minutes
📅 Generated: {datetime.now().strftime('%I:%M %p')}

The audio file is attached. Enjoy your personalized podcast!

🤖 Automated by your Email-to-Podcast AI
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach audio
            if audio_file and os.path.exists(audio_file):
                with open(audio_file, "rb") as f:
                    part = MIMEBase('audio', 'mpeg')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    filename = f"{newsletter_name.lower().replace(' ', '_')}_podcast.mp3"
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(part)
            
            # Send
            server = smtplib.SMTP(
                self.config['email_delivery']['smtp_server'],
                self.config['email_delivery']['smtp_port']
            )
            server.starttls()
            server.login(
                self.config['email_delivery']['sender_email'],
                self.config['email']['password']
            )
            server.send_message(msg)
            server.quit()
            
            logging.info("✅ Email sent successfully!")
            return True
            
        except Exception as e:
            logging.error(f"Email sending failed: {e}")
            return False
    
    def process_newsletter(self, newsletter_config):
        """Process a single newsletter"""
        newsletter_name = newsletter_config['name']
        logging.info(f"\n🚀 Processing {newsletter_name}...")
        
        # Connect to email
        imap = self.connect_to_aol()
        if not imap:
            return False
        
        try:
            # Find newsletter email
            email_message = self.find_newsletter_email(imap, newsletter_config)
            if not email_message:
                logging.info(f"No new {newsletter_name} to process")
                return False
            
            # Create podcast script
            script = self.create_podcast_script(email_message, newsletter_config)
            
            # Save script
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            script_file = f"{self.podcasts_dir}/{newsletter_name}_script_{timestamp}.txt"
            with open(script_file, 'w') as f:
                f.write(script)
            
            logging.info(f"📝 Script created: {len(script.split())} words")
            
            # Generate audio
            audio_file, duration = self.generate_audio(script, newsletter_name)
            
            if audio_file:
                # Send email
                subject = email_message.get('Subject', 'Newsletter')
                self.send_podcast_email(audio_file, duration, newsletter_config, subject)
            
            return True
            
        finally:
            imap.logout()
    
    def run_all_newsletters(self):
        """Process all enabled newsletters"""
        logging.info("🎯 Starting dual newsletter processing...")
        
        for newsletter in self.config['newsletters']:
            if newsletter.get('enabled', True):
                self.process_newsletter(newsletter)
                time.sleep(5)  # Brief pause between newsletters
        
        logging.info("✅ All newsletters processed!")
    
    def schedule_automation(self):
        """Schedule newsletter checks"""
        # Schedule Mando Minutes check at 7:45 AM
        schedule.every().day.at("07:45").do(
            lambda: self.process_newsletter(self.config['newsletters'][0])
        )
        
        # Schedule Puck News check at 8:30 AM
        schedule.every().day.at("08:30").do(
            lambda: self.process_newsletter(self.config['newsletters'][1])
        )
        
        logging.info("📅 Scheduled:")
        logging.info("   - Mando Minutes: 7:45 AM daily")
        logging.info("   - Puck News: 8:30 AM daily")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    automation = DualNewsletterAutomation()
    
    # Process both newsletters now
    automation.run_all_newsletters()
