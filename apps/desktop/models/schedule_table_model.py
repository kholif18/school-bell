# apps/desktop/models/schedule_table_model.py
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QColor
from datetime import datetime

class ScheduleTableModel(QAbstractTableModel):
    def __init__(self, schedules=None):
        super().__init__()
        self.schedules = schedules or []
        self.next_bell_id = None
        self.headers = ["Nama Jadwal", "Jam", "Hari", "Suara", "Status"]
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.schedules)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        s = self.schedules[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return s.name
            elif col == 1:
                return s.bell_time.strftime('%H:%M')
            elif col == 2:
                days = s.get_days_list()
                nama = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
                return ', '.join(nama[d] for d in days if d < 7)
            elif col == 3:
                return "🎵 Custom" if s.audio_file else "🔔 Default"
            elif col == 4:
                return "✓ Aktif" if s.is_active else "✗ Nonaktif"
        
        elif role == Qt.ItemDataRole.ForegroundRole and col == 4:
            return QColor("#39FF14") if s.is_active else QColor("#F85149")
        
        elif role == Qt.ItemDataRole.BackgroundRole:
            if self.next_bell_id and s.id == self.next_bell_id:
                return QColor("#1A3A1A")
        
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None
    
    def refresh(self, schedules, next_bell_id=None):
        self.beginResetModel()
        self.schedules = schedules
        self.next_bell_id = next_bell_id
        self.endResetModel()
    
    def get_schedule_at(self, row):
        if 0 <= row < len(self.schedules):
            return self.schedules[row]
        return None