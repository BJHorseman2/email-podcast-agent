#!/usr/bin/env python3
"""
Process Today's Mando Minutes with REAL Content
No more useless link titles - actual analysis and insights
"""

import imaplib
import email
import ssl
import json
import logging
import requests
import os
from datetime import datetime
from smart_mando_processor import SmartMandoProcessor
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

logging.basicConfig(level=logging.INFO)

# Load config
with open('multi_newsletter_config.json', 'r') as f:
    config = json.load(f)

# Connect to AOL
print("🔗 Connecting to AOL...")
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
imap.login(config['email']['username'], config['email']['password'])
print("✅ Connected!")

# Find today's Mando Minutes
imap.select('INBOX')
_, data = imap.search(None, 'SUBJECT "Mando Minutes" SINCE 07-Jul-2025')

if not data[0]:
    print("❌ No Mando Minutes found today")
    exit()

# Get the email
email_id = data[0].split()[0]
_, msg_data = imap.fetch(email_id, '(RFC822)')
email_message = email.message_from_bytes(msg_data[0][1])

subject = email_message.get('Subject', 'Mando Minutes')
print(f"\n📧 Found: {subject}")

# Extract body
body = ""
if email_message.is_multipart():
    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            break
else:
    body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')

# Process with SMART processor
print("\n🧠 Creating intelligent podcast content...")
processor = SmartMandoProcessor()
script, word_count, duration = processor.process_mando_email(body)

print(f"✅ Script created: {word_count} words (~{duration:.1f} minutes)")

# Save script
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
script_file = f"podcasts/mando_smart_{timestamp}.txt"
os.makedirs('podcasts', exist_ok=True)
with open(script_file, 'w') as f:
    f.write(script)

# Generate audio with ElevenLabs
print("\n🎙️ Generating audio...")
ELEVENLABS_API_KEY = config['voice_generation']['api_key']
VOICE_ID = config['voice_generation']['voice_id']

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": ELEVENLABS_API_KEY
}

data = {
    "text": script,
    "model_id": config['voice_generation']['model'],
    "voice_settings": config['voice_generation']['voice_settings']
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    audio_file = f"podcasts/mando_smart_{timestamp}.mp3"
    with open(audio_file, 'wb') as f:
        f.write(response.content)
    print(f"✅ Audio generated: {os.path.getsize(audio_file) / 1024 / 1024:.1f} MB")
else:
    print(f"❌ Audio generation failed: {response.status_code}")
    audio_file = None

# Send email
if audio_file:
    print("\n📧 Sending enhanced podcast email...")
    
    msg = MIMEMultipart()
    msg['From'] = config['email']['username']
    msg['To'] = config['email']['username']
    msg['Subject'] = f"🎙️ Your ENHANCED Mando Minutes Podcast - {datetime.now().strftime('%B %d')}"
    
    email_body = f"""Good morning!

Your Mando Minutes has been transformed into a comprehensive market analysis podcast.

📰 Original: {subject}
🎙️ Duration: {duration:.1f} minutes
📊 Word count: {word_count} words
🧠 Content: Full analysis and insights (not just link titles!)

What's included:
✓ Detailed market analysis
✓ Context for each news item
✓ Trading insights
✓ Actionable takeaways

The enhanced audio file is attached.

🤖 Created by your Smart Email-to-Podcast AI
"""
    
    msg.attach(MIMEText(email_body, 'plain'))
    
    # Attach audio
    with open(audio_file, "rb") as f:
        part = MIMEBase('audio', 'mpeg')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="mando_minutes_enhanced.mp3"')
        msg.attach(part)
    
    # Send
    server = smtplib.SMTP('smtp.aol.com', 587)
    server.starttls()
    server.login(config['email']['username'], config['email']['password'])
    server.send_message(msg)
    server.quit()
    
    print("✅ Enhanced podcast sent to your email!")
else:
    print("⚠️  Audio generation failed, but script is ready at:", script_file)

print("\n🎯 Summary:")
print(f"   - Extracted Mando Minutes content")
print(f"   - Created {word_count}-word analysis")
print(f"   - Generated {duration:.1f}-minute podcast")
print(f"   - Delivered to your inbox")

imap.logout()
