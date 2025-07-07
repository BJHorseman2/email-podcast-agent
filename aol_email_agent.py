#!/usr/bin/env python3
"""
AOL Email to Podcast Agent
Connects to AOL.com email and converts specific morning emails to podcasts
"""

import imaplib
import email
import json
import time
import os
import ssl
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import schedule
import logging
import re
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aol_podcast_agent.log'),
        logging.StreamHandler()
    ]
)

class AOLEmailPodcastAgent:
    def __init__(self, config_file='config.json'):
        """Initialize the AOL email agent"""
        self.config = self.load_config(config_file)
        self.imap = None
        self.podcasts_dir = self.config['output']['podcast_folder']
        os.makedirs(self.podcasts_dir, exist_ok=True)
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Configuration file {config_file} not found!")
            raise
    
    def connect_to_aol(self):
        """Establish secure connection to AOL email"""
        try:
            logging.info("Connecting to AOL email server...")
            
            # Create SSL context for secure connection
            context = ssl.create_default_context()
            
            # Connect to AOL IMAP server
            self.imap = imaplib.IMAP4_SSL(
                self.config['email']['imap_server'],
                self.config['email']['imap_port'],
                ssl_context=context
            )
            
            # Login with credentials
            self.imap.login(
                self.config['email']['username'],
                self.config['email']['password']
            )
            
            logging.info("✅ Successfully connected to AOL email!")
            return True
            
        except imaplib.IMAP4.error as e:
            logging.error(f"❌ AOL IMAP error: {e}")
            return False
        except Exception as e:
            logging.error(f"❌ Connection error: {e}")
            return False
    
    def find_target_email(self):
        """Find the specific morning email from AOL inbox"""
        try:
            # Select inbox
            self.imap.select(self.config['email']['folder'])
            
            # Build search criteria for recent emails
            search_criteria = []
            
            # Time window - emails from last 12 hours
            since_date = (datetime.now() - timedelta(hours=self.config['target_email']['max_age_hours'])).strftime('%d-%b-%Y')
            search_criteria.append(f'SINCE {since_date}')
            
            # Only unread emails if specified
            if self.config['filters']['only_unread']:
                search_criteria.append('UNSEEN')
            
            # Sender filter if specified
            if self.config['target_email']['sender']:
                search_criteria.append(f'FROM "{self.config["target_email"]["sender"]}"')
            
            # Subject filters
            subject_filters = []
            if self.config['target_email']['subject_exact']:
                subject_filters.append(f'SUBJECT "{self.config["target_email"]["subject_exact"]}"')
            else:
                for keyword in self.config['target_email']['subject_contains']:
                    subject_filters.append(f'SUBJECT "{keyword}"')
            
            # Combine search criteria
            final_criteria = '(' + ' '.join(search_criteria) + ')'
            if subject_filters:
                final_criteria += ' (' + ' OR '.join(subject_filters) + ')'
            
            logging.info(f"🔍 Searching with criteria: {final_criteria}")
            
            # Search for emails
            _, message_numbers = self.imap.search(None, final_criteria)
            
            if not message_numbers[0]:
                logging.info("📭 No matching emails found")
                return None
            
            # Get the most recent matching email
            email_ids = message_numbers[0].split()
            latest_email_id = email_ids[-1]
            
            # Fetch the email
            _, msg_data = self.imap.fetch(latest_email_id, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Extract email details
            email_data = {
                'id': latest_email_id.decode(),
                'subject': email_message['Subject'],
                'sender': email_message['From'],
                'date': email_message['Date'],
                'body': self.extract_email_body(email_message),
                'timestamp': datetime.now().isoformat()
            }
            
            # Validate email content
            if len(email_data['body']) < self.config['filters']['minimum_content_length']:
                logging.warning("⚠️ Email content too short, skipping")
                return None
            
            # Check for excluded keywords
            content_lower = email_data['body'].lower()
            for keyword in self.config['filters']['exclude_keywords']:
                if keyword.lower() in content_lower:
                    logging.warning(f"⚠️ Email contains excluded keyword '{keyword}', skipping")
                    return None
            
            logging.info(f"📧 Found target email: {email_data['subject']}")
            logging.info(f"📄 Content length: {len(email_data['body'])} characters")
            
            return email_data
            
        except Exception as e:
            logging.error(f"❌ Error finding target email: {e}")
            return None
    
    def extract_email_body(self, email_message):
        """Extract plain text body from email message"""
        body = ""
        
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode('utf-8', errors='ignore')
                            break
                    elif content_type == "text/html" and not body:
                        # Fallback to HTML if no plain text
                        payload = part.get_payload(decode=True)
                        if payload:
                            html_content = payload.decode('utf-8', errors='ignore')
                            # Simple HTML to text conversion
                            body = re.sub(r'<[^>]+>', '', html_content)
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
            
            # Clean up the text
            body = re.sub(r'\n\s*\n', '\n\n', body)  # Remove excessive newlines
            body = re.sub(r'[ \t]+', ' ', body)       # Remove excessive spaces
            body = body.strip()
            
        except Exception as e:
            logging.error(f"Error extracting email body: {e}")
            body = "Error extracting email content"
        
        return body
    
    def create_podcast_script(self, email_data):
        """Create an engaging podcast script from email content"""
        try:
            # Extract key information
            subject = email_data['subject']
            content = email_data['body']
            sender = email_data['sender']
            
            # Create summary (first few sentences)
            sentences = content.split('. ')
            summary = '. '.join(sentences[:3]) + '.' if len(sentences) >= 3 else content
            
            # Extract key points using simple heuristics
            key_points = []
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if any(indicator in line.lower() for indicator in ['•', '-', '*', 'key', 'important', 'note']):
                    if len(line) > 20 and len(line) < 200:  # Reasonable length
                        key_points.append(line)
                        
            # Limit key points
            key_points = key_points[:5]
            
            # Build the podcast script
            script_parts = []
            
            # Intro
            intro = self.config['podcast']['intro_text']
            script_parts.append(intro)
            script_parts.append(f"\nToday's topic: {subject}")
            
            # Main content
            script_parts.append(f"\nThis comes from {sender}")
            script_parts.append(f"\nHere's what you need to know:")
            script_parts.append(f"\n{summary}")
            
            # Key points if available
            if key_points:
                script_parts.append(f"\nThe key highlights include:")
                for point in key_points:
                    clean_point = re.sub(r'^[•\-\*]\s*', '', point)
                    script_parts.append(f"• {clean_point}")
            
            # Additional content if there's more
            if len(content) > len(summary) + 100:
                remaining_content = content[len(summary):].strip()
                # Get next important paragraph
                paragraphs = remaining_content.split('\n\n')
                for para in paragraphs[:2]:
                    if len(para) > 50:
                        script_parts.append(f"\n{para}")
                        break
            
            # Outro
            outro = self.config['podcast']['outro_text']
            script_parts.append(f"\n{outro}")
            
            podcast_script = '\n'.join(script_parts)
            
            # Calculate metadata
            word_count = len(podcast_script.split())
            estimated_duration = max(1, round(word_count / 150))  # 150 words per minute
            
            return {
                'script': podcast_script,
                'word_count': word_count,
                'estimated_duration': estimated_duration,
                'summary': summary,
                'key_points': key_points
            }
            
        except Exception as e:
            logging.error(f"Error creating podcast script: {e}")
            return None
    
    def save_podcast_content(self, email_data, podcast_data):
        """Save podcast content and create NotebookLM instructions"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            email_id = email_data['id']
            
            # Prepare content structure
            content = {
                'email': {
                    'subject': email_data['subject'],
                    'sender': email_data['sender'],
                    'date': email_data['date'],
                    'id': email_id
                },
                'podcast': {
                    'script': podcast_data['script'],
                    'word_count': podcast_data['word_count'],
                    'estimated_duration': f"{podcast_data['estimated_duration']} minutes",
                    'summary': podcast_data['summary'],
                    'key_points': podcast_data['key_points']
                },
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'agent_version': '1.0-AOL',
                    'source': 'AOL Email'
                }
            }
            
            # Save main content file
            content_filename = f"podcast_content_{timestamp}.json"
            content_path = os.path.join(self.podcasts_dir, content_filename)
            
            with open(content_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            
            # Save script file
            script_filename = f"podcast_script_{timestamp}.txt"
            script_path = os.path.join(self.podcasts_dir, script_filename)
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(podcast_data['script'])
            
            # Create NotebookLM instructions
            instructions = self.create_notebooklm_instructions(email_data, podcast_data, timestamp)
            instructions_filename = f"notebooklm_instructions_{timestamp}.txt"
            instructions_path = os.path.join(self.podcasts_dir, instructions_filename)
            
            with open(instructions_path, 'w', encoding='utf-8') as f:
                f.write(instructions)
            
            logging.info(f"💾 Saved podcast content: {content_filename}")
            logging.info(f"📝 Saved script: {script_filename}")
            logging.info(f"📋 Created instructions: {instructions_filename}")
            
            return {
                'content_file': content_path,
                'script_file': script_path,
                'instructions_file': instructions_path
            }
            
        except Exception as e:
            logging.error(f"Error saving podcast content: {e}")
            return None
    
    def create_notebooklm_instructions(self, email_data, podcast_data, timestamp):
        """Create detailed NotebookLM instructions"""
        instructions = f"""
🎙️ NOTEBOOKLM PODCAST GENERATION - AOL EMAIL
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Email Subject: {email_data['subject']}
Estimated Duration: {podcast_data['estimated_duration']} minutes
Word Count: {podcast_data['word_count']} words

===========================================

STEP 1: Access NotebookLM
• Go to https://notebooklm.google.com
• Sign in with your Google account

STEP 2: Create New Notebook
• Click "Create new notebook"
• Title: "{email_data['subject']} - Daily Podcast"

STEP 3: Add Source Content
• Click "Add source"
• Select "Paste text"
• Copy and paste the script below:

---BEGIN PODCAST SCRIPT---
{podcast_data['script']}
---END PODCAST SCRIPT---

STEP 4: Generate Audio Overview
• Click "Generate" in the top right
• Select "Audio Overview"
• Wait 2-5 minutes for generation to complete

STEP 5: Download Your Podcast
• Click play button to preview
• Click download icon to save MP3
• Suggested filename: aol_morning_podcast_{timestamp}.mp3
• Save to: {os.path.abspath(self.podcasts_dir)}

STEP 6: Optional Enhancements
• Adjust speaker personalities in settings
• Add follow-up questions for deeper discussion
• Generate alternative versions with different focus

===========================================

📊 EMAIL SUMMARY:
From: {email_data['sender']}
Subject: {email_data['subject']}
Content Length: {len(email_data['body'])} characters
Key Points: {len(podcast_data['key_points'])} identified

🎯 PODCAST PREVIEW:
{podcast_data['summary'][:200]}...

✅ Ready for NotebookLM audio generation!

💡 TIP: For best results, listen to the preview before downloading
and adjust the source content if needed for better flow.
        """.strip()
        
        return instructions
    
    def mark_email_as_processed(self, email_id):
        """Mark email as read after successful processing"""
        try:
            if self.config['filters']['mark_as_read_after_processing']:
                self.imap.store(email_id, '+FLAGS', '\\Seen')
                logging.info(f"✅ Marked email {email_id} as read")
        except Exception as e:
            logging.error(f"Error marking email as read: {e}")
    
    def cleanup_old_files(self):
        """Clean up old podcast files based on retention policy"""
        try:
            keep_days = self.config['output']['keep_files_days']
            cutoff_time = datetime.now() - timedelta(days=keep_days)
            
            for filename in os.listdir(self.podcasts_dir):
                filepath = os.path.join(self.podcasts_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        logging.info(f"🗑️ Cleaned up old file: {filename}")
                        
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
    
    def run_morning_process(self):
        """Main process - run every morning"""
        try:
            logging.info("🌅 Starting AOL morning email-to-podcast process...")
            
            # Connect to AOL
            if not self.connect_to_aol():
                logging.error("❌ Failed to connect to AOL email")
                return False
            
            # Find target email
            email_data = self.find_target_email()
            if not email_data:
                logging.info("📭 No target email found for processing")
                return False
            
            # Create podcast script
            podcast_data = self.create_podcast_script(email_data)
            if not podcast_data:
                logging.error("❌ Failed to create podcast script")
                return False
            
            # Save content and create instructions
            files = self.save_podcast_content(email_data, podcast_data)
            if not files:
                logging.error("❌ Failed to save podcast content")
                return False
            
            # Mark email as processed
            self.mark_email_as_processed(email_data['id'])
            
            # Cleanup old files
            self.cleanup_old_files()
            
            logging.info("🎉 Morning process completed successfully!")
            logging.info(f"📂 Files saved to: {self.podcasts_dir}")
            logging.info(f"🎙️ Estimated podcast duration: {podcast_data['estimated_duration']} minutes")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Error in morning process: {e}")
            return False
        finally:
            # Always close the connection
            if self.imap:
                try:
                    self.imap.close()
                    self.imap.logout()
                except:
                    pass
    
    def schedule_daily_run(self):
        """Schedule the agent to run daily"""
        run_time = self.config['schedule']['run_time']
        schedule.every().day.at(run_time).do(self.run_morning_process)
        
        logging.info(f"📅 Scheduled daily run at {run_time}")
        logging.info("🔄 Agent is now running in background...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def test_connection(self):
        """Test AOL email connection"""
        logging.info("🧪 Testing AOL email connection...")
        if self.connect_to_aol():
            logging.info("✅ Connection test successful!")
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass
            return True
        else:
            logging.error("❌ Connection test failed!")
            return False

def main():
    """Main execution function"""
    print("🚀 AOL Email to Podcast Agent")
    print("=" * 40)
    
    agent = AOLEmailPodcastAgent()
    
    # Test connection first
    if not agent.test_connection():
        print("❌ Please check your AOL email configuration in config.json")
        print("📝 Make sure you have:")
        print("   - Correct username@aol.com")
        print("   - Valid AOL app password (not regular password)")
        print("   - IMAP access enabled in AOL settings")
        return
    
    print("✅ AOL connection successful!")
    print(f"📁 Podcast files will be saved to: {agent.podcasts_dir}")
    
    # Run once for testing
    print("\n🧪 Running test process...")
    success = agent.run_morning_process()
    
    if success:
        print("🎉 Test completed successfully!")
        print("\n🔄 To enable daily automation:")
        print("   python3 aol_email_agent.py --schedule")
    else:
        print("❌ Test failed. Check logs for details.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        agent = AOLEmailPodcastAgent()
        agent.schedule_daily_run()
    else:
        main()
