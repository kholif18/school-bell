#!/bin/bash

echo "======================================"
echo " SCHOOL BELL AUTOMATION INSTALLER"
echo "======================================"

PROJECT_DIR="$HOME/school-bell"

echo "[1/6] Installing system dependencies..."
sudo pacman -Sy --noconfirm python python-pip git sdl2_mixer qt6-base

echo "[2/6] Creating virtual environment..."
python -m venv venv

echo "[3/6] Activating virtualenv..."
source venv/bin/activate

echo "[4/6] Installing python requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[5/6] Creating required directories..."
mkdir -p db logs assets/audio

echo "[6/6] Setting executable permissions..."
chmod +x start.sh
chmod +x service/install_service.sh

echo ""
echo "======================================"
echo " INSTALLATION SUCCESS"
echo "======================================"
echo "Run application using:"
echo "./start.sh"
