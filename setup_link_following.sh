#!/bin/bash
# Setup script for link-following email to podcast agent

echo "🚀 Setting up Link-Following Email to Podcast Agent..."

# Install enhanced requirements
echo "📦 Installing required packages..."
pip install -r requirements_enhanced.txt

# Test the link-following functionality
echo "🧪 Testing link extraction..."
python test_link_following.py

# Make scripts executable
chmod +x link_following_agent.py
chmod +x mando_minutes_agent.py
chmod +x test_link_following.py

echo "✅ Setup complete!"
echo ""
echo "To use the enhanced agent with Mando Minutes:"
echo "1. Run: python mando_minutes_agent.py"
echo ""
echo "To integrate with your existing setup:"
echo "2. Update your existing agents to use LinkFollowingNewsletterAgent"
echo "3. The agent will automatically fetch content from links in newsletters"
echo ""
echo "📝 Check the 'podcasts' folder for enhanced podcast scripts with full article content!"
