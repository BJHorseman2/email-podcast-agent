#!/usr/bin/env python3
"""
Web UI for Email-to-Podcast App
Simple interface to process newsletters and manage podcasts
"""

import streamlit as st
import json
import os
import subprocess
from datetime import datetime, timedelta
import imaplib
import email
import ssl
import pandas as pd
from pathlib import Path
import re
import requests
import tempfile
import base64

# Page config
st.set_page_config(
    page_title="📧 Email to Podcast",
    page_icon="🎙️",
    layout="wide"
)

# Title
st.title("🎙️ Email to Podcast Dashboard")
st.markdown("Convert your newsletters into podcasts with one click!")

# Load configuration
@st.cache_data
def load_config():
    # Try Streamlit secrets first (for secure cloud deployment)
    if hasattr(st, 'secrets') and 'email' in st.secrets:
        st.success("🔐 Secure Mode: Using encrypted configuration")
        return {
            "email": {
                "provider": st.secrets["email"]["provider"],
                "imap_server": st.secrets["email"]["imap_server"],
                "imap_port": st.secrets["email"]["imap_port"],
                "username": st.secrets["email"]["username"],
                "password": st.secrets["email"]["password"]
            },
            "newsletters": [
                {
                    "name": "mando_minutes",
                    "enabled": True,
                    "sender": ["hello@www.mandominutes.com", "mando@mandominutes.com"],
                    "subject_contains": ["Mando Minutes"],
                    "podcast_style": "Fast-paced crypto and markets briefing with link following"
                },
                {
                    "name": "puck_news",
                    "enabled": True,
                    "sender": ["jonkelly@puck.news", "newsletter@puck.news"],
                    "subject_contains": ["Jon Kelly", "Puck"],
                    "podcast_style": "In-depth analysis and commentary"
                }
            ],
            "ai_processing": {
                "provider": "openai",
                "api_key": st.secrets["ai_processing"]["api_key"],
                "model": "gpt-4o-mini"
            },
            "voice_generation": {
                "provider": "elevenlabs",
                "api_key": st.secrets["voice_generation"]["api_key"],
                "voice_id": st.secrets["voice_generation"]["voice_id"]
            }
        }
    
    # Try environment variables (alternative to secrets)
    elif os.getenv('EMAIL_USERNAME'):
        st.success("🔐 Secure Mode: Using environment variables")
        return {
            "email": {
                "provider": os.getenv('EMAIL_PROVIDER', 'aol'),
                "imap_server": os.getenv('EMAIL_IMAP_SERVER', 'imap.aol.com'),
                "imap_port": int(os.getenv('EMAIL_IMAP_PORT', '993')),
                "username": os.getenv('EMAIL_USERNAME'),
                "password": os.getenv('EMAIL_PASSWORD')
            },
            "newsletters": [
                {
                    "name": "mando_minutes",
                    "enabled": True,
                    "sender": ["hello@www.mandominutes.com", "mando@mandominutes.com"],
                    "subject_contains": ["Mando Minutes"],
                    "podcast_style": "Fast-paced crypto and markets briefing with link following"
                },
                {
                    "name": "puck_news",
                    "enabled": True,
                    "sender": ["jonkelly@puck.news", "newsletter@puck.news"],
                    "subject_contains": ["Jon Kelly", "Puck"],
                    "podcast_style": "In-depth analysis and commentary"
                }
            ],
            "ai_processing": {
                "provider": "openai",
                "api_key": os.getenv('OPENAI_API_KEY'),
                "model": "gpt-4o-mini"
            },
            "voice_generation": {
                "provider": "elevenlabs",
                "api_key": os.getenv('ELEVENLABS_API_KEY'),
                "voice_id": os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')
            }
        }
    
    # Try local config file (for local development)
    try:
        with open('multi_newsletter_config.json', 'r') as f:
            st.info("🏠 Local Mode: Using local configuration")
            return json.load(f)
    except FileNotFoundError:
        # Demo configuration for deployment without secrets
        st.warning("⚠️ Demo Mode: Real config file not found. This is a demonstration dashboard.")
        return {
            "email": {
                "username": "demo@example.com",
                "provider": "aol"
            },
            "newsletters": [
                {
                    "name": "mando_minutes",
                    "enabled": True,
                    "podcast_style": "Fast-paced crypto and markets briefing"
                },
                {
                    "name": "puck_news", 
                    "enabled": True,
                    "podcast_style": "In-depth analysis and commentary"
                }
            ],
            "voice_generation": {
                "provider": "elevenlabs"
            }
        }

config = load_config()

# AI and Voice Processing Functions
def process_with_ai(content, newsletter_type, config):
    """Convert email content to podcast script using OpenAI"""
    try:
        # Check if OpenAI is available and has valid API key
        ai_config = config.get('ai_processing', {})
        api_key = ai_config.get('api_key', '')
        
        if not api_key or api_key == 'YOUR_OPENAI_API_KEY':
            # Fallback to template-based script generation
            return generate_template_script(content, newsletter_type)
        
        import openai
        
        # Set up OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Different prompts for different newsletters
        if newsletter_type == "mando_minutes":
            prompt = f"""
Convert this Mando Minutes newsletter into a professional podcast script with sound effects and music cues. 
Make it energetic, fast-paced, and include professional audio production elements.

Newsletter content:
{content}

Create a podcast script that:
- Includes sound effect cues like [INTRO MUSIC], [SOUND EFFECT: description], [TRANSITION SOUND]
- Features "Mark" as the host name
- Starts with professional intro music and sound effects
- Has 3-5 minutes of content focused on crypto and markets
- Uses engaging transitions between topics
- Ends with professional outro music
- Is conversational and energetic

Format like:
[UPBEAT INTRO MUSIC FADES IN]
[SOUND EFFECT: Digital beep]
Good morning! I'm Mark, and this is your Mando Minutes briefing...
[INTRO MUSIC FADES OUT]

Script:
"""
        else:  # puck_news
            prompt = f"""
Convert this Puck newsletter into a sophisticated podcast script with professional sound design. 
Make it thoughtful, analytical, and include elegant audio production elements.

Newsletter content:
{content}

Create a podcast script that:
- Includes sophisticated sound cues like [INTRO MUSIC], [SOUND EFFECT: description], [TRANSITION SOUND]
- Features "Mark" as the host name
- Starts with sophisticated intro music and news-style sound effects
- Has 5-8 minutes of in-depth analysis
- Uses elegant transitions between topics  
- Ends with professional outro music
- Is conversational but authoritative

Format like:
[SOPHISTICATED INTRO MUSIC FADES IN]
[SOUND EFFECT: News ticker]
Welcome to Puck News Analysis. I'm Mark, and this is your deep-dive briefing...
[INTRO MUSIC FADES TO BACKGROUND]

Script:
"""
        
        response = client.chat.completions.create(
            model=config['ai_processing']['model'],
            messages=[
                {"role": "system", "content": "You are a professional podcast script writer who creates engaging, conversational audio content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "429" in error_msg:
            st.warning("⚠️ OpenAI quota exceeded. Using template script instead.")
            return generate_template_script(content, newsletter_type)
        else:
            st.error(f"AI processing failed: {error_msg}")
            st.info("💡 Using fallback template script...")
            return generate_template_script(content, newsletter_type)

def generate_template_script(content, newsletter_type):
    """Generate a professional script with sound effects and personalization"""
    try:
        import re
        from datetime import datetime
        
        # Clean content
        clean_content = re.sub(r'\[.*?\]\(.*?\)', '', content)  # Remove markdown links
        clean_content = re.sub(r'http\S+', '', clean_content)   # Remove URLs
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()  # Clean whitespace
        
        # Extract key points (enhanced approach)
        lines = clean_content.split('\n')
        key_points = []
        for line in lines:
            line = line.strip()
            if len(line) > 30 and any(keyword in line.lower() for keyword in ['bitcoin', 'crypto', 'market', 'news', 'price', 'trading', 'report', 'analysis', 'update', 'development', 'industry']):
                key_points.append(line)
        
        # Limit to top points
        key_points = key_points[:5]
        
        date_str = datetime.now().strftime('%A, %B %d, %Y')
        time_str = datetime.now().strftime('%I:%M %p')
        
        if newsletter_type == "mando_minutes":
            script = f"""[UPBEAT INTRO MUSIC FADES IN - 3 seconds]

[SOUND EFFECT: Digital beep sequence]

Good morning! I'm Mark, and this is your Mando Minutes briefing for {date_str}.

[INTRO MUSIC FADES OUT]

[SOUND EFFECT: Market bell]

It's {time_str}, and here's what's moving markets right now.

[TRANSITION SOUND: Whoosh effect]

"""
            
            for i, point in enumerate(key_points, 1):
                script += f"""**MARKET UPDATE {i}:**

{point}

[TRANSITION SOUND: Subtle ding - 0.5 seconds]

"""
            
            script += f"""[BACKGROUND MUSIC: Subtle tech beats fade in]

And that's your Mando Minutes market briefing for {date_str}. 

I'm Mark, keeping you informed and ahead of the curve.

[SOUND EFFECT: Digital flourish]

Stay sharp, stay profitable.

[OUTRO MUSIC BUILDS AND FADES OUT - 3 seconds]

[END]"""
            
        else:  # puck_news
            script = f"""[SOPHISTICATED INTRO MUSIC FADES IN - 4 seconds]

[SOUND EFFECT: News ticker]

Welcome to Puck News Analysis. I'm Mark, and this is your deep-dive briefing for {date_str}.

[INTRO MUSIC FADES TO BACKGROUND]

Today we're analyzing the stories that matter, the context you need, and the implications ahead.

[TRANSITION SOUND: Elegant chime]

"""
            
            for i, point in enumerate(key_points, 1):
                script += f"""**ANALYSIS {i}:**

{point}

[PAUSE FOR EMPHASIS - 1 second]

This development is significant because it reflects broader industry trends and regulatory shifts we've been tracking.

[TRANSITION SOUND: Soft piano note]

"""
            
            script += f"""[BACKGROUND MUSIC: Thoughtful instrumental fade in]

Those are today's key developments worth your attention.

I'm Mark, and this has been your Puck News Analysis for {date_str}.

[SOUND EFFECT: Sophisticated tone]

Stay informed, stay ahead.

[OUTRO MUSIC BUILDS ELEGANTLY AND FADES - 4 seconds]

[END]"""
        
        return script
        
    except Exception as e:
        return f"""[INTRO MUSIC]

Welcome! I'm Mark, and this is your newsletter podcast for {datetime.now().strftime('%B %d, %Y')}.

[MUSIC FADES]

Here's today's content summary:

{content[:500]}...

[OUTRO MUSIC]

That's your update for today. Thanks for listening!

[MUSIC FADES OUT]"""
        

def generate_voice(script, config):
    """Convert script to audio using ElevenLabs"""
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{config['voice_generation']['voice_id']}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": config['voice_generation']['api_key']
        }
        
        data = {
            "text": script,
            "model_id": config['voice_generation'].get('model', 'eleven_multilingual_v2'),
            "voice_settings": {
                "stability": config['voice_generation'].get('voice_settings', {}).get('stability', 0.5),
                "similarity_boost": config['voice_generation'].get('voice_settings', {}).get('similarity_boost', 0.8),
                "style": config['voice_generation'].get('voice_settings', {}).get('style', 0.2),
                "use_speaker_boost": config['voice_generation'].get('voice_settings', {}).get('use_speaker_boost', True)
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Voice generation failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Voice generation error: {str(e)}")
        return None

def save_podcast(audio_data, newsletter_type):
    """Save audio data and return file info"""
    try:
        # Create podcasts directory if it doesn't exist
        podcast_dir = Path("podcasts")
        podcast_dir.mkdir(exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{newsletter_type}_{timestamp}.mp3"
        filepath = podcast_dir / filename
        
        # Save audio file
        with open(filepath, 'wb') as f:
            f.write(audio_data)
        
        return {
            'filename': filename,
            'filepath': filepath,
            'size': len(audio_data),
            'created': datetime.now()
        }
        
    except Exception as e:
        st.error(f"Failed to save podcast: {str(e)}")
        return None

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("📧 Email Settings")
    st.text(f"Email: {config['email']['username']}")
    st.text("Server: AOL IMAP")
    
    st.subheader("🎙️ Voice Settings")
    st.text("Provider: ElevenLabs")
    st.text("Voice: Adam")
    
    st.subheader("📅 Schedule")
    st.text("Mando Minutes: 7:45 AM")
    st.text("Puck News: 8:30 AM")
    
    if st.button("🔄 Refresh Config"):
        st.cache_data.clear()
        st.rerun()

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["📬 Process Emails", "📚 Recent Podcasts", "📊 Analytics", "⚙️ Settings"])

with tab1:
    st.header("Process Newsletters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🪙 Mando Minutes")
        st.markdown("Crypto & markets newsletter with link analysis")
        
        if st.button("🚀 Process Mando Minutes", type="primary", key="mando"):
            with st.spinner("Processing Mando Minutes..."):
                # Create a placeholder for real-time updates
                status = st.empty()
                
                try:
                    # Process directly in Streamlit instead of subprocess
                    status.info("🔍 Searching for Mando Minutes email...")
                    
                    # Use config from secrets/local config
                    email_config = config['email']
                    
                    # Connect to email
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    imap = imaplib.IMAP4_SSL(email_config['imap_server'], email_config['imap_port'], ssl_context=context)
                    imap.login(email_config['username'], email_config['password'])
                    imap.select('INBOX')
                    
                    # Search for Mando Minutes
                    today = datetime.now().strftime('%d-%b-%Y')
                    search_query = f'SUBJECT "Mando Minutes" SINCE {today}'
                    _, data = imap.search(None, search_query)
                    
                    if not data[0]:
                        # Try yesterday too
                        yesterday = (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y')
                        search_query = f'SUBJECT "Mando Minutes" SINCE {yesterday}'
                        _, data = imap.search(None, search_query)
                    
                    if not data[0]:
                        st.error("❌ No recent Mando Minutes email found")
                    else:
                        email_id = data[0].split()[-1]  # Get latest email
                        _, msg_data = imap.fetch(email_id, '(RFC822)')
                        email_message = email.message_from_bytes(msg_data[0][1])
                        
                        # Extract email content
                        body = ""
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    break
                        else:
                            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                        
                        if body:
                            status.success("✅ Email found! Processing content...")
                            
                            # Show preview of content
                            with st.expander("Preview Email Content"):
                                st.text_area("Email Body", body[:1000] + "..." if len(body) > 1000 else body, height=200)
                            
                            # AI Processing
                            status.info("🤖 Creating podcast script with AI...")
                            script = process_with_ai(body, "mando_minutes", config)
                            
                            if script:
                                # Show generated script
                                with st.expander("Generated Podcast Script"):
                                    st.text_area("Script", script, height=300)
                                
                                # Voice Generation
                                status.info("🎤 Generating voice with ElevenLabs...")
                                audio_data = generate_voice(script, config)
                                
                                if audio_data:
                                    # Save podcast
                                    status.info("💾 Saving podcast file...")
                                    file_info = save_podcast(audio_data, "mando_minutes")
                                    
                                    if file_info:
                                        status.success("✅ PODCAST CREATED SUCCESSFULLY!")
                                        
                                        # Show file info
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("File Size", f"{file_info['size'] / (1024*1024):.1f} MB")
                                        with col2:
                                            st.metric("Duration", "~3-5 min")
                                        with col3:
                                            st.metric("Created", file_info['created'].strftime("%H:%M:%S"))
                                        
                                        # Download button
                                        st.download_button(
                                            label="🎧 Download Podcast",
                                            data=audio_data,
                                            file_name=file_info['filename'],
                                            mime="audio/mpeg",
                                            type="primary"
                                        )
                                        
                                        # Audio player
                                        st.audio(audio_data, format='audio/mp3')
                                        
                                        st.balloons()
                                    else:
                                        st.error("❌ Failed to save podcast file")
                                else:
                                    st.error("❌ Voice generation failed")
                            else:
                                st.error("❌ AI script generation failed")
                        else:
                            st.error("❌ Could not extract email content")
                    
                    imap.close()
                    imap.logout()
                        
                except Exception as e:
                    st.error(f"❌ Processing failed: {str(e)}")
                    with st.expander("Error Details"):
                        st.code(str(e))
    
    with col2:
        st.subheader("📰 Puck News")
        st.markdown("In-depth news and analysis")
        
        if st.button("🚀 Process Puck News", type="primary", key="puck"):
            with st.spinner("Processing Puck News..."):
                # Create a placeholder for real-time updates
                status = st.empty()
                
                try:
                    # Process directly in Streamlit
                    status.info("🔍 Searching for Puck News email...")
                    
                    # Use config from secrets/local config
                    email_config = config['email']
                    
                    # Connect to email
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    imap = imaplib.IMAP4_SSL(email_config['imap_server'], email_config['imap_port'], ssl_context=context)
                    imap.login(email_config['username'], email_config['password'])
                    imap.select('INBOX')
                    
                    # Search for Puck News - try multiple search terms
                    today = datetime.now().strftime('%d-%b-%Y')
                    search_queries = [
                        f'SUBJECT "Jon Kelly" SINCE {today}',
                        f'SUBJECT "Puck" SINCE {today}',
                        f'FROM "puck.news" SINCE {today}',
                        f'FROM "jonkelly@puck.news" SINCE {today}'
                    ]
                    
                    data = None
                    found_query = ""
                    for query in search_queries:
                        _, search_data = imap.search(None, query)
                        if search_data[0]:
                            data = search_data
                            found_query = query
                            break
                    
                    if not data or not data[0]:
                        # Try yesterday too
                        yesterday = (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y')
                        for query in search_queries:
                            query_yesterday = query.replace(today, yesterday)
                            _, search_data = imap.search(None, query_yesterday)
                            if search_data[0]:
                                data = search_data
                                found_query = query_yesterday
                                break
                    
                    if not data or not data[0]:
                        st.error("❌ No recent Puck News email found")
                        st.info("Searched for: Jon Kelly, Puck, puck.news, jonkelly@puck.news")
                    else:
                        email_id = data[0].split()[-1]  # Get latest email
                        _, msg_data = imap.fetch(email_id, '(RFC822)')
                        email_message = email.message_from_bytes(msg_data[0][1])
                        
                        # Get email subject and sender for confirmation
                        subject = email_message.get('Subject', 'No Subject')
                        sender = email_message.get('From', 'Unknown Sender')
                        
                        # Extract email content
                        body = ""
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    break
                                elif part.get_content_type() == "text/html" and not body:
                                    # Fallback to HTML if no plain text
                                    html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    # Basic HTML stripping
                                    body = re.sub(r'<[^>]+>', '', html_body)
                        else:
                            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                        
                        if body:
                            status.success("✅ Puck News email found! Processing content...")
                            
                            # Show email details
                            st.info(f"**Subject:** {subject}")
                            st.info(f"**From:** {sender}")
                            st.info(f"**Found with:** {found_query}")
                            
                            # Show preview of content
                            with st.expander("Preview Email Content"):
                                st.text_area("Email Body", body[:1500] + "..." if len(body) > 1500 else body, height=300)
                            
                            # AI Processing
                            status.info("🤖 Creating podcast script with AI...")
                            script = process_with_ai(body, "puck_news", config)
                            
                            if script:
                                # Show generated script
                                with st.expander("Generated Podcast Script"):
                                    st.text_area("Script", script, height=300)
                                
                                # Voice Generation
                                status.info("🎤 Generating voice with ElevenLabs...")
                                audio_data = generate_voice(script, config)
                                
                                if audio_data:
                                    # Save podcast
                                    status.info("💾 Saving podcast file...")
                                    file_info = save_podcast(audio_data, "puck_news")
                                    
                                    if file_info:
                                        status.success("✅ PUCK NEWS PODCAST CREATED!")
                                        
                                        # Show file info
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("File Size", f"{file_info['size'] / (1024*1024):.1f} MB")
                                        with col2:
                                            st.metric("Duration", "~5-8 min")
                                        with col3:
                                            st.metric("Created", file_info['created'].strftime("%H:%M:%S"))
                                        
                                        # Download button
                                        st.download_button(
                                            label="🎧 Download Podcast",
                                            data=audio_data,
                                            file_name=file_info['filename'],
                                            mime="audio/mpeg",
                                            type="primary"
                                        )
                                        
                                        # Audio player
                                        st.audio(audio_data, format='audio/mp3')
                                        
                                        st.balloons()
                                    else:
                                        st.error("❌ Failed to save podcast file")
                                else:
                                    st.error("❌ Voice generation failed")
                            else:
                                st.error("❌ AI script generation failed")
                        else:
                            st.error("❌ Could not extract email content")
                    
                    imap.close()
                    imap.logout()
                        
                except Exception as e:
                    st.error(f"❌ Processing failed: {str(e)}")
                    with st.expander("Error Details"):
                        st.code(str(e))
    
    # Check for new emails
    st.divider()
    st.subheader("📥 Check Inbox")
    
    if st.button("🔍 Check for New Emails"):
        with st.spinner("Checking inbox..."):
            try:
                # Connect to email
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
                imap.login(config['email']['username'], config['email']['password'])
                
                imap.select('INBOX')
                
                # Search for recent emails
                since_date = (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y')
                
                # Check Mando
                _, mando_data = imap.search(None, f'SINCE {since_date} FROM "mandominutes"')
                mando_count = len(mando_data[0].split()) if mando_data[0] else 0
                
                # Check Puck
                _, puck_data = imap.search(None, f'SINCE {since_date} FROM "puck.news"')
                puck_count = len(puck_data[0].split()) if puck_data[0] else 0
                
                imap.logout()
                
                # Display results
                col1, col2 = st.columns(2)
                with col1:
                    if mando_count > 0:
                        st.success(f"✅ {mando_count} Mando Minutes email(s) found")
                    else:
                        st.info("📭 No new Mando Minutes")
                
                with col2:
                    if puck_count > 0:
                        st.success(f"✅ {puck_count} Puck News email(s) found")
                    else:
                        st.info("📭 No new Puck News")
                        
            except Exception as e:
                st.error(f"Email check failed: {str(e)}")

with tab2:
    st.header("📚 Recent Podcasts")
    
    # List recent podcast files
    podcast_dir = Path("podcasts")
    if podcast_dir.exists():
        files = list(podcast_dir.glob("*.mp3"))
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if files:
            for file in files[:10]:  # Show last 10
                file_size = file.stat().st_size / (1024 * 1024)  # MB
                file_time = datetime.fromtimestamp(file.stat().st_mtime)
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(f"🎵 {file.name}")
                with col2:
                    st.text(f"{file_size:.1f} MB")
                with col3:
                    st.text(file_time.strftime("%m/%d %I:%M%p"))
                    
                # Download button
                with open(file, 'rb') as f:
                    st.download_button(
                        label="⬇️ Download",
                        data=f.read(),
                        file_name=file.name,
                        mime="audio/mpeg",
                        key=f"download_{file.name}"
                    )
                st.divider()
        else:
            st.info("No podcasts found yet. Process some emails!")
    else:
        st.info("Podcasts directory not found - it will be created when you process your first email")

with tab3:
    st.header("📊 Analytics")
    
    # Podcast stats
    if podcast_dir.exists():
        mp3_files = list(podcast_dir.glob("*.mp3"))
        txt_files = list(podcast_dir.glob("*.txt"))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Podcasts", len(mp3_files))
        with col2:
            total_size = sum(f.stat().st_size for f in mp3_files) / (1024 * 1024)
            st.metric("Total Size (MB)", f"{total_size:.1f}")
        with col3:
            st.metric("Script Files", len(txt_files))
            
        if mp3_files:
            # Recent activity chart
            dates = []
            counts = []
            
            # Group files by date
            file_dates = {}
            for file in mp3_files:
                file_date = datetime.fromtimestamp(file.stat().st_mtime).date()
                file_dates[file_date] = file_dates.get(file_date, 0) + 1
            
            # Create chart data
            chart_data = pd.DataFrame({
                'Date': list(file_dates.keys()),
                'Podcasts Created': list(file_dates.values())
            })
            
            st.subheader("Recent Activity")
            st.bar_chart(chart_data.set_index('Date'))
    else:
        st.info("No analytics available yet. Process some emails to see stats!")

with tab4:
    st.header("⚙️ Settings")
    
    st.subheader("📧 Email Configuration")
    
    # Show current config (non-sensitive parts)
    col1, col2 = st.columns(2)
    
    with col1:
        st.text(f"Provider: {config['email'].get('provider', 'N/A')}")
        st.text(f"Username: {config['email'].get('username', 'N/A')}")
        st.text(f"IMAP Server: {config['email'].get('imap_server', 'N/A')}")
        
    with col2:
        st.text(f"IMAP Port: {config['email'].get('imap_port', 'N/A')}")
        st.text("Password: ••••••••")
    
    st.subheader("🎙️ Voice Generation")
    voice_config = config.get('voice_generation', {})
    st.text(f"Provider: {voice_config.get('provider', 'N/A')}")
    st.text(f"Voice ID: {voice_config.get('voice_id', 'N/A')}")
    st.text("API Key: ••••••••")
    
    st.subheader("🤖 AI Processing")
    ai_config = config.get('ai_processing', {})
    st.text(f"Provider: {ai_config.get('provider', 'N/A')}")
    st.text(f"Model: {ai_config.get('model', 'N/A')}")
    st.text("API Key: ••••••••")
    
    st.divider()
    
    st.subheader("🔄 Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Cache", help="Clear cached configuration"):
            st.cache_data.clear()
            st.success("Cache cleared!")
            st.rerun()
    
    with col2:
        if st.button("🔍 Test Email Connection", help="Test connection to email server"):
            with st.spinner("Testing email connection..."):
                try:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    imap = imaplib.IMAP4_SSL(config['email']['imap_server'], config['email']['imap_port'], ssl_context=context)
                    imap.login(config['email']['username'], config['email']['password'])
                    imap.select('INBOX')
                    imap.logout()
                    
                    st.success("✅ Email connection successful!")
                except Exception as e:
                    st.error(f"❌ Email connection failed: {str(e)}")
    
    st.divider()
    
    st.subheader("ℹ️ About")
    st.markdown("""
    **Email to Podcast Dashboard v1.0**
    
    This application converts your newsletter emails into podcasts using AI.
    
    **Features:**
    - 🔐 Secure credential management
    - 📧 Email processing (Mando Minutes, Puck News)
    - 🤖 AI-powered content analysis
    - 🎙️ Voice generation with ElevenLabs
    - 📱 Mobile-friendly interface
    - ☁️ Cloud deployment ready
    
    **Next Steps:**
    - Add AI processing for content transformation
    - Implement voice generation
    - Add scheduling automation
    - Email delivery of podcasts
    """)
