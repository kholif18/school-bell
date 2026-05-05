# desktop/main_window.py - FINAL CLEAN VERSION
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from core.app_core import get_app
from core.event_manager import get_event_manager
from desktop.widgets.superbar import SuperBar
from desktop.tabs.history_tab import HistoryTab
from desktop.tabs.settings_tab import SettingsTab
from desktop.bridge.ui_bridge import UiBridge
from desktop.controllers.main_controller import MainController

INDUSTRIAL_STYLE = """ ... (style yang sama) ... """

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = get_app()
        self.event_manager = get_event_manager()
        self.bridge = UiBridge()
        
        # Controller handles all logic
        self.controller = MainController(self, self.app)
        
        self.setup_ui()
        self.setup_connections()
        
        # Start timers
        self.start_timers()
        
        # Initialize controller after UI ready
        QTimer.singleShot(100, self.controller.initialize)
    
    def setup_ui(self):
        self.setWindowTitle("SCHOOL BELL AUTOMATION")
        self.setMinimumSize(1000, 600)
        self.resize(1200, 750)
        self.setStyleSheet(INDUSTRIAL_STYLE)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Superbar
        self.superbar = SuperBar()
        main_layout.addWidget(self.superbar)
        
        # Middle section
        middle_split = QSplitter(Qt.Orientation.Horizontal)
        middle_split.setHandleWidth(5)
        middle_split.setStyleSheet("""
            QSplitter::handle { background-color: #30363D; width: 5px; margin: 0px; }
            QSplitter::handle:hover { background-color: #1F6FEB; }
        """)
        
        # LEFT: Profile Sidebar
        left_panel = QWidget()
        left_panel.setMinimumWidth(150)
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 5, 0)
        left_layout.setSpacing(5)
        
        left_layout.addWidget(QLabel("📂 PROFILES"))
        self.profile_list = QListWidget()
        left_layout.addWidget(self.profile_list)
        
        self.add_profile_btn = QPushButton("+ New Profile")
        left_layout.addWidget(self.add_profile_btn)
        
        self.activate_profile_btn = QPushButton("✓ Activate")
        self.activate_profile_btn.setObjectName("primary_btn")
        left_layout.addWidget(self.activate_profile_btn)
        
        self.delete_profile_btn = QPushButton("🗑 Delete")
        left_layout.addWidget(self.delete_profile_btn)
        left_layout.addStretch()
        
        # RIGHT: Tab Widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: Schedules
        schedules_tab = QWidget()
        schedules_layout = QVBoxLayout(schedules_tab)
        
        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(self.controller.edit_schedule)
        schedules_layout.addWidget(self.table)
        
        # Action bar
        action_bar = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add")
        self.add_btn.setObjectName("primary_btn")
        action_bar.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏️ Edit")
        action_bar.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑 Delete")
        action_bar.addWidget(self.delete_btn)
        
        self.ring_btn = QPushButton("🔊 Test")
        action_bar.addWidget(self.ring_btn)
        
        self.stop_test_btn = QPushButton("⏹ Stop Test")
        action_bar.addWidget(self.stop_test_btn)
        action_bar.addStretch()
        
        self.toggle_btn = QPushButton("▶ START SYSTEM")
        self.toggle_btn.setObjectName("start_btn")
        action_bar.addWidget(self.toggle_btn)
        
        self.reload_btn = QPushButton("⟳ Reload")
        action_bar.addWidget(self.reload_btn)
        
        schedules_layout.addLayout(action_bar)
        self.tab_widget.addTab(schedules_tab, "📋 Schedules")
        
        # Tab 2: History
        self.history_tab = HistoryTab(self.app.schedule_manager)
        self.tab_widget.addTab(self.history_tab, "📜 History")
        
        # Tab 3: Log Console
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        log_filter_bar = QHBoxLayout()
        log_filter_bar.addWidget(QLabel("Filter:"))
        self.log_filter_input = QLineEdit()
        self.log_filter_input.setPlaceholderText("Filter logs...")
        log_filter_bar.addWidget(self.log_filter_input)
        log_filter_bar.addStretch()
        self.clear_log_btn = QPushButton("Clear")
        log_filter_bar.addWidget(self.clear_log_btn)
        log_layout.addLayout(log_filter_bar)
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Consolas", 10))
        log_layout.addWidget(self.log_console)
        self.tab_widget.addTab(log_tab, "📝 Log Console")
        
        # Tab 4: Settings
        self.settings_tab = SettingsTab(self.app)
        self.tab_widget.addTab(self.settings_tab, "⚙ Settings")
        
        middle_split.addWidget(left_panel)
        middle_split.addWidget(self.tab_widget)
        middle_split.setSizes([220, self.width() - 220])
        
        main_layout.addWidget(middle_split, 1)
        
        # Footer
        footer = QLabel("SCHOOL BELL AUTOMATION v1.0 | Ravaa Creative © 2026")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #8B949E; font-size: 10px; padding: 4px;")
        main_layout.addWidget(footer)
    
    def setup_connections(self):
        self.add_profile_btn.clicked.connect(self.controller.add_profile)
        self.activate_profile_btn.clicked.connect(self.controller.activate_profile)
        self.delete_profile_btn.clicked.connect(self.controller.delete_profile)
        self.profile_list.itemClicked.connect(self.controller.on_profile_click)
        
        self.add_btn.clicked.connect(self.controller.add_schedule)
        self.edit_btn.clicked.connect(self.controller.edit_schedule)
        self.delete_btn.clicked.connect(self.controller.delete_schedule)
        self.ring_btn.clicked.connect(self.controller.test_ring)
        self.stop_test_btn.clicked.connect(self.controller.stop_test)
        self.toggle_btn.clicked.connect(self.controller.toggle_system)
        self.reload_btn.clicked.connect(self.controller.reload_schedules)
        
        self.clear_log_btn.clicked.connect(self.controller.clear_logs)
        self.log_filter_input.textChanged.connect(self.controller._filter_logs)
    
    def start_timers(self):
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.superbar.update_time)
        self.clock_timer.start(1000)
        
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.controller.update_system_status)
        self.status_timer.start(2000)
        
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.controller.sync_with_engine)
        self.sync_timer.start(2000)
    
    def closeEvent(self, event):
        self.controller.handle_close(event)


def main():
    qt_app = QApplication(sys.argv)
    qt_app.setStyle('Fusion')
    
    core_app = get_app()
    core_app.initialize()
    
    window = MainWindow()
    window.show()
    
    core_app.start()
    
    sys.exit(qt_app.exec())

if __name__ == "__main__":
    main()