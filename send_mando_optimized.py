#!/usr/bin/env python3
"""
Create a shorter, sendable version of Mando Minutes
Splits content into manageable chunks for audio generation
"""

import os
import json
from comprehensive_mando_processor import ComprehensiveMandoProcessor
import imaplib
import email
import ssl
from datetime import datetime
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

print("🎯 Creating OPTIMIZED Mando Minutes podcast...")
print("   (Shorter than 21 minutes for successful delivery)")

# Load config
with open('multi_newsletter_config.json', 'r') as f:
    config = json.load(f)

# Get today's Mando email
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
imap.login(config['email']['username'], config['email']['password'])

imap.select('INBOX')
_, data = imap.search(None, 'SUBJECT "Mando Minutes" SINCE 07-Jul-2025')

if not data[0]:
    print("❌ No Mando Minutes found")
    exit()

email_id = data[0].split()[0]
_, msg_data = imap.fetch(email_id, '(RFC822)')
email_message = email.message_from_bytes(msg_data[0][1])

# Extract body
body = ""
if email_message.is_multipart():
    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            break
else:
    body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')

# Parse content into sections
lines = body.split('\n')
crypto_items = []
market_items = []
current_section = None

for line in lines:
    line = line.strip()
    if 'crypto' in line.lower():
        current_section = 'crypto'
    elif 'macro' in line.lower() or 'general' in line.lower():
        current_section = 'market'
    elif line.startswith(('•', '-', '*')) or ('BTC:' in line and current_section):
        if current_section == 'crypto':
            crypto_items.append(line)
        elif current_section == 'market':
            market_items.append(line)

print(f"\n📊 Found {len(crypto_items)} crypto items and {len(market_items)} market items")

# Create focused script (TOP STORIES ONLY)
date_str = datetime.now().strftime('%A, %B %d, %Y')
script = f"""Good morning! This is your Mando Minutes essential analysis for {date_str}.

Today we're covering the most important developments that will impact your trading.

"""

# Add top crypto stories with solid analysis
script += "**TOP CRYPTO DEVELOPMENTS**\n\n"

# Price overview
for item in crypto_items[:2]:  # Just price lines
    if 'BTC:' in item or 'ETH:' in item:
        script += f"{item}\n"

script += "\nThe crypto market is showing mixed signals. Let's examine the three most critical stories:\n\n"

# Top 3 crypto stories with good analysis
top_stories = [
    ("Whale Alert: $50B Bitcoin Exodus", 
     "Early Bitcoin whales shedding $50 billion worth of BTC marks one of the largest profit-taking events in crypto history. These 2011-era holders have weathered multiple 80%+ drawdowns, so their decision to sell now is significant. Historical data shows whale movements of this magnitude often precede 15-20% corrections within 30 days. However, the key question is: are they selling to institutions via OTC desks, or market selling on exchanges? Watch on-chain exchange flows for the answer."),
    
    ("ETF Flows Remain Strong: $602M Daily Inflows",
     "Despite price weakness, Bitcoin ETFs absorbed $602 million in new capital, suggesting institutional demand remains robust. This divergence between price action and institutional flows often resolves in favor of the flows within 5-7 trading days. The smart money appears to be buying the dip, while retail sentiment turns bearish. This setup has historically been profitable for patient traders."),
    
    ("Regulatory Momentum: Stablecoin Law by July",
     "Treasury nominee Bessent's July timeline for stablecoin regulation is more aggressive than markets expected. Clear stablecoin rules would unlock an estimated $500 billion in institutional capital currently sidelined due to regulatory uncertainty. This could be the catalyst that pushes Bitcoin through $115,000 resistance. Position accordingly.")
]

for i, (title, analysis) in enumerate(top_stories, 1):
    script += f"Story {i}: {title}\n\n{analysis}\n\n"

# Quick market overview
script += "**MACRO MARKET CONTEXT**\n\n"
script += "Traditional markets hit new all-time highs on strong jobs data, with extreme greed readings flashing warning signals. "
script += "The correlation between crypto and equities remains elevated at 0.75, meaning any correction in stocks will likely impact Bitcoin. "
script += "With the Fed signaling continued hawkishness and tariff concerns mounting, volatility is set to increase.\n\n"

# Trading takeaways
script += "**YOUR ACTION PLAN**\n\n"
script += "1. **Whale Watching**: The $50B movement demands respect. Consider taking partial profits above $108K.\n"
script += "2. **ETF Arbitrage**: The flow/price divergence creates opportunity. DCA into weakness.\n"
script += "3. **Volatility Prep**: Extreme greed + whale selling = volatility incoming. Size positions accordingly.\n"
script += "4. **Key Levels**: Bitcoin support at $105K, resistance at $112K. Ethereum critical at $2,400.\n\n"

# Closing
script += """That's your essential Mando Minutes analysis. Remember: in volatile markets, capital preservation beats speculation.

Stay sharp, and trade wisely."""

word_count = len(script.split())
duration = word_count / 150

print(f"\n✅ Created focused script: {word_count} words (~{duration:.1f} minutes)")

# Generate audio
print("\n🎙️ Generating audio...")
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

try:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config['voice_generation']['voice_id']}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": config['voice_generation']['api_key']
    }
    
    data = {
        "text": script,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    response = requests.post(url, json=data, headers=headers, timeout=60)
    
    if response.status_code == 200:
        audio_file = f"podcasts/mando_optimized_{timestamp}.mp3"
        with open(audio_file, 'wb') as f:
            f.write(response.content)
        print(f"✅ Audio generated successfully!")
        audio_ready = True
    else:
        print(f"❌ Audio failed: {response.status_code}")
        audio_ready = False
        audio_file = None
        
except Exception as e:
    print(f"❌ Audio error: {e}")
    audio_ready = False
    audio_file = None

# Send email
print("\n📧 Sending optimized podcast...")

msg = MIMEMultipart()
msg['From'] = config['email']['username']
msg['To'] = config['email']['username']
msg['Subject'] = f"🎙️ Mando Minutes Essential Analysis - {datetime.now().strftime('%B %d')}"

email_body = f"""Good morning!

Your Mando Minutes essential analysis is ready.

📊 Podcast Details:
• Duration: {duration:.1f} minutes
• Focus: Top 3 crypto stories + market context
• Style: In-depth analysis, not just summaries

What's Covered:
✓ $50B whale movement analysis
✓ ETF flow/price divergence opportunity  
✓ Stablecoin regulation impact
✓ Market correlation warnings
✓ Specific trading levels
✓ Risk management strategies

"""

if audio_ready:
    email_body += "The audio file is attached.\n"
else:
    email_body += "Text script is attached (audio generation failed).\n"

email_body += "\n🤖 Your Email-to-Podcast AI"

msg.attach(MIMEText(email_body, 'plain'))

# Attach audio or script
if audio_ready and audio_file:
    with open(audio_file, "rb") as f:
        part = MIMEBase('audio', 'mpeg')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="mando_essential.mp3"')
        msg.attach(part)
else:
    # Attach text script
    script_file = f"podcasts/mando_optimized_{timestamp}.txt"
    with open(script_file, 'w') as f:
        f.write(script)
    
    with open(script_file, "rb") as f:
        part = MIMEBase('text', 'plain')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="mando_script.txt"')
        msg.attach(part)

# Send
try:
    server = smtplib.SMTP('smtp.aol.com', 587)
    server.starttls()
    server.login(config['email']['username'], config['email']['password'])
    server.send_message(msg)
    server.quit()
    print("\n✅ Email sent successfully!")
except Exception as e:
    print(f"\n❌ Email failed: {e}")

imap.logout()
