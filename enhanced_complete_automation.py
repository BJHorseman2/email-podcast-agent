#!/usr/bin/env python3
"""
Enhanced Complete Automation with Link Following
This patches your existing complete_automation.py to follow links
"""

import sys
import os

# Add the current directory to path so we can import link_following_agent
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the original file to extend it
from complete_automation import PodcastAutomationAgent
from link_following_agent import LinkFollowingNewsletterAgent
import logging
import json
from datetime import datetime

class EnhancedPodcastAutomationAgent(PodcastAutomationAgent, LinkFollowingNewsletterAgent):
    """Enhanced version that follows links in newsletters"""
    
    def __init__(self, config_file='aol_complete_config.json'):
        # Initialize parent class
        PodcastAutomationAgent.__init__(self, config_file)
        
        # Add link-following capabilities
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Add trusted news domains
        self.trusted_domains = {
            'bloomberg.com', 'reuters.com', 'wsj.com', 'ft.com', 
            'techcrunch.com', 'coindesk.com', 'cointelegraph.com',
            'theverge.com', 'arstechnica.com', 'wired.com',
            'puck.news', 'axios.com', 'politico.com', 'semafor.com'
        }
    
    def create_podcast_script(self, subject, body, sender):
        """Enhanced version that fetches content from links"""
        
        logging.info("📎 Extracting links from email...")
        
        # Extract links from the email body
        links = self.extract_links_from_content(body, "")  # Pass empty HTML for now
        logging.info(f"🔗 Found {len(links)} links in email")
        
        # Fetch article content if links found
        articles = []
        if links:
            logging.info("📰 Fetching article content from links...")
            articles = self.fetch_multiple_articles(links[:8])  # Limit to 8 articles
            logging.info(f"✅ Successfully fetched {len(articles)} articles")
        
        # Create enhanced script
        newsletter_name = "Mando Minutes" if "mando" in subject.lower() else "Newsletter"
        date_str = datetime.now().strftime('%A, %B %d, %Y')
        
        script = f"""Good morning! This is your {newsletter_name} podcast for {date_str}.

I'm your AI assistant, bringing you today's top stories from {sender}.

"""
        
        if articles:
            # Group articles by topic
            crypto_articles = []
            market_articles = []
            other_articles = []
            
            for article in articles:
                title_lower = article.get('title', '').lower()
                if any(word in title_lower for word in ['crypto', 'bitcoin', 'eth', 'blockchain', 'coin']):
                    crypto_articles.append(article)
                elif any(word in title_lower for word in ['market', 'stock', 'fed', 'inflation', 'economy']):
                    market_articles.append(article)
                else:
                    other_articles.append(article)
            
            # Add crypto news
            if crypto_articles:
                script += "Let's start with crypto and blockchain news.\n\n"
                for i, article in enumerate(crypto_articles[:3], 1):
                    script += f"Story {i}: {article['title']}\n\n"
                    if article['content']:
                        # Get first 150 words
                        words = article['content'].split()[:150]
                        content = ' '.join(words)
                        script += f"{content}...\n\n"
                    script += f"Source: {article['domain']}\n\n"
            
            # Add market news
            if market_articles:
                script += "Now for markets and economic news.\n\n"
                for i, article in enumerate(market_articles[:3], 1):
                    script += f"{article['title']}\n\n"
                    if article['content']:
                        words = article['content'].split()[:150]
                        content = ' '.join(words)
                        script += f"{content}...\n\n"
                    script += f"That's from {article['domain']}\n\n"
            
            # Add other news
            if other_articles:
                script += "In other news today:\n\n"
                for article in other_articles[:2]:
                    script += f"{article['title']}\n\n"
                    if article['content']:
                        words = article['content'].split()[:100]
                        content = ' '.join(words)
                        script += f"{content}...\n\n"
            
            script += f"\nThat covers {len(articles)} stories from today's newsletter.\n\n"
            
        else:
            # Fallback to original content if no articles fetched
            logging.warning("No articles fetched, using email content")
            script += f"Today's newsletter summary:\n\n{body[:1500]}\n\n"
        
        script += f"""For all the links and complete details, check your original email.

Thank you for listening to your AI-generated {newsletter_name} podcast. Have a great day!"""
        
        # Log the enhanced script stats
        word_count = len(script.split())
        char_count = len(script)
        logging.info(f"📊 Enhanced script: {word_count} words, {char_count} characters")
        logging.info(f"📊 Fetched content from {len(articles)} articles")
        
        return script

# Create a drop-in replacement function
def run_enhanced_automation():
    """Run the enhanced automation with link following"""
    
    logging.info("🚀 Starting ENHANCED podcast automation with link following...")
    
    # Check for required packages
    try:
        import bs4
    except ImportError:
        logging.error("Missing required package. Run: pip install beautifulsoup4 lxml")
        return
    
    # Create enhanced agent
    agent = EnhancedPodcastAutomationAgent()
    
    # Run the main process
    agent.run_complete_automation()
    
    logging.info("✅ Enhanced automation complete!")

if __name__ == "__main__":
    run_enhanced_automation()
