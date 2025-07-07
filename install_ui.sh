#!/bin/bash
# Quick install for UI dependencies

echo "🔧 Installing UI Dependencies..."
echo ""

# Install required packages
echo "📦 Installing packages..."
pip3 install streamlit pandas

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 To launch the UI, run:"
echo "   python3 launch.py"
echo ""
echo "Or directly:"
echo "   ./run_ui.sh"
