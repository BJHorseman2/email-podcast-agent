#!/bin/bash
# Quick fix for short Mando Minutes podcasts

echo "🔧 FIXING: Short Mando Minutes Podcasts (0.5 minutes → 3-5 minutes)"
echo ""

# Check and install dependencies
echo "📦 Checking dependencies..."
python3 -c "import bs4" 2>/dev/null || {
    echo "Installing required packages..."
    pip install beautifulsoup4 lxml html5lib requests
}

echo ""
echo "🚀 Running enhanced automation with link following..."
echo ""

# Run the enhanced version
python3 enhanced_complete_automation.py

echo ""
echo "✅ Done! Your podcast should now be 3-5 minutes with full article content!"
echo ""
echo "📊 Check the logs above for:"
echo "   - Number of links found"
echo "   - Number of articles fetched" 
echo "   - Final word count (should be 800+)"
echo ""
echo "🎙️ The enhanced podcast will be in your podcasts folder"