#!/usr/bin/env python3
"""
Enhanced Newsletter Agent with Better Content Extraction
Handles newsletters with links and incomplete content better
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
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class EnhancedNewsletterAgent:
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
    
    def extract_enhanced_content(self, email_message):
        """Enhanced content extraction that handles HTML and gets more content"""
        text_content = ""
        html_content = ""
        
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            for encoding in ['utf-8', 'iso-8859-1', 'windows-1252']:
                                try:
                                    text_content = payload.decode(encoding)
                                    break
                                except:
                                    continue
                    
                    elif content_type == "text/html":
                        payload = part.get_payload(decode=True)
                        if payload:
                            for encoding in ['utf-8', 'iso-8859-1', 'windows-1252']:
                                try:
                                    html_content = payload.decode(encoding)
                                    break
                                except:
                                    continue
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
                    for encoding in ['utf-8', 'iso-8859-1', 'windows-1252']:
                        try:
                            content = payload.decode(encoding)
                            if '<html' in content.lower():
                                html_content = content
                            else:
                                text_content = content
                            break
                        except:
                            continue
            
            # Process HTML content for better extraction
            if html_content:
                extracted_content = self.extract_from_html(html_content)
                if len(extracted_content) > len(text_content):
                    return extracted_content
            
            # Clean up text content
            if text_content:
                return self.clean_text_content(text_content)
            
            return "Content could not be extracted"
            
        except Exception as e:
            print(f"Error extracting content: {e}")
            return "Content extraction failed"
    
    def extract_from_html(self, html_content):
        """Extract better content from HTML emails"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'header', 'footer', 'nav']):
                element.decompose()
            
            # Find main content areas (common newsletter patterns)
            content_parts = []
            
            # Look for article content, main divs, etc.
            main_selectors = [
                'article', '[role="main"]', '.content', '.main-content',
                '.newsletter-content', '.email-content', 'main', '.body'
            ]
            
            for selector in main_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(separator='\n', strip=True)
                    if len(text) > 100:  # Only substantial content
                        content_parts.append(text)
            
            # If no main content found, get all paragraphs and divs
            if not content_parts:
                for tag in ['p', 'div', 'td']:
                    elements = soup.find_all(tag)
                    for element in elements:
                        text = element.get_text(strip=True)
                        if len(text) > 50 and not self.is_footer_content(text):
                            content_parts.append(text)
            
            # Combine and clean content
            combined_content = '\n\n'.join(content_parts)
            return self.clean_text_content(combined_content)
            
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            # Fallback to simple HTML stripping
            return re.sub(r'<[^>]+>', '', html_content)
    
    def is_footer_content(self, text):
        """Check if text is likely footer/unsubscribe content"""
        footer_indicators = [
            'unsubscribe', 'privacy policy', 'terms of service',
            'view in browser', 'forward to a friend', 'copyright',
            'update preferences', 'manage subscription'
        ]
        return any(indicator in text.lower() for indicator in footer_indicators)
    
    def clean_text_content(self, content):
        """Clean and format text content"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        content = re.sub(r'\r\n', '\n', content)
        
        # Remove email artifacts
        content = re.sub(r'=\s*\n', '', content)  # Remove line breaks with =
        content = re.sub(r'\[.*?\]', '', content)  # Remove [brackets] content
        
        # Remove common newsletter footers
        footer_patterns = [
            r'unsubscribe.*$',
            r'this email was sent.*$',
            r'you received this.*$',
            r'privacy policy.*$',
            r'view in browser.*$',
            r'follow us on.*$',
            r'copyright.*$',
            r'www\..*\.com.*$',
            r'click here.*$',
            r'read more.*$'
        ]
        
        for pattern in footer_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)
        
        return content.strip()
    
    def find_specific_newsletter(self, newsletter_config):
        """Find a specific newsletter with enhanced content extraction"""
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
            
            # Enhanced content extraction
            body = self.extract_enhanced_content(email_message)
            
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
                print(f"   📄 Content length: {len(body)} characters")
                return newsletter_data
            else:
                print(f"   ⚠️ {newsletter_config['name']} subject doesn't match criteria")
                return None
            
        except Exception as e:
            print(f"❌ Error finding {newsletter_config['name']}: {e}")
            return None
    
    def create_enhanced_script(self, newsletter):
        """Create enhanced script with better content handling"""
        name = newsletter['name']
        subject = newsletter['subject']
        content = newsletter['body']
        
        print(f"📝 Creating enhanced script for {name}...")
        print(f"   📊 Raw content length: {len(content)} characters")
        
        # Create personalized intro
        if "puck" in name.lower() or "jon" in name.lower():
            intro = f"Good morning! Welcome to your Puck News podcast with insights from Jon Kelly."
        elif "mando" in name.lower():
            intro = f"Good morning! Welcome to your Mando Minutes update."
        else:
            intro = f"Good morning! Welcome to your {name} podcast."
        
        # Enhanced content processing
        # Split into meaningful sections
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Filter out very short paragraphs (likely fragments)
        substantial_paragraphs = [p for p in paragraphs if len(p) > 30]
        
        # If we have substantial paragraphs, use more of them
        if substantial_paragraphs and len(substantial_paragraphs) >= 2:
            # Use up to 4 substantial paragraphs for richer content
            main_content = '\n\n'.join(substantial_paragraphs[:4])
        elif substantial_paragraphs:
            # Use what we have plus some regular paragraphs
            main_content = '\n\n'.join(substantial_paragraphs[:2])
            if len(paragraphs) > len(substantial_paragraphs):
                additional = [p for p in paragraphs if p not in substantial_paragraphs][:2]
                main_content += '\n\n' + '\n\n'.join(additional)
        else:
            # Fallback to sentence-based extraction
            sentences = [s.strip() for s in content.split('.') if s.strip() and len(s) > 20]
            main_content = '. '.join(sentences[:8]) + '.'
        
        # Ensure we have a reasonable amount of content
        if len(main_content) < 200:
            # If content is still too short, include more of the original
            main_content = content[:1500] + "..." if len(content) > 1500 else content
        
        # Limit for voice generation (ElevenLabs has limits)
        if len(main_content) > 2500:
            main_content = main_content[:2500] + "..."
        
        # Create personalized outro
        if "puck" in name.lower() or "jon" in name.lower():
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
        
        final_script = script.strip()
        word_count = len(final_script.split())
        print(f"   ✅ Enhanced script created: {word_count} words")
        print(f"   📏 Final content length: {len(final_script)} characters")
        
        return final_script
    
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

Your {newsletter['name']} email has been converted to an enhanced audio podcast with more complete content.

📧 Original: {newsletter['subject']}
🎙️ Duration: ~{audio_data['duration_minutes']} minutes  
📁 File Size: {audio_data['size_mb']} MB
⏰ Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

The MP3 file is attached below - just tap to listen!

Enjoy your personalized {newsletter['name']} podcast with enhanced content extraction.

🤖 Automated by your AOL Email-to-Podcast Agent"""
            else:
                body = f"""Good morning!

Your {newsletter['name']} email has been processed with enhanced content extraction.

📧 Original: {newsletter['subject']}
⏰ Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

Enhanced Podcast Script:
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
    
    def run_enhanced_automation(self):
        """Run enhanced automation with better content extraction"""
        print("🚀 Enhanced Newsletter Podcast Automation")
        print("📈 Better content extraction for newsletters with links")
        print("=" * 60)
        
        if not self.config:
            print("❌ Configuration not loaded")
            return False
        
        processed_count = 0
        
        # Process each newsletter separately
        for newsletter_config in self.config['target_emails']:
            print(f"\n{'='*50}")
            print(f"Processing {newsletter_config['name']} (Enhanced)")
            print(f"{'='*50}")
            
            # Find this specific newsletter
            newsletter = self.find_specific_newsletter(newsletter_config)
            
            if newsletter:
                # Create enhanced script
                script = self.create_enhanced_script(newsletter)
                
                # Generate individual audio
                audio_data = self.generate_individual_audio(script, newsletter['name'])
                
                # Send individual email
                if self.send_individual_email(newsletter, script, audio_data):
                    processed_count += 1
                    print(f"   🎉 {newsletter['name']} enhanced podcast completed!")
                else:
                    print(f"   ❌ {newsletter['name']} email failed")
            else:
                print(f"   📭 No {newsletter_config['name']} found to process")
        
        print(f"\n{'='*60}")
        if processed_count > 0:
            print(f"🎉 ENHANCED AUTOMATION SUCCESSFUL!")
            print(f"📧 Processed {processed_count} newsletters with better content")
            print(f"📧 Check your AOL inbox for enhanced podcast emails!")
            return True
        else:
            print("📭 No newsletters were processed")
            return False

def main():
    agent = EnhancedNewsletterAgent()
    agent.run_enhanced_automation()

if __name__ == "__main__":
    main()
