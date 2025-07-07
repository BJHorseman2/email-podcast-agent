#!/bin/bash
# Complete Automation Setup Script
# Helps you get everything configured quickly

echo "🎙️ Email-to-Podcast Automation Setup"
echo "===================================="
echo

# Check if we're in the right directory
if [ ! -f "complete_automation.py" ]; then
    echo "❌ Please run this script from the email_podcast_agent directory"
    exit 1
fi

echo "📋 Step 1: Installing Python dependencies..."
pip install openai requests schedule

echo
echo "🔧 Step 2: Configuration Check"
echo "Current configuration status:"

# Check if config file exists
if [ -f "full_automation_config.json" ]; then
    echo "✅ Configuration file found"
    
    # Check for placeholder values
    if grep -q "YOUR_AOL_EMAIL" full_automation_config.json; then
        echo "⚠️  AOL email needs to be configured"
    else
        echo "✅ AOL email configured"
    fi
    
    if grep -q "YOUR_ELEVENLABS_API_KEY" full_automation_config.json; then
        echo "⚠️  ElevenLabs API key needs to be configured"
    else
        echo "✅ ElevenLabs API key configured"
    fi
    
    if grep -q "YOUR_OPENAI_API_KEY" full_automation_config.json; then
        echo "⚠️  OpenAI API key not configured (optional)"
    else
        echo "✅ OpenAI API key configured"
    fi
    
    if grep -q "YOUR_GMAIL" full_automation_config.json; then
        echo "⚠️  Gmail delivery not configured"
    else
        echo "✅ Gmail delivery configured"
    fi
else
    echo "❌ Configuration file not found"
    exit 1
fi

echo
echo "🧪 Step 3: Running system test..."
python3 complete_automation.py

echo
echo "🎯 Next Steps:"
echo "1. If test failed, update full_automation_config.json with your API keys"
echo "2. To run automation once: python3 complete_automation.py"
echo "3. To enable daily automation: python3 complete_automation.py --schedule"
echo
echo "📖 For detailed setup instructions, see COMPLETE_AUTOMATION_GUIDE.md"
echo
echo "🎉 Your email-to-podcast automation is ready!"
