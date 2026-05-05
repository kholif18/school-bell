# bootstrap/tray_runner.py
import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtGui import QIcon
from core.app_core import get_app
from apps.desktop.tray_icon import TrayIcon
from core.paths import app_path

def run_tray():
    """Run system tray mode - client only, no scheduler"""
    # Get app instance as client (not master)
    app = get_app()
    app.initialize(is_master=False)  # Client mode - tidak start scheduler
    app.start_web(port=5000)  # Web untuk monitoring

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