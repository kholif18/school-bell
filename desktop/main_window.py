# desktop/main_window.py (FINAL VERSION)
import sys
from datetime import datetime, time as datetime_time, timedelta
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from core.app_core import get_app

# ============================================================
# DARK STYLE - INDUSTRIAL NOC THEME
# ============================================================
DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Consolas', monospace;
}

/* Sidebar */
QListWidget {
    background-color: #16213e;
    border: none;
    border-radius: 8px;
    padding: 5px;
}

QListWidget::item {
    padding: 12px;
    border-radius: 6px;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: #0f3460;
    border-left: 3px solid #4CAF50;
}

QListWidget::item:hover:!selected {
    background-color: #1a2a4a;
}

/* Timeline Widget */
#timeline_widget {
    background-color: #16213e;
    border-radius: 8px;
}

.timeline-item {
    background-color: #0f3460;
    border-radius: 6px;
    padding: 8px;
    margin: 4px;
}

.timeline-item:hover {
    background-color: #1a4a7a;
}

.timeline-time {
    font-size: 14px;
    font-weight: bold;
    color: #4CAF50;
}

.timeline-name {
    font-size: 14px;
    font-weight: bold;
}

.timeline-days {
    font-size: 11px;
    color: #888;
}

/* Table (as fallback) */
QTableView {
    background-color: #16213e;
    border: none;
    border-radius: 8px;
    alternate-background-color: #1a2542;
    gridline-color: #2a3a5a;
}

QTableView::item {
    padding: 10px;
}

QHeaderView::section {
    background-color: #0f3460;
    padding: 10px;
    border: none;
    font-weight: bold;
}

/* Buttons */
QPushButton {
    background-color: #0f3460;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1a4a7a;
}

QPushButton#danger_btn {
    background-color: #c62828;
}

QPushButton#danger_btn:hover {
    background-color: #e53935;
}

QPushButton#success_btn {
    background-color: #2e7d32;
}

QPushButton#success_btn:hover {
    background-color: #388e3c;
}

QPushButton#warning_btn {
    background-color: #ff9800;
    color: #1a1a2e;
}

/* Log Console */
QTextEdit {
    background-color: #0a0a1a;
    border: 1px solid #2a3a5a;
    border-radius: 6px;
    font-family: 'Consolas', monospace;
    font-size: 11px;
}

/* Status Bar */
QStatusBar {
    background-color: #0f3460;
}
"""

# ============================================================
# TIMELINE ITEM WIDGET
# ============================================================
class TimelineItem(QWidget):
    clicked = pyqtSignal(object)
    
    def __init__(self, schedule, parent=None):
        super().__init__(parent)
        self.schedule = schedule
        self.setup_ui()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Time label
        self.time_label = QLabel(self.schedule.bell_time.strftime('%H:%M'))
        self.time_label.setFixedWidth(60)
        self.time_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(self.time_label)
        
        # Bell icon
        bell_icon = QLabel("🔔")
        bell_icon.setFixedWidth(30)
        layout.addWidget(bell_icon)
        
        # Name label
        self.name_label = QLabel(self.schedule.name)
        self.name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.name_label, 1)
        
        # Days label
        days = self.schedule.get_days_list()
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        days_str = ', '.join(day_names[d] for d in days if d < len(day_names))
        self.days_label = QLabel(days_str)
        self.days_label.setStyleSheet("font-size: 11px; color: #888;")
        self.days_label.setFixedWidth(150)
        layout.addWidget(self.days_label)
        
        # Audio icon if custom
        if self.schedule.audio_file:
            audio_icon = QLabel("🎵")
            audio_icon.setFixedWidth(30)
            layout.addWidget(audio_icon)
        
        # Active indicator
        self.active_indicator = QLabel("✓" if self.schedule.is_active else "✗")
        self.active_indicator.setStyleSheet(
            "color: #4CAF50; font-weight: bold;" if self.schedule.is_active 
            else "color: #f44336; font-weight: bold;"
        )
        self.active_indicator.setFixedWidth(30)
        layout.addWidget(self.active_indicator)
        
        self.setObjectName("timeline-item")
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.schedule)

# ============================================================
# TIMELINE VIEW (Main Widget)
# ============================================================
class TimelineView(QScrollArea):
    schedule_selected = pyqtSignal(object)
    schedule_double_clicked = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.schedules = []
        self.setup_ui()
    
    def setup_ui(self):
        self.setWidgetResizable(True)
        self.setStyleSheet("background-color: #16213e; border-radius: 8px;")
        
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(4)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.setWidget(self.container)
    
    def set_schedules(self, schedules):
        self.schedules = schedules
        # Clear existing
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add time labels group
        current_hour = None
        for schedule in sorted(schedules, key=lambda x: x.bell_time):
            # Add hour separator
            hour = schedule.bell_time.hour
            if hour != current_hour:
                current_hour = hour
                hour_label = QLabel(f"━━━ {hour:02d}:00 ━━━")
                hour_label.setStyleSheet("color: #FF9800; font-weight: bold; padding: 8px 0 4px 0;")
                self.layout.addWidget(hour_label)
            
            item = TimelineItem(schedule)
            item.clicked.connect(self.on_item_clicked)
            item.mouseDoubleClickEvent = lambda e, s=schedule: self.schedule_double_clicked.emit(s)
            self.layout.addWidget(item)
        
        if not schedules:
            empty_label = QLabel("📭 No schedules in this profile")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("padding: 50px; color: #888; font-size: 16px;")
            self.layout.addWidget(empty_label)
    
    def on_item_clicked(self, schedule):
        self.schedule_selected.emit(schedule)

# ============================================================
# PROFILE SIDEBAR (Fixed)
# ============================================================
class ProfileSidebar(QWidget):
    profile_selected = pyqtSignal(int)
    profile_activate = pyqtSignal(int)
    profile_delete = pyqtSignal(int)
    profile_add = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel("📂 SCHEDULE PROFILES")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        layout.addWidget(header)
        
        self.profile_list = QListWidget()
        self.profile_list.itemClicked.connect(self.on_profile_clicked)
        layout.addWidget(self.profile_list)
        
        # Profile actions
        self.add_btn = QPushButton("+ New Profile")
        self.add_btn.clicked.connect(lambda: self.profile_add.emit())
        layout.addWidget(self.add_btn)
        
        self.activate_btn = QPushButton("✓ Activate Profile")
        self.activate_btn.setObjectName("success_btn")
        self.activate_btn.clicked.connect(self.activate_current)
        layout.addWidget(self.activate_btn)
        
        self.delete_btn = QPushButton("🗑 Delete Profile")
        self.delete_btn.setObjectName("danger_btn")
        self.delete_btn.clicked.connect(self.delete_current)
        layout.addWidget(self.delete_btn)
        
        layout.addStretch()
    
    def load_profiles(self, profiles):
        self.profile_list.clear()
        for i, p in enumerate(profiles):
            item = QListWidgetItem()
            text = f"● {p.name}" if p.is_active else p.name
            item.setText(text)
            item.setData(Qt.ItemDataRole.UserRole, p.id)
            item.setData(Qt.ItemDataRole.UserRole + 1, p.is_active)
            
            if p.is_active:
                item.setForeground(QColor("#4CAF50"))
                item.setBackground(QColor("#0f3460"))
            
            self.profile_list.addItem(item)
    
    def on_profile_clicked(self, item):
        profile_id = item.data(Qt.ItemDataRole.UserRole)
        self.profile_selected.emit(profile_id)
    
    def get_selected_profile_id(self):
        item = self.profile_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None
    
    def activate_current(self):
        profile_id = self.get_selected_profile_id()
        if profile_id:
            self.profile_activate.emit(profile_id)
    
    def delete_current(self):
        profile_id = self.get_selected_profile_id()
        if profile_id:
            self.profile_delete.emit(profile_id)

# ============================================================
# LOG CONSOLE
# ============================================================
class LogConsole(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumHeight(100)
        self.setMinimumHeight(80)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    
    def add_log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "#4CAF50",
            "WARNING": "#FF9800",
            "ERROR": "#f44336",
            "SUCCESS": "#2196F3"
        }
        color = colors.get(level, "#e0e0e0")
        
        html = f'[{timestamp}] <span style="color: {color};">[{level}]</span> {message}<br>'
        self.append(html)
        
        # Auto scroll
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

# ============================================================
# ADD/EDIT SCHEDULE DIALOG
# ============================================================
class ScheduleDialog(QDialog):
    def __init__(self, parent=None, schedule=None):
        super().__init__(parent)
        self.schedule = schedule
        self.setup_ui()
        if schedule:
            self.load_schedule()
    
    def setup_ui(self):
        self.setWindowTitle("Schedule" + (" Edit" if self.schedule else " Add"))
        self.setModal(True)
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Morning Bell, Break Time")
        form_layout.addRow("Bell Name:", self.name_input)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        form_layout.addRow("Time:", self.time_edit)
        
        days_container = QWidget()
        days_layout = QHBoxLayout(days_container)
        days_layout.setContentsMargins(0, 0, 0, 0)
        self.day_checkboxes = []
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, name in enumerate(day_names):
            cb = QCheckBox(name)
            self.day_checkboxes.append(cb)
            days_layout.addWidget(cb)
        days_layout.addStretch()
        form_layout.addRow("Active Days:", days_container)
        
        # Quick presets
        preset_container = QWidget()
        preset_layout = QHBoxLayout(preset_container)
        weekdays_btn = QPushButton("Weekdays")
        weekdays_btn.clicked.connect(lambda: self.set_days([0,1,2,3,4]))
        weekend_btn = QPushButton("Weekend")
        weekend_btn.clicked.connect(lambda: self.set_days([5,6]))
        everyday_btn = QPushButton("Everyday")
        everyday_btn.clicked.connect(lambda: self.set_days([0,1,2,3,4,5,6]))
        preset_layout.addWidget(weekdays_btn)
        preset_layout.addWidget(weekend_btn)
        preset_layout.addWidget(everyday_btn)
        preset_layout.addStretch()
        form_layout.addRow("Presets:", preset_container)
        
        layout.addWidget(form_widget)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.set_days([0, 1, 2, 3, 4])
    
    def set_days(self, days):
        for i, cb in enumerate(self.day_checkboxes):
            cb.setChecked(i in days)
    
    def load_schedule(self):
        if self.schedule:
            self.name_input.setText(self.schedule.name)
            self.time_edit.setTime(QTime(
                self.schedule.bell_time.hour,
                self.schedule.bell_time.minute
            ))
            days = self.schedule.get_days_list()
            for i, cb in enumerate(self.day_checkboxes):
                cb.setChecked(i in days)
    
    def get_data(self):
        days = [i for i, cb in enumerate(self.day_checkboxes) if cb.isChecked()]
        time_val = self.time_edit.time()
        return {
            'name': self.name_input.text().strip(),
            'hour': time_val.hour(),
            'minute': time_val.minute(),
            'days': days if days else [0, 1, 2, 3, 4]
        }
    
    def accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter schedule name")
            return
        super().accept()

# ============================================================
# MAIN WINDOW
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = get_app()
        self.current_profile_id = None
        self.current_schedules = []
        self.setup_ui()
        self.load_profiles()
        self.start_refresh_timer()
        self.add_log("Application started", "SUCCESS")
    
    def setup_ui(self):
        self.setWindowTitle("🏫 School Bell Automation System - NOC Control Panel")
        self.setGeometry(50, 50, 1300, 800)
        self.setStyleSheet(DARK_STYLE)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # ========== LEFT PANEL (20%) ==========
        left_panel = QWidget()
        left_panel.setFixedWidth(260)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.profile_sidebar = ProfileSidebar(self)
        self.profile_sidebar.profile_selected.connect(self.on_profile_selected)
        self.profile_sidebar.profile_activate.connect(self.activate_profile)
        self.profile_sidebar.profile_delete.connect(self.delete_profile)
        self.profile_sidebar.profile_add.connect(self.add_profile)
        left_layout.addWidget(self.profile_sidebar)
        
        main_layout.addWidget(left_panel)
        
        # ========== RIGHT PANEL (80%) ==========
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        
        # Top status bar
        status_bar = QWidget()
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(10, 8, 10, 8)
        
        self.active_profile_label = QLabel("📋 Active: --")
        self.active_profile_label.setStyleSheet("background-color: #0f3460; padding: 6px 12px; border-radius: 6px; font-weight: bold;")
        status_layout.addWidget(self.active_profile_label)
        
        # Compact clock
        self.clock_label = QLabel("🕒 --:--:--")
        self.clock_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        status_layout.addWidget(self.clock_label)
        
        self.date_label = QLabel("--")
        self.date_label.setStyleSheet("color: #888;")
        status_layout.addWidget(self.date_label)
        
        self.countdown_label = QLabel("⏳ Next: --:--:--")
        self.countdown_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        status_layout.addWidget(self.countdown_label)
        
        status_layout.addStretch()
        
        self.scheduler_status = QLabel("⚙ Running")
        self.scheduler_status.setStyleSheet("background-color: #2e7d32; padding: 4px 10px; border-radius: 4px;")
        status_layout.addWidget(self.scheduler_status)
        
        right_layout.addWidget(status_bar)
        
        # Timeline/Table area (DOMINANT)
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget::pane { background-color: #16213e; border-radius: 8px; }")
        
        # Timeline View
        self.timeline_view = TimelineView()
        self.timeline_view.schedule_selected.connect(self.on_schedule_selected)
        self.timeline_view.schedule_double_clicked.connect(self.edit_schedule)
        self.tab_widget.addTab(self.timeline_view, "📅 Timeline View")
        
        # Table View (alternative)
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.doubleClicked.connect(self.edit_schedule)
        self.tab_widget.addTab(self.table_view, "📊 Table View")
        
        right_layout.addWidget(self.tab_widget, 1)  # Stretch factor 1 = takes most space
        
        # Action buttons
        action_bar = QWidget()
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(10, 5, 10, 5)
        
        self.add_btn = QPushButton("➕ Add Bell")
        self.add_btn.clicked.connect(self.add_schedule)
        action_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.clicked.connect(self.edit_schedule)
        action_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑 Delete")
        self.delete_btn.clicked.connect(self.delete_schedule)
        action_layout.addWidget(self.delete_btn)
        
        self.manual_btn = QPushButton("🔊 Manual Ring")
        self.manual_btn.setObjectName("warning_btn")
        self.manual_btn.clicked.connect(self.manual_ring)
        action_layout.addWidget(self.manual_btn)
        
        action_layout.addStretch()
        
        self.reload_btn = QPushButton("⟳ Reload")
        self.reload_btn.clicked.connect(self.reload_data)
        action_layout.addWidget(self.reload_btn)
        
        # Volume
        volume_label = QLabel("🔊")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.app.config.get('audio.volume', 80))
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.volume_value = QLabel(f"{self.volume_slider.value()}%")
        action_layout.addWidget(volume_label)
        action_layout.addWidget(self.volume_slider)
        action_layout.addWidget(self.volume_value)
        
        right_layout.addWidget(action_bar)
        
        # Log console (bottom)
        log_label = QLabel("📋 LIVE EVENT LOG")
        log_label.setStyleSheet("font-weight: bold; font-size: 11px; margin-top: 4px;")
        right_layout.addWidget(log_label)
        
        self.log_console = LogConsole()
        right_layout.addWidget(self.log_console)
        
        main_layout.addWidget(right_panel, 1)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Update clock
        self.update_clock()
        clock_timer = QTimer()
        clock_timer.timeout.connect(self.update_clock)
        clock_timer.start(1000)
    
    def update_clock(self):
        now = datetime.now()
        self.clock_label.setText(f"🕒 {now.strftime('%H:%M:%S')}")
        self.date_label.setText(now.strftime('%d/%m/%Y'))
    
    def add_log(self, message, level="INFO"):
        self.log_console.add_log(message, level)
    
    def change_volume(self, value):
        self.volume_value.setText(f"{value}%")
        self.app.audio_manager.set_volume(value)
        self.app.config.set('audio.volume', value)
    
    def load_profiles(self):
        profiles = self.app.schedule_manager.get_all_profiles()
        self.profile_sidebar.load_profiles(profiles)
        
        active = self.app.schedule_manager.get_active_profile()
        if active:
            self.active_profile_label.setText(f"📋 Active: {active.name}")
            self.current_profile_id = active.id
            self.load_schedules(active.id)
    
    def load_schedules(self, profile_id):
        schedules = self.app.schedule_manager.get_schedules_by_profile(profile_id, include_inactive=True)
        self.current_schedules = schedules
        
        # Update timeline
        self.timeline_view.set_schedules(schedules)
        
        # Update table
        if not hasattr(self, 'table_model'):
            self.table_model = ScheduleTableModel(schedules)
            self.table_view.setModel(self.table_model)
        else:
            self.table_model.refresh(schedules)
        
        active_count = sum(1 for s in schedules if s.is_active)
        self.statusBar().showMessage(f"Profile: {active_count} active schedules | Total: {len(schedules)}")
    
    def on_profile_selected(self, profile_id):
        self.current_profile_id = profile_id
        self.load_schedules(profile_id)
    
    def on_schedule_selected(self, schedule):
        # Highlight in table too
        for row, s in enumerate(self.current_schedules):
            if s.id == schedule.id:
                self.table_view.selectRow(row)
                break
    
    def add_profile(self):
        name, ok = QInputDialog.getText(self, "New Profile", "Profile name:")
        if ok and name:
            desc, ok2 = QInputDialog.getText(self, "Description", "Description (optional):")
            profile_id = self.app.schedule_manager.create_profile(name, desc if ok2 else None)
            if profile_id:
                self.load_profiles()
                self.add_log(f"Created profile: {name}", "SUCCESS")
    
    def activate_profile(self, profile_id):
        if self.app.schedule_manager.set_active_profile(profile_id):
            self.app.reload_schedules()
            self.load_profiles()
            self.add_log(f"Activated profile", "SUCCESS")
    
    def delete_profile(self, profile_id):
        active = self.app.schedule_manager.get_active_profile()
        if active and active.id == profile_id:
            QMessageBox.warning(self, "Warning", "Cannot delete active profile")
            return
        
        reply = QMessageBox.question(self, "Confirm", "Delete this profile and all its schedules?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.app.schedule_manager.delete_profile(profile_id)
            self.load_profiles()
            self.add_log(f"Deleted profile", "WARNING")
    
    def add_schedule(self):
        if not self.current_profile_id:
            QMessageBox.warning(self, "Warning", "Select a profile first")
            return
        
        dialog = ScheduleDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            bell_time = datetime_time(data['hour'], data['minute'])
            self.app.schedule_manager.add_schedule(
                profile_id=self.current_profile_id,
                name=data['name'],
                bell_time=bell_time,
                days=data['days']
            )
            if self.app.scheduler.running:
                self.app.reload_schedules()
            self.load_schedules(self.current_profile_id)
            self.add_log(f"Added: {data['name']} at {data['hour']:02d}:{data['minute']:02d}", "SUCCESS")
    
    def edit_schedule(self):
        # Get selected from current view (timeline or table)
        selected = None
        if self.tab_widget.currentIndex() == 0:  # Timeline tab
            # Timeline selection handled by signal
            pass
        else:  # Table tab
            selection = self.table_view.selectedIndexes()
            if selection:
                row = selection[0].row()
                selected = self.current_schedules[row] if row < len(self.current_schedules) else None
        
        if not selected:
            # Try to get from timeline via stored selection
            return
        
        dialog = ScheduleDialog(self, selected)
        if dialog.exec():
            data = dialog.get_data()
            bell_time = datetime_time(data['hour'], data['minute'])
            self.app.schedule_manager.update_schedule(
                selected.id,
                name=data['name'],
                bell_time=bell_time,
                days_of_week=','.join(str(d) for d in data['days'])
            )
            if self.app.scheduler.running:
                self.app.reload_schedules()
            self.load_schedules(self.current_profile_id)
            self.add_log(f"Updated: {data['name']}", "INFO")
    
    def delete_schedule(self):
        # Get selected from table view
        selection = self.table_view.selectedIndexes()
        if not selection:
            QMessageBox.information(self, "Info", "Select a schedule to delete")
            return
        
        row = selection[0].row()
        schedule = self.current_schedules[row]
        
        reply = QMessageBox.question(self, "Confirm", f"Delete '{schedule.name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.app.schedule_manager.delete_schedule(schedule.id)
            if self.app.scheduler.running:
                self.app.reload_schedules()
            self.load_schedules(self.current_profile_id)
            self.add_log(f"Deleted: {schedule.name}", "WARNING")
    
    def manual_ring(self):
        selection = self.table_view.selectedIndexes()
        if not selection:
            QMessageBox.information(self, "Info", "Select a schedule to test")
            return
        
        row = selection[0].row()
        schedule = self.current_schedules[row]
        
        self.add_log(f"Manual ring: {schedule.name}", "INFO")
        self.app.audio_manager.play(schedule.audio_file)
    
    def reload_data(self):
        if self.app.scheduler.running:
            self.app.reload_schedules()
        self.load_schedules(self.current_profile_id)
        self.add_log("Schedules reloaded", "INFO")
    
    def update_status(self):
        status = self.app.get_status()
        if status['scheduler']['running']:
            active_jobs = status['scheduler']['active_jobs']
            self.scheduler_status.setText(f"⚙ Running ({active_jobs} jobs)")
            self.scheduler_status.setStyleSheet("background-color: #2e7d32; padding: 4px 10px; border-radius: 4px;")
        else:
            self.scheduler_status.setText("⚙ Stopped")
            self.scheduler_status.setStyleSheet("background-color: #c62828; padding: 4px 10px; border-radius: 4px;")
        
        # Update countdown
        next_bell = status['scheduler']['next_bell']
        if next_bell:
            if hasattr(next_bell, 'tzinfo') and next_bell.tzinfo is not None:
                next_bell = next_bell.replace(tzinfo=None)
            now = datetime.now()
            if next_bell > now:
                diff = next_bell - now
                total_seconds = int(diff.total_seconds())
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                self.countdown_label.setText(f"⏳ Next: {minutes:02d}:{seconds:02d}")
            else:
                self.countdown_label.setText("🔔 Ringing soon!")
        else:
            self.countdown_label.setText("⏳ Next: --:--")
    
    def start_refresh_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Exit", "Stop scheduler and exit?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.app.stop()
            event.accept()

# ============================================================
# TABLE MODEL
# ============================================================
class ScheduleTableModel(QAbstractTableModel):
    def __init__(self, schedules=None):
        super().__init__()
        self.schedules = schedules or []
        self.headers = ["Name", "Time", "Days", "Active"]
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.schedules)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        schedule = self.schedules[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return schedule.name
            elif col == 1:
                return schedule.bell_time.strftime('%H:%M')
            elif col == 2:
                days = schedule.get_days_list()
                day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                return ', '.join(day_names[d] for d in days if d < len(day_names))
            elif col == 3:
                return '✓ Active' if schedule.is_active else '✗ Inactive'
        
        elif role == Qt.ItemDataRole.ForegroundRole:
            if col == 3:
                return QColor("#4CAF50") if schedule.is_active else QColor("#f44336")
        
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None
    
    def refresh(self, schedules):
        self.beginResetModel()
        self.schedules = schedules
        self.endResetModel()

# ============================================================
# RUN
# ============================================================
def run_desktop():
    qt_app = QApplication(sys.argv)
    qt_app.setStyle('Fusion')
    
    app = get_app()
    app.initialize()
    app.start()
    
    window = MainWindow()
    window.show()
    
    sys.exit(qt_app.exec())

if __name__ == "__main__":
    run_desktop()