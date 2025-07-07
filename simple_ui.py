#!/usr/bin/env python3
"""
Simple Web UI for Email-to-Podcast
Just the essentials - process emails with one click
"""

import streamlit as st
import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

# Page setup
st.set_page_config(page_title="Email to Podcast", page_icon="🎙️")

# Custom CSS for better styling
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        height: 80px;
        font-size: 20px;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🎙️ Email to Podcast")
st.markdown("### Convert newsletters to podcasts with one click!")

# Status check
with st.expander("📊 System Status", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    # Check podcasts folder
    podcast_count = len(list(Path("podcasts").glob("*.mp3"))) if Path("podcasts").exists() else 0
    col1.metric("Podcasts Created", podcast_count)
    
    # Check config
    config_exists = Path("multi_newsletter_config.json").exists()
    col2.metric("Config Status", "✅ Ready" if config_exists else "❌ Missing")
    
    # Last run
    try:
        latest = max(Path("podcasts").glob("*.mp3"), key=os.path.getctime)
        last_run = datetime.fromtimestamp(latest.stat().st_mtime).strftime("%m/%d %I:%M%p")
        col3.metric("Last Podcast", last_run)
    except:
        col3.metric("Last Podcast", "Never")

st.divider()

# Main action buttons
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🪙 Mando Minutes")
    st.markdown("*Crypto & markets analysis*")
    
    if st.button("🚀 Create Mando Podcast", type="primary", use_container_width=True):
        # Show processing status
        with st.spinner("Creating your Mando Minutes podcast..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Update progress
            status_text.text("🔍 Finding Mando Minutes email...")
            progress_bar.progress(20)
            
            # Run the processor
            result = subprocess.run(
                ["python3", "send_clean_mando.py"],
                capture_output=True,
                text=True
            )
            
            progress_bar.progress(80)
            status_text.text("🎙️ Generating audio...")
            
            if "✅" in result.stdout or "sent" in result.stdout.lower():
                progress_bar.progress(100)
                status_text.empty()
                st.success("✅ Mando Minutes podcast sent to your email!")
                st.balloons()
                
                # Show what was created
                if "words" in result.stdout:
                    # Extract stats from output
                    output_lines = result.stdout.split('\n')
                    for line in output_lines:
                        if "words" in line and "minutes" in line:
                            st.info(f"📊 {line.strip()}")
                            break
            else:
                st.error("❌ Something went wrong. Check details below.")
                with st.expander("Error Details"):
                    st.code(result.stdout + "\n" + result.stderr)

with col2:
    st.markdown("### 📰 Puck News")
    st.markdown("*In-depth journalism*")
    
    if st.button("🚀 Create Puck Podcast", use_container_width=True):
        st.info("🚧 Puck News processing coming soon!")

st.divider()

# Recent podcasts
st.markdown("### 📚 Recent Podcasts")

podcast_dir = Path("podcasts")
if podcast_dir.exists():
    mp3_files = sorted(podcast_dir.glob("*.mp3"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if mp3_files:
        for file in mp3_files[:5]:  # Show last 5
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                # Clean up filename for display
                display_name = file.name.replace('_', ' ').replace('.mp3', '')
                st.markdown(f"🎵 **{display_name}**")
            
            with col2:
                size_mb = file.stat().st_size / (1024 * 1024)
                st.text(f"{size_mb:.1f} MB")
            
            with col3:
                # Download button
                with open(file, 'rb') as f:
                    st.download_button(
                        "⬇️ Download",
                        data=f.read(),
                        file_name=file.name,
                        mime="audio/mpeg",
                        key=file.name
                    )
    else:
        st.info("No podcasts yet. Click a button above to create your first one!")

# Help section
with st.expander("❓ Need Help?"):
    st.markdown("""
    **How it works:**
    1. Click "Create Mando Podcast" or "Create Puck Podcast"
    2. The system finds your latest newsletter email
    3. Creates a podcast with analysis and insights
    4. Sends it to your email inbox
    5. You can also download recent podcasts from this page
    
    **Troubleshooting:**
    - Make sure you have newsletters in your inbox
    - Check your spam folder for podcast emails
    - Podcasts are usually 5-7 minutes long
    """)

# Footer
st.divider()
st.caption("Email-to-Podcast AI | Auto-processes daily at 7:45 AM (Mando) & 8:30 AM (Puck)")
