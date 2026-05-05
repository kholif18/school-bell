# apps/desktop/tray_icon.py
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer
from core.paths import app_path
import os

class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = get_app()
        self.setup_icon()
        self.setup_menu()
        self.setup_timer()
        self.show()

    def setup_icon(self):
        icon_path = app_path("assets", "icon", "schoolbell.png")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setToolTip("School Bell Automation System")

    def setup_menu(self):
        menu = QMenu()

        self.status_action = QAction("🔴 System: Stopped", menu)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)

        menu.addSeparator()

        self.next_bell_action = QAction("⏰ Next bell: --:--", menu)
        self.next_bell_action.setEnabled(False)
        menu.addAction(self.next_bell_action)

        menu.addSeparator()

        web_action = QAction("🌐 Open Web UI", menu)
        web_action.triggered.connect(self.open_web_ui)
        menu.addAction(web_action)

        dashboard_action = QAction("🖥️ Open Dashboard", menu)
        dashboard_action.triggered.connect(self.open_dashboard)
        menu.addAction(dashboard_action)

        menu.addSeparator()

        self.toggle_action = QAction("▶ Start Service", menu)
        self.toggle_action.triggered.connect(self.toggle_service)
        menu.addAction(self.toggle_action)

        menu.addSeparator()

        quit_action = QAction("🚪 Quit Tray", menu)
        quit_action.triggered.connect(self.quit_application)
        menu.addAction(quit_action)

        self.setContextMenu(menu)


    def get_runtime(self):
        return get_runtime_state().get()

    def update_status(self):
        state = self.get_runtime()

        if not state:
            return

        if state.is_running:
            self.status_action.setText("🟢 System: Running")
            self.toggle_action.setText("⏹ Stop Service")
            self.setToolTip(f"School Bell System\nRunning | {state.active_jobs} jobs")
        else:
            self.status_action.setText("🔴 System: Stopped")
            self.toggle_action.setText("▶ Start Service")
            self.setToolTip("School Bell System\nStopped")

        if state.next_bell:
            next_bell = state.next_bell
            if hasattr(next_bell, 'tzinfo') and next_bell.tzinfo:
                next_bell = next_bell.replace(tzinfo=None)
            self.next_bell_action.setText(f"⏰ Next bell: {next_bell.strftime('%H:%M:%S')}")
        else:
            self.next_bell_action.setText("⏰ Next bell: --:--")

    def toggle_service(self):
        state = self.get_runtime()

        if state and state.is_running:
            self.app.ipc.send("STOP_SCHEDULER")
            self.show_notification("Stopping", "Sending stop command to master service...")
        else:
            self.app.ipc.send("START_SCHEDULER")
            self.show_notification("Starting", "Sending start command to master service...")

    def open_web_ui(self):
        import webbrowser
        webbrowser.open("http://localhost:5000")

    def open_dashboard(self):
        from apps.desktop.main_window import MainWindow

        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, MainWindow):
                widget.show()
                widget.raise_()
                widget.activateWindow()
                return

        self.window = MainWindow()
        self.window.show()

    def show_notification(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information):
        self.showMessage(title, message, icon, 3000)

    def quit_application(self):
        QApplication.quit()