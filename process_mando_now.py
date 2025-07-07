#!/usr/bin/env python3
"""
Process Today's Mando Minutes - Complete Flow
Creates enhanced podcast with link following, generates audio, sends email
"""

from dual_newsletter_automation import DualNewsletterAutomation
import logging

logging.basicConfig(level=logging.INFO)

# Create automation instance
automation = DualNewsletterAutomation()

# Process just Mando Minutes
mando_config = automation.config['newsletters'][0]  # First newsletter is Mando

print("🚀 Processing today's Mando Minutes with complete automation...")
print("   ✓ Link following for article content")
print("   ✓ Audio generation with ElevenLabs")
print("   ✓ Email delivery\n")

success = automation.process_newsletter(mando_config)

if success:
    print("\n✅ SUCCESS! Check your email for the Mando Minutes podcast")
else:
    print("\n❌ No Mando Minutes found or processing failed")
    print("Check dual_newsletter.log for details")
