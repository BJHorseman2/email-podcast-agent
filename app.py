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
                    import ssl
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
                            
                            # For now, show success - we can add AI processing later
                            st.success("✅ Email processed! (AI processing will be added next)")
                            st.balloons()
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
                st.info("🚧 Puck News processing coming soon!")
                # Would run the Puck processor here
    
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
        st.error("Podcasts directory not found")

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
            st.metric("Total Size", f"{total_size:.1f} MB")
        with col3:
            avg_size = total_size / len(mp3_files) if mp3_files else 0
            st.metric("Average Size", f"{avg_size:.1f} MB")
        
        # Recent activity chart
        if mp3_files:
            st.subheader("📈 Recent Activity")
            
            # Create activity data
            dates = []
            for f in mp3_files[-30:]:  # Last 30 files
                dates.append(datetime.fromtimestamp(f.stat().st_mtime).date())
            
            # Count by date
            date_counts = pd.Series(dates).value_counts().sort_index()
            
            # Create chart
            st.bar_chart(date_counts)

with tab4:
    st.header("⚙️ Settings")
    
    # Test email
    st.subheader("✉️ Test Email Connection")
    if st.button("Test Email Connection"):
        with st.spinner("Testing..."):
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                imap = imaplib.IMAP4_SSL('imap.aol.com', 993, ssl_context=context)
                imap.login(config['email']['username'], config['email']['password'])
                imap.logout()
                
                st.success("✅ Email connection successful!")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
    
    # Test audio
    st.subheader("🎙️ Test Audio Generation")
    test_text = st.text_area("Test Text", "This is a test of the email to podcast system.")
    if st.button("Generate Test Audio"):
        st.info("🚧 Audio test coming soon!")
    
    # Clean up old files
    st.subheader("🗑️ Cleanup")
    if st.button("Remove Old Podcasts (>7 days)"):
        if podcast_dir.exists():
            cutoff = datetime.now() - timedelta(days=7)
            removed = 0
            for file in podcast_dir.glob("*.mp3"):
                if datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
                    file.unlink()
                    removed += 1
            st.success(f"✅ Removed {removed} old podcast files")

# Footer
st.divider()
st.markdown("Made with ❤️ by your Email-to-Podcast AI")
