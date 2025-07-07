#!/usr/bin/env python3
"""
Multi-Newsletter Podcast Agent
Processes multiple newsletters into a single daily digest podcast
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class MultiNewsletterAgent:
    def __init__(self):
        self.config = self.load_config()
        self.podcasts_dir = "podcasts"
        os.makedirs(self.podcasts_dir, exist_ok=True)
        
    def load_config(self):
        """Load multi-newsletter configuration"""
        try:
            with open('multi_email_config.json', 'r') as f:
                return json.load(f)
        except:
            print("❌ Multi-email config file not found")
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
        """Extract and clean email body"""
        body = ""
        
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
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
                                body = re.sub(r'<[^>]+>', '', html_content)
                            except:
                                continue
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
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
            
            # Remove email footers
            cleanup_patterns = [
                r'unsubscribe.*$',
                r'this email was sent.*$',
                r'you received this.*$',
                r'privacy policy.*$',
                r'view in browser.*$',
                r'follow us on.*$',
                r'Copyright.*$'
            ]
            
            for pattern in cleanup_patterns:
                body = re.sub(pattern, '', body, flags=re.IGNORECASE | re.MULTILINE)
            
            return body.strip()
            
        except Exception as e:
            print(f"Error extracting body: {e}")
            return "Content could not be extracted"
    
    def find_newsletters(self):
        """Find all configured newsletters"""
        found_newsletters = []
        
        try:
            print("🔍 Looking for newsletters...")
            
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
            imap.login(self.config['email']['username'], self.config['email']['password'])
            imap.select('INBOX')
            
            # Search for each configured newsletter
            for newsletter_config in self.config['target_emails']:
                print(f"   🔎 Searching for {newsletter_config['name']}...")
                
                # Search by sender
                _, messages = imap.search(None, f'FROM "{newsletter_config["sender"]}"')
                
                if messages[0]:
                    # Get the most recent email
                    email_ids = messages[0].split()
                    latest_id = email_ids[-1]
                    
                    _, msg_data = imap.fetch(latest_id, '(RFC822)')
                    email_message = email.message_from_bytes(msg_data[0][1])
                    
                    # Decode headers
                    subject = self.decode_email_header(email_message['Subject'])
                    sender = self.decode_email_header(email_message['From'])
                    date = email_message['Date']
                    body = self.extract_clean_body(email_message)
                    
                    # Check if subject matches
                    subject_match = any(keyword.lower() in subject.lower() 
                                      for keyword in newsletter_config['subject_contains'])
                    
                    if subject_match:
                        newsletter_data = {
                            'name': newsletter_config['name'],
                            'subject': subject,
                            'sender': sender,
                            'date': date,
                            'body': body,
                            'priority': newsletter_config['priority']
                        }
                        found_newsletters.append(newsletter_data)
                        print(f"   ✅ Found {newsletter_config['name']}: {subject}")
                    else:
                        print(f"   ⚠️ {newsletter_config['name']} subject doesn't match criteria")
                else:
                    print(f"   📭 No {newsletter_config['name']} emails found")
            
            imap.close()
            imap.logout()
            
            # Sort by priority
            found_newsletters.sort(key=lambda x: x['priority'])
            
            return found_newsletters
            
        except Exception as e:
            print(f"❌ Error finding newsletters: {e}")
            return []
    
    def create_digest_script(self, newsletters):
        """Create a combined digest podcast script"""
        
        if not newsletters:
            return "No newsletters found for today's digest."
        
        # Create introduction
        newsletter_names = [n['name'] for n in newsletters]
        if len(newsletter_names) == 1:
            intro = f"Good morning! Welcome to your daily newsletter podcast featuring {newsletter_names[0]}."
        else:
            intro = f"Good morning! Welcome to your daily newsletter digest featuring {', '.join(newsletter_names[:-1])} and {newsletter_names[-1]}."
        
        script_parts = [intro, ""]
        
        # Add each newsletter
        for i, newsletter in enumerate(newsletters, 1):
            script_parts.append(f"First up, let's dive into {newsletter['name']}.")
            script_parts.append(f"Today's update: {newsletter['subject']}")
            script_parts.append("")
            
            # Get key content
            content = newsletter['body']
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p) > 50]
            
            if paragraphs:
                main_content = '\n\n'.join(paragraphs[:2])
            else:
                sentences = [s.strip() for s in content.split('.') if s.strip()]
                main_content = '. '.join(sentences[:4]) + '.'
            
            # Limit content length
            if len(main_content) > 800:
                main_content = main_content[:800] + "..."
            
            script_parts.append(main_content)
            script_parts.append("")
            
            if i < len(newsletters):
                script_parts.append("Now, let's move on to our next update.")
                script_parts.append("")
        
        # Add closing
        script_parts.append("That wraps up today's newsletter digest. Stay informed, and I'll see you tomorrow with your next daily update!")
        
        return '\n'.join(script_parts)
    
    def generate_voice_audio(self, script):
        """Generate audio using ElevenLabs"""
        try:
            print("🎙️ Generating voice audio for digest...")
            
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
            
            print("   🔄 Generating digest audio...")
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                audio_filename = f"newsletter_digest_{timestamp}.mp3"
                audio_path = os.path.join(self.podcasts_dir, audio_filename)
                
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content) / 1024 / 1024
                duration_estimate = len(script.split()) / 150
                
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
    
    def send_digest_email(self, newsletters, script, audio_data=None):
        """Send digest email"""
        try:
            print("📧 Sending newsletter digest...")
            
            msg = MIMEMultipart()
            msg['From'] = self.config['email_delivery']['sender_email']
            msg['To'] = self.config['email_delivery']['recipient_email']
            
            # Create subject
            date_str = datetime.now().strftime('%B %d, %Y')
            msg['Subject'] = f"🎙️ Daily Newsletter Digest - {date_str}"
            
            # Create sources list
            sources = ', '.join([n['name'] for n in newsletters])
            
            # Create email body
            if audio_data:
                body = f"""Good morning!

Your daily newsletters have been converted to an audio digest podcast.

📧 Today's Sources: {sources}
🎙️ Duration: ~{audio_data['duration_minutes']} minutes  
📁 File Size: {audio_data['size_mb']} MB
⏰ Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

The MP3 file is attached below - just tap to listen to your personalized digest!

Enjoy staying informed with your automated newsletter podcast.

🤖 Automated by your AOL Email-to-Podcast Agent"""
            else:
                body = f"""Good morning!

Your daily newsletters have been processed into a digest.

📧 Today's Sources: {sources}
⏰ Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

Digest Script:
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
            server.login(self.config['email_delivery']['sender_email'], self.config['email_delivery']['sender_password'])
            server.sendmail(self.config['email_delivery']['sender_email'], self.config['email_delivery']['recipient_email'], msg.as_string())
            server.quit()
            
            print("   ✅ Digest email sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False
    
    def run_multi_newsletter_automation(self):
        """Run multi-newsletter automation"""
        print("🚀 Multi-Newsletter Digest Automation")
        print("=" * 60)
        
        if not self.config:
            print("❌ Configuration not loaded")
            return False
        
        # Find all newsletters
        newsletters = self.find_newsletters()
        
        if not newsletters:
            print("📭 No newsletters found for digest")
            return False
        
        print(f"\n📊 Found {len(newsletters)} newsletters for digest")
        
        # Create combined script
        print("📝 Creating digest script...")
        script = self.create_digest_script(newsletters)
        word_count = len(script.split())
        print(f"   ✅ Digest script ready ({word_count} words)")
        
        # Generate voice
        audio_data = self.generate_voice_audio(script)
        
        # Send digest email
        if self.send_digest_email(newsletters, script, audio_data):
            print("\n🎉 MULTI-NEWSLETTER AUTOMATION SUCCESSFUL!")
            print("📧 Check your AOL inbox for your newsletter digest!")
            if audio_data:
                print(f"🎵 Digest audio: {audio_data['filename']} ({audio_data['duration_minutes']} min)")
            return True
        else:
            return False

def main():
    agent = MultiNewsletterAgent()
    agent.run_multi_newsletter_automation()

if __name__ == "__main__":
    main()
