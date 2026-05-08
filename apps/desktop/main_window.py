from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from apps.desktop.widgets.superbar import SuperBar
from apps.desktop.tabs.history_tab import HistoryTab
from apps.desktop.tabs.settings_tab import SettingsTab
from apps.desktop.controllers.main_controller import MainController
from core.paths import get_paths
from PyQt6.QtGui import QIcon

from core.styles.loader import load_stylesheet
from core.paths import get_paths

paths = get_paths()
icon_path = paths.icon_dir / "schoolbell.png"

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
        QTimer.singleShot(0, self.controller.initialize)

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

        self.status_bar.addPermanentWidget(footer, 1)

    def _set_window(self):
        self.setWindowTitle("SCHOOL BELL AUTOMATION")
        self.resize(1200, 750)
        self.setMinimumSize(1000, 600)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        paths = get_paths()
        # style_path = paths.base_dir / "apps/desktop/styles/main_dark.qss"
        # style_path = paths.base_dir / "apps/desktop/styles/main_light.qss"

        saved_theme = self.app.config.get("theme", "dark")
        if not hasattr(self, "_theme_loaded"):
            self.app.theme.apply(saved_theme)
            self._theme_loaded = True

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

        # Tambahkan rounded corner untuk table
        self.table.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # Set row height lebih besar
        self.table.verticalHeader().setDefaultSectionSize(28)

        layout.addWidget(self.table)

        # ================= BUTTON BAR =================
        bar = QHBoxLayout()
        bar.setSpacing(8)

        self.add_btn = QPushButton("➕ Add")
        self.edit_btn = QPushButton("✏️ Edit")
        self.delete_btn = QPushButton("🗑 Delete")
        self.ring_btn = QPushButton("🔊 Test")
        self.ring_btn.setEnabled(False)
        self.stop_test_btn = QPushButton("⏹ Stop Bell")
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

        self.ring_btn.setEnabled(False)
        QTimer.singleShot(0, self._bind_table_selection)

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

    def _bind_table_selection(self):
        def bind():
            model = self.table.selectionModel()
            if not model:
                QTimer.singleShot(100, bind)
                return

            try:
                model.selectionChanged.disconnect()
            except:
                pass

            model.selectionChanged.connect(self._on_selection_change)

        bind()
            
    # =====================================================
    # HELPER
    # =====================================================

    def _get_selected_schedule(self):
        try:
            indexes = self.table.selectionModel().selectedRows()
            if not indexes:
                return None

            row = indexes[0].row()

            return self.controller.get_schedule_by_row(row)

        except Exception as e:
            print("Selection error:", e)
            return None
    
    def _on_test_clicked(self):
        schedule = self.controller._get_selected_schedule()

        if not schedule:
            QMessageBox.warning(self, "No Selection", "Pilih schedule dulu")
            return

        self.controller.test_ring(schedule.id)

    def _on_selection_change(self):
        model = self.table.selectionModel()
        if not model:
            self.ring_btn.setEnabled(False)
            return

        has_selection = len(model.selectedRows()) > 0
        self.ring_btn.setEnabled(has_selection)
        
    def on_schedules_loaded(self):
        try:
            model = self.table.model()
            if model:
                self.ring_btn.setEnabled(model.rowCount() > 0)
            else:
                self.ring_btn.setEnabled(False)
        except:
            self.ring_btn.setEnabled(False)
    # =====================================================
    # SIGNALS
    # =====================================================

    def _connect_ui(self):
        c = self.controller

        self.add_profile_btn.clicked.connect(c.add_profile)
        self.activate_profile_btn.clicked.connect(c.activate_profile)
        self.profile_list.itemDoubleClicked.connect(c.rename_profile)
        self.delete_profile_btn.clicked.connect(c.delete_profile)
        self.profile_list.itemClicked.connect(c.on_profile_click)

        self.add_btn.clicked.connect(c.add_schedule)
        self.edit_btn.clicked.connect(c.edit_schedule)
        self.delete_btn.clicked.connect(c.delete_schedule)
        self.ring_btn.clicked.connect(self._on_test_clicked)
        self.stop_test_btn.clicked.connect(c.stop_test)
        self.toggle_btn.clicked.connect(c.toggle_system)
        self.reload_btn.clicked.connect(c.load_schedules)

        self.table.doubleClicked.connect(c.edit_schedule)

        self.clear_log_btn.clicked.connect(c.clear_logs)
        self.log_filter_input.textChanged.connect(c._filter_logs)

        # CORE EVENT BUS
        self.app.events.on("JOBS_UPDATED", lambda _: self._safe_reload(c))
        self.app.events.on("SYSTEM_STARTED", lambda _: c.update_system_status())
        self.app.events.on("SYSTEM_STOPPED", lambda _: c.update_system_status())
        self.app.events.on("PROFILE_CHANGED", lambda _: c.load_profiles())
        self.app.events.on("BELL_TRIGGERED", self._on_bell_triggered)

        # SUPERBAR HEARTBEAT
        self.superbar.tick.connect(c._update_next_bell_display)

    def _on_bell_triggered(self, data):
        QTimer.singleShot(0, lambda: self._handle_bell(data))
        self._handle_bell(data)
    
    def _handle_bell(self, data):
        print("BELL UI:", data)
        self.superbar.set_running(True)

    def _safe_reload(self, controller):
        QTimer.singleShot(0, controller.load_schedules)