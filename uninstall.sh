#!/bin/bash

echo "🗑 Removing School Bell..."

sudo rm -rf /opt/school-bell
sudo rm -f /usr/share/applications/school-bell.desktop
sudo rm -f /usr/bin/school-bell
rm -f ~/.config/autostart/school-bell.desktop

echo "✅ Uninstalled successfully"