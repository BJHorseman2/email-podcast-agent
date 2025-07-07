#!/bin/bash

# Create Email Podcast Dashboard App
APP_NAME="Email Podcast Dashboard"
APP_DIR="/Users/markbaumrind/Desktop/${APP_NAME}.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

# Create directory structure
mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES_DIR}"

# Create Info.plist
cat > "${CONTENTS_DIR}/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch_dashboard</string>
    <key>CFBundleIdentifier</key>
    <string>com.local.email-podcast-dashboard</string>
    <key>CFBundleName</key>
    <string>Email Podcast Dashboard</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

# Create launcher script
cat > "${MACOS_DIR}/launch_dashboard" << 'EOF'
#!/bin/bash
cd /Users/markbaumrind/Desktop/email_podcast_agent

# Check if already running
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "Dashboard already running, opening browser..."
    open http://localhost:8501
else
    echo "Starting Email Podcast Dashboard..."
    # Start Streamlit and open browser
    streamlit run app.py --browser.gatherUsageStats false &
    sleep 3
    open http://localhost:8501
fi
EOF

# Make executable
chmod +x "${MACOS_DIR}/launch_dashboard"

echo "✅ Created: ${APP_NAME}.app on your Desktop!"
echo "🎯 Double-click it to launch your dashboard!"
