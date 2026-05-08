from PyQt6.QtWidgets import QApplication
from core.styles.loader import load_stylesheet

class ThemeManager:
    def __init__(self):
        self.current_theme = "dark"

    def apply(self, theme="dark"):
        self.current_theme = theme

        file = "main_dark.qss" if theme == "dark" else "main_light.qss"

        # ❗ FIX: jangan kirim path manual lagi
        style = load_stylesheet(file)

        app = QApplication.instance()
        if app:
            app.setStyleSheet(style)

    def toggle(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply(new_theme)
        return new_theme