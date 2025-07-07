#!/usr/bin/env python3
"""
Link-Following Newsletter Agent
Extracts links from newsletters and fetches their content for richer podcasts
"""

import imaplib
import email
import json
import os
import ssl
import time
import requests
import re
from datetime import datetime, timedelta
from email.header import decode_header
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LinkFollowingNewsletterAgent:
    def __init__(self):
        self.config = self.load_config()
        self.podcasts_dir = "podcasts"
        os.makedirs(self.podcasts_dir, exist_ok=True)
        
        # User agent for web requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Common news domains to prioritize
        self.trusted_domains = {
            'bloomberg.com', 'reuters.com', 'wsj.com', 'ft.com', 
            'techcrunch.com', 'coindesk.com', 'cointelegraph.com',
            'theverge.com', 'arstechnica.com', 'wired.com'
        }
        
    def load_config(self):
        """Load configuration"""
        try:
            with open('multi_email_config.json', 'r') as f:
                return json.load(f)
        except:
            logging.error("Config file not found")
            return None
    
    def extract_links_from_content(self, content, html_content=""):
        """Extract all URLs from email content"""
        urls = set()
        
        # Extract from HTML if available
        if html_content:
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                for link in soup.find_all('a', href=True):
                    url = link['href']
                    # Skip mailto, unsubscribe, and tracking links
                    if (url.startswith('http') and 
                        'unsubscribe' not in url.lower() and
                        'email-preferences' not in url.lower() and
                        'click.pstmrk.it' not in url.lower() and
                        'list-manage.com' not in url.lower()):
                        urls.add(url)
            except Exception as e:
                logging.error(f"Error parsing HTML for links: {e}")
        
        # Also extract from plain text using regex
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?:[/?#][^\s<>"{}|\\^`\[\]]*)?'
        text_urls = re.findall(url_pattern, content)
        urls.update(text_urls)
        
        # Filter and prioritize URLs
        filtered_urls = []
        for url in urls:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Skip social media, tracking, and email management links
            skip_domains = ['twitter.com', 'x.com', 'facebook.com', 'linkedin.com', 
                          'instagram.com', 'youtube.com', 'bit.ly', 'tinyurl.com']
            if any(skip in domain for skip in skip_domains):
                continue
                
            # Prioritize trusted news sources
            if any(trusted in domain for trusted in self.trusted_domains):
                filtered_urls.insert(0, url)  # Add to front
            else:
                filtered_urls.append(url)
        
        return filtered_urls[:10]  # Limit to 10 most relevant links
    
    def fetch_article_content(self, url, timeout=10):
        """Fetch and extract article content from a URL"""
        try:
            logging.info(f"Fetching content from: {url}")
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                               'aside', 'form', 'button', 'iframe']):
                element.decompose()
            
            # Try to find article content using common selectors
            article_text = ""
            
            # Common article selectors
            article_selectors = [
                'article', 'main', '[role="main"]', '.article-content',
                '.post-content', '.entry-content', '.content-body',
                '.story-body', '.article-body', '.post-body'
            ]
            
            for selector in article_selectors:
                elements = soup.select(selector)
                if elements:
                    article_text = ' '.join([elem.get_text(strip=True) for elem in elements])
                    if len(article_text) > 200:  # Found substantial content
                        break
            
            # Fallback: get all paragraphs
            if len(article_text) < 200:
                paragraphs = soup.find_all('p')
                article_text = ' '.join([p.get_text(strip=True) for p in paragraphs 
                                       if len(p.get_text(strip=True)) > 50])
            
            # Extract title
            title = ""
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            # Clean up text
            article_text = re.sub(r'\s+', ' ', article_text)
            article_text = re.sub(r'\n{3,}', '\n\n', article_text)
            
            # Limit length for podcast (first 500 words)
            words = article_text.split()
            if len(words) > 500:
                article_text = ' '.join(words[:500]) + "..."
            
            return {
                'url': url,
                'title': title[:100],  # Limit title length
                'content': article_text,
                'domain': urlparse(url).netloc
            }
            
        except requests.exceptions.Timeout:
            logging.warning(f"Timeout fetching {url}")
            return None
        except requests.exceptions.RequestException as e:
            logging.warning(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error fetching {url}: {e}")
            return None
    
    def fetch_multiple_articles(self, urls, max_workers=5):
        """Fetch multiple articles concurrently"""
        articles = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.fetch_article_content, url): url 
                           for url in urls}
            
            for future in as_completed(future_to_url):
                result = future.result()
                if result and result['content']:
                    articles.append(result)
        
        return articles
    
    def create_enhanced_podcast_script(self, email_subject, sender, email_content, 
                                     articles, newsletter_name):
        """Create podcast script including fetched article content"""
        
        # Clean up newsletter name
        clean_name = newsletter_name.replace('_', ' ').title()
        
        script = f"""Good morning! Welcome to your {clean_name} podcast for {datetime.now().strftime('%B %d, %Y')}.

Today's {clean_name} comes from {sender} with the subject: {email_subject}

"""
        
        # Add original email summary if it has substantial content
        if len(email_content.strip()) > 200:
            script += f"Here's the newsletter overview:\n{email_content[:500]}...\n\n"
        
        # Add fetched article content
        if articles:
            script += f"Now, let's dive into today's top stories:\n\n"
            
            for i, article in enumerate(articles[:5], 1):  # Limit to top 5 articles
                script += f"Story {i}: {article['title']}\n"
                script += f"From {article['domain']}\n\n"
                
                # Add article content
                content = article['content']
                if content:
                    # Make it more conversational
                    script += f"{content[:400]}...\n\n"
                else:
                    script += "Unfortunately, I couldn't access the full content of this article.\n\n"
                
                script += "---\n\n"
        else:
            script += "I wasn't able to fetch additional content from the links in this newsletter.\n\n"
        
        # Add closing
        script += f"""That wraps up today's {clean_name} podcast. 

Thank you for listening, and have a great day!

---
Generated by your Email-to-Podcast AI Assistant
"""
        
        return script
    
    def process_newsletter_with_links(self, email_message, newsletter_config):
        """Process a newsletter and fetch linked content"""
        try:
            # Extract basic email info
            subject = self.decode_email_header(email_message.get('Subject', 'No Subject'))
            sender = self.decode_email_header(email_message.get('From', 'Unknown'))
            
            # Extract email content
            text_content, html_content = self.extract_email_content(email_message)
            
            # Extract links
            links = self.extract_links_from_content(text_content, html_content)
            logging.info(f"Found {len(links)} links in email")
            
            # Fetch article content from links
            articles = []
            if links:
                logging.info("Fetching article content...")
                articles = self.fetch_multiple_articles(links)
                logging.info(f"Successfully fetched {len(articles)} articles")
            
            # Create enhanced podcast script
            podcast_script = self.create_enhanced_podcast_script(
                subject, sender, text_content, articles, 
                newsletter_config['newsletter_name']
            )
            
            # Save podcast script
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{newsletter_config['newsletter_name']}_podcast_{timestamp}.txt"
            filepath = os.path.join(self.podcasts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(podcast_script)
            
            logging.info(f"✅ Created enhanced podcast script: {filename}")
            
            # Also save fetched articles data for reference
            data_filename = f"{newsletter_config['newsletter_name']}_data_{timestamp}.json"
            data_filepath = os.path.join(self.podcasts_dir, data_filename)
            
            with open(data_filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'subject': subject,
                    'sender': sender,
                    'links_found': len(links),
                    'articles_fetched': len(articles),
                    'articles': articles
                }, f, indent=2)
            
            return True
            
        except Exception as e:
            logging.error(f"Error processing newsletter: {e}")
            return False
    
    def extract_email_content(self, email_message):
        """Extract both text and HTML content from email"""
        text_content = ""
        html_content = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        text_content = payload.decode('utf-8', errors='ignore')
                
                elif content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        html_content = payload.decode('utf-8', errors='ignore')
        else:
            payload = email_message.get_payload(decode=True)
            if payload:
                content = payload.decode('utf-8', errors='ignore')
                if '<html' in content.lower():
                    html_content = content
                else:
                    text_content = content
        
        # Clean text content
        if not text_content and html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text(separator='\n', strip=True)
        
        return text_content, html_content
    
    def decode_email_header(self, header):
        """Decode email header"""
        if not header:
            return ""
        
        decoded_parts = decode_header(header)
        decoded_string = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_string += part
        
        return decoded_string

# Test the agent
if __name__ == "__main__":
    agent = LinkFollowingNewsletterAgent()
    
    # Test with a sample URL
    test_url = "https://www.coindesk.com/markets/2025/01/06/bitcoin-price/"
    logging.info("Testing link extraction...")
    
    article = agent.fetch_article_content(test_url)
    if article:
        print(f"\n✅ Successfully fetched article:")
        print(f"Title: {article['title']}")
        print(f"Content preview: {article['content'][:200]}...")
    else:
        print("❌ Failed to fetch article")
