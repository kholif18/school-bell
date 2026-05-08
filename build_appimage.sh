#!/bin/bash

set -e

APP_NAME="SchoolBell"
APPDIR="$APP_NAME.AppDir"

echo "======================================"
echo "🔔 BUILD APPIMAGE - $APP_NAME"
echo "======================================"

# =====================================================
# CLEAN
# =====================================================

rm -rf build dist *.spec $APPDIR

mkdir -p $APPDIR/usr/bin
mkdir -p $APPDIR/usr/lib
mkdir -p $APPDIR/usr/share/icons

# =====================================================
# PYINSTALLER BUILD
# =====================================================

echo "⚙️ Running PyInstaller..."

pyinstaller main.py \
--name $APP_NAME \
--noconfirm \
--clean \
--windowed \
--add-data "assets:assets" \
--add-data "apps/desktop/styles:apps/desktop/styles" \
--add-data "apps/web/templates:apps/web/templates" \
--add-data "apps/web/static:apps/web/static"

# =====================================================
# COPY RESULT TO APPDIR
# =====================================================

echo "📦 Copying build to AppDir..."

cp -r dist/$APP_NAME/* $APPDIR/usr/bin/

# =====================================================
# APPRUN (WAJIB)
# =====================================================

cat > $APPDIR/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "$HERE/usr/bin/SchoolBell" "$@"
EOF

chmod +x $APPDIR/AppRun

# =====================================================
# DESKTOP FILE
# =====================================================

cat > $APPDIR/SchoolBell.desktop << EOF
[Desktop Entry]
Name=School Bell
Exec=SchoolBell
Icon=SchoolBell
Type=Application
Categories=Utility;
EOF

# =====================================================
# ICON
# =====================================================

cp assets/icon/schoolbell.png $APPDIR/SchoolBell.png

# =====================================================
# BUILD APPIMAGE
# =====================================================

echo "🚀 Creating AppImage..."

./appimagetool-x86_64.AppImage $APPDIR

echo "======================================"
echo "✅ APPIMAGE BUILD COMPLETE"
echo "======================================"