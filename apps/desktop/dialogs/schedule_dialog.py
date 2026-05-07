# apps/desktop/dialogs/schedule_dialog.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTime

from apps.desktop.widgets.audio_picker import AudioPicker


class ScheduleDialog(QDialog):

    SCHOOL_DAYS = [0, 1, 2, 3, 4, 5] 
    WEEKDAYS = [0, 1, 2, 3, 4]
    WEEKEND = [5, 6]
    ALL = [0, 1, 2, 3, 4, 5, 6]
    DAYS = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]

    def __init__(self, app_core, parent=None, schedule=None):
        super().__init__(parent)

        self.app = app_core
        self.schedule = schedule

        self._ui()

        if schedule:
            self._load()
        else:
            self._set_days(self.SCHOOL_DAYS)

    # =====================================================
    # UI
    # =====================================================

    def _ui(self):
        self.setWindowTitle("Edit Schedule" if self.schedule else "Add Schedule")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        self.name = QLineEdit()

        self.time = QTimeEdit()
        self.time.setDisplayFormat("HH:mm")

        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.name)

        layout.addWidget(QLabel("Time"))
        layout.addWidget(self.time)

        self._days(layout)
        self._preset(layout)

        self.is_active = QCheckBox("Active")
        self.is_active.setChecked(True)

        layout.addWidget(self.is_active)

        layout.addWidget(QLabel("Audio"))

        self.audio = AudioPicker(self.app)
        layout.addWidget(self.audio)

        btn = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        btn.accepted.connect(self._ok)
        btn.rejected.connect(self.reject)

        layout.addWidget(btn)

    # =====================================================
    # DAYS
    # =====================================================

    def _days(self, layout):
        box = QHBoxLayout()
        self.checks = []

        for i, d in enumerate(self.DAYS):
            cb = QCheckBox(d)
            self.checks.append(cb)
            box.addWidget(cb)

        layout.addLayout(box)

    def _set_days(self, days):
        for i, cb in enumerate(self.checks):
            cb.setChecked(i in days)

    def _get_days(self):
        return [i for i, cb in enumerate(self.checks) if cb.isChecked()]

    # =====================================================
    # PRESET
    # =====================================================

    def _preset(self, layout):
        layout.addWidget(QLabel("Preset Hari"))

        box = QHBoxLayout()

        btn1 = QPushButton("School")
        btn2 = QPushButton("Weekdays")
        btn3 = QPushButton("Weekend")
        btn4 = QPushButton("All")

        btn1.clicked.connect(lambda: self._set_days(self.SCHOOL_DAYS))
        btn2.clicked.connect(lambda: self._set_days(self.WEEKDAYS))
        btn3.clicked.connect(lambda: self._set_days(self.WEEKEND))
        btn4.clicked.connect(lambda: self._set_days(self.ALL))

        for btn in [btn1, btn2, btn3, btn4]:
            btn.setMaximumHeight(28)
            box.addWidget(btn)

        layout.addLayout(box)

    # =====================================================
    # LOAD
    # =====================================================

    def _load(self):
        s = self.schedule

        self.name.setText(s.name)
        self.time.setTime(QTime(s.bell_time.hour, s.bell_time.minute))
        self._set_days(s.get_days_list())

        self.is_active.setChecked(s.is_active)

        if s.audio_file:
            self.audio.set_value(s.audio_file)

    # =====================================================
    # OUTPUT
    # =====================================================

    def get_data(self):
        t = self.time.time()

        return {
            "name": self.name.text().strip(),
            "hour": t.hour(),
            "minute": t.minute(),
            "days": self._get_days() or self.SCHOOL_DAYS,
            "audio_file": self.audio.get_value(),
            "is_active": self.is_active.isChecked()
        }

    def _ok(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Error", "Name required")
            return

        self.accept()