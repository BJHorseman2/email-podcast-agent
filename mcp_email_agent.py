#!/usr/bin/env python3
"""
MCP-Based Email to Podcast Agent
Uses available MCP capabilities to automate email-to-podcast workflow
"""

import json
import os
import requests
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import asyncio
import aiohttp
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_agent.log'),
        logging.StreamHandler()
    ]
)

class MCPEmailPodcastAgent:
    def __init__(self, base_dir: str = "/Users/markbaumrind/Desktop/email_podcast_agent"):
        self.base_dir = base_dir
        self.config_path = os.path.join(base_dir, "config.json")
        self.podcasts_dir = os.path.join(base_dir, "podcasts")
        self.logs_dir = os.path.join(base_dir, "logs")
        self.temp_dir = os.path.join(base_dir, "temp")
        
        # Create directories
        os.makedirs(self.podcasts_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.config = self.load_or_create_config()
        
    def load_or_create_config(self) -> Dict:
        """Load configuration or create default"""
        default_config = {
            "email": {
                "service": "gmail",
                "check_interval_hours": 24,
                "max_emails_per_run": 5
            },
            "filters": {
                "sender_keywords": ["newsletter", "digest", "brief"],
                "subject_keywords": ["daily", "weekly", "update"],
                "exclude_keywords": ["unsubscribe", "spam", "promotional"]
            },
            "podcast": {
                "max_length_minutes": 15,
                "voice_style": "conversational",
                "include_summary": True
            },
            "schedule": {
                "run_time": "08:00",
                "enabled": True
            }
        }
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def search_for_emails(self) -> List[Dict]:
        """Search for emails using web search as a proxy for email discovery"""
        emails = []
        
        # Simulate email discovery by searching for newsletter content
        # In a real MCP implementation, this would use email MCP servers
        search_terms = [
            "daily newsletter digest",
            "tech news brief",
            "morning roundup email"
        ]
        
        for term in search_terms:
            try:
                # This is a simulation - in real MCP, we'd use email servers
                email_data = {
                    "id": f"email_{int(time.time())}_{term.replace(' ', '_')}",
                    "subject": f"Daily Brief: {term.title()}",
                    "sender": "newsletter@example.com",
                    "timestamp": datetime.now().isoformat(),
                    "content": f"Sample content for {term}. This would be actual email content in a real implementation.",
                    "relevance_score": 0.8
                }
                emails.append(email_data)
                
            except Exception as e:
                logging.error(f"Error searching for emails with term '{term}': {e}")
        
        return emails
    
    def process_email_content(self, email_data: Dict) -> Dict:
        """Process email content for podcast generation"""
        try:
            # Extract key information
            processed_content = {
                "title": email_data["subject"],
                "summary": self.generate_summary(email_data["content"]),
                "key_points": self.extract_key_points(email_data["content"]),
                "podcast_script": self.create_podcast_script(email_data),
                "metadata": {
                    "source": email_data["sender"],
                    "timestamp": email_data["timestamp"],
                    "processing_time": datetime.now().isoformat()
                }
            }
            
            return processed_content
            
        except Exception as e:
            logging.error(f"Error processing email content: {e}")
            return None
    
    def generate_summary(self, content: str) -> str:
        """Generate a summary of the email content"""
        # Simple summary generation - in real implementation, this could use AI
        sentences = content.split('. ')
        if len(sentences) > 3:
            return '. '.join(sentences[:3]) + '.'
        return content
    
    def extract_key_points(self, content: str) -> List[str]:
        """Extract key points from email content"""
        # Simple key point extraction
        points = []
        lines = content.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['important', 'key', 'note', 'update']):
                points.append(line.strip())
        return points[:5]  # Limit to 5 key points
    
    def create_podcast_script(self, email_data: Dict) -> str:
        """Create a podcast script from email content"""
        script = f"""
        Welcome to your daily email podcast! 

        Today we're covering: {email_data['subject']}

        Here's what you need to know:

        {email_data['content']}

        Key takeaways:
        {chr(10).join(f"• {point}" for point in self.extract_key_points(email_data['content']))}

        That's your update for today. Stay informed!
        """
        return script.strip()
    
    def save_podcast_content(self, processed_content: Dict, email_id: str) -> str:
        """Save podcast content to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"podcast_content_{email_id}_{timestamp}.json"
        filepath = os.path.join(self.podcasts_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(processed_content, f, indent=2)
        
        # Also save the script separately
        script_filename = f"podcast_script_{email_id}_{timestamp}.txt"
        script_filepath = os.path.join(self.podcasts_dir, script_filename)
        
        with open(script_filepath, 'w') as f:
            f.write(processed_content['podcast_script'])
        
        return filepath
    
    def create_notebooklm_instructions(self, processed_content: Dict, email_id: str) -> str:
        """Create instructions for NotebookLM processing"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        instructions = f"""
        NOTEBOOKLM PODCAST GENERATION INSTRUCTIONS
        Generated: {timestamp}
        Email ID: {email_id}

        ===========================================

        STEP 1: Go to https://notebooklm.google.com

        STEP 2: Create a new notebook with the title: "{processed_content['title']}"

        STEP 3: Add the following content as a source:

        ---BEGIN CONTENT---
        {processed_content['podcast_script']}
        ---END CONTENT---

        STEP 4: Generate Audio Overview
        - Click "Generate" button
        - Select "Audio Overview" 
        - Wait for generation to complete

        STEP 5: Download and Save
        - Download the generated audio file
        - Save as: podcast_{email_id}_{timestamp}.mp3
        - Move to: {self.podcasts_dir}

        OPTIONAL CUSTOMIZATIONS:
        - Adjust speaker personalities in NotebookLM settings
        - Add additional context or sources if needed
        - Modify the content before generation for better flow

        ===========================================
        """
        
        instructions_file = f"notebooklm_instructions_{email_id}_{timestamp}.txt"
        instructions_path = os.path.join(self.podcasts_dir, instructions_file)
        
        with open(instructions_path, 'w') as f:
            f.write(instructions)
        
        return instructions_path
    
    def generate_automation_script(self) -> str:
        """Generate a shell script for automation"""
        script_content = f"""#!/bin/bash
# Email to Podcast Automation Script
# Generated: {datetime.now().isoformat()}

cd "{self.base_dir}"

echo "Starting Email to Podcast Agent..."
python3 mcp_email_agent.py

echo "Process completed. Check logs at: {self.logs_dir}"
echo "Podcast content saved to: {self.podcasts_dir}"
"""
        
        script_path = os.path.join(self.base_dir, "run_agent.sh")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        return script_path
    
    def run_once(self) -> Dict:
        """Run the agent once"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "emails_processed": 0,
            "podcasts_created": 0,
            "files_generated": [],
            "errors": []
        }
        
        try:
            logging.info("Starting email to podcast agent...")
            
            # Search for emails
            emails = self.search_for_emails()
            logging.info(f"Found {len(emails)} potential emails")
            
            for email_data in emails:
                try:
                    # Process email content
                    processed_content = self.process_email_content(email_data)
                    if not processed_content:
                        continue
                    
                    # Save podcast content
                    content_file = self.save_podcast_content(processed_content, email_data["id"])
                    results["files_generated"].append(content_file)
                    
                    # Create NotebookLM instructions
                    instructions_file = self.create_notebooklm_instructions(processed_content, email_data["id"])
                    results["files_generated"].append(instructions_file)
                    
                    results["emails_processed"] += 1
                    results["podcasts_created"] += 1
                    
                    logging.info(f"Processed email: {email_data['subject']}")
                    
                except Exception as e:
                    error_msg = f"Error processing email {email_data.get('id', 'unknown')}: {e}"
                    logging.error(error_msg)
                    results["errors"].append(error_msg)
            
            # Generate automation script
            script_path = self.generate_automation_script()
            results["files_generated"].append(script_path)
            
            logging.info(f"Agent run completed. Processed {results['emails_processed']} emails")
            
        except Exception as e:
            error_msg = f"Fatal error in agent run: {e}"
            logging.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
    
    def schedule_daily_run(self):
        """Schedule the agent to run daily"""
        run_time = self.config["schedule"]["run_time"]
        schedule.every().day.at(run_time).do(self.run_once)
        
        logging.info(f"Scheduled daily run at {run_time}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """Main execution function"""
    agent = MCPEmailPodcastAgent()
    
    print("🚀 MCP Email to Podcast Agent Starting...")
    print(f"📁 Working directory: {agent.base_dir}")
    print(f"🎧 Podcasts directory: {agent.podcasts_dir}")
    
    # Run once
    results = agent.run_once()
    
    print("\n✅ Agent execution completed!")
    print(f"📧 Emails processed: {results['emails_processed']}")
    print(f"🎙️ Podcasts created: {results['podcasts_created']}")
    print(f"📄 Files generated: {len(results['files_generated'])}")
    
    if results['errors']:
        print(f"⚠️ Errors encountered: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")
    
    print(f"\n📂 Check your files at: {agent.podcasts_dir}")
    
    return results

if __name__ == "__main__":
    main()
