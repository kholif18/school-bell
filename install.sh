#!/bin/bash

set -e

APP_NAME="School Bell Automation"
APP_DIR="/opt/school-bell"
BIN_NAME="school-bell"
DESKTOP_FILE="/usr/share/applications/school-bell.desktop"
LAUNCHER_LINK="/usr/bin/$BIN_NAME"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "🔔 Installing $APP_NAME ..."

# =========================================================
# CHECK DEPENDENCIES
# =========================================================

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found"
    exit 1
fi

if ! command -v rsync &> /dev/null; then
    echo "❌ rsync not found"
    exit 1
fi

if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "❌ python3-venv not installed"
    echo "Install with:"
    echo "sudo apt install python3-venv"
    exit 1
fi

# =========================================================
# CREATE APP DIR
# =========================================================

echo "📁 Creating application directory..."

sudo mkdir -p "$APP_DIR"

# =========================================================
# COPY PROJECT
# =========================================================

echo "📦 Copying project files..."

echo "SCRIPT_DIR=$SCRIPT_DIR"
echo "PROJECT_DIR=$PROJECT_DIR"

sudo rsync -a \
    --exclude "__pycache__" \
    --exclude "*.pyc" \
    --exclude ".git" \
    --exclude "venv" \
    --exclude "dist" \
    --exclude "build" \
    "$PROJECT_DIR"/ "$APP_DIR"/

# =========================================================
# CREATE VENV
# =========================================================

echo "🐍 Creating virtual environment..."

if [ ! -d "$APP_DIR/venv" ]; then
    sudo python3 -m venv "$APP_DIR/venv"
fi

# =========================================================
# FIX OWNERSHIP
# =========================================================

echo "🔐 Setting ownership..."

sudo chown -R $USER:$USER "$APP_DIR"

# =========================================================
# PERMISSIONS
# =========================================================

echo "🔐 Setting permissions..."

find "$APP_DIR" \
    -path "$APP_DIR/venv" -prune -o \
    -type d -exec chmod 755 {} \;
find "$APP_DIR" \
    -path "$APP_DIR/venv" -prune -o \
    -type f -exec chmod 644 {} \;

chmod +x "$APP_DIR/install.sh"
chmod +x "$APP_DIR/uninstall.sh"
# =========================================================
# INSTALL DEPENDENCIES
# =========================================================

echo "📥 Installing dependencies..."

"$APP_DIR/venv/bin/pip" install --upgrade pip

if [ -f "$APP_DIR/requirements.txt" ]; then
    "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"
else
    echo "⚠️ requirements.txt not found"
fi

# =========================================================
# CREATE RUNNER
# =========================================================

echo "🚀 Creating launcher script..."

cat <<EOF > "$APP_DIR/run.sh"
#!/bin/bash

cd "$APP_DIR"

exec "$APP_DIR/venv/bin/python" main.py
EOF

chmod +x "$APP_DIR/run.sh"

# =========================================================
# GLOBAL COMMAND
# =========================================================

echo "🔗 Creating global launcher..."

sudo ln -sf "$APP_DIR/run.sh" "$LAUNCHER_LINK"

# =========================================================
# DESKTOP ENTRY
# =========================================================

echo "🖥️ Creating desktop launcher..."

cat <<EOF | sudo tee "$DESKTOP_FILE" > /dev/null
[Desktop Entry]
Version=1.0
Type=Application
Name=School Bell Automation
Comment=Automatic School Bell System
Exec=$APP_DIR/run.sh
Icon=$APP_DIR/assets/icon/schoolbell.png
Terminal=false
Categories=Education;Utility;
StartupNotify=true
EOF

sudo chmod 644 "$DESKTOP_FILE"

# =========================================================
# AUTOSTART
# =========================================================

echo "⚡ Creating autostart entry..."

mkdir -p ~/.config/autostart

ln -sf "$DESKTOP_FILE" \
    ~/.config/autostart/school-bell.desktop

# =========================================================
# POST INSTALL
# =========================================================

echo "🔄 Updating desktop database..."

sudo update-desktop-database || true
sudo gtk-update-icon-cache >/dev/null 2>&1 || true

echo "📁 Ensuring audio directory exists..."

mkdir -p "$APP_DIR/assets/audio"

echo ""
echo "🌐 Web dashboard:"
echo "👉 http://YOUR-IP:5000"
echo ""

# =========================================================
# DONE
# =========================================================

echo ""
echo "✅ Installation complete!"
echo ""

echo "Run application:"
echo "👉 school-bell"
echo ""

echo "Installed at:"
echo "👉 $APP_DIR"