#!/usr/bin/env python3
"""
Choose your Email-to-Podcast interface
"""

import subprocess
import sys

print("""
🎙️ Email-to-Podcast Launcher
============================

Choose your interface:

1. 🌐 Web UI (Simple) - Best for most users
2. 🎨 Web UI (Full Dashboard) - More features
3. 🖥️  Desktop App - Native window
4. 💻 Command Line - Original version

""")

choice = input("Enter your choice (1-4): ").strip()

if choice == "1":
    print("\n🚀 Launching Simple Web UI...")
    print("This will open in your browser at http://localhost:8501")
    subprocess.run(["python3", "-m", "streamlit", "run", "simple_ui.py"])
    
elif choice == "2":
    print("\n🚀 Launching Full Dashboard...")
    print("This will open in your browser at http://localhost:8501")
    subprocess.run(["python3", "-m", "streamlit", "run", "app.py"])
    
elif choice == "3":
    print("\n🚀 Launching Desktop App...")
    subprocess.run(["python3", "desktop_app.py"])
    
elif choice == "4":
    print("\n📝 Command Line Usage:")
    print("- Process Mando: python3 send_clean_mando.py")
    print("- Process Both: python3 dual_newsletter_automation.py")
    print("- Check emails: python3 find_mando_by_subject.py")
    
else:
    print("\n❌ Invalid choice. Please run again and choose 1-4.")
