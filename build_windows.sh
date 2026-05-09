#!/bin/bash

set -e

APP_NAME="SchoolBell"
ENTRY_FILE="main.py"

echo "======================================"
echo "🔔 BUILDING $APP_NAME (PRODUCTION)"
echo "======================================"

# =========================================================
# 1. CLEAN OLD BUILD
# =========================================================

echo "🧹 Cleaning old build artifacts..."

rm -rf build dist __pycache__ *.spec

find . -type d -name "__pycache__" -exec rm -rf {} +

echo "✔ Clean completed"

# =========================================================
# 2. ENSURE REQUIRED FOLDERS EXIST
# =========================================================

echo "📁 Ensuring runtime folders exist..."

mkdir -p db
mkdir -p logs

# =========================================================
# 3. BUILD WITH PYINSTALLER
# =========================================================

echo "⚙️ Running PyInstaller..."

pyinstaller $ENTRY_FILE \
--name $APP_NAME \
--noconfirm \
--clean \
--windowed \
--add-data "assets;assets" \
--add-data "apps/desktop/styles;apps/desktop/styles" \
--add-data "apps/web/templates;apps/web/templates" \
--add-data "apps/web/static;apps/web/static" \
--add-data "db;db" \
--add-data "logs;logs"

# =========================================================
# 4. POST BUILD CHECK
# =========================================================

echo "🔍 Checking build output..."

if [ -f "dist/$APP_NAME/$APP_NAME.exe" ] || [ -f "dist/$APP_NAME/$APP_NAME" ]; then
    echo "======================================"
    echo "✅ BUILD SUCCESS!"
    echo "📦 Output: dist/$APP_NAME/"
    echo "======================================"
else
    echo "❌ BUILD FAILED!"
    exit 1
fi