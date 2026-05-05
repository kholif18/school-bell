import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
USER_HOME = Path.home()
APP_NAME = "School Bell Automation"

if platform.system() == "Windows":
    PYTHON_BIN = PROJECT_DIR / "venv" / "Scripts" / "python.exe"
else:
    PYTHON_BIN = PROJECT_DIR / "venv" / "bin" / "python"

MAIN_FILE = PROJECT_DIR / "main.py"

def run(cmd):
    print(f"> {cmd}")
    subprocess.run(cmd, shell=True, check=False)

# ---------------------------------------------------
# PACKAGE MANAGER DETECTION
# ---------------------------------------------------
def detect_package_manager():
    for pm in ["pacman", "apt", "dnf", "yum", "zypper"]:
        if shutil.which(pm):
            return pm
    return None

def install_linux_dependencies():
    pm = detect_package_manager()

    if pm == "pacman":
        run("sudo pacman -Sy --noconfirm python python-pip python-virtualenv git sdl2_mixer qt6-base")
    elif pm == "apt":
        run("sudo apt update")
        run("sudo apt install -y python3 python3-pip python3-venv git libsdl2-mixer-2.0-0 qt6-base-dev")
    elif pm == "dnf":
        run("sudo dnf install -y python3 python3-pip git SDL2_mixer qt6-qtbase")
    elif pm == "yum":
        run("sudo yum install -y python3 python3-pip git SDL2_mixer qt6-qtbase")
    elif pm == "zypper":
        run("sudo zypper install -y python3 python3-pip git libSDL2_mixer-2_0-0 qt6-base")
    else:
        print("Unsupported package manager. Please install dependencies manually.")

# ---------------------------------------------------
# PYTHON ENV
# ---------------------------------------------------
def setup_python_env():
    venv_dir = PROJECT_DIR / "venv"

    if not venv_dir.exists():
        run(f"{sys.executable} -m venv {venv_dir}")

    if platform.system() == "Windows":
        pip = venv_dir / "Scripts" / "pip.exe"
    else:
        pip = venv_dir / "bin" / "pip"

    run(f"{pip} install --upgrade pip")
    run(f"{pip} install -r requirements.txt")
    run(f"{pip} install pyinstaller")

# ---------------------------------------------------
# RUNTIME DIRS
# ---------------------------------------------------
def create_runtime_dirs():
    os.makedirs(PROJECT_DIR / "db", exist_ok=True)
    os.makedirs(PROJECT_DIR / "logs", exist_ok=True)
    os.makedirs(PROJECT_DIR / "assets/audio", exist_ok=True)

# ---------------------------------------------------
# DESKTOP LAUNCHER
# ---------------------------------------------------
def create_desktop_launcher():
    if platform.system() != "Linux":
        return

    app_dir = USER_HOME / ".local/share/applications"
    autostart_dir = USER_HOME / ".config/autostart"
    icon_path = PROJECT_DIR / "assets" / "icon" / "schoolbell.png"

    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(autostart_dir, exist_ok=True)
    
    gui_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={APP_NAME}
Comment=Automated School Bell Management System
Exec="{PYTHON_BIN}" "{MAIN_FILE}"
Icon={icon_path}
Terminal=false
Categories=Education;Utility;
StartupNotify=true
"""
    
    # TRAY Launcher (autostart - minimize to tray)
    tray_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={APP_NAME} (Tray)
Comment=School Bell System Tray
Exec="{PYTHON_BIN}" "{MAIN_FILE}" --tray
Icon={icon_path}
Terminal=false
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""

    launcher_gui = app_dir / "schoolbell.desktop"
    launcher_tray = autostart_dir / "schoolbell-tray.desktop"

    with open(launcher_gui, "w") as f:
        f.write(gui_content)

    with open(launcher_tray, "w") as f:
        f.write(tray_content)

    os.chmod(launcher_gui, 0o755)
    os.chmod(launcher_tray, 0o755)

    print("Desktop launcher installed.")
    print("Tray autostart on login enabled.")

# ---------------------------------------------------
# SYSTEMD SERVICE
# ---------------------------------------------------
def create_systemd_service():
    if platform.system() != "Linux":
        return

    service_content = f"""[Unit]
Description=School Bell Automation Background Service
After=network.target sound.target

[Service]
Type=simple
User={os.getenv('USER')}
WorkingDirectory={PROJECT_DIR}
ExecStart={PYTHON_BIN} {MAIN_FILE} --headless
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

    temp_service = PROJECT_DIR / "schoolbell.service"

    with open(temp_service, "w") as f:
        f.write(service_content)

    run(f"sudo cp {temp_service} /etc/systemd/system/schoolbell.service")
    run("sudo systemctl daemon-reload")
    run("sudo systemctl enable schoolbell.service")

    print("Background boot service installed.")

# ---------------------------------------------------
# WINDOWS SHORTCUT (later)
# ---------------------------------------------------
def create_windows_shortcut():
    if platform.system() != "Windows":
        return
    print("Windows shortcut installer can be added later.")

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------
def main():
    print("======================================")
    print(" SCHOOL BELL UNIVERSAL INSTALLER")
    print("======================================")

    if platform.system() == "Linux":
        install_linux_dependencies()

    setup_python_env()
    create_runtime_dirs()
    create_desktop_launcher()
    create_systemd_service()
    create_windows_shortcut()

    print("======================================")
    print(" INSTALLATION COMPLETE")
    print("======================================")
    print("Application launcher created.")
    print("Background autostart enabled.")
    print("")
    print("Run GUI:")
    print(f"{PYTHON_BIN} {MAIN_FILE}")
    print("")
    print("Run Headless:")
    print(f"{PYTHON_BIN} {MAIN_FILE} --headless")

if __name__ == "__main__":
    main()