# desktop/main_window.py
import sys
from datetime import time
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from core.app_core import get_app

class ScheduleTableModel(QAbstractTableModel):
    """Model for schedule table"""
    
    def __init__(self, schedules=None):
        super().__init__()
        self.schedules = schedules or []
        self.headers = ["ID", "Name", "Time", "Days", "Audio", "Active"]
    
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
                return str(schedule.id)
            elif col == 1:
                return schedule.name
            elif col == 2:
                return schedule.bell_time.strftime('%H:%M')
            elif col == 3:
                days = schedule.get_days_list()
                day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                return ', '.join(day_names[d] for d in days if d < len(day_names))
            elif col == 4:
                return schedule.audio_file or 'Default'
            elif col == 5:
                return '✓' if schedule.is_active else '✗'
        
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None
    
    def refresh(self, schedules):
        self.beginResetModel()
        self.schedules = schedules
        self.endResetModel()

class AddScheduleDialog(QDialog):
    """Dialog for adding/editing schedule"""
    
    def __init__(self, parent=None, schedule=None):
        super().__init__(parent)
        self.schedule = schedule
        self.setup_ui()
        if schedule:
            self.load_schedule()
    
    def setup_ui(self):
        self.setWindowTitle("Schedule" + (" Edit" if self.schedule else " Add"))
        self.setModal(True)
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        layout.addRow("Name:", self.name_input)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        layout.addRow("Time:", self.time_edit)
        
        # Days checkboxes
        days_layout = QHBoxLayout()
        self.day_checkboxes = []
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, name in enumerate(day_names):
            cb = QCheckBox(name)
            self.day_checkboxes.append(cb)
            days_layout.addWidget(cb)
        layout.addRow("Days:", days_layout)
        
        self.audio_input = QLineEdit()
        self.audio_input.setPlaceholderText("Path to audio file (optional)")
        layout.addRow("Audio File:", self.audio_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        # Set default days (Monday-Friday)
        for i in range(5):
            self.day_checkboxes[i].setChecked(True)
    
    def load_schedule(self):
        """Load schedule data into form"""
        if self.schedule:
            self.name_input.setText(self.schedule.name)
            self.time_edit.setTime(QTime(
                self.schedule.bell_time.hour,
                self.schedule.bell_time.minute
            ))
            days = self.schedule.get_days_list()
            for i, cb in enumerate(self.day_checkboxes):
                cb.setChecked(i in days)
            if self.schedule.audio_file:
                self.audio_input.setText(self.schedule.audio_file)
    
    def get_data(self):
        """Get form data"""
        days = [i for i, cb in enumerate(self.day_checkboxes) if cb.isChecked()]
        time_val = self.time_edit.time()
        return {
            'name': self.name_input.text(),
            'hour': time_val.hour(),
            'minute': time_val.minute(),
            'days': days if days else [0, 1, 2, 3, 4],
            'audio_file': self.audio_input.text() or None
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = get_app()
        self.setup_ui()
        self.load_schedules()
        self.start_refresh_timer()
    
    def setup_ui(self):
        self.setWindowTitle("School Bell Automation System")
        self.setGeometry(100, 100, 1000, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Toolbar
        toolbar = self.addToolBar("Main")
        toolbar.addAction("Add Schedule", self.add_schedule)
        toolbar.addAction("Edit Schedule", self.edit_schedule)
        toolbar.addAction("Delete Schedule", self.delete_schedule)
        toolbar.addAction("Refresh", self.load_schedules)
        toolbar.addSeparator()
        
        # Status indicator
        self.status_label = QLabel()
        toolbar.addWidget(self.status_label)
        
        # Table view
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setAlternatingRowColors(True)
        layout.addWidget(self.table_view)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Update status
        self.update_status()
    
    def load_schedules(self):
        """Load schedules from database"""
        schedules = self.app.schedule_manager.get_all_schedules(include_inactive=True)
        
        if not hasattr(self, 'table_model'):
            self.table_model = ScheduleTableModel(schedules)
            self.table_view.setModel(self.table_model)
            self.table_view.horizontalHeader().setStretchLastSection(True)
        else:
            self.table_model.refresh(schedules)
        
        self.statusBar().showMessage(f"Loaded {len(schedules)} schedules")
    
    def add_schedule(self):
        dialog = AddScheduleDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            from datetime import time
            bell_time = time(data['hour'], data['minute'])
            self.app.schedule_manager.add_schedule(
                name=data['name'],
                bell_time=bell_time,
                days=data['days'],
                audio_file=data['audio_file']
            )
            self.app.reload_schedules()
            self.load_schedules()
            self.statusBar().showMessage("Schedule added successfully")
    
    def edit_schedule(self):
        selected = self.table_view.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a schedule to edit")
            return
        
        row = selected[0].row()
        schedule_id = int(self.table_model.schedules[row].id)
        schedule = self.app.schedule_manager.get_schedule_by_id(schedule_id)
        
        if schedule:
            dialog = AddScheduleDialog(self, schedule)
            if dialog.exec():
                data = dialog.get_data()
                from datetime import time
                bell_time = time(data['hour'], data['minute'])
                self.app.schedule_manager.update_schedule(
                    schedule_id,
                    name=data['name'],
                    bell_time=bell_time,
                    days_of_week=','.join(str(d) for d in data['days']),
                    audio_file=data['audio_file']
                )
                self.app.reload_schedules()
                self.load_schedules()
                self.statusBar().showMessage("Schedule updated successfully")
    
    def delete_schedule(self):
        selected = self.table_view.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a schedule to delete")
            return
        
        reply = QMessageBox.question(self, 'Confirm Delete',
                                    'Are you sure you want to delete this schedule?',
                                    QMessageBox.StandardButton.Yes |
                                    QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected[0].row()
            schedule_id = int(self.table_model.schedules[row].id)
            self.app.schedule_manager.delete_schedule(schedule_id)
            self.app.reload_schedules()
            self.load_schedules()
            self.statusBar().showMessage("Schedule deleted successfully")
    
    def update_status(self):
        """Update status indicator"""
        status = self.app.get_status()
        if status['scheduler']['running']:
            self.status_label.setText(f"🟢 Running | Jobs: {status['scheduler']['active_jobs']}")
        else:
            self.status_label.setText("🔴 Stopped")
    
    def start_refresh_timer(self):
        """Start timer to refresh status periodically"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)  # Every 2 seconds
    
    def closeEvent(self, event):
        """Handle window close"""
        reply = QMessageBox.question(self, 'Confirm Exit',
                                    'Stop scheduler and exit?',
                                    QMessageBox.StandardButton.Yes |
                                    QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.app.stop()
            event.accept()
        else:
            event.ignore()

def run_desktop():
    """Run desktop GUI"""
    qt_app = QApplication(sys.argv)
    
    # Initialize and start app
    app = get_app()
    app.initialize()
    app.start()
    
    # Show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(qt_app.exec())

if __name__ == "__main__":
    run_desktop()