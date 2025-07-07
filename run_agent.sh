#!/bin/bash
# MCP Email to Podcast Agent - Daily Runner
# Generated: July 2, 2025

echo "🚀 Starting MCP Email to Podcast Agent..."
echo "📅 $(date)"

cd "/Users/markbaumrind/Desktop/email_podcast_agent"

# Check if Python script exists
if [ -f "mcp_email_agent.py" ]; then
    echo "✅ Agent script found"
    echo "🔄 Executing agent..."
    
    # Run the Python agent
    python3 mcp_email_agent.py
    
    echo "✅ Agent execution completed"
    echo "📂 Check podcasts directory for new content"
    
    # List generated files
    echo "📄 Generated files:"
    ls -la podcasts/
    
else
    echo "❌ Agent script not found!"
    exit 1
fi

echo "🎉 Daily email-to-podcast process completed!"
echo "📍 Location: $(pwd)"