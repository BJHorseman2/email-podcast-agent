#!/bin/bash
# AOL Email to Podcast Agent - Daily Runner
# Customized for AOL.com email accounts

echo "🌅 AOL Email to Podcast Agent - Daily Runner"
echo "📅 $(date)"
echo "📧 Checking AOL inbox for morning email..."

cd "/Users/markbaumrind/Desktop/email_podcast_agent"

# Check if AOL agent script exists
if [ -f "aol_email_agent.py" ]; then
    echo "✅ AOL agent script found"
    
    # Check if config file exists
    if [ -f "config.json" ]; then
        echo "⚙️ Configuration found"
        echo "🔄 Processing AOL email..."
        
        # Run the AOL email agent
        python3 aol_email_agent.py
        
        # Check if podcast files were created
        if [ "$(ls -A podcasts/ 2>/dev/null)" ]; then
            echo "✅ Podcast content generated successfully!"
            echo "📂 Files created in podcasts/ directory:"
            ls -la podcasts/ | grep "$(date +%Y%m%d)"
            
            echo ""
            echo "🎙️ Next step: Follow the NotebookLM instructions to create your audio podcast"
            echo "📋 Look for the instruction file in the podcasts directory"
        else
            echo "📭 No new podcast content generated"
            echo "💡 This might mean:"
            echo "   - No matching email found in AOL inbox"
            echo "   - Email already processed today"
            echo "   - Check aol_podcast_agent.log for details"
        fi
        
    else
        echo "❌ config.json not found!"
        echo "📝 Please configure your AOL email settings first"
        echo "📖 See AOL_SETUP_GUIDE.md for instructions"
        exit 1
    fi
    
else
    echo "❌ AOL agent script not found!"
    echo "📁 Expected: aol_email_agent.py"
    exit 1
fi

echo ""
echo "🎉 AOL email processing completed!"
echo "📍 Location: $(pwd)"
echo "📊 Check logs: aol_podcast_agent.log"
