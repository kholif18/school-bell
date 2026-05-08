#!/bin/bash

set -e

APP_NAME="School Bell Automation"
APP_DIR="/opt/school-bell"
DESKTOP_FILE="/usr/share/applications/school-bell.desktop"
LAUNCHER_LINK="/usr/bin/school-bell"

echo "🗑️ Uninstalling $APP_NAME..."

# =========================================================
# STOP RUNNING APP
# =========================================================

echo "🛑 Stopping running application..."

pkill -f "$APP_DIR" || true

# =========================================================
# REMOVE FILES
# =========================================================

echo "🧹 Removing application files..."

sudo rm -f "$DESKTOP_FILE"
sudo rm -f "$LAUNCHER_LINK"
sudo rm -rf "$APP_DIR"

# =========================================================
# REMOVE AUTOSTART
# =========================================================

echo "⚡ Removing autostart..."

rm -f ~/.config/autostart/school-bell.desktop

# =========================================================
# UPDATE DESKTOP CACHE
# =========================================================

echo "🔄 Updating desktop database..."

sudo update-desktop-database || true

# =========================================================
# DONE
# =========================================================

echo ""
echo "✅ Uninstall complete!"