# apps/desktop/controllers/main_controller.py

from PyQt6.QtWidgets import QMessageBox, QInputDialog, QListWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from datetime import datetime, time

from apps.desktop.dialogs.schedule_dialog import ScheduleDialog
from apps.desktop.bridge.client_bridge import ClientBridge


class MainController:

    def __init__(self, view, app_core):
        self.view = view
        self.bridge = ClientBridge(app_core)

        self.current_profile_id = None
        self._logs = []

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

        self.view.profile_list.blockSignals(True)
        self.view.profile_list.clear()

        for p in profiles:
            item = QListWidgetItem(p.name)
            item.setData(Qt.ItemDataRole.UserRole, p.id)

            if p.is_active:
                item.setText(f"● {p.name}")
                item.setForeground(QColor("#39FF14"))

            self.view.profile_list.addItem(item)

        self.view.profile_list.blockSignals(False)

        active = self.bridge.get_active_profile()
        if active:
            self.current_profile_id = active.id
            self.view.superbar.update_profile(active.name)
            self.load_schedules()
        else:
            self.current_profile_id = None
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

        if not hasattr(self.view, "table_model"):
            self._init_table_model(schedules)
        else:
            self.view.table_model.refresh(schedules)

    def _init_table_model(self, schedules):
        from apps.desktop.models.schedule_table_model import ScheduleTableModel
        from PyQt6.QtCore import QSortFilterProxyModel

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

    def _get_selected_schedule(self):
        indexes = self.view.table.selectedIndexes()
        if not indexes:
            return None

        source = self.view.proxy_model.mapToSource(indexes[0])
        return self.view.table_model.schedules[source.row()]

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
            audio_file=data["audio_file"]
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
            audio_file=data["audio_file"]
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
    # SYSTEM
    # =====================================================

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

    def test_ring(self):
        schedule = self._get_selected_schedule()
        file = schedule.audio_file if schedule else None
        self.bridge.test_ring(file)
        self.add_log("Test bell ringing")

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