#!/usr/bin/env python3
"""
Send the comprehensive Mando podcast that was already created
"""

import os
import json
import requests
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

print("📧 Sending your comprehensive Mando Minutes podcast...")

# Load config
with open('multi_newsletter_config.json', 'r') as f:
    config = json.load(f)

# Find the comprehensive script
script_file = "podcasts/mando_comprehensive_20250707_110807.txt"
if not os.path.exists(script_file):
    print("❌ Script file not found!")
    exit()

# Read the script
with open(script_file, 'r') as f:
    script = f.read()

word_count = len(script.split())
duration = word_count / 150

print(f"\n📝 Found comprehensive script:")
print(f"   Words: {word_count:,}")
print(f"   Duration: {duration:.1f} minutes")

# Try to generate audio again
print("\n🎙️ Generating audio (this may take a moment for long content)...")

ELEVENLABS_API_KEY = config['voice_generation']['api_key']
VOICE_ID = config['voice_generation']['voice_id']

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": ELEVENLABS_API_KEY
}

# For very long content, we might need to adjust settings
data = {
    "text": script,
    "model_id": "eleven_monolingual_v1",  # More stable for long content
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}

try:
    response = requests.post(url, json=data, headers=headers, timeout=120)  # Longer timeout
    
    if response.status_code == 200:
        audio_file = f"podcasts/mando_comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        with open(audio_file, 'wb') as f:
            f.write(response.content)
        file_size_mb = os.path.getsize(audio_file) / 1024 / 1024
        print(f"✅ Audio generated: {file_size_mb:.1f} MB")
        audio_success = True
    else:
        print(f"❌ Audio generation failed: {response.status_code}")
        print(f"Error: {response.text[:200]}...")
        audio_file = None
        audio_success = False
        
        # Check if it's a length issue
        if "string_too_long" in response.text or "too_long" in response.text:
            print("\n⚠️  Script may be too long for ElevenLabs in one request")
            print("   Attempting to send podcast with script attached instead...")
            
except Exception as e:
    print(f"❌ Audio generation error: {e}")
    audio_file = None
    audio_success = False

# Send email regardless
print("\n📧 Sending email...")

msg = MIMEMultipart()
msg['From'] = config['email']['username']
msg['To'] = config['email']['username']
msg['Subject'] = f"🎙️ Your COMPREHENSIVE Mando Minutes ({word_count:,} words) - {datetime.now().strftime('%B %d')}"

email_body = f"""Good morning!

Your comprehensive Mando Minutes analysis is ready.

📊 Analysis Statistics:
• News items covered: 42
• Word count: {word_count:,} words
• Estimated duration: {duration:.1f} minutes
• Coverage: EVERY item analyzed in detail

"""

if audio_success:
    email_body += """✅ Audio Status: Successfully generated!
The MP3 file is attached below.

"""
else:
    email_body += """⚠️ Audio Status: Generation failed (content may be too long)
The full text script is attached instead. You can:
1. Read the comprehensive analysis
2. Use your own text-to-speech tool
3. Upload to ElevenLabs in smaller chunks

"""

email_body += """What's Included in Your Analysis:
• Detailed breakdown of all crypto price movements
• In-depth analysis of whale movements ($2.2B and $50B transfers)
• ETF flow analysis with institutional positioning insights
• Regulatory developments (stablecoin law, crypto tax bills)
• Market sentiment indicators (extreme greed implications)
• Traditional market correlation analysis
• Specific trading levels and risk management strategies
• Actionable insights for each news item

This is comprehensive market intelligence, not just a summary.

🤖 Created by your Comprehensive Email-to-Podcast AI
"""

msg.attach(MIMEText(email_body, 'plain'))

# Attach audio if available
if audio_file and os.path.exists(audio_file):
    print("📎 Attaching audio file...")
    with open(audio_file, "rb") as f:
        part = MIMEBase('audio', 'mpeg')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="mando_comprehensive.mp3"')
        msg.attach(part)

# Always attach the script
print("📎 Attaching text script...")
with open(script_file, "rb") as f:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="mando_comprehensive_script.txt"')
    msg.attach(part)

# Send via AOL
try:
    print("📮 Connecting to AOL SMTP...")
    server = smtplib.SMTP('smtp.aol.com', 587)
    server.set_debuglevel(1)  # Show debug info
    server.starttls()
    server.login(config['email']['username'], config['email']['password'])
    
    print("📤 Sending message...")
    server.send_message(msg)
    server.quit()
    
    print("\n✅ Email sent successfully!")
    print("📬 Check your inbox for the comprehensive analysis")
    
except Exception as e:
    print(f"\n❌ Email sending failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check your internet connection")
    print("2. Verify your AOL password is correct")
    print("3. Try using an app-specific password for AOL")
    print("\nYour comprehensive script is saved at:")
    print(f"👉 {script_file}")
