# bootstrap/gui_runner.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from bootstrap.app_runtime import boot_runtime
from desktop.main_window import MainWindow
from core.path_helper import app_path

def run_gui():
    """Run desktop GUI mode - attaches to existing engine if available"""
    boot_runtime()

    qt_app = QApplication(sys.argv)
    qt_app.setQuitOnLastWindowClosed(False)
    qt_app.setStyle("Fusion")

    icon_path = app_path("assets", "icon", "schoolbell.png")
    if os.path.exists(icon_path):
        qt_app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    sys.exit(qt_app.exec())