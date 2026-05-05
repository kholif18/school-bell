# apps/desktop/main_window.py
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from apps.desktop.widgets.superbar import SuperBar
from apps.desktop.tabs.history_tab import HistoryTab
from apps.desktop.tabs.settings_tab import SettingsTab
from apps.desktop.bridge.ui_bridge import UiBridge
from apps.desktop.controllers.main_controller import MainController


class MainWindow(QMainWindow):

    def __init__(self, app_core):
        super().__init__()

        self.app = app_core
        self.bridge = UiBridge()

        self.controller = MainController(self, self.app)

        self._build_ui()
        self._connect_ui()
        self.controller.initialize()

    # =========================================================
    # UI ROOT
    # =========================================================
    def _build_ui(self):
        self._set_window()
        self._create_root()
        self._create_superbar()
        self._create_middle()
        self._create_footer()

    def _set_window(self):
        self.setWindowTitle("SCHOOL BELL AUTOMATION")
        self.setMinimumSize(1000, 600)
        self.resize(1200, 750)
        self.setStyleSheet(INDUSTRIAL_STYLE)

    def _create_root(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        self.layout.setContentsMargins(8, 8, 8, 8)

    # =========================================================
    # SUPERBAR
    # =========================================================
    def _create_superbar(self):
        self.superbar = SuperBar()
        self.layout.addWidget(self.superbar)

    # =========================================================
    # MIDDLE SECTION
    # =========================================================
    def _create_middle(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._create_sidebar(splitter)
        self._create_tabs(splitter)

        splitter.setSizes([220, 800])
        self.layout.addWidget(splitter, 1)

    # ================= SIDEBAR =================
    def _create_sidebar(self, parent):
        panel = QWidget()
        panel.setMinimumWidth(150)
        panel.setMaximumWidth(400)

        layout = QVBoxLayout(panel)

        layout.addWidget(QLabel("📂 PROFILES"))

        self.profile_list = QListWidget()
        layout.addWidget(self.profile_list)

        self.add_profile_btn = QPushButton("+ New Profile")
        self.activate_profile_btn = QPushButton("✓ Activate")
        self.delete_profile_btn = QPushButton("🗑 Delete")

        self.activate_profile_btn.setObjectName("primary_btn")

        layout.addWidget(self.add_profile_btn)
        layout.addWidget(self.activate_profile_btn)
        layout.addWidget(self.delete_profile_btn)

        layout.addStretch()

        parent.addWidget(panel)

    # ================= TABS =================
    def _create_tabs(self, parent):
        self.tabs = QTabWidget()

        self._tab_schedule()
        self._tab_history()
        self._tab_log()
        self._tab_settings()

        parent.addWidget(self.tabs)

    # -------- TAB 1: SCHEDULE --------
    def _tab_schedule(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.table = QTableView()
        self.table.doubleClicked.connect(self.controller.edit_schedule)

        layout.addWidget(self.table)

        self._schedule_actions(layout)

        self.tabs.addTab(tab, "📋 Schedules")

    def _schedule_actions(self, layout):
        bar = QHBoxLayout()

        self.add_btn = QPushButton("➕ Add")
        self.edit_btn = QPushButton("✏️ Edit")
        self.delete_btn = QPushButton("🗑 Delete")
        self.ring_btn = QPushButton("🔊 Test")
        self.stop_test_btn = QPushButton("⏹ Stop Test")
        self.toggle_btn = QPushButton("▶ START SYSTEM")
        self.reload_btn = QPushButton("⟳ Reload")

        self.toggle_btn.setObjectName("start_btn")

        bar.addWidget(self.add_btn)
        bar.addWidget(self.edit_btn)
        bar.addWidget(self.delete_btn)
        bar.addWidget(self.ring_btn)
        bar.addWidget(self.stop_test_btn)
        bar.addStretch()
        bar.addWidget(self.toggle_btn)
        bar.addWidget(self.reload_btn)

        layout.addLayout(bar)

    # -------- TAB 2: HISTORY --------
    def _tab_history(self):
        self.history_tab = HistoryTab(self.app.schedule_manager)
        self.tabs.addTab(self.history_tab, "📜 History")

    # -------- TAB 3: LOG --------
    def _tab_log(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        bar = QHBoxLayout()

        self.log_filter_input = QLineEdit()
        self.log_filter_input.setPlaceholderText("Filter logs...")

        self.clear_log_btn = QPushButton("Clear")

        bar.addWidget(QLabel("Filter:"))
        bar.addWidget(self.log_filter_input)
        bar.addStretch()
        bar.addWidget(self.clear_log_btn)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Consolas", 10))

        layout.addLayout(bar)
        layout.addWidget(self.log_console)

        self.tabs.addTab(tab, "📝 Log")

    # -------- TAB 4: SETTINGS --------
    def _tab_settings(self):
        self.settings_tab = SettingsTab(self.app)
        self.tabs.addTab(self.settings_tab, "⚙ Settings")

    # =========================================================
    # CONNECTIONS
    # =========================================================
    def _connect_ui(self):
        c = self.controller

        self.add_profile_btn.clicked.connect(c.add_profile)
        self.activate_profile_btn.clicked.connect(c.activate_profile)
        self.delete_profile_btn.clicked.connect(c.delete_profile)
        self.profile_list.itemClicked.connect(c.on_profile_click)

        self.add_btn.clicked.connect(c.add_schedule)
        self.edit_btn.clicked.connect(c.edit_schedule)
        self.delete_btn.clicked.connect(c.delete_schedule)
        self.ring_btn.clicked.connect(c.test_ring)
        self.stop_test_btn.clicked.connect(c.stop_test)
        self.toggle_btn.clicked.connect(c.toggle_system)
        self.reload_btn.clicked.connect(c.reload_schedules)

        self.clear_log_btn.clicked.connect(c.clear_logs)
        self.log_filter_input.textChanged.connect(c._filter_logs)

        # EVENT BUS
        self.bridge.events().on("JOBS_UPDATED", c.on_jobs_updated)
        self.bridge.events().on("SYSTEM_STARTED", lambda _: c.update_system_status())
        self.bridge.events().on("SYSTEM_STOPPED", lambda _: c.update_system_status())
        self.bridge.events().on("PROFILE_CHANGED", lambda _: c.load_profiles())

    # =========================================================
    # CLEANUP
    # =========================================================
    def closeEvent(self, event):
        self.controller.handle_close(event)