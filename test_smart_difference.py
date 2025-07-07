#!/usr/bin/env python3
"""
Quick test to show the difference between useless and smart processing
"""

from smart_mando_processor import SmartMandoProcessor

# Sample Mando content (like what's in your email)
mando_email = """
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

Macro & General
• NASDAQ: 20.6k (+1%), Gold: 3352 (0%)
• US stocks ATH on strong jobs report, yields soar
• Trump's Big, Beautiful bill passes House
• Extreme Greed in stock market for 1st time in 2025
• Trump's 10-70% tariff letters set to start today
"""

print("="*60)
print("WORTHLESS VERSION (what you got):")
print("="*60)
print("""
Story 1: Bitcoin & Ethereum ETFs Inflows...
DashSearch NFTs, Crypto, or FT...NFTsCryptoNFTsCrypto...

Story 2: Mando Minutes
Mando MinutesPostsMando Minutes7 July...
""")
print("\nResult: Garbage that provides no value!")

print("\n" + "="*60)
print("SMART VERSION (what you'll get now):")
print("="*60)

processor = SmartMandoProcessor()
script, words, duration = processor.process_mando_email(mando_email)

print(script[:1500] + "...")
print(f"\nResult: {words} words of actual analysis and insights!")
print(f"Duration: {duration:.1f} minutes of valuable content")
