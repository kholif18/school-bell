# desktop/main_window.py (REFACTORED FINAL)
import sys
from datetime import datetime, time, timedelta
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from core.event_manager import get_event_manager

from core.app_core import get_app

# ============================================================
# INDUSTRIAL DARK THEME
# ============================================================
INDUSTRIAL_STYLE = """
QMainWindow, QWidget {
    background-color: #0D1117;
    color: #E6EDF3;
    font-family: 'Segoe UI', 'Consolas', monospace;
}

/* Superbar */
#superbar {
    background-color: #161B22;
    border-bottom: 2px solid #238636;
    min-height: 70px;
}

#clock_display {
    font-size: 32px;
    font-weight: bold;
    color: #39FF14;
    font-family: 'Consolas', monospace;
}

#date_display {
    font-size: 12px;
    color: #8B949E;
}

#next_bell_time {
    font-size: 22px;
    font-weight: bold;
    color: #FFA500;
}

#next_bell_name {
    font-size: 12px;
    color: #FFA500;
}

/* Profile Sidebar */
QListWidget {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    padding: 5px;
}

QListWidget::item {
    padding: 10px;
    border-radius: 4px;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: #1F6FEB;
    border-left: 3px solid #39FF14;
}

/* Table */
QTableView {
    background-color: #161B22;
    alternate-background-color: #1A202C;
    gridline-color: #30363D;
    border: 1px solid #30363D;
    border-radius: 6px;
}

QTableView::item {
    padding: 8px;
}

QTableView::item:selected {
    background-color: #1F6FEB;
}

QHeaderView::section {
    background-color: #21262D;
    padding: 8px;
    border: none;
    font-weight: bold;
}

/* Buttons */
QPushButton {
    background-color: #21262D;
    border: 1px solid #30363D;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #30363D;
}

QPushButton#primary_btn {
    background-color: #238636;
    border: none;
}

QPushButton#primary_btn:hover {
    background-color: #2EA043;
}

QPushButton#start_btn {
    background-color: #1F6FEB;
    border: none;
    font-weight: bold;
}

QPushButton#stop_btn {
    background-color: #DA3633;
    border: none;
    font-weight: bold;
}

QPushButton#start_btn:hover {
    background-color: #388BF0;
}

QPushButton#stop_btn:hover {
    background-color: #F85149;
}

/* Log Console */
QTextEdit {
    background-color: #0A0C10;
    border: 1px solid #30363D;
    border-radius: 6px;
    font-family: 'Consolas', monospace;
    font-size: 11px;
}

/* Tab Widget */
QTabWidget::pane {
    background-color: #0D1117;
    border: 1px solid #30363D;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #21262D;
    padding: 8px 16px;
    margin: 2px;
    border-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #1F6FEB;
}

/* Status indicators */
QLabel#running_indicator {
    background-color: #238636;
    border-radius: 4px;
    padding: 4px 10px;
    font-weight: bold;
}

QLabel#stopped_indicator {
    background-color: #DA3633;
    border-radius: 4px;
    padding: 4px 10px;
    font-weight: bold;
}
"""

# ============================================================
# SUPER BAR
# ============================================================
class SuperBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("superbar")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        
        # ===== LEFT: Profile & Status =====
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(2)
        
        self.profile_label = QLabel("📋 Profile: --")
        self.profile_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        left_layout.addWidget(self.profile_label)
        
        self.status_indicator = QLabel("🟢 RUNNING")
        self.status_indicator.setObjectName("running_indicator")
        left_layout.addWidget(self.status_indicator)
        
        layout.addWidget(left_widget, 1)
        
        # ===== CENTER: Clock (JAM DIGITAL) =====
        clock_widget = QWidget()
        clock_layout = QVBoxLayout(clock_widget)
        clock_layout.setSpacing(2)
        clock_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.clock_label = QLabel("--:--:--")
        self.clock_label.setObjectName("clock_display")
        clock_layout.addWidget(self.clock_label)
        
        self.date_label = QLabel("--, -- -- ----")
        self.date_label.setObjectName("date_display")
        clock_layout.addWidget(self.date_label)
        
        layout.addWidget(clock_widget, 2)
        
        # ===== RIGHT: Next Bell =====
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_layout.setSpacing(2)
        
        next_title = QLabel("🔔 NEXT BELL")
        next_title.setStyleSheet("font-size: 10px; color: #8B949E;")
        right_layout.addWidget(next_title)
        
        self.next_time_label = QLabel("--:--:--")
        self.next_time_label.setObjectName("next_bell_time")
        right_layout.addWidget(self.next_time_label)
        
        self.next_name_label = QLabel("No schedule")
        self.next_name_label.setObjectName("next_bell_name")
        right_layout.addWidget(self.next_name_label)
        
        layout.addWidget(right_widget, 1)
    
    def update_time(self):
        now = datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%a, %d %b %Y"))
    
    def update_next_bell(self, next_time, next_name):
        if next_time:
            if hasattr(next_time, 'strftime'):
                # Hitung countdown
                now = datetime.now()
                if hasattr(next_time, 'tzinfo') and next_time.tzinfo:
                    next_time = next_time.replace(tzinfo=None)
                
                if next_time > now:
                    diff = next_time - now
                    total_seconds = int(diff.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    
                    if hours > 0:
                        countdown_text = f"{hours}h {minutes}m"
                    elif minutes > 0:
                        countdown_text = f"{minutes}m {seconds}s"
                    else:
                        countdown_text = f"{seconds}s"
                        self.next_time_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #39FF14;")
                else:
                    countdown_text = "🔔 NOW!"
                    self.next_time_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFA500;")
            else:
                countdown_text = str(next_time)
            
            self.next_time_label.setText(countdown_text)
            self.next_name_label.setText(next_name[:30] if next_name else "Bell")
        else:
            self.next_time_label.setText("--:--:--")
            self.next_time_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFA500;")
            self.next_name_label.setText("No upcoming bell")
    
    def update_profile(self, profile_name):
        self.profile_label.setText(f"📋 Profile: {profile_name}")
    
    def set_running(self, is_running):
        if is_running:
            self.status_indicator.setText("🟢 RUNNING")
            self.status_indicator.setObjectName("running_indicator")
        else:
            self.status_indicator.setText("🔴 STOPPED")
            self.status_indicator.setObjectName("stopped_indicator")
        self.status_indicator.style().unpolish(self.status_indicator)
        self.status_indicator.style().polish(self.status_indicator)

# ============================================================
# HISTORY TAB
# ============================================================
class HistoryLoader(QThread):
    """Load history in background thread to prevent UI freeze"""
    history_loaded = pyqtSignal(list)
    
    def __init__(self, schedule_manager, filter_text=""):
        super().__init__()
        self.schedule_manager = schedule_manager
        self.filter_text = filter_text
    
    def run(self):
        history = self.schedule_manager.get_recent_history(limit=200)
        if self.filter_text:
            history = [h for h in history if self.filter_text.lower() in h.schedule_name.lower()]
        self.history_loaded.emit(history)


class HistoryTab(QWidget):
    def __init__(self, schedule_manager):
        super().__init__()
        self.schedule_manager = schedule_manager
        self.setup_ui()
        self.loader = None
        self.load_history()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Filter bar
        filter_bar = QHBoxLayout()
        filter_bar.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search by schedule name...")
        self.filter_input.textChanged.connect(self.on_filter_changed)
        filter_bar.addWidget(self.filter_input)
        
        filter_bar.addStretch()
        
        self.refresh_btn = QPushButton("⟳ Refresh")
        self.refresh_btn.clicked.connect(self.load_history)
        filter_bar.addWidget(self.refresh_btn)
        
        layout.addLayout(filter_bar)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Time", "Schedule", "Profile", "Status", "Audio"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setAlternatingRowColors(True)
        layout.addWidget(self.history_table)
        
        # Loading indicator
        self.loading_label = QLabel("Loading history...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: #8B949E; padding: 20px;")
        self.loading_label.setVisible(False)
        layout.addWidget(self.loading_label)
    
    def on_filter_changed(self):
        """Handle filter text change"""
        self.load_history()
    
    def load_history(self):
        """Load history asynchronously"""
        # Cancel existing loader if running
        if self.loader and self.loader.isRunning():
            self.loader.quit()
            self.loader.wait(500)
        
        # Show loading indicator
        self.loading_label.setVisible(True)
        self.history_table.setVisible(False)
        
        # Start new loader
        self.loader = HistoryLoader(self.schedule_manager, self.filter_input.text())
        self.loader.history_loaded.connect(self._display_history)
        self.loader.start()
    
    def _display_history(self, history):
        """Display history in table (called from main thread)"""
        # Hide loading indicator
        self.loading_label.setVisible(False)
        self.history_table.setVisible(True)
        
        # Clear existing data
        self.history_table.setRowCount(0)
        
        if not history:
            # Show empty message
            self.history_table.setRowCount(1)
            empty_item = QTableWidgetItem("No history yet. Click 'Ring' to test.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_table.setItem(0, 0, empty_item)
            self.history_table.setSpan(0, 0, 1, 5)
            self.history_table.resizeColumnsToContents()
            return
        
        # Populate table
        self.history_table.setRowCount(len(history))
        for row, h in enumerate(history):
            # Time column
            time_str = h.rang_at.strftime("%H:%M:%S %d/%m") if h.rang_at else "--:--:-- --/--"
            self.history_table.setItem(row, 0, QTableWidgetItem(time_str))
            
            # Schedule name column
            self.history_table.setItem(row, 1, QTableWidgetItem(h.schedule_name))
            
            # Profile name column
            self.history_table.setItem(row, 2, QTableWidgetItem(h.profile_name or "-"))
            
            # Status column
            status_item = QTableWidgetItem(h.status.upper())
            if h.status == "success":
                status_item.setForeground(QColor("#39FF14"))
            else:
                status_item.setForeground(QColor("#F85149"))
            self.history_table.setItem(row, 3, status_item)
            
            # Audio column
            audio_name = h.audio_played.split('/')[-1] if h.audio_played else "-"
            self.history_table.setItem(row, 4, QTableWidgetItem(audio_name[:20]))
        
        self.history_table.resizeColumnsToContents()

# ============================================================
# SETTINGS TAB
# ============================================================
class SettingsTab(QWidget):
    def __init__(self, app_core):
        super().__init__()
        self.app = app_core
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Audio settings
        audio_group = QGroupBox("Audio Settings")
        audio_layout = QFormLayout(audio_group)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.valueChanged.connect(self.on_volume_change)
        self.volume_label = QLabel("80%")
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        audio_layout.addRow("Master Volume:", volume_layout)
        
        self.test_audio_btn = QPushButton("🔊 Test Audio")
        self.test_audio_btn.clicked.connect(self.test_audio)
        audio_layout.addRow("", self.test_audio_btn)
        
        layout.addWidget(audio_group)
        
        # Scheduler settings
        sched_group = QGroupBox("Scheduler Settings")
        sched_layout = QFormLayout(sched_group)
        
        self.auto_start_cb = QCheckBox("Auto-start scheduler on app launch")
        sched_layout.addRow("", self.auto_start_cb)
        
        layout.addWidget(sched_group)
        
        # System settings
        system_group = QGroupBox("System")
        system_layout = QFormLayout(system_group)
        
        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        system_layout.addRow("Log Level:", self.log_level)
        
        layout.addWidget(system_group)
        layout.addStretch()
        
        # Save button
        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.setObjectName("primary_btn")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
    
    def load_settings(self):
        volume = self.app.config.get('audio.volume', 80)
        self.volume_slider.setValue(volume)
        self.volume_label.setText(f"{volume}%")
    
    def on_volume_change(self, val):
        self.volume_label.setText(f"{val}%")
        self.app.audio_manager.set_volume(val)
    
    def test_audio(self):
        try:
            self.app.audio_manager.play(None)
        except Exception as e:
            QMessageBox.critical(self, "Audio Error", f"Failed to play audio:\n{str(e)}")
    
    def save_settings(self):
        self.app.config.set('audio.volume', self.volume_slider.value())
        self.app.config.set('auto_start', self.auto_start_cb.isChecked())
        # Log level
        level = self.log_level.currentText()
        self.app.config.set('logging.level', level)
        
        QMessageBox.information(self, "Settings", "Settings saved successfully")

# ============================================================
# SCHEDULE TABLE MODEL
# ============================================================
class ScheduleTableModel(QAbstractTableModel):
    def __init__(self, schedules=None):
        super().__init__()
        self.schedules = schedules or []
        self.next_bell_id = None
        self.headers = ["Nama Jadwal", "Jam", "Hari", "Suara", "Status"]
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.schedules)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        s = self.schedules[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return s.name
            elif col == 1:
                return s.bell_time.strftime('%H:%M')
            elif col == 2:
                days = s.get_days_list()
                nama = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
                return ', '.join(nama[d] for d in days if d < 7)
            elif col == 3:
                return "🎵 Custom" if s.audio_file else "🔔 Default"
            elif col == 4:
                return "✓ Aktif" if s.is_active else "✗ Nonaktif"
        
        elif role == Qt.ItemDataRole.ForegroundRole and col == 4:
            return QColor("#39FF14") if s.is_active else QColor("#F85149")
        
        elif role == Qt.ItemDataRole.BackgroundRole:
            if self.next_bell_id and s.id == self.next_bell_id:
                return QColor("#1A3A1A")
        
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None
    
    def refresh(self, schedules, next_bell_id=None):
        self.beginResetModel()
        self.schedules = schedules
        self.next_bell_id = next_bell_id
        self.endResetModel()
    
    def get_schedule_at(self, row):
        if 0 <= row < len(self.schedules):
            return self.schedules[row]
        return None

# ============================================================
# THREAD-SAFE UI BRIDGE
# ============================================================
class UiBridge(QObject):
    """Bridge untuk marshalling events dari backend threads ke GUI thread"""
    systemStarted = pyqtSignal()
    systemStopped = pyqtSignal()
    schedulesReloaded = pyqtSignal()
    profilesUpdated = pyqtSignal()
    profileActivated = pyqtSignal(dict)

# ============================================================
# AUDIO PICKER
# ============================================================
class AudioPicker(QWidget):
    fileChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel("🔔 Default bell")
        self.label.setStyleSheet("color: #8B949E;")
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse)
        
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.preview)
        self.play_btn.setEnabled(False)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear)
        self.clear_btn.setEnabled(False)
        
        layout.addWidget(self.label, 2)
        layout.addWidget(self.browse_btn)
        layout.addWidget(self.play_btn)
        layout.addWidget(self.clear_btn)
    
    def browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Audio", "", "Audio (*.mp3 *.wav *.ogg)")
        if path:
            self.set_file(path)
    
    def set_file(self, path):
        self.current_file = path
        name = path.split('/')[-1]
        self.label.setText(f"🎵 {name}")
        self.label.setStyleSheet("color: #39FF14;")
        self.play_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.fileChanged.emit(path)
    
    def preview(self):
        if self.current_file:
            from core.audio_manager import get_audio_manager
            get_audio_manager().play(self.current_file)
    
    def clear(self):
        self.current_file = None
        self.label.setText("🔔 Default bell")
        self.label.setStyleSheet("color: #8B949E;")
        self.play_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.fileChanged.emit("")
    
    def get_path(self):
        return self.current_file

# ============================================================
# SCHEDULE DIALOG
# ============================================================
class ScheduleDialog(QDialog):
    def __init__(self, parent=None, schedule=None):
        super().__init__(parent)
        self.schedule = schedule
        self.setup_ui()
        if schedule:
            self.load_data()
    
    def setup_ui(self):
        self.setWindowTitle("Schedule" + (" Edit" if self.schedule else " Add"))
        self.setModal(True)
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)
        
        # Name
        layout.addWidget(QLabel("Schedule Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Morning Bell, Break Time")
        layout.addWidget(self.name_input)
        
        # Time
        layout.addWidget(QLabel("Time:"))
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        layout.addWidget(self.time_edit)
        
        # Days
        layout.addWidget(QLabel("Active Days:"))
        days_widget = QWidget()
        days_layout = QHBoxLayout(days_widget)
        self.days = []
        for i, nama in enumerate(['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']):
            cb = QCheckBox(nama)
            self.days.append(cb)
            days_layout.addWidget(cb)
        days_layout.addStretch()
        layout.addWidget(days_widget)
        
        # Presets
        preset_widget = QWidget()
        preset_layout = QHBoxLayout(preset_widget)
        weekdays = QPushButton("Weekdays")
        weekdays.clicked.connect(lambda: self.set_days([0,1,2,3,4]))
        weekend = QPushButton("Weekend")
        weekend.clicked.connect(lambda: self.set_days([5,6]))
        everyday = QPushButton("Everyday")
        everyday.clicked.connect(lambda: self.set_days([0,1,2,3,4,5,6]))
        preset_layout.addWidget(weekdays)
        preset_layout.addWidget(weekend)
        preset_layout.addWidget(everyday)
        preset_layout.addStretch()
        layout.addWidget(preset_widget)
        
        # Audio
        layout.addWidget(QLabel("Custom Audio (optional):"))
        self.audio_picker = AudioPicker()
        layout.addWidget(self.audio_picker)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.set_days([0,1,2,3,4])
    
    def set_days(self, days_list):
        for i, cb in enumerate(self.days):
            cb.setChecked(i in days_list)
    
    def load_data(self):
        if self.schedule:
            self.name_input.setText(self.schedule.name)
            self.time_edit.setTime(QTime(self.schedule.bell_time.hour, self.schedule.bell_time.minute))
            days = self.schedule.get_days_list()
            self.set_days(days)
            if self.schedule.audio_file:
                self.audio_picker.set_file(self.schedule.audio_file)
    
    def get_data(self):
        days = [i for i, cb in enumerate(self.days) if cb.isChecked()]
        t = self.time_edit.time()
        return {
            'name': self.name_input.text(),
            'hour': t.hour(),
            'minute': t.minute(),
            'days': days if days else [0,1,2,3,4],
            'audio_file': self.audio_picker.get_path()
        }
    
    def accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "Schedule name is required")
            return
        super().accept()

# ============================================================
# MAIN WINDOW
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = get_app()
        self.event_manager = get_event_manager()
        self.current_profile_id = None
        self.next_bell_id = None
        self.clock_timer = None
        self.status_timer = None
        self.next_bell_timer = None
        self.table_model = None
        self.proxy_model = None

        # ========== THREAD-SAFE BRIDGE ==========
        self.bridge = UiBridge()
        self.bridge.systemStarted.connect(self.on_system_started)
        self.bridge.systemStopped.connect(self.on_system_stopped)
        self.bridge.schedulesReloaded.connect(self.on_schedules_reloaded)
        self.bridge.profilesUpdated.connect(self.on_profiles_updated)
        self.bridge.profileActivated.connect(self.on_profile_activated)
        
        # Backend events -> marshalled ke GUI thread via bridge (HANYA SEKALI)
        self.event_manager.on('system_started', lambda *_: self.bridge.systemStarted.emit())
        self.event_manager.on('system_stopped', lambda *_: self.bridge.systemStopped.emit())
        self.event_manager.on('schedules_reloaded', lambda *_: self.bridge.schedulesReloaded.emit())
        self.event_manager.on('profiles_updated', lambda *_: self.bridge.profilesUpdated.emit())
        self.event_manager.on('profile_activated', lambda data=None: self.bridge.profileActivated.emit(data or {}))
        
        # Setup UI dan load data (HANYA SEKALI)
        self.setup_ui()
        self.load_profiles()
        self.start_timers()
        self.add_log("System initialized", "INFO")

    def setup_ui(self):
        self.setWindowTitle("SCHOOL BELL AUTOMATION")
        self.setMinimumSize(1000, 600)
        self.resize(1200, 750)
        self.setStyleSheet(INDUSTRIAL_STYLE)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # ========== SUPER BAR ==========
        self.superbar = SuperBar()
        main_layout.addWidget(self.superbar)
        
        # ========== MIDDLE SECTION ==========
        middle_split = QSplitter(Qt.Orientation.Horizontal)
        middle_split.setHandleWidth(5) 
        middle_split.setChildrenCollapsible(True)
        
        # Style handle agar terlihat
        middle_split.setStyleSheet("""
            QSplitter::handle {
                background-color: #30363D;
                width: 5px;
                margin: 0px;
            }
            QSplitter::handle:hover {
                background-color: #1F6FEB;
            }
        """)

        # LEFT: Profile Sidebar (fixed width 220)
        left_panel = QWidget()
        left_panel.setMinimumWidth(150)
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 5, 0)
        left_layout.setSpacing(5)
        
        left_layout.addWidget(QLabel("📂 PROFILES"))
        self.profile_list = QListWidget()
        self.profile_list.itemClicked.connect(self.on_profile_click)
        left_layout.addWidget(self.profile_list)
        
        self.add_profile_btn = QPushButton("+ New Profile")
        self.add_profile_btn.clicked.connect(self.add_profile)
        left_layout.addWidget(self.add_profile_btn)
        
        self.activate_profile_btn = QPushButton("✓ Activate")
        self.activate_profile_btn.setObjectName("primary_btn")
        self.activate_profile_btn.clicked.connect(self.activate_profile)
        left_layout.addWidget(self.activate_profile_btn)
        
        self.delete_profile_btn = QPushButton("🗑 Delete")
        self.delete_profile_btn.clicked.connect(self.delete_profile)
        left_layout.addWidget(self.delete_profile_btn)
        
        left_layout.addStretch()
        
        # RIGHT: Tab Widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: Schedules
        schedules_tab = QWidget()
        schedules_layout = QVBoxLayout(schedules_tab)
        schedules_layout.setSpacing(5)

        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(self.edit_schedule)
        schedules_layout.addWidget(self.table)

        # Action bar
        action_bar = QHBoxLayout()
        action_bar.setSpacing(8)

        self.add_btn = QPushButton("➕ Add")
        self.add_btn.setObjectName("primary_btn")
        self.add_btn.clicked.connect(self.add_schedule)
        action_bar.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.clicked.connect(self.edit_schedule)
        action_bar.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑 Delete")
        self.delete_btn.clicked.connect(self.delete_schedule)
        action_bar.addWidget(self.delete_btn)

        self.ring_btn = QPushButton("🔊 Test")
        self.ring_btn.clicked.connect(self.test_ring)
        action_bar.addWidget(self.ring_btn)

        action_bar.addStretch()
        
        # SINGLE TOGGLE BUTTON (Start/Stop)
        self.toggle_btn = QPushButton("⏹ STOP SYSTEM")
        self.toggle_btn.setObjectName("stop_btn")
        self.toggle_btn.clicked.connect(self.toggle_system)
        action_bar.addWidget(self.toggle_btn)
        
        self.reload_btn = QPushButton("⟳ Reload")
        self.reload_btn.clicked.connect(self.reload_schedules)
        action_bar.addWidget(self.reload_btn)
        
        schedules_layout.addLayout(action_bar)
        
        self.tab_widget.addTab(schedules_tab, "📋 Schedules")
        
        # Tab 2: History
        self.history_tab = HistoryTab(self.app.schedule_manager)
        self.tab_widget.addTab(self.history_tab, "📜 History")
        
        # Tab 3: Settings
        self.settings_tab = SettingsTab(self.app)
        self.tab_widget.addTab(self.settings_tab, "⚙ Settings")
        
        middle_split.addWidget(left_panel)
        middle_split.addWidget(self.tab_widget)
        middle_split.setSizes([220, self.width() - 220])
        main_layout.addWidget(middle_split, 1)
        
        # ========== LOG CONSOLE ==========
        log_header = QHBoxLayout()
        log_header.addWidget(QLabel("📋 EVENT LOG"))
        log_header.addStretch()
        self.clear_log_btn = QPushButton("Clear")
        self.clear_log_btn.clicked.connect(lambda: self.log_console.clear())
        log_header.addWidget(self.clear_log_btn)
        main_layout.addLayout(log_header)
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumHeight(120)
        self.log_console.setMinimumHeight(80)
        main_layout.addWidget(self.log_console)
        
        # Footer
        footer = QLabel("SCHOOL BELL AUTOMATION v1.0 | Ravaa Creative © 2026")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #8B949E; font-size: 10px; padding: 4px;")
        main_layout.addWidget(footer)
        
        # Set table column widths properly
        self.table.setColumnWidth(0, 300)  # Nama Jadwal - lebih lebar
        self.table.setColumnWidth(1, 70)   # Jam
        self.table.setColumnWidth(2, 130)  # Hari
        self.table.setColumnWidth(3, 100)  # Suara
        self.table.setColumnWidth(4, 80)   # Status

    def on_system_started(self):
        self.add_log("System started via remote", "INFO")
        self.update_system_status()

    def on_system_stopped(self):
        self.add_log("System stopped via remote", "WARNING")
        self.update_system_status()
    
    def on_schedules_reloaded(self):
        """Called when schedules are reloaded"""
        self.add_log("Schedules reloaded", "INFO")
        self.load_schedules()
        self.update_next_bell_highlight()

    def on_profiles_updated(self):
        """Called when profiles change (add/delete)"""
        self.add_log("Profiles updated", "INFO")
        self.load_profiles()
    
    def on_profile_activated(self, data):
        """Called when profile is activated from web"""
        profile_id = data.get('profile_id')
        self.add_log(f"Profile activated from web: {profile_id}", "INFO")
        self.load_profiles()
        if profile_id:
            self.current_profile_id = profile_id
            self.load_schedules()
            self._update_next_bell_display()

    def toggle_system(self):
        if self.app.scheduler.running:
            # Running -> Stop
            self.app.scheduler.stop()
            self.add_log("System STOPPED", "WARNING")
            self.superbar.set_running(False)
            self.toggle_btn.setText("▶ START SYSTEM")
            self.toggle_btn.setObjectName("start_btn")
        else:
            # Stopped -> Start
            self.app.scheduler.start()
            self.add_log("System STARTED", "SUCCESS")
            self.superbar.set_running(True)
            self.toggle_btn.setText("⏹ STOP SYSTEM")
            self.toggle_btn.setObjectName("stop_btn")
        self.toggle_btn.style().unpolish(self.toggle_btn)
        self.toggle_btn.style().polish(self.toggle_btn)
        
    def add_log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {"INFO": "#39FF14", "WARNING": "#FFA500", "ERROR": "#F85149", "SUCCESS": "#1F6FEB"}
        color = colors.get(level, "#E6EDF3")
        self.log_console.append(f'<span style="color: #8B949E;">[{timestamp}]</span> <span style="color: {color};">[{level}]</span> {msg}')
        scroll = self.log_console.verticalScrollBar()
        scroll.setValue(scroll.maximum())
    
    def load_profiles(self):
        print("DEBUG: load_profiles called")
        profiles = self.app.schedule_manager.get_all_profiles()
        self.profile_list.clear()
        for p in profiles:
            item = QListWidgetItem()
            if p.is_active:
                item.setText(f"● {p.name}")
                item.setForeground(QColor("#39FF14"))
            else:
                item.setText(p.name)
            item.setData(Qt.ItemDataRole.UserRole, p.id)
            self.profile_list.addItem(item)
        
        active = self.app.schedule_manager.get_active_profile()
        if active:
            print(f"DEBUG: Active profile found: {active.name} (id={active.id})")
            self.superbar.update_profile(active.name)
            self.current_profile_id = active.id
            self.load_schedules()
        else:
            print("DEBUG: No active profile found")
            self.current_profile_id = None
            self.superbar.update_profile("None")
            if hasattr(self, 'table_model') and self.table_model:
                self.table_model.refresh([])
            if hasattr(self, 'history_tab'):
                self.history_tab.load_history()

    def _get_schedule_from_selection(self):
        """Get schedule from current selection (handles proxy model)"""
        selected = self.table.selectedIndexes()
        if not selected:
            return None
        proxy_index = selected[0]
        
        # Map proxy index ke source model index
        if hasattr(self, 'proxy_model'):
            source_index = self.proxy_model.mapToSource(proxy_index)
        else:
            source_index = proxy_index
        
        row = source_index.row()
        if hasattr(self, 'table_model') and 0 <= row < len(self.table_model.schedules):
            return self.table_model.schedules[row]
        return None

    def load_schedules(self):
        if not self.current_profile_id:
            print("DEBUG: No profile selected, returning")
            return
        
        schedules = self.app.schedule_manager.get_schedules_by_profile(self.current_profile_id, include_inactive=True)
        
        if not hasattr(self, 'table_model') or self.table_model is None:
            print("DEBUG: Creating new table model")
            self.table_model = ScheduleTableModel(schedules)
            
            from PyQt6.QtCore import QSortFilterProxyModel
            self.proxy_model = QSortFilterProxyModel()
            self.proxy_model.setSourceModel(self.table_model)
            self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.table.setModel(self.proxy_model)
            self.table.setSortingEnabled(True)
            self.table.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        else:
            self.table_model.refresh(schedules, self.next_bell_id)
        
        if hasattr(self, 'history_tab'):
            self.history_tab.load_history()
        
    def update_next_bell_highlight(self):
        if not self.current_profile_id:
            return
        
        status = self.app.get_status()
        next_bell = status['scheduler']['next_bell']
        next_name = None
        next_id = None
        
        if next_bell:
            if hasattr(next_bell, 'tzinfo') and next_bell.tzinfo:
                next_bell = next_bell.replace(tzinfo=None)
            
            schedules = self.app.schedule_manager.get_schedules_by_profile(self.current_profile_id)
            now = datetime.now()
            
            # Find next schedule
            for s in schedules:
                if not s.is_active:
                    continue
                bell_today = datetime(now.year, now.month, now.day, s.bell_time.hour, s.bell_time.minute)
                if bell_today > now:
                    if not next_id or bell_today < next_bell:
                        next_bell = bell_today
                        next_name = s.name
                        next_id = s.id
                    break
            
            if next_id:
                self.next_bell_id = next_id
                self.superbar.update_next_bell(next_bell, next_name)
            else:
                self.superbar.update_next_bell(None, None)
        else:
            self.superbar.update_next_bell(None, None)
            self.next_bell_id = None
        
        if hasattr(self, 'table_model'):
            self.table_model.refresh(self.table_model.schedules, self.next_bell_id)
    
    def on_profile_click(self, item):
        self.current_profile_id = item.data(Qt.ItemDataRole.UserRole)
        self.load_schedules()
        self.update_next_bell_highlight()
    
    def add_profile(self):
        name, ok = QInputDialog.getText(self, "New Profile", "Profile name:")
        if ok and name:
            self.app.schedule_manager.create_profile(name)
            self.load_profiles()
            self.add_log(f"Profile '{name}' created", "SUCCESS")
    
    def activate_profile(self):
        item = self.profile_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Select a profile first")
            return
        profile_id = item.data(Qt.ItemDataRole.UserRole)
        if self.app.schedule_manager.set_active_profile(profile_id):
            self.app.reload_schedules()
            self.load_profiles()
            self.update_next_bell_highlight()
            self.add_log(f"Profile activated", "SUCCESS")

            try:
                from web.server import socketio
                socketio.emit('profile_activated', {'profile_id': profile_id})
                socketio.emit('schedules_updated')
                socketio.emit('profiles_updated')
            except Exception as e:
                self.add_log(f"Socket sync failed: {e}", "WARNING")
    
    def delete_profile(self):
        item = self.profile_list.currentItem()
        if not item:
            return
        profile_id = item.data(Qt.ItemDataRole.UserRole)
        active = self.app.schedule_manager.get_active_profile()
        if active and active.id == profile_id:
            QMessageBox.warning(self, "Error", "Cannot delete active profile")
            return
        if QMessageBox.question(self, "Delete", "Delete this profile?") == QMessageBox.StandardButton.Yes:
            self.app.schedule_manager.delete_profile(profile_id)
            self.load_profiles()
            self.add_log("Profile deleted", "WARNING")
    
    def add_schedule(self):
        if not self.current_profile_id:
            QMessageBox.warning(self, "Error", "Select a profile first")
            return
        dialog = ScheduleDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            t = time(data['hour'], data['minute'])
            self.app.schedule_manager.add_schedule(
                profile_id=self.current_profile_id,
                name=data['name'],
                bell_time=t,
                days=data['days'],
                audio_file=data['audio_file']
            )
            self.app.reload_schedules()
            self.load_schedules()
            self.update_next_bell_highlight()
            self.add_log(f"Schedule '{data['name']}' added", "SUCCESS")
    
    def edit_schedule(self):
        schedule = self._get_schedule_from_selection()
        if not schedule:
            return
        
        dialog = ScheduleDialog(self, schedule)
        if dialog.exec():
            data = dialog.get_data()
            t = time(data['hour'], data['minute'])
            self.app.schedule_manager.update_schedule(
                schedule.id,
                name=data['name'],
                bell_time=t,
                days_of_week=','.join(str(d) for d in data['days']),
                audio_file=data['audio_file']
            )
            self.app.reload_schedules()
            self.load_schedules()
            self.update_next_bell_highlight()
            self.add_log(f"Schedule '{data['name']}' updated", "INFO")

    def delete_schedule(self):
        schedule = self._get_schedule_from_selection()
        if not schedule:
            return
        if QMessageBox.question(self, "Delete", f"Delete '{schedule.name}'?") == QMessageBox.StandardButton.Yes:
            self.app.schedule_manager.delete_schedule(schedule.id)
            self.app.reload_schedules()
            self.load_schedules()
            self.update_next_bell_highlight()
            self.add_log(f"Schedule '{schedule.name}' deleted", "WARNING")

    def test_ring(self):
        schedule = self._get_schedule_from_selection()
        if not schedule:
            QMessageBox.information(self, "Info", "Select a schedule to test")
            return
        self.app.audio_manager.play(schedule.audio_file)
        self.add_log(f"Test ring: {schedule.name}", "INFO")
    
    def _find_next_schedule_today(self, schedules):
        """Find next schedule today - CORRECT algorithm"""
        now = datetime.now()
        candidates = []

        for s in schedules:
            if not s.is_active:
                continue

            days = s.get_days_list()
            if now.weekday() not in days:
                continue

            bell_dt = datetime(now.year, now.month, now.day, s.bell_time.hour, s.bell_time.minute)

            if bell_dt > now:
                candidates.append((bell_dt, s))

        if not candidates:
            return None, None, None

        candidates.sort(key=lambda x: x[0])
        bell_dt, sched = candidates[0]
        return bell_dt, sched.name, sched.id

    def start_system(self):
        if not self.app.scheduler.running:
            self.app.scheduler.start()
            self.add_log("System STARTED", "SUCCESS")
            self.superbar.set_running(True)
    
    def stop_system(self):
        if self.app.scheduler.running:
            self.app.scheduler.stop()
            self.add_log("System STOPPED", "WARNING")
            self.superbar.set_running(False)
    
    def emergency_stop(self):
        if QMessageBox.question(self, "EMERGENCY STOP", "Stop all bells immediately?") == QMessageBox.StandardButton.Yes:
            self.app.audio_manager.stop()
            self.add_log("EMERGENCY STOP - All bells silenced", "ERROR")
    
    def reload_schedules(self):
        self.app.reload_schedules()
        self.load_schedules()
        self.update_next_bell_highlight()
        self.add_log("Schedules reloaded", "INFO")
    
    def update_system_status(self):
        """Update status - dipanggil hanya saat ada perubahan"""
        status = self.app.get_status()
        is_running = status['scheduler']['running']
        self.superbar.set_running(is_running)
        
        if is_running:
            self.toggle_btn.setText("⏹ STOP SYSTEM")
            self.toggle_btn.setObjectName("stop_btn")
        else:
            self.toggle_btn.setText("▶ START SYSTEM")
            self.toggle_btn.setObjectName("start_btn")
        self.toggle_btn.style().unpolish(self.toggle_btn)
        self.toggle_btn.style().polish(self.toggle_btn)

        self._update_next_bell_display()
    
    def _update_next_bell_only(self):
        """Update next bell highlight tanpa reload seluruh tabel"""
        if not self.current_profile_id:
            return
        
        status = self.app.get_status()
        next_bell = status['scheduler']['next_bell']
        next_id = None
        
        if next_bell:
            if hasattr(next_bell, 'tzinfo') and next_bell.tzinfo:
                next_bell = next_bell.replace(tzinfo=None)
            
            schedules = self.app.schedule_manager.get_schedules_by_profile(self.current_profile_id)
            now = datetime.now()
            
            for s in schedules:
                if not s.is_active:
                    continue
                bell_today = datetime(now.year, now.month, now.day, s.bell_time.hour, s.bell_time.minute)
                if bell_today > now:
                    next_id = s.id
                    break
        
        # Update highlight tanpa reload
        if self.next_bell_id != next_id:
            self.next_bell_id = next_id
            if hasattr(self, 'table_model'):
                self.table_model.refresh(self.table_model.schedules, self.next_bell_id)
                
    def start_timers(self):
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.superbar.update_time)
        self.clock_timer.start(1000)

        self.next_bell_timer = QTimer()
        self.next_bell_timer.timeout.connect(self._update_next_bell_display)
        self.next_bell_timer.start(1000)
        
        self.superbar.update_time()
        self._update_next_bell_display()
    
    def _update_status_only(self):
        """Update status tanpa menyentuh selection tabel"""
        status = self.app.get_status()
        is_running = status['scheduler']['running']
        self.superbar.set_running(is_running)
        
        # Update toggle button text
        if is_running:
            self.toggle_btn.setText("⏹ STOP SYSTEM")
            self.toggle_btn.setObjectName("stop_btn")
        else:
            self.toggle_btn.setText("▶ START SYSTEM")
            self.toggle_btn.setObjectName("start_btn")
        self.toggle_btn.style().unpolish(self.toggle_btn)
        self.toggle_btn.style().polish(self.toggle_btn)
        
        # Update next bell info di superbar TANPA refresh tabel
        self._update_next_bell_display()

    def _update_next_bell_display(self):
        """Update next bell display dan highlight - FIXED algorithm"""
        if not self.current_profile_id:
            return
        
        schedules = self.app.schedule_manager.get_schedules_by_profile(self.current_profile_id)
        next_bell, next_name, new_next_id = self._find_next_schedule_today(schedules)
        
        if next_bell:
            self.superbar.update_next_bell(next_bell, next_name)
            
            if hasattr(self, 'table_model') and self.next_bell_id != new_next_id:
                self.next_bell_id = new_next_id
                self.table_model.next_bell_id = new_next_id
                if self.table_model.rowCount() > 0:
                    for row in range(self.table_model.rowCount()):
                        index = self.table_model.index(row, 0)
                        self.table.update(index)
        else:
            self.superbar.update_next_bell(None, None)
            if self.next_bell_id is not None:
                self.next_bell_id = None
                if hasattr(self, 'table_model'):
                    self.table_model.next_bell_id = None
        
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 
            "Exit", 
            "Stop scheduler and exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.app.shutdown_all()  # Use shutdown_all instead of just stop()
            except Exception as e:
                QMessageBox.critical(self, "Shutdown Error", f"Error during shutdown:\n{str(e)}")
            event.accept()
        else:
            event.ignore()

# ============================================================
# RUN
# ============================================================
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