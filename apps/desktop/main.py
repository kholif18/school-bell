import sys
from PyQt6.QtWidgets import QApplication

from core.app import CoreApp
from apps.desktop.main_window import MainWindow
from apps.desktop.tray_icon import TrayIcon


def run():
    qt = QApplication(sys.argv)

    backend = CoreApp()
    backend.initialize()

    window = MainWindow(backend)

    backend.desktop_window = window

    tray = TrayIcon(qt, window, backend)

    window.show()

    sys.exit(qt.exec())


if __name__ == "__main__":
    run()