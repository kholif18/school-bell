# desktop/tabs/history_tab.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QColor

class HistoryLoader(QThread):
    """Load history in background thread to prevent UI freeze"""
    history_loaded = pyqtSignal(list)
    
    def __init__(self, schedule_manager, filter_text=""):
        super().__init__()
        self.schedule_manager = schedule_manager
        self.filter_text = filter_text
    
    def run(self):
        history = self.schedule_manager.get_recent_history(limit=200)
        if self.filter_text:
            history = [h for h in history if self.filter_text.lower() in h.schedule_name.lower()]
        self.history_loaded.emit(history)


class HistoryTab(QWidget):
    def __init__(self, schedule_manager):
        super().__init__()
        self.schedule_manager = schedule_manager
        self.setup_ui()
        self.loader = None
        self.load_history()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Filter bar
        filter_bar = QHBoxLayout()
        filter_bar.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search by schedule name...")
        self.filter_input.textChanged.connect(self.on_filter_changed)
        filter_bar.addWidget(self.filter_input)
        
        filter_bar.addStretch()
        
        self.refresh_btn = QPushButton("⟳ Refresh")
        self.refresh_btn.clicked.connect(self.load_history)
        filter_bar.addWidget(self.refresh_btn)
        
        layout.addLayout(filter_bar)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Time", "Schedule", "Profile", "Status", "Audio"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setAlternatingRowColors(True)
        layout.addWidget(self.history_table)
        
        # Loading indicator
        self.loading_label = QLabel("Loading history...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: #8B949E; padding: 20px;")
        self.loading_label.setVisible(False)
        layout.addWidget(self.loading_label)
    
    def on_filter_changed(self):
        self.load_history()
    
    def load_history(self):
        if self.loader and self.loader.isRunning():
            self.loader.quit()
            self.loader.wait(500)
        
        self.loading_label.setVisible(True)
        self.history_table.setVisible(False)
        
        self.loader = HistoryLoader(self.schedule_manager, self.filter_input.text())
        self.loader.history_loaded.connect(self._display_history)
        self.loader.start()
    
    def _display_history(self, history):
        self.loading_label.setVisible(False)
        self.history_table.setVisible(True)
        self.history_table.setRowCount(0)
        
        if not history:
            self.history_table.setRowCount(1)
            empty_item = QTableWidgetItem("No history yet. Click 'Ring' to test.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_table.setItem(0, 0, empty_item)
            self.history_table.setSpan(0, 0, 1, 5)
            self.history_table.resizeColumnsToContents()
            return
        
        self.history_table.setRowCount(len(history))
        for row, h in enumerate(history):
            time_str = h.rang_at.strftime("%H:%M:%S %d/%m") if h.rang_at else "--:--:-- --/--"
            self.history_table.setItem(row, 0, QTableWidgetItem(time_str))
            self.history_table.setItem(row, 1, QTableWidgetItem(h.schedule_name))
            self.history_table.setItem(row, 2, QTableWidgetItem(h.profile_name or "-"))
            
            status_item = QTableWidgetItem(h.status.upper())
            if h.status == "success":
                status_item.setForeground(QColor("#39FF14"))
            else:
                status_item.setForeground(QColor("#F85149"))
            self.history_table.setItem(row, 3, status_item)
            
            audio_name = h.audio_played.split('/')[-1] if h.audio_played else "-"
            self.history_table.setItem(row, 4, QTableWidgetItem(audio_name[:20]))
        
        self.history_table.resizeColumnsToContents()
    
    def refresh(self):
        self.load_history()