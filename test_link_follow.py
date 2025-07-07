#!/usr/bin/env python3
"""
Quick test to verify link-following is working
"""

from link_following_agent import LinkFollowingNewsletterAgent
import logging

logging.basicConfig(level=logging.INFO)

# Test with a crypto news link
test_url = "https://www.coindesk.com/markets/2025/01/06/bitcoin-etfs-see-602m-inflows/"

agent = LinkFollowingNewsletterAgent()

print("🧪 Testing link extraction...")
print(f"📎 Testing URL: {test_url}")

article = agent.fetch_article_content(test_url)

if article and article['content']:
    print(f"\n✅ SUCCESS! Link following is working!")
    print(f"📰 Title: {article['title']}")
    print(f"📊 Content length: {len(article['content'])} characters")
    print(f"💬 Preview: {article['content'][:200]}...")
else:
    print("\n❌ Link following test failed. Check your internet connection.")
    print("If the issue persists, the website may be blocking automated requests.")
