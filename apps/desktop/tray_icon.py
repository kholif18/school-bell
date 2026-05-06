import os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QStyle
from core.paths import get_paths


class TrayIcon(QSystemTrayIcon):

    def __init__(self, qt_app, window, app_core):
        super().__init__(window)

        self.qt_app = qt_app
        self.window = window
        self.app = app_core

        self.app.events.on("SYSTEM_STARTED", lambda _: self.refresh_state())
        self.app.events.on("SYSTEM_STOPPED", lambda _: self.refresh_state())
        self.app.events.on("BELL_TRIGGERED", lambda p: self.on_bell(p))
        self.app.events.on("BELL_TRIGGERED", lambda payload: self.on_bell(payload))

        paths = get_paths()

        icon_file = paths.icon_dir / "schoolbell.png"
        icon = QIcon(str(icon_file))

        if icon.isNull():
            print("❌ ICON FAILED TO LOAD")
            icon = self.window.style().standardIcon(
                QStyle.StandardPixmap.SP_ComputerIcon
            )

        self.setIcon(icon)
        self.setToolTip("School Bell Automation")

        self._build_menu()

        self.refresh_state()

        self.show()

    # =========================
    # MENU
    # =========================

    def _build_menu(self):
        menu = QMenu()

        self.show_action = QAction(
            self.window.style().standardIcon(QStyle.StandardPixmap.SP_DesktopIcon),
            "Show"
        )

        self.hide_action = QAction(
            self.window.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarShadeButton),
            "Hide"
        )

        self.toggle_system_action = QAction(
            self.window.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay),
            "Start System"
        )

        self.quit_action = QAction(
            self.window.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton),
            "Quit"
        )

        self.show_action.triggered.connect(self.show_window)
        self.hide_action.triggered.connect(self.hide_window)

        self.toggle_system_action.triggered.connect(self.toggle_system)
        self.quit_action.triggered.connect(self.quit_app)

        menu.addAction(self.show_action)
        menu.addAction(self.hide_action)
        menu.addSeparator()
        menu.addAction(self.toggle_system_action)
        menu.addSeparator()
        menu.addAction(self.quit_action)

        self.setContextMenu(menu)

    # =========================
    # ACTIONS
    # =========================

    def toggle_system(self):
        if self.app.is_running():
            self.app.stop_system()
            self.toggle_system_action.setText("Start System")
        else:
            self.app.start_system()
            self.toggle_system_action.setText("Stop System")

    def refresh_state(self):
        if self.app.is_running():
            self.toggle_system_action.setText("Stop System")
            self.toggle_system_action.setIcon(
                self.window.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
            )
        else:
            self.toggle_system_action.setText("Start System")
            self.toggle_system_action.setIcon(
                self.window.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )
            
    def show_window(self):
        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()

    def hide_window(self):
        self.window.hide()

    def start_system(self):
        self.app.start_system()

    def stop_system(self):
        self.app.stop_system()

    def on_system_started(self):
        self.showMessage(
            "System Running",
            "School bell system started",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
        self.refresh_state()

    def on_system_stopped(self):
        self.showMessage(
            "System Stopped",
            "School bell system stopped",
            QSystemTrayIcon.MessageIcon.Warning,
            3000
        )
        self.refresh_state()

    def on_bell(self, payload):
        schedule_name = payload["schedule"]["name"] if "schedule" in payload else "Bell"

        self.showMessage(
            "🔔 Bell Triggered",
            f"{schedule_name}",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
        
    def quit_app(self):
        reply = QMessageBox.question(
            self.window,
            "Quit",
            "Stop system and exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.app.shutdown()
            self.qt_app.quit()
        