#!/bin/bash

set -e

APP_NAME="SchoolBell"
APPDIR="${APP_NAME}.AppDir"

echo "======================================"
echo "🔔 BUILD APPIMAGE - ${APP_NAME}"
echo "======================================"

# =====================================================
# CLEAN
# =====================================================

echo "🧹 Cleaning old build..."

rm -rf build dist *.spec "${APPDIR}"
rm -f ./*.AppImage

# =====================================================
# CREATE APPDIR STRUCTURE
# =====================================================

mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

# =====================================================
# PYINSTALLER BUILD
# =====================================================

echo "⚙️ Running PyInstaller..."

pyinstaller main.py \
  --name "${APP_NAME}" \
  --noconfirm \
  --clean \
  --windowed \
  --add-data "assets:assets" \
  --add-data "apps/desktop/styles:apps/desktop/styles" \
  --add-data "apps/web/templates:apps/web/templates" \
  --add-data "apps/web/static:apps/web/static"

# =====================================================
# COPY BUILD
# =====================================================

echo "📦 Copying files..."

cp -r "dist/${APP_NAME}/"* "${APPDIR}/usr/bin/"

# =====================================================
# DESKTOP ENTRY
# =====================================================

cat > "${APPDIR}/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Name=School Bell
Exec=${APP_NAME}
Icon=${APP_NAME}
Type=Application
Categories=Utility;
Terminal=false
StartupNotify=true
EOF

cp "${APPDIR}/${APP_NAME}.desktop" \
"${APPDIR}/usr/share/applications/"

# =====================================================
# ICON
# =====================================================

cp assets/icon/schoolbell.png \
"${APPDIR}/${APP_NAME}.png"

cp assets/icon/schoolbell.png \
"${APPDIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"

# =====================================================
# APPRUN
# =====================================================

cat > "${APPDIR}/AppRun" << 'EOF'
#!/bin/bash

HERE="$(dirname "$(readlink -f "${0}")")"

export PATH="${HERE}/usr/bin:${PATH}"

exec "${HERE}/usr/bin/SchoolBell" "$@"
EOF

chmod +x "${APPDIR}/AppRun"

# =====================================================
# DOWNLOAD APPIMAGETOOL
# =====================================================

if [ ! -f "appimagetool.AppImage" ]; then
    echo "⬇ Downloading appimagetool..."

    wget -O appimagetool.AppImage \
    https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage

    chmod +x appimagetool.AppImage
fi

# =====================================================
# BUILD APPIMAGE
# =====================================================

echo "🚀 Creating AppImage..."

ARCH=x86_64 ./appimagetool.AppImage "${APPDIR}"

echo ""
echo "✅ BUILD SUCCESS!"
echo ""
echo "📦 AppImage generated:"
ls -lah *.AppImage