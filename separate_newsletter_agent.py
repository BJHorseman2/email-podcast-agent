#!/usr/bin/env python3
"""
Separate Newsletter Podcast Agent
Creates individual podcasts for each newsletter
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

class SeparateNewsletterAgent:
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
    
    def find_specific_newsletter(self, newsletter_config):
        """Find a specific newsletter"""
        try:
            print(f"🔍 Looking for {newsletter_config['name']}...")
            
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
            imap.login(self.config['email']['username'], self.config['email']['password'])
            imap.select('INBOX')
            
            # Search by sender
            _, messages = imap.search(None, f'FROM "{newsletter_config["sender"]}"')
            
            if not messages[0]:
                print(f"   📭 No {newsletter_config['name']} emails found")
                imap.close()
                imap.logout()
                return None
            
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
            
            imap.close()
            imap.logout()
            
            if subject_match:
                newsletter_data = {
                    'name': newsletter_config['name'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body': body
                }
                print(f"   ✅ Found {newsletter_config['name']}: {subject}")
                return newsletter_data
            else:
                print(f"   ⚠️ {newsletter_config['name']} subject doesn't match criteria")
                return None
            
        except Exception as e:
            print(f"❌ Error finding {newsletter_config['name']}: {e}")
            return None
    
    def create_individual_script(self, newsletter):
        """Create script for individual newsletter"""
        name = newsletter['name']
        subject = newsletter['subject']
        content = newsletter['body']
        
        # Create personalized intro based on newsletter
        if "puck" in name.lower():
            intro = f"Good morning! Welcome to your Puck News podcast with insights from Jon Kelly."
        elif "mando" in name.lower():
            intro = f"Good morning! Welcome to your Mando Minutes update."
        else:
            intro = f"Good morning! Welcome to your {name} podcast."
        
        # Get key content
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p) > 50]
        
        if paragraphs:
            main_content = '\n\n'.join(paragraphs[:2])
        else:
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            main_content = '. '.join(sentences[:5]) + '.'
        
        # Limit content length for voice generation
        if len(main_content) > 1000:
            main_content = main_content[:1000] + "..."
        
        # Create personalized outro
        if "puck" in name.lower():
            outro = "That's your Puck News briefing for today. Stay informed and have a great day!"
        elif "mando" in name.lower():
            outro = "That wraps up your Mando Minutes update. See you next time!"
        else:
            outro = f"That's your {name} update for today. Stay informed!"
        
        script = f"""{intro}

Today's update: {subject}

Here's what you need to know:

{main_content}

{outro}"""
        
        return script.strip()
    
    def generate_individual_audio(self, script, newsletter_name):
        """Generate audio for individual newsletter"""
        try:
            print(f"🎙️ Generating audio for {newsletter_name}...")
            
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
            
            print(f"   🔄 Generating {newsletter_name} audio...")
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_name = re.sub(r'[^\w\s-]', '', newsletter_name).replace(' ', '_').lower()
                audio_filename = f"{safe_name}_podcast_{timestamp}.mp3"
                audio_path = os.path.join(self.podcasts_dir, audio_filename)
                
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content) / 1024 / 1024
                duration_estimate = len(script.split()) / 150
                
                print(f"   ✅ {newsletter_name} audio created: {audio_filename}")
                print(f"   📁 Size: {file_size:.1f} MB")
                print(f"   ⏱️ Duration: ~{duration_estimate:.1f} minutes")
                
                return {
                    'audio_file': audio_path,
                    'filename': audio_filename,
                    'size_mb': round(file_size, 1),
                    'duration_minutes': round(duration_estimate, 1)
                }
            else:
                print(f"   ❌ ElevenLabs error for {newsletter_name}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Voice generation failed for {newsletter_name}: {e}")
            return None
    
    def send_individual_email(self, newsletter, script, audio_data=None):
        """Send individual newsletter email"""
        try:
            print(f"📧 Sending {newsletter['name']} podcast...")
            
            msg = MIMEMultipart()
            msg['From'] = self.config['email_delivery']['sender_email']
            msg['To'] = self.config['email_delivery']['recipient_email']
            
            # Create subject
            date_str = datetime.now().strftime('%B %d, %Y')
            msg['Subject'] = f"🎙️ {newsletter['name']} Podcast - {date_str}"
            
            # Create email body
            if audio_data:
                body = f"""Good morning!

Your {newsletter['name']} email has been converted to an audio podcast.

📧 Original: {newsletter['subject']}
🎙️ Duration: ~{audio_data['duration_minutes']} minutes  
📁 File Size: {audio_data['size_mb']} MB
⏰ Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

The MP3 file is attached below - just tap to listen!

Enjoy your personalized {newsletter['name']} podcast.

🤖 Automated by your AOL Email-to-Podcast Agent"""
            else:
                body = f"""Good morning!

Your {newsletter['name']} email has been processed.

📧 Original: {newsletter['subject']}
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
            server.login(self.config['email_delivery']['sender_email'], self.config['email_delivery']['sender_password'])
            server.sendmail(self.config['email_delivery']['sender_email'], self.config['email_delivery']['recipient_email'], msg.as_string())
            server.quit()
            
            print(f"   ✅ {newsletter['name']} email sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed for {newsletter['name']}: {e}")
            return False
    
    def run_separate_newsletter_automation(self):
        """Run separate newsletter automation"""
        print("🚀 Separate Newsletter Podcast Automation")
        print("=" * 60)
        
        if not self.config:
            print("❌ Configuration not loaded")
            return False
        
        processed_count = 0
        
        # Process each newsletter separately
        for newsletter_config in self.config['target_emails']:
            print(f"\n{'='*50}")
            print(f"Processing {newsletter_config['name']}")
            print(f"{'='*50}")
            
            # Find this specific newsletter
            newsletter = self.find_specific_newsletter(newsletter_config)
            
            if newsletter:
                # Create individual script
                print(f"📝 Creating {newsletter['name']} script...")
                script = self.create_individual_script(newsletter)
                word_count = len(script.split())
                print(f"   ✅ {newsletter['name']} script ready ({word_count} words)")
                
                # Generate individual audio
                audio_data = self.generate_individual_audio(script, newsletter['name'])
                
                # Send individual email
                if self.send_individual_email(newsletter, script, audio_data):
                    processed_count += 1
                    print(f"   🎉 {newsletter['name']} podcast completed!")
                else:
                    print(f"   ❌ {newsletter['name']} email failed")
            else:
                print(f"   📭 No {newsletter_config['name']} found to process")
        
        print(f"\n{'='*60}")
        if processed_count > 0:
            print(f"🎉 SEPARATE AUTOMATION SUCCESSFUL!")
            print(f"📧 Processed {processed_count} newsletters")
            print(f"📧 Check your AOL inbox for individual podcast emails!")
            return True
        else:
            print("📭 No newsletters were processed")
            return False

def main():
    agent = SeparateNewsletterAgent()
    agent.run_separate_newsletter_automation()

if __name__ == "__main__":
    main()
