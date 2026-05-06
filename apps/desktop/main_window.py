from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from apps.desktop.widgets.superbar import SuperBar
from apps.desktop.tabs.history_tab import HistoryTab
from apps.desktop.tabs.settings_tab import SettingsTab
from apps.desktop.controllers.main_controller import MainController
from core.paths import get_paths
from PyQt6.QtGui import QIcon

paths = get_paths()
icon_path = paths.icon_dir / "schoolbell.png"

INDUSTRIAL_STYLE = """
/* =========================================================
   GLOBAL
========================================================= */
QMainWindow, QWidget {
    background-color: #15161a;
    color: #e7e7e7;
    font-family: Segoe UI;
    font-size: 12px;
}

/* =========================================================
   SUPERBAR
========================================================= */
QFrame#superbar {
    background-color: #101115;
    border: 1px solid #2a2d35;
    border-radius: 8px;
}

/* =========================================================
   PANELS
========================================================= */
QFrame#sidepanel, 
QFrame#mainpanel {
    background-color: #191b20;
    border: 1px solid #2f323c;
    border-radius: 8px;
}

/* =========================================================
   SECTION TITLE
========================================================= */
QLabel#sectionTitle {
    font-size: 11px;
    font-weight: 600;
    color: #8f96a3;
    padding: 2px 0 6px 2px;
    letter-spacing: 1px;
}

/* =========================================================
   LABEL
========================================================= */
QLabel {
    background: transparent;
}

/* =========================================================
   BUTTON
========================================================= */
QPushButton {
    background-color: #2b2e36;
    border: 1px solid #3d414c;
    border-radius: 5px;
    padding: 9px 14px;
    color: #e9e9e9;
    min-height: 16px;
}

QPushButton:hover {
    background-color: #353944;
    border: 1px solid #4a5060;
}

QPushButton:pressed {
    background-color: #202229;
}

QPushButton:disabled {
    background-color: #24262d;
    color: #666;
    border: 1px solid #2d3038;
}

/* =========================================================
   LIST WIDGET
========================================================= */
QListWidget {
    background-color: #20232b;
    border: 1px solid #323642;
    border-radius: 6px;
    padding: 8px;
    outline: none;
}

QListWidget::item {
    padding: 8px;
    margin-bottom: 3px;
    border-radius: 4px;
}

QListWidget::item:hover {
    background: #2b3040;
}

QListWidget::item:selected {
    background: #1e8e3e;
    color: white;
}

/* =========================================================
   TAB WIDGET
========================================================= */
QTabWidget::pane {
    border: 1px solid #30343e;
    background: #17191f;
    border-radius: 6px;
    margin-top: 4px;
}

QTabBar::tab {
    background: #262932;
    border: 1px solid #3a3e49;
    padding: 8px 18px;
    margin-right: 3px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background: #343946;
    border-bottom: 1px solid #343946;
}

QTabBar::tab:hover {
    background: #303542;
}

/* =========================================================
   TABLE VIEW
========================================================= */
QTableView {
    background-color: #20232b;
    border: 1px solid #323642;
    border-radius: 6px;
    padding: 4px;
    color: #eaeaea;
    gridline-color: #2f3340;
    selection-background-color: #4d5eff;
    alternate-background-color: #242833;
}

QHeaderView::section {
    background-color: #2a2e38;
    color: #dcdcdc;
    border: 1px solid #3a3f4b;
    padding: 6px;
    height: 28px;
    font-weight: bold;
}

QTableCornerButton::section {
    background-color: #2a2e38;
    border: 1px solid #3a3f4b;
}

QTableView::item:selected {
    background: #4d5eff;
    color: white;
}

/* =========================================================
   INPUTS
========================================================= */
QLineEdit,
QTimeEdit,
QComboBox,
QTextEdit {
    background-color: #20232b;
    border: 1px solid #323642;
    border-radius: 5px;
    padding: 6px;
    color: #f1f1f1;
}

QComboBox::drop-down {
    border: none;
}

/* =========================================================
   SCROLLBAR
========================================================= */
QScrollBar:vertical {
    background: #17191f;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #404552;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #525868;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #17191f;
    height: 10px;
}

QScrollBar::handle:horizontal {
    background: #404552;
    min-width: 25px;
    border-radius: 4px;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ================= SYSTEM BUTTON ================= */

QPushButton#systemButton[running="false"] {
    background-color: #1f7a35;
    border: 1px solid #2ca24a;
    color: white;
    font-weight: bold;
}

QPushButton#systemButton[running="false"]:hover {
    background-color: #259140;
}

QPushButton#systemButton[running="true"] {
    background-color: #8a1f1f;
    border: 1px solid #b52a2a;
    color: white;
    font-weight: bold;
}

QPushButton#systemButton[running="true"]:hover {
    background-color: #a22626;
}

/* ================= DANGER BUTTON ================= */

QPushButton#dangerButton {
    background-color: #7b2020;
    border: 1px solid #9d2c2c;
    color: white;
    font-weight: bold;
}

QPushButton#dangerButton:hover {
    background-color: #922626;
}

/* ================= SUCCESS BUTTON ================= */

QPushButton#successButton {
    background-color: #1f7a35;
    border: 1px solid #2ca24a;
    color: white;
    font-weight: bold;
}

QPushButton#successButton:hover {
    background-color: #259140;
}
"""

class MainWindow(QMainWindow):

    def __init__(self, app_core):
        super().__init__()

        self.app = app_core
        
        paths = get_paths()

        self.setWindowIcon(
            QIcon(str(paths.icon_dir / "schoolbell.png"))
        )

        self.controller = MainController(self, self.app)

        self._build_ui()
        self._connect_ui()
        self.controller.initialize()

    # =====================================================
    # UI BUILD
    # =====================================================

    def _build_ui(self):
        self._set_window()
        self._create_root()
        self._create_superbar()
        self._create_middle()
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        footer = QLabel("SCHOOL BELL AUTOMATION | V1.0 - Ravaa Creative")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # styling biar soft (tidak putih mencolok)
        footer.setStyleSheet("""
            color: #8f96a3;
            font-size: 11px;
            padding: 4px;
        """)

        self.status_bar.addPermanentWidget(footer, 1)

    def _set_window(self):
        self.setWindowTitle("SCHOOL BELL AUTOMATION")
        self.resize(1200, 750)
        self.setMinimumSize(1000, 600)
        self.setStyleSheet(INDUSTRIAL_STYLE)

    def _create_root(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.layout = QVBoxLayout(self.central)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(10)

    def _create_superbar(self):
        self.superbar = SuperBar()
        self.layout.addWidget(self.superbar)

    def _create_middle(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._create_sidebar(splitter)
        self._create_tabs(splitter)

        splitter.setSizes([220, 900])
        self.layout.addWidget(splitter)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.app.events.emit("WINDOW_HIDDEN", {})

    # =====================================================
    # SIDEBAR
    # =====================================================

    def _create_sidebar(self, parent):
        panel = QFrame()
        panel.setObjectName("sidepanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("📂 PROFILES")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.profile_list = QListWidget()
        layout.addWidget(self.profile_list)

        self.add_profile_btn = QPushButton("+ New Profile")
        self.activate_profile_btn = QPushButton("✓ Activate")
        self.delete_profile_btn = QPushButton("🗑 Delete")

        self.activate_profile_btn.setObjectName("successButton")
        self.delete_profile_btn.setObjectName("dangerButton")

        layout.addWidget(self.add_profile_btn)
        layout.addWidget(self.activate_profile_btn)
        layout.addWidget(self.delete_profile_btn)
        layout.addStretch()

        parent.addWidget(panel)

    # =====================================================
    # TABS
    # =====================================================

    def _create_tabs(self, parent):
        wrapper = QFrame()
        wrapper.setObjectName("mainpanel")

        wrap_layout = QVBoxLayout(wrapper)
        wrap_layout.setContentsMargins(10, 10, 10, 10)

        self.tabs = QTabWidget()

        self._tab_schedule()
        self._tab_history()
        self._tab_log()
        self._tab_settings()

        wrap_layout.addWidget(self.tabs)
        parent.addWidget(wrapper)

    def _tab_schedule(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 6, 4, 4)
        layout.setSpacing(8)

        # ================= TABLE =================
        self.table = QTableView()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setMouseTracking(True)
        self.table.setSortingEnabled(True)

        layout.addWidget(self.table)

        # ================= BUTTON BAR =================
        bar = QHBoxLayout()
        bar.setSpacing(8)

        self.add_btn = QPushButton("➕ Add")
        self.edit_btn = QPushButton("✏️ Edit")
        self.delete_btn = QPushButton("🗑 Delete")
        self.ring_btn = QPushButton("🔊 Test")
        self.stop_test_btn = QPushButton("⏹ Stop Sound")
        self.toggle_btn = QPushButton("▶ START SYSTEM")
        self.stop_test_btn.setObjectName("dangerButton")
        self.toggle_btn.setObjectName("systemButton")
        self.reload_btn = QPushButton("⟳ Reload")

        left_buttons = [
            self.add_btn,
            self.edit_btn,
            self.delete_btn,
            self.ring_btn,
            self.stop_test_btn,
        ]

        for b in left_buttons:
            b.setMinimumHeight(34)
            bar.addWidget(b)

        bar.addStretch()

        self.toggle_btn.setMinimumHeight(34)
        self.reload_btn.setMinimumHeight(34)

        bar.addWidget(self.toggle_btn)
        bar.addWidget(self.reload_btn)

        layout.addLayout(bar)

        self.tabs.addTab(tab, "📋 Schedules")

    def _tab_history(self):
        self.history_tab = HistoryTab(self.app.repo)
        self.tabs.addTab(self.history_tab, "📜 History")

    def _tab_log(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.log_filter_input = QLineEdit()
        self.log_filter_input.setPlaceholderText("Filter logs...")

        self.clear_log_btn = QPushButton("Clear")

        top = QHBoxLayout()
        top.addWidget(self.log_filter_input)
        top.addWidget(self.clear_log_btn)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)

        layout.addLayout(top)
        layout.addWidget(self.log_console)

        self.tabs.addTab(tab, "📝 Log")

    def _tab_settings(self):
        self.settings_tab = SettingsTab(self.app)
        self.tabs.addTab(self.settings_tab, "⚙ Settings")

    # =====================================================
    # SIGNALS
    # =====================================================

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
        self.reload_btn.clicked.connect(c.load_schedules)

        self.table.doubleClicked.connect(c.edit_schedule)

        self.clear_log_btn.clicked.connect(c.clear_logs)
        self.log_filter_input.textChanged.connect(c._filter_logs)

        # CORE EVENT BUS
        self.app.events.on("JOBS_UPDATED", lambda _: c.load_schedules())
        self.app.events.on("SYSTEM_STARTED", lambda _: c.update_system_status())
        self.app.events.on("SYSTEM_STOPPED", lambda _: c.update_system_status())
        self.app.events.on("PROFILE_CHANGED", lambda _: c.load_profiles())
        self.app.events.on("BELL_TRIGGERED", lambda _: self.history_tab.refresh())

        # SUPERBAR HEARTBEAT
        self.superbar.tick.connect(c._update_next_bell_display)

    # =====================================================
    # CLOSE
    # =====================================================

    def closeEvent(self, event):
        event.ignore()
        self.hide()