#!/bin/bash

set -e

APP_NAME="School Bell Automation"
APP_DIR="/opt/school-bell"
BIN_NAME="school-bell"
DESKTOP_FILE="/usr/share/applications/school-bell.desktop"
LAUNCHER_LINK="/usr/bin/school-bell"

echo "🔔 Installing $APP_NAME ..."

# 1. Copy project
sudo mkdir -p $APP_DIR
sudo cp -r ../* $APP_DIR

# 2. Permission
sudo chmod -R 755 $APP_DIR

# 3. Create symlink (global command)
sudo ln -sf $APP_DIR/main.py $LAUNCHER_LINK

# 4. Desktop entry (launcher icon)
cat <<EOF | sudo tee $DESKTOP_FILE > /dev/null
[Desktop Entry]
Name=School Bell Automation
Comment=Automatic School Bell System
Exec=python3 $APP_DIR/main.py
Icon=$APP_DIR/assets/icon/schoolbell.png
Terminal=false
Type=Application
Categories=Utility;Education;
StartupNotify=true
EOF

# 5. Auto start (GNOME / XFCE compatible)
mkdir -p ~/.config/autostart

cat <<EOF > ~/.config/autostart/school-bell.desktop
[Desktop Entry]
Type=Application
Exec=python3 $APP_DIR/main.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=School Bell
Comment=Auto start School Bell system
EOF

echo "✅ Installation complete!"
echo "👉 Run with: school-bell"