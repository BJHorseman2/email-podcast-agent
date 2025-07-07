#!/usr/bin/env python3
"""
AOL Email-to-Podcast Agent with ElevenLabs Voice Generation
Complete automation: Email → Script → Voice → Audio File → Email Delivery
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
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class VoiceEnabledAOLAgent:
    def __init__(self):
        self.config = self.load_config()
        self.podcasts_dir = "podcasts"
        os.makedirs(self.podcasts_dir, exist_ok=True)
        
    def load_config(self):
        """Load AOL configuration"""
        try:
            with open('aol_complete_config.json', 'r') as f:
                return json.load(f)
        except:
            print("❌ Config file not found")
            return None
    
    def test_connections(self):
        """Test all connections"""
        print("🧪 Testing Complete System")
        print("=" * 40)
        
        # Test AOL
        if not self.test_aol():
            return False
            
        # Test ElevenLabs
        if not self.test_elevenlabs():
            print("⚠️ ElevenLabs not configured - will send text only")
            
        return True
    
    def test_aol(self):
        """Test AOL connections"""
        try:
            print("1. Testing AOL IMAP...")
            
            # IMAP Test
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
            imap.login(self.config['email']['username'], self.config['email']['password'])
            imap.select('INBOX')
            
            print("   ✅ AOL IMAP working!")
            imap.close()
            imap.logout()
            
            print("2. Testing AOL SMTP...")
            
            # SMTP Test
            server = smtplib.SMTP('smtp.aol.com', 587)
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.quit()
            
            print("   ✅ AOL SMTP working!")
            return True
            
        except Exception as e:
            print(f"   ❌ AOL connection failed: {e}")
            return False
    
    def test_elevenlabs(self):
        """Test ElevenLabs API"""
        try:
            print("3. Testing ElevenLabs...")
            
            if not self.config.get('voice_generation', {}).get('api_key') or self.config['voice_generation']['api_key'] == "YOUR_ELEVENLABS_API_KEY_HERE":
                print("   ⚠️ ElevenLabs API key not configured")
                return False
            
            # Test with a short phrase
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.config['voice_generation']['api_key']
            }
            
            voice_id = self.config['voice_generation']['voice_id']
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            data = {
                "text": "Testing voice generation.",
                "model_id": self.config['voice_generation']['model'],
                "voice_settings": self.config['voice_generation']['voice_settings']
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print("   ✅ ElevenLabs working!")
                return True
            else:
                print(f"   ❌ ElevenLabs error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ ElevenLabs test failed: {e}")
            return False
    
    def find_puck_email(self):
        """Find latest Puck News email"""
        try:
            print("🔍 Looking for Puck News email...")
            
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
            body = self.extract_body(email_message)
            
            print(f"📧 Found: {subject}")
            
            imap.close()
            imap.logout()
            
            return {
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body
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
        
        # Clean up text
        body = re.sub(r'\n\s*\n', '\n\n', body)
        body = re.sub(r'[ \t]+', ' ', body)
        
        # Remove email signatures and footers
        cleanup_patterns = [
            r'unsubscribe.*$',
            r'this email was sent.*$',
            r'you received this.*$',
            r'privacy policy.*$',
            r'view in browser.*$',
            r'follow us on.*$'
        ]
        
        for pattern in cleanup_patterns:
            body = re.sub(pattern, '', body, flags=re.IGNORECASE | re.MULTILINE)
        
        return body.strip()
    
    def create_podcast_script(self, email_data):
        """Create engaging podcast script"""
        
        # Get key content from email
        content = email_data['body']
        
        # Split into paragraphs and get key content
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Take first few meaningful paragraphs
        main_content = '\n\n'.join(paragraphs[:3]) if len(paragraphs) >= 3 else content
        
        # Create the podcast script
        script = f"""Good morning! Welcome to your daily Puck News podcast with insights from Jon Kelly.

Today's update: {email_data['subject']}

Here's what you need to know:

{main_content}

That's your Puck News briefing for today. Stay informed and have a great day!"""
        
        return script.strip()
    
    def generate_voice_audio(self, script):
        """Generate audio using ElevenLabs"""
        try:
            print("🎙️ Generating voice audio...")
            
            if not self.config.get('voice_generation', {}).get('api_key') or self.config['voice_generation']['api_key'] == "YOUR_ELEVENLABS_API_KEY_HERE":
                print("⚠️ ElevenLabs not configured, skipping voice generation")
                return None
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.config['voice_generation']['api_key']
            }
            
            voice_id = self.config['voice_generation']['voice_id']
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            data = {
                "text": script,
                "model_id": self.config['voice_generation']['model'],
                "voice_settings": self.config['voice_generation']['voice_settings']
            }
            
            print("   🔄 Calling ElevenLabs API...")
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                # Save audio file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                audio_filename = f"puck_news_podcast_{timestamp}.mp3"
                audio_path = os.path.join(self.podcasts_dir, audio_filename)
                
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content) / 1024 / 1024  # MB
                print(f"   ✅ Audio generated: {audio_filename} ({file_size:.1f} MB)")
                
                return {
                    'audio_file': audio_path,
                    'filename': audio_filename,
                    'size_mb': round(file_size, 1)
                }
            else:
                print(f"   ❌ ElevenLabs API error: {response.status_code}")
                if response.text:
                    print(f"   Error details: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Voice generation failed: {e}")
            return None
    
    def send_podcast_email(self, email_data, script, audio_data=None):
        """Send podcast via email"""
        try:
            print("📧 Sending podcast email...")
            
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = self.config['email']['username']
            
            # Create subject
            date_str = datetime.now().strftime('%B %d, %Y')
            if audio_data:
                msg['Subject'] = f"🎙️ Your Puck News Podcast - {date_str}"
            else:
                msg['Subject'] = f"📝 Your Puck News Update - {date_str}"
            
            # Create email body
            if audio_data:
                body = f"""Good morning!

Your daily Puck News email has been converted to an audio podcast!

📧 Original Email: {email_data['subject']}
🎙️ Audio Duration: ~{len(script.split()) // 150} minutes
📁 File Size: {audio_data['size_mb']} MB
⏰ Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

The MP3 file is attached - just tap to listen!

🤖 Automated by your AOL Email-to-Podcast Agent
"""
            else:
                body = f"""Good morning!

Your daily Puck News email has been processed into podcast format.

📧 Original Email: {email_data['subject']}
📝 Script Length: ~{len(script.split()) // 150} minutes
⏰ Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

Podcast Script:
{script}

🤖 Automated by your AOL Email-to-Podcast Agent
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach audio file if available
            if audio_data and os.path.exists(audio_data['audio_file']):
                with open(audio_data['audio_file'], "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {audio_data["filename"]}'
                )
                msg.attach(part)
                print(f"   📎 Attached audio: {audio_data['filename']}")
            
            # Send email
            server = smtplib.SMTP('smtp.aol.com', 587)
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.sendmail(self.config['email']['username'], self.config['email']['username'], msg.as_string())
            server.quit()
            
            print("   ✅ Podcast email sent!")
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False
    
    def run_complete_automation(self):
        """Run the complete email-to-podcast automation"""
        print("🚀 AOL Email-to-Podcast with Voice Generation")
        print("=" * 60)
        
        if not self.config:
            print("❌ Configuration not loaded")
            return False
        
        # Step 1: Test connections
        if not self.test_connections():
            print("❌ Connection tests failed")
            return False
        
        print("\n" + "="*50)
        
        # Step 2: Find Puck email
        email_data = self.find_puck_email()
        if not email_data:
            print("📭 No new Puck emails found")
            return False
        
        # Step 3: Create podcast script
        print("📝 Creating podcast script...")
        script = self.create_podcast_script(email_data)
        print(f"   ✅ Script created ({len(script.split())} words)")
        
        # Step 4: Generate voice (if configured)
        audio_data = self.generate_voice_audio(script)
        
        # Step 5: Send email
        if self.send_podcast_email(email_data, script, audio_data):
            print("\n🎉 COMPLETE AUTOMATION SUCCESSFUL!")
            print("📧 Check your AOL inbox for your podcast!")
            if audio_data:
                print(f"🎵 Audio file: {audio_data['filename']}")
            return True
        else:
            print("❌ Email sending failed")
            return False

def main():
    agent = VoiceEnabledAOLAgent()
    agent.run_complete_automation()

if __name__ == "__main__":
    main()
