# desktop/dialogs/schedule_dialog.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTime
from desktop.widgets.audio_picker import AudioPicker

class ScheduleDialog(QDialog):
    def __init__(self, parent=None, schedule=None):
        super().__init__(parent)
        self.schedule = schedule
        self.setup_ui()
        if schedule:
            self.load_data()
        else:
            self.set_days([0,1,2,3,4,5])
    
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
            'days': days if days else [0,1,2,3,4,5],
            'audio_file': self.audio_picker.get_path()
        }
    
    def accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "Schedule name is required")
            return
        super().accept()