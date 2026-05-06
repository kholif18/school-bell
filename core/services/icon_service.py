from PyQt6.QtGui import QIcon
from pathlib import Path

class IconService:
    def __init__(self):
        self.base = Path("assets/icon")

    def get(self, name: str) -> QIcon:
        return QIcon(str(self.base / name))