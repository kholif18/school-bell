from PyQt6.QtWidgets import QApplication
from core.paths import get_paths
from core.styles.loader import load_stylesheet

class ThemeManager:
    def __init__(self):
        self.paths = get_paths()
        self.current_theme = "dark"

    def apply(self, theme="dark"):
        self.current_theme = theme

        file = "main_dark.qss" if theme == "dark" else "main_light.qss"

        style = load_stylesheet(
            self.paths.base_dir / f"apps/desktop/styles/{file}"
        )

        # 🔥 INI WAJIB GLOBAL
        app = QApplication.instance()
        app.setStyleSheet(style)

    def toggle(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply(new_theme)
        return new_theme