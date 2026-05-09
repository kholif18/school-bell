import sys
from pathlib import Path


def resource_path(relative_path):
    """
    Support dev + PyInstaller
    """

    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    return Path(relative_path)