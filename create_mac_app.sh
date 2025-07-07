#!/bin/bash
# Create a macOS app for Email-to-Podcast

echo "📱 Creating Email-to-Podcast App..."

# Create app structure
APP_NAME="Email to Podcast"
APP_DIR="$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Create directories
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.emailtopodcast.app</string>
    <key>CFBundleName</key>
    <string>Email to Podcast</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

# Create launcher script
cat > "$MACOS_DIR/launcher" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/../../../"
/usr/bin/python3 desktop_app.py
EOF

# Make launcher executable
chmod +x "$MACOS_DIR/launcher"

# Create app icon (placeholder)
echo "🎨 Note: Add an icon file at $RESOURCES_DIR/icon.icns for a custom icon"

echo "✅ macOS app created: $APP_DIR"
echo ""
echo "To use:"
echo "1. Double-click '$APP_DIR' to launch"
echo "2. Drag to Applications folder for permanent installation"
echo ""
echo "Or run directly:"
echo "python3 desktop_app.py"
