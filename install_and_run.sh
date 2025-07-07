#!/bin/bash
# Fix for pip command not found on macOS

echo "🔧 Fixing pip command not found issue..."
echo ""

# Method 1: Try pip3 (most common on macOS)
if command -v pip3 &> /dev/null; then
    echo "✅ Found pip3! Installing packages..."
    pip3 install beautifulsoup4 lxml requests
    echo ""
    echo "✅ Packages installed successfully!"
    echo ""
    echo "Now running the enhanced Mando Minutes agent..."
    python3 enhanced_complete_automation.py
    exit 0
fi

# Method 2: Try python3 -m pip
if command -v python3 &> /dev/null; then
    echo "✅ Using python3 -m pip to install packages..."
    python3 -m pip install beautifulsoup4 lxml requests
    echo ""
    echo "✅ Packages installed successfully!"
    echo ""
    echo "Now running the enhanced Mando Minutes agent..."
    python3 enhanced_complete_automation.py
    exit 0
fi

# Method 3: Check if packages are already installed
echo "🔍 Checking if packages are already installed..."
if python3 -c "import bs4, lxml, requests" 2>/dev/null; then
    echo "✅ All packages are already installed!"
    echo ""
    echo "Running the enhanced Mando Minutes agent..."
    python3 enhanced_complete_automation.py
    exit 0
fi

# If nothing worked
echo "❌ Could not find pip or pip3"
echo ""
echo "Try one of these commands manually:"
echo "1. pip3 install beautifulsoup4 lxml requests"
echo "2. python3 -m pip install beautifulsoup4 lxml requests"
echo "3. /usr/bin/pip3 install beautifulsoup4 lxml requests"
echo ""
echo "If none work, you may need to install pip first:"
echo "curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"
echo "python3 get-pip.py"
