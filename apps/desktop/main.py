# apps/desktop/main.py
import sys
from PyQt6.QtWidgets import QApplication

from core.app import CoreApp
from apps.desktop.main_window import MainWindow
from apps.desktop.tray_icon import TrayIcon


def run():
    backend = CoreApp()
    backend.initialize()

    qt = QApplication(sys.argv)

    window = MainWindow(backend)
    tray = TrayIcon(qt, window)

    window.show()

    sys.exit(qt.exec())


if __name__ == "__main__":
    run()