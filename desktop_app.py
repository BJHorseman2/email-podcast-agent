#!/usr/bin/env python3
"""
Desktop App for Email-to-Podcast
Simple native window with just two buttons
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import json
import os
from datetime import datetime
from pathlib import Path

class EmailToPodcastApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email to Podcast")
        self.root.geometry("600x500")
        
        # Header
        header = tk.Label(root, text="🎙️ Email to Podcast", font=("Arial", 24, "bold"))
        header.pack(pady=20)
        
        # Subtitle
        subtitle = tk.Label(root, text="Convert newsletters to podcasts with one click!", font=("Arial", 12))
        subtitle.pack()
        
        # Button frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=30)
        
        # Mando button
        self.mando_btn = tk.Button(
            button_frame,
            text="🪙 Create Mando Minutes Podcast",
            font=("Arial", 16),
            bg="#007bff",
            fg="white",
            width=25,
            height=2,
            command=self.process_mando
        )
        self.mando_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # Puck button
        self.puck_btn = tk.Button(
            button_frame,
            text="📰 Create Puck News Podcast",
            font=("Arial", 16),
            bg="#6c757d",
            fg="white",
            width=25,
            height=2,
            command=self.process_puck
        )
        self.puck_btn.grid(row=1, column=0, padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(root, text="Ready to create podcasts!", font=("Arial", 12))
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(root, length=400, mode='indeterminate')
        self.progress.pack(pady=10)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(root, height=10, width=70)
        self.output_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Check status on startup
        self.check_status()
    
    def check_status(self):
        """Check if system is ready"""
        try:
            # Check for config
            if Path("multi_newsletter_config.json").exists():
                self.output_text.insert(tk.END, "✅ Configuration loaded\n")
            else:
                self.output_text.insert(tk.END, "❌ Configuration missing\n")
            
            # Check podcasts folder
            podcast_count = len(list(Path("podcasts").glob("*.mp3"))) if Path("podcasts").exists() else 0
            self.output_text.insert(tk.END, f"📊 Total podcasts created: {podcast_count}\n")
            
            # Show last podcast
            try:
                latest = max(Path("podcasts").glob("*.mp3"), key=os.path.getctime)
                last_run = datetime.fromtimestamp(latest.stat().st_mtime).strftime("%m/%d %I:%M%p")
                self.output_text.insert(tk.END, f"📅 Last podcast: {last_run}\n")
            except:
                self.output_text.insert(tk.END, "📅 No podcasts created yet\n")
                
            self.output_text.insert(tk.END, "\n" + "="*50 + "\n\n")
            
        except Exception as e:
            self.output_text.insert(tk.END, f"Error checking status: {e}\n")
    
    def process_mando(self):
        """Process Mando Minutes in background thread"""
        self.mando_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Creating Mando Minutes podcast...")
        self.progress.start()
        
        # Run in background thread
        thread = threading.Thread(target=self._process_mando_thread)
        thread.start()
    
    def _process_mando_thread(self):
        """Background thread for Mando processing"""
        try:
            self.output_text.insert(tk.END, "🚀 Starting Mando Minutes processing...\n")
            self.output_text.see(tk.END)
            
            # Run the processor
            result = subprocess.run(
                ["python3", "send_clean_mando.py"],
                capture_output=True,
                text=True
            )
            
            # Update UI in main thread
            self.root.after(0, self._mando_complete, result)
            
        except Exception as e:
            self.root.after(0, self._mando_error, str(e))
    
    def _mando_complete(self, result):
        """Handle Mando completion in main thread"""
        self.progress.stop()
        self.mando_btn.config(state=tk.NORMAL)
        
        if "✅" in result.stdout or "sent" in result.stdout.lower():
            self.status_label.config(text="✅ Mando Minutes podcast sent to your email!")
            self.output_text.insert(tk.END, "\n✅ SUCCESS! Podcast created and sent!\n")
            
            # Extract stats
            for line in result.stdout.split('\n'):
                if "words" in line or "minutes" in line:
                    self.output_text.insert(tk.END, f"📊 {line.strip()}\n")
                    
            messagebox.showinfo("Success", "Mando Minutes podcast sent to your email!")
        else:
            self.status_label.config(text="❌ Processing failed")
            self.output_text.insert(tk.END, f"\n❌ Error:\n{result.stdout}\n{result.stderr}\n")
            messagebox.showerror("Error", "Failed to create podcast. Check the output for details.")
        
        self.output_text.see(tk.END)
    
    def _mando_error(self, error):
        """Handle Mando error in main thread"""
        self.progress.stop()
        self.mando_btn.config(state=tk.NORMAL)
        self.status_label.config(text="❌ Error occurred")
        self.output_text.insert(tk.END, f"\n❌ Error: {error}\n")
        self.output_text.see(tk.END)
        messagebox.showerror("Error", f"Failed to process: {error}")
    
    def process_puck(self):
        """Process Puck News"""
        messagebox.showinfo("Coming Soon", "Puck News processing coming soon!")

def main():
    root = tk.Tk()
    app = EmailToPodcastApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
