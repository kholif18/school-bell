# core/paths.py
from pathlib import Path
import sys
import os


class Paths:
    """
    Centralized application paths

    Design goals:
    - No hardcoded string path scattered
    - Works for dev + bundled (PyInstaller)
    - Single source of truth for filesystem structure
    """

    def __init__(self):
        self.BASE_DIR = self._get_base_dir()
        self.RESOURCE_DIR = self._get_resource_dir()

        # =========================
        # WRITABLE
        # =========================

        self.DB_DIR = self.BASE_DIR / "db"
        self.LOG_DIR = self.BASE_DIR / "logs"
        self.CONFIG_FILE = self.BASE_DIR / "config.json"

        # =========================
        # READONLY RESOURCES
        # =========================

        self.ASSETS_DIR = self.RESOURCE_DIR / "assets"
        self.ICON_DIR = self.ASSETS_DIR / "icon"

        self.AUDIO_DIR = self.ASSETS_DIR / "audio"
        self.DEFAULT_AUDIO = self.AUDIO_DIR / "default_bell.wav"

        # backward compatibility aliases
        self.base_dir = self.BASE_DIR
        self.db_dir = self.DB_DIR
        self.icon_dir = self.ICON_DIR
        self.log_dir = self.LOG_DIR
        self.assets_dir = self.ASSETS_DIR

        self.config_file = self.CONFIG_FILE
        self.audio_dir = self.AUDIO_DIR
        self.default_audio = self.DEFAULT_AUDIO

    # =========================
    # BASE DIR RESOLUTION
    # =========================

    def _get_base_dir(self) -> Path:
        """
        Writable app data directory
        """

        # =========================
        # APPIMAGE / PYINSTALLER
        # =========================

        if getattr(sys, "frozen", False):

            # Linux AppImage
            if sys.platform.startswith("linux"):
                return Path.home() / ".local/share/SchoolBell"

            # Windows EXE
            if sys.platform.startswith("win"):
                return Path(os.getenv("APPDATA")) / "SchoolBell"

        # =========================
        # DEVELOPMENT
        # =========================

        return Path(__file__).resolve().parent.parent

    def _get_resource_dir(self) -> Path:
        """
        Readonly bundled resources
        """

        # =========================
        # PYINSTALLER / APPIMAGE
        # =========================

        if getattr(sys, "frozen", False):

            # PyInstaller temporary extraction dir
            if hasattr(sys, "_MEIPASS"):
                return Path(sys._MEIPASS)

            return Path(sys.executable).parent

        # =========================
        # DEVELOPMENT
        # =========================

        return Path(__file__).resolve().parent.parent
        
    # =========================
    # HELPERS
    # =========================

    def ensure_dirs(self):
        """Create required directories safely"""
        for path in [
            self.DB_DIR,
            self.LOG_DIR,
            self.AUDIO_DIR,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    # =========================
    # PATH HELPERS
    # =========================

    def db_path(self, filename: str = "school_bell.db") -> Path:
        return self.DB_DIR / filename

    def log_path(self, filename: str = "app.log") -> Path:
        return self.LOG_DIR / filename

    def audio_path(self, filename: str) -> Path:
        return self.AUDIO_DIR / filename


# =========================
# SINGLETON
# =========================

_paths = None


def get_paths() -> Paths:
    global _paths
    if _paths is None:
        _paths = Paths()
        _paths.ensure_dirs()
    return _paths


# backward compatibility (optional)
paths = get_paths()