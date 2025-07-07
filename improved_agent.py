#!/usr/bin/env python3
"""
AOL Email-to-Podcast Agent with Better Text Processing
Fixed version that handles email encoding properly
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
from email.header import decode_header
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class ImprovedAOLAgent:
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
    
    def decode_email_header(self, header):
        """Properly decode email headers"""
        if not header:
            return ""
        
        try:
            decoded_parts = decode_header(header)
            decoded_string = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            
            return decoded_string
        except:
            return str(header)
    
    def extract_clean_body(self, email_message):
        """Extract and clean email body with better encoding handling"""
        body = ""
        
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            # Try different encodings
                            for encoding in ['utf-8', 'iso-8859-1', 'windows-1252']:
                                try:
                                    body = payload.decode(encoding)
                                    break
                                except:
                                    continue
                            break
                    elif content_type == "text/html" and not body:
                        payload = part.get_payload(decode=True)
                        if payload:
                            try:
                                html_content = payload.decode('utf-8', errors='ignore')
                                # Simple HTML to text conversion
                                body = re.sub(r'<[^>]+>', '', html_content)
                            except:
                                continue
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
                    # Try different encodings
                    for encoding in ['utf-8', 'iso-8859-1', 'windows-1252']:
                        try:
                            body = payload.decode(encoding)
                            break
                        except:
                            continue
            
            # Clean up text
            body = re.sub(r'\n\s*\n', '\n\n', body)
            body = re.sub(r'[ \t]+', ' ', body)
            body = re.sub(r'\r\n', '\n', body)
            
            # Remove email signatures and footers
            cleanup_patterns = [
                r'unsubscribe.*$',
                r'this email was sent.*$',
                r'you received this.*$',
                r'privacy policy.*$',
                r'view in browser.*$',
                r'follow us on.*$',
                r'Copyright.*$',
                r'www\..*\.com.*$'
            ]
            
            for pattern in cleanup_patterns:
                body = re.sub(pattern, '', body, flags=re.IGNORECASE | re.MULTILINE)
            
            return body.strip()
            
        except Exception as e:
            print(f"Error extracting body: {e}")
            return "Content could not be extracted properly"
    
    def find_puck_email(self):
        """Find latest Puck News email with better text handling"""
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
            
            # Properly decode headers
            subject = self.decode_email_header(email_message['Subject'])
            sender = self.decode_email_header(email_message['From'])
            date = email_message['Date']
            
            # Extract body with improved handling
            body = self.extract_clean_body(email_message)
            
            print(f"📧 Found: {subject}")
            print(f"📄 Content preview: {body[:100]}...")
            
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
    
    def create_enhanced_script(self, email_data):
        """Create a better podcast script"""
        
        content = email_data['body']
        subject = email_data['subject']
        
        # Split content into sentences and paragraphs
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p) > 50]
        
        # Create main content - use paragraphs if available, otherwise sentences
        if paragraphs:
            main_content = '\n\n'.join(paragraphs[:2])
        else:
            main_content = '. '.join(sentences[:5]) + '.'
        
        # Ensure we have reasonable content
        if len(main_content) < 100:
            main_content = content[:500] + "..." if len(content) > 500 else content
        
        # Create the enhanced script
        script = f"""Good morning and welcome to your daily Puck News podcast.

I'm bringing you the latest insights from Jon Kelly's newsletter.

Today's topic: {subject}

Here's what you need to know:

{main_content}

That wraps up today's Puck News briefing. Stay informed, and I'll see you tomorrow with your next update!"""
        
        return script.strip()
    
    def generate_voice_audio(self, script):
        """Generate audio using ElevenLabs"""
        try:
            print("🎙️ Generating voice audio...")
            
            if not self.config.get('voice_generation', {}).get('api_key') or self.config['voice_generation']['api_key'] == "YOUR_ELEVENLABS_API_KEY_HERE":
                print("⚠️ ElevenLabs not configured")
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
            
            print("   🔄 Generating audio...")
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                audio_filename = f"puck_news_{timestamp}.mp3"
                audio_path = os.path.join(self.podcasts_dir, audio_filename)
                
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content) / 1024 / 1024
                duration_estimate = len(script.split()) / 150  # 150 words per minute
                
                print(f"   ✅ Audio created: {audio_filename}")
                print(f"   📁 Size: {file_size:.1f} MB")
                print(f"   ⏱️ Duration: ~{duration_estimate:.1f} minutes")
                
                return {
                    'audio_file': audio_path,
                    'filename': audio_filename,
                    'size_mb': round(file_size, 1),
                    'duration_minutes': round(duration_estimate, 1)
                }
            else:
                print(f"   ❌ ElevenLabs error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Voice generation failed: {e}")
            return None
    
    def send_clean_email(self, email_data, script, audio_data=None):
        """Send clean, properly formatted email"""
        try:
            print("📧 Sending podcast email...")
            
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = self.config['email']['username']
            
            # Clean subject line
            date_str = datetime.now().strftime('%B %d, %Y')
            clean_subject = re.sub(r'[^\w\s\-\.]', '', email_data['subject'])
            msg['Subject'] = f"🎙️ Puck News Podcast - {date_str}"
            
            # Create clean email body
            if audio_data:
                body = f"""Good morning!

Your daily Puck News update has been converted to an audio podcast.

📧 Original Topic: {clean_subject}
🎙️ Duration: ~{audio_data['duration_minutes']} minutes  
📁 File Size: {audio_data['size_mb']} MB
⏰ Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

The MP3 file is attached below - just tap to listen!

Enjoy your personalized Puck News podcast.

🤖 Automated by your AOL Email-to-Podcast Agent"""
            else:
                body = f"""Good morning!

Your daily Puck News update has been processed.

📧 Original Topic: {clean_subject}
⏰ Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

Podcast Script:
{script}

🤖 Automated by your AOL Email-to-Podcast Agent"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach audio file
            if audio_data and os.path.exists(audio_data['audio_file']):
                with open(audio_data['audio_file'], "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{audio_data["filename"]}"'
                )
                msg.attach(part)
                print(f"   📎 Attached: {audio_data['filename']}")
            
            # Send email
            server = smtplib.SMTP('smtp.aol.com', 587)
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.sendmail(self.config['email']['username'], self.config['email']['username'], msg.as_string())
            server.quit()
            
            print("   ✅ Clean email sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False
    
    def run_improved_automation(self):
        """Run improved automation with better text handling"""
        print("🚀 Improved Puck News to Podcast Automation")
        print("=" * 60)
        
        if not self.config:
            print("❌ Configuration not loaded")
            return False
        
        # Find Puck email with better text processing
        email_data = self.find_puck_email()
        if not email_data:
            print("📭 No new Puck emails found")
            return False
        
        # Create enhanced script
        print("📝 Creating enhanced podcast script...")
        script = self.create_enhanced_script(email_data)
        word_count = len(script.split())
        print(f"   ✅ Script ready ({word_count} words)")
        
        # Generate voice
        audio_data = self.generate_voice_audio(script)
        
        # Send clean email
        if self.send_clean_email(email_data, script, audio_data):
            print("\n🎉 IMPROVED AUTOMATION SUCCESSFUL!")
            print("📧 Check your AOL inbox - the text should be much cleaner now!")
            if audio_data:
                print(f"🎵 Audio: {audio_data['filename']} ({audio_data['duration_minutes']} min)")
            return True
        else:
            return False

def main():
    agent = ImprovedAOLAgent()
    agent.run_improved_automation()

if __name__ == "__main__":
    main()
