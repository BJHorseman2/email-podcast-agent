#!/bin/bash
# Run Enhanced Mando Minutes with Link Following

echo "🚀 Running Enhanced Mando Minutes with Link Following..."
echo ""

# Check if required packages are installed
python3 -c "import beautifulsoup4" 2>/dev/null || {
    echo "📦 Installing required packages..."
    pip install beautifulsoup4 lxml html5lib
}

# Run the enhanced agent
python3 run_enhanced_mando.py

echo ""
echo "✅ Enhanced Mando Minutes processing complete!"
echo "📊 Check the podcasts folder for enhanced scripts with full article content"