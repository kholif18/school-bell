from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QSizePolicy, QGraphicsDropShadowEffect
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QColor
from datetime import datetime, timezone


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

        # Tambahkan shadow effect (opsional)
        # HAPUS ATAU COMMENT bagian ini jika masih error
        try:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 30))
            shadow.setOffset(0, 2)
            self.setGraphicsEffect(shadow)
        except:
            pass  # Shadow effect tidak tersedia, lanjutkan tanpa shadow

        # ================= LEFT =================
        left = QVBoxLayout()
        left.setSpacing(2)

        self.profile_label = QLabel("📋 Profile: None")
        self.profile_label.setObjectName("profileLabel")

        self.status_indicator = QLabel("🔴 STOPPED")
        self.status_indicator.setObjectName("statusIndicator")

        left.addWidget(self.profile_label)
        left.addWidget(self.status_indicator)

        # ================= CENTER CLOCK =================
        center_wrap = QWidget()
        center_wrap.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )

        center = QVBoxLayout(center_wrap)
        center.setSpacing(0)
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.clock_label = QLabel("--:--:--")
        self.clock_label.setObjectName("clockLabel")

        self.date_label = QLabel("-- --- ----")
        self.date_label.setObjectName("dateLabel")

        center.addWidget(self.clock_label)
        center.addWidget(self.date_label)

        # ================= RIGHT NEXT BELL =================
        right = QVBoxLayout()
        right.setSpacing(2)
        right.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.next_title = QLabel("🔔 NEXT BELL")
        self.next_title.setObjectName("nextTitle")

        self.next_time_label = QLabel("--:--")
        self.next_time_label.setObjectName("nextTime")

        self.next_name_label = QLabel("No upcoming bell")
        self.next_name_label.setObjectName("nextName")

        right.addWidget(self.next_title)
        right.addWidget(self.next_time_label)
        right.addWidget(self.next_name_label)

        # ================= COMPOSE =================
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
        self.status_indicator.setText(
            "🟢 RUNNING" if running else "🔴 STOPPED"
        )

    # =====================================================
    # NEXT BELL
    # =====================================================

    def update_next_bell(self, next_time, next_name):
        if not next_time:
            self.next_time_label.setText("--:--")
            self.next_name_label.setText("No upcoming bell")
            return

        # 🔥 FIX: pastikan datetime aware
        if isinstance(next_time, str):
            next_time = datetime.fromisoformat(next_time)

        now = datetime.now(next_time.tzinfo) if next_time.tzinfo else datetime.now(timezone.utc)

        diff = int((next_time - now).total_seconds())

        if diff <= 0:
            self.next_time_label.setText("🔔 NOW")
        else:
            self.next_time_label.setText(self._format_countdown(diff))

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