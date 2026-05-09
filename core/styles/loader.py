from pathlib import Path
import sys


def resource_path(relative_path: str) -> Path:
    """
    Support development + PyInstaller
    """

    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    return Path(__file__).resolve().parent.parent.parent / relative_path


def load_stylesheet(filename: str) -> str:
    """
    Load QSS stylesheet safely
    """

    path = resource_path(
        f"apps/desktop/styles/{filename}"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Style not found: {path}"
        )

    return path.read_text(encoding="utf-8")