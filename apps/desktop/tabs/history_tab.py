# apps/desktop/tabs/history_tab.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QColor


class HistoryLoader(QThread):
    history_loaded = pyqtSignal(list)

    def __init__(self, schedule_manager, filter_text=""):
        super().__init__()
        self.schedule_manager = schedule_manager
        self.filter_text = filter_text.lower().strip()

    def run(self):
        data = self.schedule_manager.get_recent_history(limit=200)

        if self.filter_text:
            data = [
                h for h in data
                if self.filter_text in h.schedule_name.lower()
            ]

        self.history_loaded.emit(data)


class HistoryTab(QWidget):
    def __init__(self, schedule_manager):
        super().__init__()
        self.schedule_manager = schedule_manager
        self.loader = None
        self._build_ui()
        self.load_history()

    # ================= UI =================
    def _build_ui(self):
        layout = QVBoxLayout(self)

        self._build_filter(layout)
        self._build_table(layout)
        self._build_loading(layout)

    def _build_filter(self, layout):
        bar = QHBoxLayout()

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search schedule...")
        self.filter_input.textChanged.connect(self.load_history)

        self.refresh_btn = QPushButton("⟳ Refresh")
        self.refresh_btn.clicked.connect(self.load_history)

        bar.addWidget(QLabel("Filter:"))
        bar.addWidget(self.filter_input)
        bar.addStretch()
        bar.addWidget(self.refresh_btn)

        layout.addLayout(bar)

    def _build_table(self, layout):
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Time", "Schedule", "Profile", "Status", "Audio"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

    def _build_loading(self, layout):
        self.loading = QLabel("Loading...")
        self.loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading.hide()
        layout.addWidget(self.loading)

    # ================= LOGIC =================
    def load_history(self):
        if self.loader and self.loader.isRunning():
            self.loader.terminate()

        self.loading.show()
        self.table.hide()

        self.loader = HistoryLoader(
            self.schedule_manager,
            self.filter_input.text()
        )

        self.loader.history_loaded.connect(self._render)
        self.loader.start()

    def _render(self, data):
        self.loading.hide()
        self.table.show()

        self.table.setRowCount(0)

        if not data:
            self._show_empty()
            return

        self.table.setRowCount(len(data))

        for r, h in enumerate(data):
            self._set_row(r, h)

    def _show_empty(self):
        self.table.setRowCount(1)
        item = QTableWidgetItem("No history")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(0, 0, item)
        self.table.setSpan(0, 0, 1, 5)

    def _set_row(self, row, h):
        self.table.setItem(row, 0, QTableWidgetItem(
            h.rang_at.strftime("%H:%M:%S") if h.rang_at else "-"
        ))

        self.table.setItem(row, 1, QTableWidgetItem(h.schedule_name))
        self.table.setItem(row, 2, QTableWidgetItem(h.profile_name or "-"))

        status = QTableWidgetItem(h.status.upper())

        if h.status == "success":
            status.setForeground(QColor("#39FF14"))
        else:
            status.setForeground(QColor("#F85149"))

        self.table.setItem(row, 3, status)

        audio = h.audio_played.split("/")[-1] if h.audio_played else "-"
        self.table.setItem(row, 4, QTableWidgetItem(audio[:20]))