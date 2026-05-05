# desktop/tray_icon.py
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from core.app_core import get_app
from core.path_helper import app_path
import os
import subprocess
import threading
import sys  # <-- TAMBAHKAN INI

class TrayIcon(QSystemTrayIcon):
    """System tray icon with menu and notifications"""
    
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
        else:
            print(f"Warning: Icon not found at {icon_path}")
    
    def setup_menu(self):
        menu = QMenu()
        
        # Status indicator (non-clickable)
        self.status_action = QAction("🟢 System: Running", menu)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        
        menu.addSeparator()
        
        # Next bell info
        self.next_bell_action = QAction("⏰ Next bell: --:--", menu)
        self.next_bell_action.setEnabled(False)
        menu.addAction(self.next_bell_action)
        
        menu.addSeparator()
        
        # Open Web UI
        web_action = QAction("🌐 Open Web UI", menu)
        web_action.triggered.connect(self.open_web_ui)
        menu.addAction(web_action)
        
        # Open Dashboard (GUI)
        dashboard_action = QAction("🖥️ Open Dashboard", menu)
        dashboard_action.triggered.connect(self.open_dashboard)
        menu.addAction(dashboard_action)
        
        menu.addSeparator()
        
        # Start/Stop service
        self.toggle_action = QAction("⏹ Stop Service", menu)
        self.toggle_action.triggered.connect(self.toggle_service)
        menu.addAction(self.toggle_action)
        
        menu.addSeparator()
        
        # Quit
        quit_action = QAction("🚪 Quit", menu)
        quit_action.triggered.connect(self.quit_application)
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
    
    def setup_timer(self):
        """Update tray info periodically"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)
        self.update_status()
    
    def update_status(self):
        """Update tray icon status and tooltip"""
        status = self.app.get_status()
        is_running = status['scheduler']['running']
        
        # Update status action
        if is_running:
            self.status_action.setText("🟢 System: Running")
            self.toggle_action.setText("⏹ Stop Service")
            self.setToolTip(f"School Bell System\nRunning | {status['scheduler']['active_jobs']} jobs")
        else:
            self.status_action.setText("🔴 System: Stopped")
            self.toggle_action.setText("▶ Start Service")
            self.setToolTip("School Bell System\nStopped")
        
        # Update next bell info
        next_bell = status['scheduler']['next_bell']
        if next_bell:
            if hasattr(next_bell, 'tzinfo') and next_bell.tzinfo:
                next_bell = next_bell.replace(tzinfo=None)
            time_str = next_bell.strftime('%H:%M:%S')
            self.next_bell_action.setText(f"⏰ Next bell: {time_str}")
        else:
            self.next_bell_action.setText("⏰ Next bell: --:--")
    
    def toggle_service(self):
        """Toggle service start/stop"""
        if self.app.scheduler.running:
            self.app.scheduler.stop()
            self.show_notification("System Stopped", "Bell scheduler has been stopped")
            self.toggle_action.setText("▶ Start Service")
        else:
            # Check if there are schedules
            active_profile = self.app.schedule_manager.get_active_profile()
            if not active_profile:
                self.show_notification("Cannot Start", "No active profile", QSystemTrayIcon.MessageIcon.Warning)
                return
            
            schedules = self.app.schedule_manager.get_schedules_by_profile(active_profile.id, include_inactive=False)
            if not schedules:
                self.show_notification("Cannot Start", "No schedules in profile", QSystemTrayIcon.MessageIcon.Warning)
                return
            
            self.app.scheduler.start()
            self.show_notification("System Started", "Bell scheduler is now running")
            self.toggle_action.setText("⏹ Stop Service")
    
    def open_web_ui(self):
        """Open web UI in default browser"""
        import webbrowser
        webbrowser.open("http://localhost:5000")
        self.show_notification("Web UI", "Opening in browser", QSystemTrayIcon.MessageIcon.Information)
    
    def open_dashboard(self):
        """Open desktop GUI (if not already open)"""
        from desktop.main_window import MainWindow
        
        # Check if main window already exists
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, MainWindow):
                widget.show_from_tray()
                widget.raise_()
                widget.activateWindow()
                found = True
                break
        
        window = MainWindow()
        window.show()
    
    def show_notification(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information):
        """Show system notification"""
        self.showMessage(title, message, icon, 3000)
    
    def quit_application(self):
        """Quit application completely"""
        self.app.shutdown_all()
        QApplication.quit()