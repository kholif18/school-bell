# desktop/widgets/superbar.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from datetime import datetime


class SuperBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("superbar")
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)

        # LEFT
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(2)

        self.profile_label = QLabel("📋 Profile: --")
        self.profile_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.status_indicator = QLabel("🟢 RUNNING")
        self.status_indicator.setObjectName("running_indicator")

        left_layout.addWidget(self.profile_label)
        left_layout.addWidget(self.status_indicator)

        # CENTER
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.clock_label = QLabel("--:--:--")
        self.clock_label.setObjectName("clock_display")

        self.date_label = QLabel("--, -- -- ----")
        self.date_label.setObjectName("date_display")

        center_layout.addWidget(self.clock_label)
        center_layout.addWidget(self.date_label)

        # RIGHT
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        right_layout.addWidget(QLabel("🔔 NEXT BELL"))

        self.next_time_label = QLabel("--:--:--")
        self.next_time_label.setObjectName("next_bell_time")

        self.next_name_label = QLabel("No schedule")
        self.next_name_label.setObjectName("next_bell_name")

        right_layout.addWidget(self.next_time_label)
        right_layout.addWidget(self.next_name_label)

        layout.addWidget(left, 1)
        layout.addWidget(center, 2)
        layout.addWidget(right, 1)

    # =========================
    # TIME
    # =========================
    def update_time(self):
        now = datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%a, %d %b %Y"))

    # =========================
    # NEXT BELL
    # =========================
    def update_next_bell(self, next_time, next_name):
        if not next_time:
            self._set_no_bell()
            return

        if not hasattr(next_time, "strftime"):
            self._set_raw(next_time, next_name)
            return

        self._set_countdown(next_time, next_name)

    def _set_no_bell(self):
        self.next_time_label.setText("--:--:--")
        self.next_time_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFA500;")
        self.next_name_label.setText("No upcoming bell")

    def _set_raw(self, next_time, next_name):
        self.next_time_label.setText(str(next_time))
        self.next_name_label.setText(next_name or "Bell")

    def _set_countdown(self, next_time, next_name):
        now = datetime.now()

        if next_time.tzinfo:
            next_time = next_time.replace(tzinfo=None)

        diff = (next_time - now).total_seconds()

        if diff <= 0:
            self._set_now()
        else:
            self.next_time_label.setText(self._format_countdown(int(diff)))
            self.next_name_label.setText((next_name or "Bell")[:30])

    def _set_now(self):
        self.next_time_label.setText("🔔 NOW!")
        self.next_time_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #39FF14;")

    def _format_countdown(self, seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60

        if h > 0:
            return f"{h}h {m}m"
        if m > 0:
            return f"{m}m {s}s"
        return f"{s}s"

    # =========================
    # STATE UI
    # =========================
    def update_profile(self, name):
        self.profile_label.setText(f"📋 Profile: {name}")

    def set_running(self, running: bool):
        if running:
            self.status_indicator.setText("🟢 RUNNING")
            self.status_indicator.setObjectName("running_indicator")
        else:
            self.status_indicator.setText("🔴 STOPPED")
            self.status_indicator.setObjectName("stopped_indicator")

        self.status_indicator.style().unpolish(self.status_indicator)
        self.status_indicator.style().polish(self.status_indicator)