#!/bin/bash
# Launch the Email-to-Podcast Web UI

echo "🎙️ Email-to-Podcast Web UI"
echo "=========================="
echo ""

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing Streamlit..."
    pip3 install streamlit pandas
fi

echo "🚀 Starting web interface..."
echo ""
echo "The app will open in your browser automatically."
echo "If not, go to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the app
python3 -m streamlit run app.py --server.headless true
