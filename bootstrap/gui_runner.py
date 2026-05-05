# bootstrap/gui_runner.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from core.app_core import get_app
from desktop.main_window import MainWindow
from core.path_helper import app_path

def run_gui():
    """Run desktop GUI mode - client only, no scheduler"""
    # Get app instance as client (not master)
    app = get_app()
    app.initialize(is_master=False)  # Client mode - tidak start scheduler
    app.start_web(port=5000)  # Web untuk monitoring

    qt_app = QApplication(sys.argv)
    qt_app.setQuitOnLastWindowClosed(False)
    qt_app.setStyle("Fusion")

    icon_path = app_path("assets", "icon", "schoolbell.png")
    if os.path.exists(icon_path):
        qt_app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    sys.exit(qt_app.exec())