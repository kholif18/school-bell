from PyQt6.QtWidgets import QMessageBox, QInputDialog, QListWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from datetime import datetime, time

from apps.desktop.dialogs.schedule_dialog import ScheduleDialog


class MainController:
    """
    Controller sekarang:
    - UI handling tetap di view
    - logic sudah dipisah per domain
    - tidak ada duplication load/update
    """

    # =========================================================
    # INIT
    # =========================================================
    def __init__(self, view, app_core):
        self.view = view
        self.app = app_core

        self.current_profile_id = None
        self.next_bell_id = None
        self._logs = []

    def initialize(self):
        self.load_profiles()
        self._auto_start_if_needed()

    def _auto_start_if_needed(self):
        if self.app.config.get("auto_start", False):
            self.add_log("Auto-start enabled", "INFO")
            self._auto_start_scheduler()

    # =========================================================
    # PROFILE MANAGEMENT
    # =========================================================
    def load_profiles(self):
        try:
            profiles = self.app.schedule_manager.get_all_profiles()

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

            active = self.app.schedule_manager.get_active_profile()
            if not active:
                self._reset_profile_state()
                return

            self.current_profile_id = active.id
            self.view.superbar.update_profile(active.name)
            self.load_schedules()

        except Exception as e:
            print(f"[load_profiles] {e}")

    def _reset_profile_state(self):
        self.current_profile_id = None
        self.view.superbar.update_profile("None")

        if hasattr(self.view, "table_model") and self.view.table_model:
            self.view.table_model.refresh([])

    def on_profile_click(self, item):
        self.current_profile_id = item.data(Qt.ItemDataRole.UserRole)
        self.load_schedules()
        self._update_next_bell_display()

    def add_profile(self):
        name, ok = QInputDialog.getText(self.view, "New Profile", "Profile name:")
        if not (ok and name):
            return

        self.app.schedule_manager.create_profile(name)
        self.load_profiles()
        self.add_log(f"Profile '{name}' created", "SUCCESS")

    def activate_profile(self):
        item = self.view.profile_list.currentItem()
        if not item:
            return QMessageBox.warning(self.view, "Error", "Select profile first")

        profile_id = item.data(Qt.ItemDataRole.UserRole)

        if self.app.schedule_manager.set_active_profile(profile_id):
            self.app.reload_schedules()
            self.load_profiles()
            self._update_next_bell_display()

            self.add_log("Profile activated", "SUCCESS")

    def delete_profile(self):
        item = self.view.profile_list.currentItem()
        if not item:
            return

        profile_id = item.data(Qt.ItemDataRole.UserRole)
        active = self.app.schedule_manager.get_active_profile()

        if active and active.id == profile_id:
            return QMessageBox.warning(self.view, "Error", "Active profile cannot be deleted")

        if QMessageBox.question(self.view, "Delete", "Delete profile?") != QMessageBox.StandardButton.Yes:
            return

        self.app.schedule_manager.delete_profile(profile_id)
        self.load_profiles()
        self.add_log("Profile deleted", "WARNING")

    # =========================================================
    # SCHEDULE MANAGEMENT
    # =========================================================
    def load_schedules(self):
        if not self.current_profile_id:
            return

        try:
            schedules = self.app.schedule_manager.get_schedules_by_profile(
                self.current_profile_id,
                include_inactive=True
            )

            if not hasattr(self.view, "table_model") or not self.view.table_model:
                self._init_table_model(schedules)
            else:
                self.view.table_model.refresh(schedules, self.next_bell_id)

        except Exception as e:
            print(f"[load_schedules] {e}")

    def _init_table_model(self, schedules):
        from apps.desktop.models.schedule_table_model import ScheduleTableModel
        from PyQt6.QtCore import QSortFilterProxyModel

        self.view.table_model = ScheduleTableModel(schedules)

        self.view.proxy_model = QSortFilterProxyModel()
        self.view.proxy_model.setSourceModel(self.view.table_model)

        self.view.table.setModel(self.view.proxy_model)
        self.view.table.setSortingEnabled(True)

    def _get_selected_schedule(self):
        indexes = self.view.table.selectedIndexes()
        if not indexes:
            return None

        index = indexes[0]
        source = self.view.proxy_model.mapToSource(index) if hasattr(self.view, "proxy_model") else index

        row = source.row()
        if hasattr(self.view, "table_model"):
            return self.view.table_model.schedules[row]
        return None

    def add_schedule(self):
        if not self.current_profile_id:
            return QMessageBox.warning(self.view, "Error", "Select profile first")

        dialog = ScheduleDialog(self.view)
        if not dialog.exec():
            return

        data = dialog.get_data()
        t = time(data["hour"], data["minute"])

        self.app.schedule_manager.add_schedule(
            profile_id=self.current_profile_id,
            name=data["name"],
            bell_time=t,
            days=data["days"],
            audio_file=data["audio_file"]
        )

        self._after_schedule_change("added", data["name"])

    def edit_schedule(self):
        schedule = self._get_selected_schedule()
        if not schedule:
            return

        dialog = ScheduleDialog(self.view, schedule)
        if not dialog.exec():
            return

        data = dialog.get_data()
        t = time(data["hour"], data["minute"])

        self.app.schedule_manager.update_schedule(
            schedule.id,
            name=data["name"],
            bell_time=t,
            days_of_week=",".join(str(d) for d in data["days"]),
            audio_file=data["audio_file"]
        )

        self._after_schedule_change("updated", data["name"])

    def delete_schedule(self):
        schedule = self._get_selected_schedule()
        if not schedule:
            return

        if QMessageBox.question(self.view, "Delete", f"Delete {schedule.name}?") != QMessageBox.StandardButton.Yes:
            return

        self.app.schedule_manager.delete_schedule(schedule.id)
        self._after_schedule_change("deleted", schedule.name)

    def _after_schedule_change(self, action, name):
        self.app.reload_schedules()
        self.load_schedules()
        self._update_next_bell_display()
        self.add_log(f"Schedule {name} {action}", "INFO")

    # =========================================================
    # SYSTEM CONTROL
    # =========================================================
    def toggle_system(self):
        is_running = self.app.scheduler.running

        if is_running:
            self.app.scheduler.stop()
            self.view.superbar.set_running(False)
            self.view.toggle_btn.setText("▶ START SYSTEM")
            self.add_log("System stopped", "WARNING")
        else:
            self.app.scheduler.start()
            self.view.superbar.set_running(True)
            self.view.toggle_btn.setText("⏹ STOP SYSTEM")
            self.add_log("System started", "SUCCESS")

        self._refresh_toggle_style()

    def _refresh_toggle_style(self):
        self.view.toggle_btn.style().unpolish(self.view.toggle_btn)
        self.view.toggle_btn.style().polish(self.view.toggle_btn)

    def update_system_status(self):
        running = self.app.scheduler.running
        self.view.superbar.set_running(running)

        self.view.toggle_btn.setText(
            "⏹ STOP SYSTEM" if running else "▶ START SYSTEM"
        )

        self._update_next_bell_display()

    # =========================================================
    # NEXT BELL
    # =========================================================
    def _update_next_bell_display(self):
        if not self.current_profile_id:
            return

        schedules = self.app.schedule_manager.get_schedules_by_profile(self.current_profile_id)
        next_bell = self._find_next(schedules)

        if next_bell:
            self.view.superbar.update_next_bell(*next_bell)
        else:
            self.view.superbar.update_next_bell(None, None)

    def _find_next(self, schedules):
        now = datetime.now()
        candidates = []

        for s in schedules:
            if not s.is_active:
                continue

            if now.weekday() not in s.get_days_list():
                continue

            dt = datetime(now.year, now.month, now.day, s.bell_time.hour, s.bell_time.minute)

            if dt > now:
                candidates.append((dt, s))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[0])
        dt, s = candidates[0]
        return dt, s.name

    # =========================================================
    # LOG SYSTEM
    # =========================================================
    def add_log(self, msg, level="INFO"):
        ts = datetime.now().strftime("%H:%M:%S")

        self._logs.append({
            "ts": ts,
            "level": level,
            "msg": msg,
            "html": f"[{ts}] [{level}] {msg}<br>"
        })

        if len(self._logs) > 500:
            self._logs = self._logs[-500:]

        self._render_logs()

    def _render_logs(self):
        self.view.log_console.clear()

        for log in self._logs:
            self.view.log_console.append(log["html"])

    def clear_logs(self):
        self._logs = []
        self.view.log_console.clear()

    # =========================================================
    # CLOSE HANDLER
    # =========================================================
    def handle_close(self, event):
        self.app.shutdown_all()
        event.accept()