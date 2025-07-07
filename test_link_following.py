#!/usr/bin/env python3
"""
Test the link-following functionality with Mando Minutes content
"""

from link_following_agent import LinkFollowingNewsletterAgent
import logging

logging.basicConfig(level=logging.INFO)

def test_mando_minutes_links():
    """Test with actual Mando Minutes content"""
    
    agent = LinkFollowingNewsletterAgent()
    
    # Sample Mando Minutes content (from your screenshots)
    email_content = """
    Crypto pulls back, Big Beautiful Bill passes, Extreme Greed in stocks
    
    Crypto:
    • BTC: 108.6k (-1%), ETH: 2545 (-2%), SOL: 150 (-4%)
    • Top Gainers: PENGU, TRX, TKX, LEO, XDC
    • BTC ETFs: +$602mn, ETH ETFs: +$148mn
    • Crypto lower despite strong jobs data & large inflows
    • Dormant 2011 wallet shifts $2.2b BTC
    • Early BTC whales shed $50b BTC: Bloomberg
    • BMNR stock parabolic post ETH treasury move
    • Bessent targets Mid-July for stablecoin law
    • BTC may hit $90-95k after Big Beautiful Bill: Hayes
    • Lummis' new bill to remove crypto tax under $300
    • US House designates July 14-18 as 'Crypto Week'
    • Nano Labs buys $50m BNB
    """
    
    # Sample HTML with links (simulated)
    html_content = """
    <html>
    <body>
    <h2>Crypto</h2>
    <ul>
    <li><a href="https://www.bloomberg.com/news/articles/2025-01-06/bitcoin-whales-sell-50-billion">Early BTC whales shed $50b BTC: Bloomberg</a></li>
    <li><a href="https://www.coindesk.com/policy/2025/01/06/bessent-stablecoin-law-july">Bessent targets Mid-July for stablecoin law</a></li>
    <li><a href="https://www.theblock.co/post/123456/lummis-crypto-tax-bill">Lummis' new bill to remove crypto tax under $300</a></li>
    </ul>
    
    <h2>Macro & General</h2>
    <ul>
    <li><a href="https://www.wsj.com/articles/nasdaq-hits-record-jobs-report">US stocks ATH on strong jobs report, yields soar</a></li>
    <li><a href="https://www.ft.com/content/trump-tariff-letters">Trump's 10-70% tariff letters set to start today</a></li>
    </ul>
    </body>
    </html>
    """
    
    # Extract links
    print("\n🔍 Extracting links from Mando Minutes...")
    links = agent.extract_links_from_content(email_content, html_content)
    
    print(f"\n📎 Found {len(links)} links:")
    for i, link in enumerate(links, 1):
        print(f"  {i}. {link}")
    
    # Fetch article content (limit to first 3 for demo)
    print("\n📰 Fetching article content...")
    articles = agent.fetch_multiple_articles(links[:3])
    
    print(f"\n✅ Successfully fetched {len(articles)} articles")
    
    # Create podcast script
    print("\n🎙️ Generating podcast script...")
    podcast_script = agent.create_enhanced_podcast_script(
        "Mando Minutes: 4 July",
        "Mando <mando@newsletter.com>",
        email_content,
        articles,
        "mando_minutes"
    )
    
    # Save sample output
    with open('podcasts/mando_minutes_sample_enhanced.txt', 'w') as f:
        f.write(podcast_script)
    
    print("\n📝 Sample enhanced podcast script preview:")
    print("=" * 50)
    print(podcast_script[:1000] + "...")
    print("=" * 50)
    
    print("\n✅ Test complete! Check 'podcasts/mando_minutes_sample_enhanced.txt' for full script")

if __name__ == "__main__":
    test_mando_minutes_links()
