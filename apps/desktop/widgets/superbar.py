from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from datetime import datetime


class SuperBar(QFrame):
    tick = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("superbar")
        self.setFixedHeight(82)

        self._build()

        self.timer = QTimer()
        self.timer.timeout.connect(self._heartbeat)
        self.timer.start(1000)
        self.update_time()

    # =====================================================
    # BUILD UI
    # =====================================================

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(18, 8, 18, 8)
        root.setSpacing(25)

        # ---------- LEFT INFO ----------
        left = QVBoxLayout()
        left.setSpacing(2)

        self.profile_label = QLabel("📋 Profile: None")
        self.profile_label.setStyleSheet("font-size:13px; font-weight:bold;")

        self.status_indicator = QLabel("🔴 STOPPED")
        self.status_indicator.setStyleSheet("font-size:13px;")

        left.addWidget(self.profile_label)
        left.addWidget(self.status_indicator)

        # ---------- CENTER CLOCK ----------
        center_wrap = QWidget()
        center_wrap.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        center = QVBoxLayout(center_wrap)
        center.setSpacing(0)
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.clock_label = QLabel("--:--:--")
        self.clock_label.setStyleSheet("font-size:24px; font-weight:bold;")

        self.date_label = QLabel("-- --- ----")
        self.date_label.setStyleSheet("font-size:11px; color:#999;")

        center.addWidget(self.clock_label)
        center.addWidget(self.date_label)

        # ---------- RIGHT NEXT BELL ----------
        right = QVBoxLayout()
        right.setSpacing(2)
        right.setAlignment(Qt.AlignmentFlag.AlignRight)

        title = QLabel("🔔 NEXT BELL")
        title.setStyleSheet("font-size:11px; color:#bbb;")

        self.next_time_label = QLabel("--:--")
        self.next_time_label.setStyleSheet("font-size:18px; font-weight:bold; color:#ffaa00;")

        self.next_name_label = QLabel("No upcoming bell")
        self.next_name_label.setStyleSheet("font-size:11px; color:#ccc;")

        right.addWidget(title)
        right.addWidget(self.next_time_label)
        right.addWidget(self.next_name_label)

        # ---------- COMPOSE ----------
        root.addLayout(left)
        root.addWidget(center_wrap)
        root.addLayout(right)

    # =====================================================
    # CLOCK
    # =====================================================

    def _heartbeat(self):
        self.update_time()
        self.tick.emit()
        
    def update_time(self):
        now = datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%A, %d %B %Y"))

    # =====================================================
    # PROFILE / STATE
    # =====================================================

    def update_profile(self, name):
        self.profile_label.setText(f"📋 Profile: {name}")

    def set_running(self, running: bool):
        if running:
            self.status_indicator.setText("🟢 RUNNING")
        else:
            self.status_indicator.setText("🔴 STOPPED")

    # =====================================================
    # NEXT BELL
    # =====================================================

    def update_next_bell(self, next_time, next_name):
        if not next_time:
            self.next_time_label.setText("--:--")
            self.next_name_label.setText("No upcoming bell")
            return

        if hasattr(next_time, "strftime"):
            now = datetime.now()

            if getattr(next_time, "tzinfo", None):
                next_time = next_time.replace(tzinfo=None)

            diff = int((next_time - now).total_seconds())

            if diff <= 0:
                self.next_time_label.setText("🔔 NOW")
            else:
                self.next_time_label.setText(self._format_countdown(diff))
        else:
            self.next_time_label.setText(str(next_time))

        self.next_name_label.setText(next_name or "Bell")

    def _format_countdown(self, sec):
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60

        if h > 0:
            return f"{h}h {m}m"
        if m > 0:
            return f"{m}m {s}s"
        return f"{s}s"