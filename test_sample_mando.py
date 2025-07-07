#!/usr/bin/env python3
"""
Test enhanced link following with sample Mando Minutes content
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_complete_automation import EnhancedPodcastAutomationAgent
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# Sample Mando Minutes content from your screenshot
SAMPLE_MANDO_CONTENT = """
Crypto pulls back, Big Beautiful Bill passes, Extreme Greed in stocks

Crypto

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
• Ondo, Pantera allocate $250m for RWA tokenisation
• JP Morgan cuts stablecoin market outlook to $500b
• FTX recovery trust freezes payout to 49 nations

Macro & General

• NASDAQ: 20.6k (+1%), Gold: 3352 (0%)
• US stocks ATH on strong jobs report, yields soar
• Trump's Big, Beautiful bill passes House
• Extreme Greed in stock market for 1st time in 2025
• Odds of rate cut in July FOMC fall to 5%
• Trump's 10-70% tariff letters set to start today
• Countries to pay tariffs from Aug 1: Trump
• Higher inflation likely for a period: Fed's Bostic
• US Home seller-buyer gap continues to hit ATH
• Our new tech takes AI to new level: Nvidia CEO
• There will be real pain from AI: Altman
• No progress with Putin on Ukraine war: Trump
• Iran wants nuclear talks: Trump
• China plans subsidies to boost birth rates

Left Curve Corner

• Hot coins: FARTCOIN, PENGU, GP, DBC
• Hot NFTs: Broken Keys, CDBs
• Jupiter intros new launchpad Jupiter Studio
• PENGU, FARTCOIN lead memecoins higher

YEET: Crypto's Casino
Just passed $230m in lifetime volume!
"""

def test_with_sample():
    """Test the enhanced agent with sample Mando content"""
    
    agent = EnhancedPodcastAutomationAgent()
    
    # Create enhanced podcast script
    logging.info("🧪 Testing with sample Mando Minutes content...")
    
    subject = "Mando Minutes: 4 July"
    sender = "Jon Kelly <jonkelly@puck.news>"
    
    # The agent will extract links from this content
    # For demo, let's add some real links
    enhanced_content = SAMPLE_MANDO_CONTENT + """
    
    Links:
    https://www.bloomberg.com/news/articles/bitcoin-whales-50-billion-selloff
    https://www.coindesk.com/policy/bessent-stablecoin-regulation-july
    https://www.reuters.com/markets/us-stocks-hit-record-jobs-report
    """
    
    # Create podcast script with link following
    script = agent.create_podcast_script(subject, enhanced_content, sender)
    
    # Save the enhanced script
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"podcasts/mando_sample_enhanced_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(script)
    
    print(f"\n✅ Enhanced podcast script created!")
    print(f"📝 Saved to: {filename}")
    print(f"📊 Stats: {len(script.split())} words, {len(script)} characters")
    print(f"⏱️ Estimated duration: {len(script.split()) / 150:.1f} minutes")
    
    print("\n" + "="*60)
    print("ENHANCED PODCAST PREVIEW:")
    print("="*60)
    print(script[:800] + "...")
    print("="*60)
    print(f"\n👉 Full script saved to: {filename}")

if __name__ == "__main__":
    test_with_sample()
