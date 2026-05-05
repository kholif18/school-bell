# apps/desktop/main.py
import sys
from PyQt6.QtWidgets import QApplication

from apps.desktop.main_window import MainWindow
from apps.desktop.tray_icon import TrayIcon


def run():
    app = QApplication(sys.argv)

    window = MainWindow()
    tray = TrayIcon(app, window)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run()