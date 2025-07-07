#!/usr/bin/env python3
"""
AOL-Only Email-to-Podcast Automation System
Uses AOL email for both receiving newsletters and sending podcasts
"""

import imaplib
import smtplib
import email
import json
import os
import ssl
import time
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import schedule
import logging
import re
from typing import Dict, Optional
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aol_podcast_automation.log'),
        logging.StreamHandler()
    ]
)

class AOLPodcastAutomationAgent:
    def __init__(self, config_file='aol_complete_config.json'):
        """Initialize the AOL-only automation agent"""
        self.config = self.load_config(config_file)
        self.podcasts_dir = self.config['output']['podcast_folder']
        os.makedirs(self.podcasts_dir, exist_ok=True)
        
        # Initialize API clients
        self.setup_openai()
        
    def load_config(self, config_file):
        """Load configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Configuration file {config_file} not found!")
            raise
    
    def setup_openai(self):
        """Setup OpenAI client"""
        if self.config['ai_processing']['api_key'] != "YOUR_OPENAI_API_KEY":
            openai.api_key = self.config['ai_processing']['api_key']
        
    def connect_to_aol_imap(self):
        """Connect to AOL email for reading"""
        try:
            logging.info("🔗 Connecting to AOL IMAP server...")
            
            context = ssl.create_default_context()
            imap = imaplib.IMAP4_SSL(
                self.config['email']['imap_server'],
                self.config['email']['imap_port'],
                ssl_context=context
            )
            
            imap.login(
                self.config['email']['username'],
                self.config['email']['password']
            )
            
            logging.info("✅ Connected to AOL IMAP successfully!")
            return imap
            
        except Exception as e:
            logging.error(f"❌ AOL IMAP connection failed: {e}")
            return None
    
    def find_target_email(self, imap):
        """Find the target email from AOL inbox"""
        try:
            imap.select('INBOX')
            
            # Search criteria for recent emails
            since_date = (datetime.now() - timedelta(hours=self.config['target_email']['max_age_hours'])).strftime('%d-%b-%Y')
            search_criteria = f'SINCE {since_date} UNSEEN'
            
            # Add sender filter if configured
            if self.config['target_email']['sender'] != "NEWSLETTER_SENDER@example.com":
                search_criteria += f' FROM "{self.config["target_email"]["sender"]}"'
            
            logging.info(f"🔍 Searching AOL emails: {search_criteria}")
            
            _, message_numbers = imap.search(None, search_criteria)
            
            if not message_numbers[0]:
                logging.info("📭 No new emails found in AOL inbox")
                return None
            
            # Get the most recent email
            email_ids = message_numbers[0].split()
            latest_email_id = email_ids[-1]
            
            _, msg_data = imap.fetch(latest_email_id, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Check subject matches criteria
            subject = email_message['Subject'] or ""
            subject_match = any(keyword.lower() in subject.lower() 
                              for keyword in self.config['target_email']['subject_contains'])
            
            if not subject_match:
                logging.info(f"📧 Email subject '{subject}' doesn't match criteria")
                return None
            
            # Extract email content
            email_data = {
                'id': latest_email_id.decode(),
                'subject': subject,
                'sender': email_message['From'],
                'date': email_message['Date'],
                'body': self.extract_email_body(email_message),
                'timestamp': datetime.now().isoformat()
            }
            
            logging.info(f"📧 Found target email: {email_data['subject']}")
            logging.info(f"📄 Content length: {len(email_data['body'])} characters")
            
            return email_data
            
        except Exception as e:
            logging.error(f"❌ Error finding email: {e}")
            return None
    
    def extract_email_body(self, email_message):
        """Extract clean text from email"""
        body = ""
        
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode('utf-8', errors='ignore')
                            break
                    elif part.get_content_type() == "text/html" and not body:
                        payload = part.get_payload(decode=True)
                        if payload:
                            html_content = payload.decode('utf-8', errors='ignore')
                            # Simple HTML to text conversion
                            body = re.sub(r'<[^>]+>', '', html_content)
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
            
            # Clean up text
            body = re.sub(r'\n\s*\n', '\n\n', body)
            body = re.sub(r'[ \t]+', ' ', body)
            body = body.strip()
            
            # Remove common email footers
            cleanup_patterns = [
                r'unsubscribe.*$',
                r'this email was sent.*$',
                r'you received this.*$',
                r'privacy policy.*$',
                r'view in browser.*$'
            ]
            
            for pattern in cleanup_patterns:
                body = re.sub(pattern, '', body, flags=re.IGNORECASE | re.MULTILINE)
            
        except Exception as e:
            logging.error(f"Error extracting email body: {e}")
            body = "Error extracting email content"
        
        return body.strip()
    
    def generate_podcast_script(self, email_data):
        """Generate podcast script using AI or fallback"""
        try:
            logging.info("🤖 Generating podcast script...")
            
            if self.config['ai_processing']['api_key'] == "YOUR_OPENAI_API_KEY":
                # Fallback to built-in processing
                return self.create_basic_script(email_data)
            
            # Use OpenAI to create script
            prompt = f"""
            Subject: {email_data['subject']}
            From: {email_data['sender']}
            
            Email Content:
            {email_data['body'][:3000]}
            
            {self.config['ai_processing']['system_prompt']}
            
            Make it sound natural and engaging, like a friendly morning briefing.
            """
            
            response = openai.ChatCompletion.create(
                model=self.config['ai_processing']['model'],
                messages=[
                    {"role": "system", "content": "You are a professional podcast script writer who creates engaging, conversational content from email newsletters."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            script = response.choices[0].message.content.strip()
            
            # Calculate metadata
            word_count = len(script.split())
            estimated_duration = round(word_count / 150)
            
            logging.info(f"✅ Generated AI script: {word_count} words, ~{estimated_duration} min")
            
            return {
                'script': script,
                'word_count': word_count,
                'estimated_duration': estimated_duration,
                'method': 'openai'
            }
            
        except Exception as e:
            logging.error(f"❌ AI script generation failed: {e}")
            return self.create_basic_script(email_data)
    
    def create_basic_script(self, email_data):
        """Fallback script generation"""
        logging.info("📝 Creating basic podcast script...")
        
        content = email_data['body']
        sentences = content.split('. ')
        summary = '. '.join(sentences[:4]) + '.' if len(sentences) >= 4 else content
        
        script = f"""
        Good morning! Welcome to your daily email podcast.

        Today's update comes from {email_data['sender']} with the subject: {email_data['subject']}

        Here's what you need to know:

        {summary}

        That's your update for today. Have a great day and stay informed!
        """.strip()
        
        word_count = len(script.split())
        estimated_duration = round(word_count / 150)
        
        return {
            'script': script,
            'word_count': word_count,
            'estimated_duration': estimated_duration,
            'method': 'basic'
        }
    
    def generate_voice_audio(self, script_data):
        """Generate audio using ElevenLabs"""
        try:
            logging.info("🎙️ Generating voice audio with ElevenLabs...")
            
            if self.config['voice_generation']['api_key'] == "YOUR_ELEVENLABS_API_KEY":
                logging.warning("⚠️ ElevenLabs API key not configured")
                return None
            
            # ElevenLabs API endpoint
            voice_id = self.config['voice_generation']['voice_id']
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.config['voice_generation']['api_key']
            }
            
            data = {
                "text": script_data['script'],
                "model_id": self.config['voice_generation']['model'],
                "voice_settings": self.config['voice_generation']['voice_settings']
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                # Save audio file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                audio_filename = f"daily_podcast_{timestamp}.mp3"
                audio_path = os.path.join(self.podcasts_dir, audio_filename)
                
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                
                logging.info(f"✅ Audio generated: {audio_filename}")
                
                return {
                    'audio_file': audio_path,
                    'filename': audio_filename,
                    'size_mb': round(len(response.content) / 1024 / 1024, 2)
                }
            else:
                logging.error(f"❌ ElevenLabs API error: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Voice generation failed: {e}")
            return None
    
    def send_podcast_via_aol(self, email_data, script_data, audio_data):
        """Send podcast using AOL SMTP"""
        try:
            logging.info("📧 Sending podcast via AOL email...")
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.config['email_delivery']['sender_email']
            msg['To'] = self.config['email_delivery']['recipient_email']
            msg['Subject'] = self.config['email_delivery']['subject_template'].format(
                date=datetime.now().strftime('%B %d, %Y')
            )
            
            # Email body
            body = self.config['email_delivery']['body_template'].format(
                email_subject=email_data['subject'],
                duration=script_data['estimated_duration'],
                timestamp=datetime.now().strftime('%B %d, %Y at %I:%M %p')
            )
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach audio file if available
            if audio_data:
                with open(audio_data['audio_file'], "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {audio_data["filename"]}'
                )
                msg.attach(part)
                logging.info(f"📎 Attached audio: {audio_data['filename']} ({audio_data['size_mb']} MB)")
            else:
                # Attach script as text file if no audio
                script_attachment = MIMEText(script_data['script'])
                script_attachment.add_header(
                    'Content-Disposition',
                    'attachment; filename="podcast_script.txt"'
                )
                msg.attach(script_attachment)
                logging.info("📎 Attached script as text file")
            
            # Connect to AOL SMTP server
            server = smtplib.SMTP(
                self.config['email_delivery']['smtp_server'],
                self.config['email_delivery']['smtp_port']
            )
            server.starttls()
            server.login(
                self.config['email_delivery']['sender_email'],
                self.config['email_delivery']['sender_password']
            )
            
            # Send email
            text = msg.as_string()
            server.sendmail(
                self.config['email_delivery']['sender_email'],
                self.config['email_delivery']['recipient_email'],
                text
            )
            server.quit()
            
            logging.info(f"✅ Podcast emailed successfully via AOL!")
            logging.info(f"📧 Sent to: {self.config['email_delivery']['recipient_email']}")
            return True
            
        except Exception as e:
            logging.error(f"❌ AOL email sending failed: {e}")
            return False
    
    def mark_email_processed(self, imap, email_id):
        """Mark email as read in AOL inbox"""
        try:
            imap.store(email_id, '+FLAGS', '\\Seen')
            logging.info("✅ Email marked as read in AOL")
        except Exception as e:
            logging.error(f"Error marking email: {e}")
    
    def run_aol_automation(self):
        """Main AOL automation process"""
        try:
            logging.info("🚀 Starting AOL email-to-podcast automation...")
            
            # Step 1: Connect to AOL IMAP
            imap = self.connect_to_aol_imap()
            if not imap:
                return False
            
            # Step 2: Find target email
            email_data = self.find_target_email(imap)
            if not email_data:
                logging.info("📭 No new emails to process")
                imap.close()
                imap.logout()
                return False
            
            # Step 3: Generate podcast script
            script_data = self.generate_podcast_script(email_data)
            if not script_data:
                logging.error("❌ Script generation failed")
                return False
            
            # Step 4: Generate voice audio
            audio_data = self.generate_voice_audio(script_data)
            
            # Step 5: Send via AOL email
            email_sent = self.send_podcast_via_aol(email_data, script_data, audio_data)
            
            if email_sent:
                # Step 6: Mark email as processed
                self.mark_email_processed(imap, email_data['id'])
                
                logging.info("🎉 AOL automation completed successfully!")
                logging.info(f"📊 Processed: {email_data['subject']}")
                logging.info(f"🎙️ Duration: ~{script_data['estimated_duration']} minutes")
                if audio_data:
                    logging.info(f"📁 Audio: {audio_data['size_mb']} MB")
            
            # Close connections
            imap.close()
            imap.logout()
            
            return email_sent
            
        except Exception as e:
            logging.error(f"❌ AOL automation failed: {e}")
            return False
    
    def test_aol_system(self):
        """Test all AOL components"""
        print("🧪 Testing AOL Email-to-Podcast System")
        print("=" * 50)
        
        # Test 1: AOL IMAP Connection
        print("1. Testing AOL IMAP connection...")
        imap = self.connect_to_aol_imap()
        if imap:
            print("   ✅ AOL IMAP connection successful")
            imap.close()
            imap.logout()
        else:
            print("   ❌ AOL IMAP connection failed")
            return False
        
        # Test 2: AOL SMTP (email sending)
        print("2. Testing AOL SMTP connection...")
        try:
            server = smtplib.SMTP(
                self.config['email_delivery']['smtp_server'],
                self.config['email_delivery']['smtp_port']
            )
            server.starttls()
            server.login(
                self.config['email_delivery']['sender_email'],
                self.config['email_delivery']['sender_password']
            )
            server.quit()
            print("   ✅ AOL SMTP connection successful")
        except Exception as e:
            print(f"   ❌ AOL SMTP connection failed: {e}")
            return False
        
        # Test 3: ElevenLabs (if configured)
        if self.config['voice_generation']['api_key'] != "YOUR_ELEVENLABS_API_KEY":
            print("3. Testing ElevenLabs API...")
            test_script = {"script": "This is a test of the AOL voice generation system."}
            audio_result = self.generate_voice_audio(test_script)
            if audio_result:
                print("   ✅ ElevenLabs working")
                print(f"   📁 Test audio: {audio_result['filename']}")
            else:
                print("   ❌ ElevenLabs test failed")
        else:
            print("3. ElevenLabs API not configured")
        
        # Test 4: Configuration check
        print("4. Checking AOL configuration...")
        if self.config['email']['username'] != "YOUR_AOL_EMAIL@aol.com":
            print("   ✅ AOL credentials configured")
        else:
            print("   ⚠️ AOL credentials need configuration")
        
        print("\n🎯 AOL System Status:")
        print("   ✅ Ready for automation!" if imap else "   ❌ Needs configuration")
        
        return True
    
    def schedule_daily_automation(self):
        """Schedule daily AOL automation"""
        run_time = self.config['schedule']['run_time']
        schedule.every().day.at(run_time).do(self.run_aol_automation)
        
        logging.info(f"📅 Scheduled AOL automation for {run_time} daily")
        logging.info("🔄 AOL agent running in background...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """Main execution"""
    print("🎙️ AOL Email-to-Podcast Automation System")
    print("=" * 60)
    print("📧 Uses AOL for both receiving newsletters and sending podcasts")
    print()
    
    agent = AOLPodcastAutomationAgent()
    
    # Test system
    if not agent.test_aol_system():
        print("\n❌ AOL system test failed. Please check configuration.")
        print("📝 Update aol_complete_config.json with your AOL credentials")
        return
    
    print("\n🚀 Running AOL automation once...")
    success = agent.run_aol_automation()
    
    if success:
        print("\n🎉 AOL automation successful!")
        print("📧 Check your AOL email for the podcast!")
        print("\n🔄 To enable daily scheduling:")
        print("   python3 aol_automation.py --schedule")
    else:
        print("\n⚠️ No emails processed (normal if no new emails)")
        print("📋 Check aol_podcast_automation.log for details")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        agent = AOLPodcastAutomationAgent()
        agent.schedule_daily_automation()
    else:
        main()
