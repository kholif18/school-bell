# core/path_helper.py
from pathlib import Path
import sys

def get_base_dir():
    """Get base directory (works for both script and frozen executable)"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()

def app_path(*paths):
    """Get absolute path relative to application root"""
    return str(BASE_DIR.joinpath(*paths))

# Common paths
DB_PATH = app_path("db", "school_bell.db")
LOG_PATH = app_path("logs", "school_bell.log")
CONFIG_PATH = app_path("config.json")
DEFAULT_AUDIO_PATH = app_path("assets", "audio", "default_bell.wav")
AUDIO_DIR = app_path("assets", "audio")