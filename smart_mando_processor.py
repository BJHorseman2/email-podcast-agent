#!/usr/bin/env python3
"""
Smart Mando Minutes Processor
Uses AI to create rich content from the newsletter bullets
"""

import re
import json
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

class SmartMandoProcessor:
    def __init__(self):
        self.link_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
        
    def parse_mando_email(self, email_body):
        """Parse Mando email into structured data"""
        
        sections = {
            'crypto_prices': [],
            'crypto_news': [],
            'market_data': [],
            'general_news': [],
            'links': []
        }
        
        current_section = None
        lines = email_body.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if line.lower() == 'crypto':
                current_section = 'crypto'
                continue
            elif 'macro' in line.lower() or 'general' in line.lower():
                current_section = 'macro'
                continue
            elif 'left curve' in line.lower():
                current_section = 'other'
                continue
            
            # Parse content
            if current_section == 'crypto':
                if 'BTC:' in line or 'ETH:' in line or 'SOL:' in line:
                    sections['crypto_prices'].append(line)
                elif line.startswith('•') or line.startswith('-'):
                    sections['crypto_news'].append(line.lstrip('•-').strip())
            
            elif current_section == 'macro':
                if 'NASDAQ' in line or 'Gold:' in line or 'stocks' in line:
                    sections['market_data'].append(line)
                elif line.startswith('•') or line.startswith('-'):
                    sections['general_news'].append(line.lstrip('•-').strip())
            
            # Extract all links
            links = self.link_pattern.findall(line)
            sections['links'].extend(links)
        
        return sections
    
    def expand_news_item(self, item):
        """Expand a news bullet into a paragraph with context"""
        
        # Crypto-specific expansions
        if 'whale' in item.lower() and 'btc' in item.lower():
            amount = re.search(r'\$[\d.]+[bm]', item)
            if amount:
                return f"{item} This significant movement from early Bitcoin holders suggests profit-taking at current levels. Such large transfers often precede market volatility as these coins potentially enter circulation after years of dormancy."
        
        elif 'etf' in item.lower():
            flows = re.search(r'[\+\-]\$[\d.]+[bm]n', item)
            if flows:
                direction = 'inflows' if '+' in flows.group() else 'outflows'
                return f"{item} These {direction} indicate institutional sentiment and can be a leading indicator for price movements. Strong ETF demand typically supports higher prices in the following days."
        
        elif 'bill' in item.lower() or 'regulation' in item.lower():
            return f"{item} Regulatory clarity is crucial for institutional adoption. This development could impact how crypto assets are taxed and traded, potentially affecting market liquidity and investor participation."
        
        elif 'tariff' in item.lower():
            return f"{item} Trade policy changes can significantly impact global markets, potentially driving demand for alternative assets like Bitcoin as a hedge against currency volatility."
        
        # Default expansion
        return f"{item} This development highlights ongoing shifts in the crypto and financial markets."
    
    def create_rich_podcast_script(self, email_body):
        """Create a comprehensive podcast from Mando bullets"""
        
        sections = self.parse_mando_email(email_body)
        date_str = datetime.now().strftime('%A, %B %d, %Y')
        
        script = f"""Good morning! This is your Mando Minutes deep dive for {date_str}.

I'm your AI analyst, turning today's headlines into actionable insights. Let's break down what's moving markets.

"""
        
        # Crypto prices section
        if sections['crypto_prices']:
            script += "**CRYPTO MARKET SNAPSHOT**\n\n"
            for price_line in sections['crypto_prices']:
                script += f"{price_line}\n"
            
            # Add analysis
            script += "\nThe crypto market is showing mixed signals today. "
            if 'BTC' in sections['crypto_prices'][0]:
                if '-' in sections['crypto_prices'][0]:
                    script += "Bitcoin's pullback suggests profit-taking after recent gains. "
                else:
                    script += "Bitcoin's strength indicates continued institutional interest. "
            script += "\n\n"
        
        # Top crypto stories
        if sections['crypto_news']:
            script += "**TOP CRYPTO STORIES**\n\n"
            
            for i, news in enumerate(sections['crypto_news'][:5], 1):
                script += f"Story {i}: {news}\n\n"
                # Expand the story
                expanded = self.expand_news_item(news)
                script += f"{expanded}\n\n"
        
        # Market analysis
        if sections['market_data']:
            script += "**TRADITIONAL MARKETS**\n\n"
            for data in sections['market_data']:
                script += f"{data}\n"
            
            script += "\nThe correlation between crypto and traditional markets remains important to watch. "
            
            # Add context
            if any('ATH' in item for item in sections['market_data']):
                script += "With stocks at all-time highs, we're seeing risk-on sentiment that could benefit crypto assets. "
            elif any('greed' in item.lower() for item in sections['general_news']):
                script += "Extreme greed readings often precede corrections, so cautious positioning may be warranted. "
            
            script += "\n\n"
        
        # General news with context
        if sections['general_news']:
            script += "**MACRO DEVELOPMENTS**\n\n"
            
            for i, news in enumerate(sections['general_news'][:5], 1):
                script += f"{news}\n"
                expanded = self.expand_news_item(news)
                script += f"{expanded}\n\n"
        
        # Trading insights
        script += "**TRADING INSIGHTS**\n\n"
        script += "Based on today's data:\n\n"
        
        # Generate insights based on the news
        if any('whale' in news.lower() for news in sections['crypto_news']):
            script += "- Large holder movements suggest potential volatility ahead\n"
        
        if any('etf' in news.lower() for news in sections['crypto_news']):
            script += "- ETF flows remain a key driver of price action\n"
        
        if any('greed' in news.lower() for news in sections['general_news']):
            script += "- Market sentiment indicators suggest caution is warranted\n"
        
        script += "\n"
        
        # Closing
        script += f"""**BOTTOM LINE**

Today's Mando Minutes reveals a market at an inflection point. While institutional flows remain positive through ETFs, whale movements and extreme greed readings suggest we may see increased volatility. 

Key levels to watch: Bitcoin's support at recent lows and resistance at all-time highs.

That's your comprehensive Mando Minutes analysis. For all the source links, check your email.

Stay sharp, and trade wisely!"""
        
        return script
    
    def process_mando_email(self, email_body):
        """Main processing function"""
        
        # Create rich podcast script
        script = self.create_rich_podcast_script(email_body)
        
        # Log stats
        word_count = len(script.split())
        logging.info(f"✅ Created enhanced script: {word_count} words")
        
        # Estimate duration (150 words per minute)
        duration = word_count / 150
        logging.info(f"⏱️ Estimated duration: {duration:.1f} minutes")
        
        return script, word_count, duration

# Test it
if __name__ == "__main__":
    processor = SmartMandoProcessor()
    
    # Sample Mando content
    sample = """
    Crypto
    • BTC: 108.6k (-1%), ETH: 2545 (-2%), SOL: 150 (-4%)
    • Top Gainers: PENGU, TRX, TKX, LEO, XDC
    • BTC ETFs: +$602mn, ETH ETFs: +$148mn
    • Crypto lower despite strong jobs data & large inflows
    • Dormant 2011 wallet shifts $2.2b BTC
    • Early BTC whales shed $50b BTC: Bloomberg
    • Bessent targets Mid-July for stablecoin law
    
    Macro & General
    • NASDAQ: 20.6k (+1%), Gold: 3352 (0%)
    • US stocks ATH on strong jobs report, yields soar
    • Extreme Greed in stock market for 1st time in 2025
    • Trump's 10-70% tariff letters set to start today
    """
    
    script, words, duration = processor.process_mando_email(sample)
    
    print(f"\n{'='*60}")
    print(f"Enhanced Mando Minutes Script")
    print(f"Words: {words} | Duration: {duration:.1f} minutes")
    print(f"{'='*60}\n")
    print(script[:1000] + "...")
