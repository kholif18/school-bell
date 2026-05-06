import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from core.models import BellHistory


class HistoryTab(QWidget):

    def __init__(self, repo, theme=None):
        super().__init__()
        self.repo = repo
        self.theme = theme
        self._build_ui()
        self.refresh()

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # ================= TOP BAR =================
        top = QHBoxLayout()

        self.title = QLabel("🔔 Bell Ring History")
        self.title.setObjectName("sectionTitle")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search history...")
        self.search_input.textChanged.connect(self._filter_rows)

        self.refresh_btn = QPushButton("⟳ Refresh")

        top.addWidget(self.title)
        top.addStretch()
        top.addWidget(self.search_input)
        top.addWidget(self.refresh_btn)

        root.addLayout(top)

        # ================= TABLE =================
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Time", "Profile", "Schedule", "Audio", "Status"
        ])

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        root.addWidget(self.table)

        # ================= SIGNAL =================
        self.refresh_btn.clicked.connect(self.refresh)
    
    def refresh(self):
        session = self.repo._session()

        try:
            rows = (
                session.query(BellHistory)
                .order_by(BellHistory.rang_at.desc())
                .limit(300)
                .all()
            )
        except Exception as e:
            print("History load error:", e)
            rows = []
        finally:
            session.close()

        self.table.setRowCount(len(rows))

            
        for r, item in enumerate(rows):
            rang_time = item.rang_at.strftime("%Y-%m-%d %H:%M:%S") if item.rang_at else "-"
            audio_name = "-"

            if item.audio_played:
                audio_name = os.path.basename(item.audio_played)

            self.table.setItem(r, 0, QTableWidgetItem(rang_time))
            self.table.setItem(r, 1, QTableWidgetItem(item.profile_name or "-"))
            self.table.setItem(r, 2, QTableWidgetItem(item.schedule_name or "-"))
            self.table.setItem(r, 3, QTableWidgetItem(audio_name))
            self.table.setItem(r, 4, QTableWidgetItem(item.status or "-"))

        self.table.clearSelection()

    def _filter_rows(self, text):
        text = text.lower()

        for row in range(self.table.rowCount()):
            visible = False

            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    visible = True
                    break

            self.table.setRowHidden(row, not visible)