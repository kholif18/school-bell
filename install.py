import os
import sys
import platform
import subprocess
import shutil

def run(cmd):
    print(f"> {cmd}")
    subprocess.run(cmd, shell=True, check=False)

def detect_linux_package_manager():
    managers = ['pacman', 'apt', 'dnf', 'yum', 'zypper']
    for m in managers:
        if shutil.which(m):
            return m
    return None

def install_linux_dependencies():
    pm = detect_linux_package_manager()

    if pm == 'pacman':
        run('sudo pacman -Sy --noconfirm python python-pip git sdl2_mixer qt6-base')
    elif pm == 'apt':
        run('sudo apt update')
        run('sudo apt install -y python3 python3-pip python3-venv git libsdl2-mixer-2.0-0 qt6-base-dev')
    elif pm == 'dnf':
        run('sudo dnf install -y python3 python3-pip git SDL2_mixer qt6-qtbase')
    elif pm == 'yum':
        run('sudo yum install -y python3 python3-pip git SDL2_mixer qt6-qtbase')
    elif pm == 'zypper':
        run('sudo zypper install -y python3 python3-pip git libSDL2_mixer-2_0-0 qt6-base')
    else:
        print("Unsupported Linux package manager. Please install dependencies manually.")

def install_windows_dependencies():
    print("Windows detected.")
    print("Please ensure Python 3.13 is installed.")
    run('python -m venv venv')
    run(r'venv\\Scripts\\pip install --upgrade pip')
    run(r'venv\\Scripts\\pip install -r requirements.txt')

def install_common():
    if not os.path.exists('venv'):
        run(f'{sys.executable} -m venv venv')

    if platform.system() == 'Windows':
        pip = r'venv\\Scripts\\pip'
    else:
        pip = 'venv/bin/pip'

    run(f'{pip} install --upgrade pip')
    run(f'{pip} install -r requirements.txt')

    os.makedirs('db', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('assets/audio', exist_ok=True)

def main():
    system = platform.system()

    print("===================================")
    print(" SCHOOL BELL UNIVERSAL INSTALLER")
    print("===================================")

    if system == 'Linux':
        install_linux_dependencies()
    elif system == 'Windows':
        install_windows_dependencies()

    install_common()

    print("===================================")
    print(" INSTALLATION COMPLETE")
    print("===================================")

if __name__ == "__main__":
    main()
