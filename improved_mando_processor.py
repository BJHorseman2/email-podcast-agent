#!/usr/bin/env python3
"""
Enhanced Mando Minutes Processor with Better Link Following
Uses multiple strategies to get actual article content
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
import time
import re
from urllib.parse import urlparse
import cloudscraper  # Better for bypassing anti-bot measures

logging.basicConfig(level=logging.INFO)

class ImprovedMandoProcessor:
    def __init__(self):
        # Use cloudscraper to bypass Cloudflare and other protections
        self.scraper = cloudscraper.create_scraper()
        
        # Better headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Site-specific selectors for better content extraction
        self.site_selectors = {
            'bloomberg.com': ['article', '.article-content', '.body-content'],
            'coindesk.com': ['article', '.article-content', '.at-content'],
            'cointelegraph.com': ['article', '.post-content', '.article__content'],
            'reuters.com': ['article', '.article-body', '[data-testid="article-body"]'],
            'wsj.com': ['article', '.article-content', '.wsj-snippet-body'],
            'theverge.com': ['article', '.c-entry-content', '.duet--article--article-body-component'],
            'techcrunch.com': ['article', '.article-content', '.content'],
            'axios.com': ['article', '[data-module="StoryBody"]', '.gtm-story-text'],
            'ft.com': ['article', '.article__content', '.article-body'],
            'puck.news': ['article', '.post-content', '.article-content']
        }
    
    def extract_links_from_mando(self, email_body):
        """Extract links from Mando Minutes email format"""
        links = []
        
        # Mando often has links in bullet points
        lines = email_body.split('\n')
        
        for line in lines:
            # Look for URLs
            urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', line)
            for url in urls:
                # Clean up URL
                url = url.rstrip('.,;:')
                # Skip email/social media links
                if not any(skip in url for skip in ['unsubscribe', 'twitter.com', 'mailto:', 'list-manage']):
                    links.append(url)
        
        # Also try BeautifulSoup if there's HTML
        try:
            soup = BeautifulSoup(email_body, 'html.parser')
            for link in soup.find_all('a', href=True):
                url = link['href']
                if url.startswith('http') and url not in links:
                    links.append(url)
        except:
            pass
        
        return links[:15]  # Limit to 15 most relevant links
    
    def fetch_article_content(self, url):
        """Fetch article with better extraction"""
        try:
            logging.info(f"Fetching: {url}")
            
            # Parse domain
            domain = urlparse(url).netloc.lower().replace('www.', '')
            
            # Try cloudscraper first
            try:
                response = self.scraper.get(url, headers=self.headers, timeout=10)
            except:
                # Fallback to regular requests
                response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logging.warning(f"Failed to fetch {url}: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Try site-specific selectors
            article_text = ""
            
            if domain in self.site_selectors:
                for selector in self.site_selectors[domain]:
                    elements = soup.select(selector)
                    if elements:
                        article_text = ' '.join([elem.get_text(strip=True) for elem in elements])
                        if len(article_text) > 200:
                            break
            
            # Generic article extraction
            if not article_text:
                # Try common article patterns
                article_candidates = soup.find_all(['article', 'main', 'div'], 
                                                 class_=re.compile('content|article|story|post'))
                
                for candidate in article_candidates:
                    text = candidate.get_text(strip=True)
                    if len(text) > len(article_text):
                        article_text = text
            
            # Last resort: get all paragraphs
            if len(article_text) < 200:
                paragraphs = soup.find_all('p')
                article_text = ' '.join([p.get_text(strip=True) for p in paragraphs 
                                       if len(p.get_text(strip=True)) > 50])
            
            # Get title
            title = ""
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            # Clean up text
            article_text = re.sub(r'\s+', ' ', article_text)
            article_text = article_text[:2000]  # Limit length
            
            return {
                'url': url,
                'title': title[:200],
                'content': article_text,
                'domain': domain
            }
            
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return None
    
    def create_enhanced_podcast_script(self, email_body, fetched_articles):
        """Create a proper podcast script with actual content"""
        
        # Parse the email to get the bullet points
        lines = email_body.split('\n')
        
        # Extract crypto and market data
        crypto_data = []
        market_data = []
        news_items = []
        
        for line in lines:
            line = line.strip()
            if 'BTC:' in line or 'ETH:' in line:
                crypto_data.append(line)
            elif 'NASDAQ' in line or 'Gold:' in line:
                market_data.append(line)
            elif line.startswith('•') or line.startswith('-'):
                news_items.append(line)
        
        # Create script
        date_str = datetime.now().strftime('%A, %B %d, %Y')
        
        script = f"""Good morning! This is your Mando Minutes podcast for {date_str}.

I'm your AI assistant with today's comprehensive crypto and market analysis.

"""
        
        # Market snapshot
        if crypto_data:
            script += "Let's start with the market snapshot:\n\n"
            for data in crypto_data[:3]:
                script += f"{data}\n"
            script += "\n"
        
        # Add fetched article content
        if fetched_articles:
            script += "Now for today's top stories with full analysis:\n\n"
            
            story_num = 1
            for article in fetched_articles:
                if article and article['content'] and len(article['content']) > 100:
                    script += f"Story {story_num}: {article['title']}\n\n"
                    
                    # Add meaningful content
                    content = article['content']
                    # First 300 words
                    words = content.split()[:300]
                    script += ' '.join(words) + "...\n\n"
                    script += f"Source: {article['domain']}\n\n"
                    
                    story_num += 1
                    if story_num > 5:  # Limit to 5 stories
                        break
        
        # If no articles fetched, use email bullet points with context
        if not fetched_articles or story_num == 1:
            script += "\nToday's key developments:\n\n"
            
            for item in news_items[:10]:
                # Clean up bullet point
                item = item.lstrip('•-').strip()
                if len(item) > 10:
                    script += f"- {item}\n"
            script += "\n"
        
        # Market analysis section
        if market_data:
            script += "Market indicators:\n\n"
            for data in market_data:
                script += f"{data}\n"
            script += "\n"
        
        # Closing
        script += f"""That concludes today's Mando Minutes with {story_num-1 if fetched_articles else 'multiple'} stories analyzed.

Key takeaway: The crypto markets are showing mixed signals with BTC maintaining strength while broader markets exhibit volatility.

For all the links and additional details, check your Mando Minutes email.

Have a profitable day!"""
        
        return script

# Test the improved processor
if __name__ == "__main__":
    processor = ImprovedMandoProcessor()
    
    # Test with a sample Mando email
    sample_email = """
    Crypto
    • BTC: 108.6k (-1%), ETH: 2545 (-2%), SOL: 150 (-4%)
    • Top Gainers: PENGU, TRX, TKX, LEO, XDC
    • BTC ETFs: +$602mn, ETH ETFs: +$148mn
    • Crypto lower despite strong jobs data: https://www.coindesk.com/markets/btc-analysis
    • Early BTC whales shed $50b: https://www.bloomberg.com/crypto-whales
    """
    
    # Extract links
    links = processor.extract_links_from_mando(sample_email)
    print(f"Found {len(links)} links")
    
    # Fetch articles
    articles = []
    for link in links[:3]:  # Test with first 3
        article = processor.fetch_article_content(link)
        if article:
            articles.append(article)
            print(f"✅ Fetched: {article['title']}")
    
    # Create script
    script = processor.create_enhanced_podcast_script(sample_email, articles)
    print(f"\nScript preview ({len(script.split())} words):")
    print(script[:500] + "...")
