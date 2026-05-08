# apps/desktop/controllers/main_controller.py

from PyQt6.QtWidgets import QMessageBox, QInputDialog, QListWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from datetime import datetime, time

from apps.desktop.dialogs.schedule_dialog import ScheduleDialog
from apps.desktop.bridge.client_bridge import ClientBridge
from core.styles.loader import load_stylesheet
from core.paths import get_paths

class MainController:

    def __init__(self, view, app_core):
        self.view = view
        self.bridge = ClientBridge(app_core)
        self.app = app_core

        self.current_profile_id = None
        self._logs = []
        self.dark_mode = True

    # =====================================================
    # INIT
    # =====================================================

    def initialize(self):
        self.load_profiles()
        self.update_system_status()

        if self.bridge.get_config("auto_start", False):
            self.add_log("Auto-start enabled", "INFO")
            self.bridge.start_system()
            self.update_system_status()

    # =====================================================
    # PROFILE
    # =====================================================

    def load_profiles(self):
        profiles = self.bridge.get_profiles()

        active = self.bridge.get_active_profile()

        # fallback pertama kali
        if self.current_profile_id is None and active:
            self.current_profile_id = active.id

        self.view.profile_list.blockSignals(True)
        self.view.profile_list.clear()

        selected_row = None

        for index, p in enumerate(profiles):
            item = QListWidgetItem(p.name)
            item.setData(Qt.ItemDataRole.UserRole, p.id)

            if p.is_active:
                item.setText(f"● {p.name}")
                item.setForeground(QColor("#39FF14"))

            self.view.profile_list.addItem(item)

            if p.id == self.current_profile_id:
                selected_row = index

        if selected_row is not None:
            self.view.profile_list.setCurrentRow(selected_row)

        self.view.profile_list.blockSignals(False)

        if self.current_profile_id:
            self.load_schedules()

        if active:
            self.view.superbar.update_profile(active.name)
        else:
            self.view.superbar.update_profile("None")

    def on_profile_click(self, item):
        self.current_profile_id = item.data(Qt.ItemDataRole.UserRole)
        self.load_schedules()
        self._update_next_bell_display()

    def add_profile(self):
        name, ok = QInputDialog.getText(self.view, "New Profile", "Profile name:")
        if ok and name:
            self.bridge.create_profile(name)
            self.load_profiles()
            self.add_log(f"Profile '{name}' created", "SUCCESS")

    def activate_profile(self):
        item = self.view.profile_list.currentItem()
        if not item:
            return QMessageBox.warning(self.view, "Error", "Select profile first")

        pid = item.data(Qt.ItemDataRole.UserRole)

        if self.bridge.activate_profile(pid):
            self.load_profiles()
            self._update_next_bell_display()
            self.add_log("Profile activated", "SUCCESS")

    def delete_profile(self):
        item = self.view.profile_list.currentItem()
        if not item:
            return

        pid = item.data(Qt.ItemDataRole.UserRole)
        active = self.bridge.get_active_profile()

        if active and active.id == pid:
            return QMessageBox.warning(self.view, "Error", "Active profile cannot be deleted")

        if QMessageBox.question(self.view, "Delete", "Delete profile?") == QMessageBox.StandardButton.Yes:
            self.bridge.delete_profile(pid)
            self.load_profiles()
            self.add_log("Profile deleted", "WARNING")

    # =====================================================
    # SCHEDULE
    # =====================================================

    def load_schedules(self):
        if not self.current_profile_id:
            return

        schedules = self.bridge.get_schedules(self.current_profile_id)

        QTimer.singleShot(0, lambda: self._safe_set_model(schedules))
        QTimer.singleShot(0, self.view.on_schedules_loaded)

    def _safe_set_model(self, schedules):
        self._init_table_model(schedules)
        self._update_next_bell_display()

    def _init_table_model(self, schedules):
        self.view.table.blockSignals(True)
        from apps.desktop.models.schedule_table_model import ScheduleTableModel
        from PyQt6.QtCore import QSortFilterProxyModel

        self.view.table.clearSelection()

        self.view.table_model = ScheduleTableModel(schedules)
        self.view.proxy_model = QSortFilterProxyModel()
        self.view.proxy_model.setSourceModel(self.view.table_model)

        self.view.table.setModel(self.view.proxy_model)
        header = self.view.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)   # Nama Jadwal
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Jam
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)   # Hari
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Suara
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Status
        self.view.table.setSortingEnabled(True)
        self.view.table.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        self.view.table.blockSignals(False)

    def _get_selected_schedule(self):
        indexes = self.view.table.selectionModel().selectedRows()
        if not indexes:
            return None

        proxy_index = indexes[0]
        if not proxy_index.isValid():
            return None

        source_index = self.view.proxy_model.mapToSource(proxy_index)

        row = source_index.row()
        if row < 0 or row >= len(self.view.table_model.schedules):
            return None

        return self.view.table_model.schedules[row]

    def add_schedule(self):
        if not self.current_profile_id:
            return QMessageBox.warning(self.view, "Error", "Select profile first")

        dialog = ScheduleDialog(self.bridge.core, self.view)
        if not dialog.exec():
            return

        data = dialog.get_data()

        self.bridge.add_schedule(
            profile_id=self.current_profile_id,
            name=data["name"],
            bell_time=time(data["hour"], data["minute"]),
            days=data["days"],
            audio_file=data["audio_file"],
            is_active=data["is_active"]
        )

        self.load_schedules()
        self._update_next_bell_display()
        self.add_log(f"Schedule {data['name']} added")

    def edit_schedule(self):
        schedule = self._get_selected_schedule()
        if not schedule:
            return

        dialog = ScheduleDialog(self.bridge.core, self.view, schedule)
        if not dialog.exec():
            return

        data = dialog.get_data()

        self.bridge.update_schedule(
            schedule.id,
            name=data["name"],
            bell_time=time(data["hour"], data["minute"]),
            days_of_week=",".join(map(str, data["days"])),
            audio_file=data["audio_file"],
            is_active=data["is_active"]
        )

        self.load_schedules()
        self._update_next_bell_display()
        self.add_log(f"Schedule {data['name']} updated")

    def delete_schedule(self):
        schedule = self._get_selected_schedule()
        if not schedule:
            return

        if QMessageBox.question(self.view, "Delete", f"Delete {schedule.name}?") == QMessageBox.StandardButton.Yes:
            self.bridge.delete_schedule(schedule.id)
            self.load_schedules()
            self._update_next_bell_display()
            self.add_log(f"Schedule {schedule.name} deleted")

    # =====================================================
    # THEME
    # =====================================================
    def toggle_theme(self):
        """Toggle theme and update all components"""
        new_theme = self.app.theme.toggle()
        self.app.config.set("theme", new_theme)
        
        # Update table model colors (CRITICAL!)
        if hasattr(self.view, "table_model"):
            self.view.table_model.set_theme(new_theme)
        
        # Update status indicator jika perlu
        self.update_system_status()
        
    # def toggle_theme(self):
    #     self.app.theme.toggle(self.view)

    # =====================================================
    # SYSTEM
    # =====================================================
    def rename_profile(self, item):
        if not item:
            return

        profile_id = item.data(Qt.ItemDataRole.UserRole)
        old_name = item.text().replace("● ", "")

        name, ok = QInputDialog.getText(
            self.view,
            "Rename Profile",
            "New name:",
            text=old_name
        )

        if ok and name and name.strip():
            self.bridge.update_profile(profile_id, name=name.strip())
            self.load_profiles()
        
    def toggle_system(self):
        if self.bridge.is_running():
            self.bridge.stop_system()
            self.add_log("System stopped", "WARNING")
        else:
            self.bridge.start_system()
            self.add_log("System started", "SUCCESS")

        self.update_system_status()

    def update_system_status(self):
        running = self.bridge.is_running()

        self.view.superbar.set_running(running)

        if running:
            self.view.toggle_btn.setText("⏹ STOP SYSTEM")
            self.view.toggle_btn.setProperty("running", True)
        else:
            self.view.toggle_btn.setText("▶ START SYSTEM")
            self.view.toggle_btn.setProperty("running", False)

        self.view.toggle_btn.style().unpolish(self.view.toggle_btn)
        self.view.toggle_btn.style().polish(self.view.toggle_btn)

        self._update_next_bell_display()

    # =====================================================
    # AUDIO TEST
    # =====================================================

    def test_ring(self, schedule_id=None):
        schedule = self.bridge.get_schedule(schedule_id)

        if not schedule:
            return

        file = schedule.audio_file
        self.bridge.test_ring(file)

    def stop_test(self):
        self.bridge.stop_ring()
        self.add_log("Test bell stopped")

    # =====================================================
    # NEXT BELL
    # =====================================================

    def _update_next_bell_display(self):
        state = self.bridge.get_state()

        self.view.superbar.update_next_bell(
            state["next_bell"],
            state.get("next_bell_name")
        )

        if hasattr(self.view, "table_model"):
            self.view.table_model.update_next_bell(state.get("next_bell_id"))

    # =====================================================
    # LOG
    # =====================================================

    def add_log(self, msg, level="INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.view.log_console.append(f"[{ts}] [{level}] {msg}")

    def clear_logs(self):
        self.view.log_console.clear()

    def _filter_logs(self, text):
        pass

    # =====================================================
    # CLOSE
    # =====================================================

    def handle_close(self, event):
        self.bridge.shutdown()
        event.accept()