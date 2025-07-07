#!/bin/bash

# Quick launcher - saves to your Applications folder
APP_PATH="/Applications/Email Podcast Dashboard.app"
mkdir -p "${APP_PATH}/Contents/MacOS"

cat > "${APP_PATH}/Contents/MacOS/Email Podcast Dashboard" << 'EOF'
#!/bin/bash
# Quick check if running, if not start it
if ! curl -s http://localhost:8501 > /dev/null 2>&1; then
    cd /Users/markbaumrind/Desktop/email_podcast_agent
    streamlit run app.py --server.headless true &
    sleep 2
fi
open http://localhost:8501
EOF

chmod +x "${APP_PATH}/Contents/MacOS/Email Podcast Dashboard"

# Create Info.plist for Applications folder
cat > "${APP_PATH}/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Email Podcast Dashboard</string>
    <key>CFBundleIdentifier</key>
    <string>com.local.email-podcast-dashboard</string>
    <key>CFBundleName</key>
    <string>Email Podcast Dashboard</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF

echo "✅ Created app in Applications folder!"
echo "🔍 Open Spotlight (Cmd+Space) and type 'Email Podcast Dashboard'"
