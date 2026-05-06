# apps/desktop/tabs/history_tab.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class HistoryTab(QWidget):

    def __init__(self, repo):
        super().__init__()
        self.repo = repo

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.refresh()

    def refresh(self):
        session = self.repo._session()

        try:
            rows = session.query(self.repo.__class__.__mro__[0].__globals__['BellHistory']).order_by(
                self.repo.__class__.__mro__[0].__globals__['BellHistory'].created_at.desc()
            ).limit(200).all()
        except:
            rows = []
        finally:
            session.close()

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Time", "Schedule", "Audio", "Status"])
        self.table.setRowCount(len(rows))

        for r, item in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(item.created_at)))
            self.table.setItem(r, 1, QTableWidgetItem(item.schedule_name or ""))
            self.table.setItem(r, 2, QTableWidgetItem(item.audio_played or ""))
            self.table.setItem(r, 3, QTableWidgetItem(item.status or ""))

        self.table.resizeColumnsToContents()