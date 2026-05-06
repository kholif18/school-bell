# core/paths.py
from pathlib import Path
import sys


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

        self.DB_DIR = self.BASE_DIR / "db"
        self.LOG_DIR = self.BASE_DIR / "logs"
        self.ASSETS_DIR = self.BASE_DIR / "assets"
        self.CONFIG_FILE = self.BASE_DIR / "config.json"

        self.AUDIO_DIR = self.ASSETS_DIR / "audio"
        self.DEFAULT_AUDIO = self.AUDIO_DIR / "default_bell.wav"

        # backward compatibility aliases
        self.base_dir = self.BASE_DIR
        self.db_dir = self.DB_DIR
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
        Support:
        - normal python run
        - PyInstaller bundled app
        """
        if getattr(sys, "frozen", False):
            return Path(sys.executable).parent

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