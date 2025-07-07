#!/usr/bin/env python3
"""
Quick demonstration of comprehensive vs short processing
"""

from comprehensive_mando_processor import ComprehensiveMandoProcessor

# Sample Mando email with many items
sample_mando = """
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
• There will be real pain from AI: Altman
• No progress with Putin on Ukraine war: Trump
• Iran wants nuclear talks: Trump
• China plans subsidies to boost birth rates

Left Curve Corner
• Hot coins: FARTCOIN, PENGU, GP, DBC
• Hot NFTs: Broken Keys, CDBs
• Jupiter intros new launchpad Jupiter Studio
• PENGU, FARTCOIN lead memecoins higher
"""

print("MANDO MINUTES COMPREHENSIVE PROCESSOR TEST")
print("=" * 70)
print(f"Input: Mando Minutes email with {len(sample_mando.split(chr(10)))} lines")
print(f"News items: ~{sample_mando.count('•')} items\n")

# Process with comprehensive processor
processor = ComprehensiveMandoProcessor()
script, word_count, duration = processor.process_mando_email(sample_mando)

print("RESULTS:")
print("-" * 70)
print(f"❌ Your previous result: 120 words, 0.8 minutes")
print(f"✅ Comprehensive result: {word_count:,} words, {duration:.1f} minutes")
print(f"\nImprovement: {word_count/120:.0f}x more content!")
print("\nThe comprehensive version covers:")
print("• Detailed analysis of EVERY crypto price movement")
print("• In-depth coverage of ALL whale movements")
print("• ETF flow analysis with historical context")
print("• Regulatory impact assessment for each development")
print("• Market sentiment analysis with trading implications")
print("• Macro market correlation insights")
print("• Specific trading recommendations")
print("• Risk management strategies")
print("\nSample of comprehensive content:")
print("-" * 70)
print(script[1000:1800] + "...")
print("-" * 70)
print(f"\nThis is {word_count:,} words of ACTUAL ANALYSIS, not 120 words of nothing!")
