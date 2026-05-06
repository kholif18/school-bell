# apps/desktop/models/schedule_table_model.py

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QColor
from core.styles.theme_colors import ThemeColors


class ScheduleTableModel(QAbstractTableModel):
    def __init__(self, schedules=None, theme="dark"):
        super().__init__()

        self.schedules = schedules or []
        self.next_bell_id = None

        self.headers = ["Nama Jadwal", "Jam", "Hari", "Suara", "Status"]

        self.theme = theme
        self.colors = ThemeColors.get(theme)

    # =====================================================
    # THEME
    # =====================================================
    def set_theme(self, theme):
        self.theme = theme
        self.colors = ThemeColors.get(theme)

        # FORCE Qt re-evaluate semua role
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount() - 1, self.columnCount() - 1),
            [Qt.ItemDataRole.BackgroundRole, Qt.ItemDataRole.ForegroundRole]
        )

    # =====================================================
    # BASIC MODEL
    # =====================================================
    def rowCount(self, parent=QModelIndex()):
        return len(self.schedules)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    # =====================================================
    # DATA
    # =====================================================
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        s = self.schedules[index.row()]
        col = index.column()

        # -------------------------
        # TEXT DISPLAY
        # -------------------------
        if role == Qt.ItemDataRole.DisplayRole:

            if col == 0:
                return s.name

            elif col == 1:
                return s.bell_time.strftime("%H:%M")

            elif col == 2:
                days = s.get_days_list()
                nama = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
                return ", ".join(nama[d] for d in days if 0 <= d < 7)

            elif col == 3:
                return "🎵 Custom" if s.audio_file else "🔔 Default"

            elif col == 4:
                return "✓ Aktif" if s.is_active else "✗ Nonaktif"

        elif role == Qt.ItemDataRole.BackgroundRole:
            if self.next_bell_id and s.id == self.next_bell_id:
                return QColor(self.colors["next_bell_bg"])

        elif role == Qt.ItemDataRole.ForegroundRole:
            # PRIORITY: highlight row wins
            if self.next_bell_id and s.id == self.next_bell_id:
                return QColor("#000000" if self.theme == "light" else "#FFFFFF")

            # normal status color
            if col == 4:
                return QColor(self.colors["active"] if s.is_active else self.colors["inactive"])

        return None

    # =====================================================
    # HEADER
    # =====================================================
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None

    # =====================================================
    # REFRESH DATA (SAFE)
    # =====================================================
    def refresh(self, schedules, next_bell_id=None):
        """
        Full data update (safe, but avoid calling too often)
        """

        self.schedules = schedules
        self.next_bell_id = next_bell_id

        self.layoutChanged.emit()

    # =====================================================
    # NEXT BELL ONLY UPDATE (OPTIMIZED)
    # =====================================================
    def update_next_bell(self, next_bell_id):
        """
        Only update highlight row (NO FULL REFRESH)
        """

        old_id = self.next_bell_id
        self.next_bell_id = next_bell_id

        affected_rows = []

        # old row
        if old_id is not None:
            for i, s in enumerate(self.schedules):
                if s.id == old_id:
                    affected_rows.append(i)
                    break

        # new row
        if next_bell_id is not None:
            for i, s in enumerate(self.schedules):
                if s.id == next_bell_id:
                    affected_rows.append(i)
                    break

        # emit only affected rows
        for row in affected_rows:
            top_left = self.index(row, 0)
            bottom_right = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right)

    # =====================================================
    # HELPERS
    # =====================================================
    def get_schedule_at(self, row):
        if 0 <= row < len(self.schedules):
            return self.schedules[row]
        return None