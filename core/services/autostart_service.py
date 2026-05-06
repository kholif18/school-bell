import os
import sys
from pathlib import Path
import platform


class AutoStartService:
    """
    Handle OS-level autostart (Linux + Windows)
    """

    def __init__(self, app_name="School Bell", entry_file="main.py"):
        self.app_name = app_name
        self.entry_file = entry_file

    # =====================================================
    # PUBLIC API
    # =====================================================

    def enable(self):
        system = platform.system().lower()

        if system == "linux":
            self._enable_linux()
        elif system == "windows":
            self._enable_windows()
        else:
            raise NotImplementedError(f"Autostart not supported: {system}")

    def disable(self):
        system = platform.system().lower()

        if system == "linux":
            self._disable_linux()
        elif system == "windows":
            self._disable_windows()
        else:
            raise NotImplementedError(f"Autostart not supported: {system}")

    # =====================================================
    # LINUX
    # =====================================================

    def _enable_linux(self):
        autostart_dir = Path.home() / ".config/autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)

        desktop_file = autostart_dir / "school-bell.desktop"

        app_path = os.path.abspath(self.entry_file)

        content = f"""[Desktop Entry]
Type=Application
Name={self.app_name}
Exec=python3 {app_path}
X-GNOME-Autostart-enabled=true
"""

        desktop_file.write_text(content)

    def _disable_linux(self):
        file = Path.home() / ".config/autostart/school-bell.desktop"

        if file.exists():
            file.unlink()

    # =====================================================
    # WINDOWS
    # =====================================================

    def _enable_windows(self):
        startup_dir = Path(os.getenv("APPDATA")) / \
            "Microsoft/Windows/Start Menu/Programs/Startup"

        startup_dir.mkdir(parents=True, exist_ok=True)

        bat_file = startup_dir / "SchoolBell.bat"

        app_path = os.path.abspath(self.entry_file)

        content = f'@echo off\npython "{app_path}"\n'

        bat_file.write_text(content)

    def _disable_windows(self):
        startup_dir = Path(os.getenv("APPDATA")) / \
            "Microsoft/Windows/Start Menu/Programs/Startup"

        file = startup_dir / "SchoolBell.bat"

        if file.exists():
            file.unlink()