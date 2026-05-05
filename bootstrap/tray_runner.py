# bootstrap/tray_runner.py
import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtGui import QIcon
from bootstrap.app_runtime import boot_runtime
from desktop.tray_icon import TrayIcon
from core.path_helper import app_path

def run_tray():
    """Run system tray mode - attaches to existing engine if available"""
    boot_runtime()

    qt_app = QApplication(sys.argv)
    qt_app.setQuitOnLastWindowClosed(False)

    icon_path = app_path("assets", "icon", "schoolbell.png")
    if os.path.exists(icon_path):
        qt_app.setWindowIcon(QIcon(icon_path))

    tray = TrayIcon()
    tray.show()

    # Show startup notification
    tray.show_notification(
        "School Bell System",
        "Application running in system tray",
        QSystemTrayIcon.MessageIcon.Information
    )

    sys.exit(qt_app.exec())