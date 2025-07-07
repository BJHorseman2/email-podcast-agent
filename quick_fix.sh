#!/bin/bash
# Install missing packages and run enhanced Mando Minutes

echo "📦 Installing missing packages (lxml)..."
echo ""

# Use python3 -m pip which should work on your system
python3 -m pip install lxml requests beautifulsoup4

echo ""
echo "✅ Packages installed!"
echo ""
echo "🚀 Now running the enhanced Mando Minutes with link following..."
echo ""

# Run the enhanced automation
python3 enhanced_complete_automation.py
