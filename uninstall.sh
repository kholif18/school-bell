# uninstall.sh
#!/bin/bash

set -e

APP_DIR="/opt/school-bell"
DESKTOP_FILE="/usr/share/applications/school-bell.desktop"
LAUNCHER_LINK="/usr/bin/school-bell"

echo "🗑️ Uninstalling School Bell Automation..."

sudo rm -f "$DESKTOP_FILE"
sudo rm -f "$LAUNCHER_LINK"
sudo rm -rf "$APP_DIR"

rm -f ~/.config/autostart/school-bell.desktop

echo "✅ Uninstall complete!"