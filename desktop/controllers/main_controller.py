# desktop/controllers/main_controller.py
from PyQt6.QtWidgets import QMessageBox, QInputDialog
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor
from datetime import datetime, time

from desktop.dialogs.schedule_dialog import ScheduleDialog


class MainController:
    """Semua business logic MainWindow dipindahkan ke sini"""
    
    def __init__(self, view, app_core):
        self.view = view
        self.app = app_core
        self.current_profile_id = None
        self.next_bell_id = None
        self._logs = []
    
    def setup_connections(self):
        """Hubungkan signal dari view ke controller methods"""
        # Profile buttons
        self.view.add_profile_btn.clicked.connect(self.add_profile)
        self.view.activate_profile_btn.clicked.connect(self.activate_profile)
        self.view.delete_profile_btn.clicked.connect(self.delete_profile)
        self.view.profile_list.itemClicked.connect(self.on_profile_click)
        
        # Schedule buttons
        self.view.add_btn.clicked.connect(self.add_schedule)
        self.view.edit_btn.clicked.connect(self.edit_schedule)
        self.view.delete_btn.clicked.connect(self.delete_schedule)
        self.view.ring_btn.clicked.connect(self.test_ring)
        self.view.stop_test_btn.clicked.connect(self.stop_test)
        self.view.toggle_btn.clicked.connect(self.toggle_system)
        self.view.reload_btn.clicked.connect(self.reload_schedules)
        
        # Log buttons
        self.view.clear_log_btn.clicked.connect(self.clear_logs)
    
    def initialize(self):
        """Initial load after UI is ready"""
        self.load_profiles()
        
        # Auto-start scheduler
        auto_start = self.app.config.get('auto_start', False)
        if auto_start:
            self.add_log("Auto-start enabled, starting scheduler...", "INFO")
            QTimer.singleShot(500, self._auto_start_scheduler)
    
    def _auto_start_scheduler(self):
        active_profile = self.app.schedule_manager.get_active_profile()
        if not active_profile:
            self.add_log("Auto-start skipped: No active profile", "WARNING")
            return
        
        schedules = self.app.schedule_manager.get_schedules_by_profile(active_profile.id, include_inactive=False)
        if not schedules:
            self.add_log(f"Auto-start skipped: No schedules in profile '{active_profile.name}'", "WARNING")
            return
        
        if self.app.scheduler.start():
            self.add_log("Scheduler auto-started successfully", "SUCCESS")
        else:
            self.add_log("Scheduler auto-start failed", "ERROR")
    
    def sync_with_engine(self):
        """Sinkronkan UI dengan status engine yang sebenarnya"""
        is_running = self.app.scheduler.get_scheduler_state_from_db()
        if is_running != getattr(self.app.scheduler, 'running', False):
            self.app.scheduler.running = is_running
        self.update_system_status()
    
    def load_profiles(self):
        try:
            profiles = self.app.schedule_manager.get_all_profiles()
            
            self.view.profile_list.blockSignals(True)
            self.view.profile_list.clear()
            
            for p in profiles:
                item = QListWidgetItem()
                if p.is_active:
                    item.setText(f"● {p.name}")
                    item.setForeground(QColor("#39FF14"))
                else:
                    item.setText(p.name)
                item.setData(Qt.ItemDataRole.UserRole, p.id)
                self.view.profile_list.addItem(item)
            
            self.view.profile_list.blockSignals(False)
            
            active = self.app.schedule_manager.get_active_profile()
            if active:
                self.view.superbar.update_profile(active.name)
                self.current_profile_id = active.id
                self.load_schedules()
            else:
                self.current_profile_id = None
                self.view.superbar.update_profile("None")
                if hasattr(self.view, 'table_model') and self.view.table_model:
                    self.view.table_model.refresh([])
                if hasattr(self.view, 'history_tab'):
                    self.view.history_tab.load_history()
        except Exception as e:
            print(f"Error loading profiles: {e}")
    
    def load_schedules(self):
        if not self.current_profile_id:
            return
        
        if not hasattr(self.view, 'table'):
            return
        
        try:
            schedules = self.app.schedule_manager.get_schedules_by_profile(self.current_profile_id, include_inactive=True)
            
            if not hasattr(self.view, 'table_model') or self.view.table_model is None:
                from desktop.models.schedule_table_model import ScheduleTableModel
                self.view.table_model = ScheduleTableModel(schedules)
                
                from PyQt6.QtCore import QSortFilterProxyModel
                self.view.proxy_model = QSortFilterProxyModel()
                self.view.proxy_model.setSourceModel(self.view.table_model)
                self.view.table.setModel(self.view.proxy_model)
                self.view.table.setSortingEnabled(True)
                self.view.table.sortByColumn(1, Qt.SortOrder.AscendingOrder)
            else:
                self.view.table_model.refresh(schedules, self.next_bell_id)
            
            if hasattr(self.view, 'history_tab'):
                self.view.history_tab.load_history()
        except Exception as e:
            print(f"Error loading schedules: {e}")
    
    def on_profile_click(self, item):
        self.current_profile_id = item.data(Qt.ItemDataRole.UserRole)
        self.load_schedules()
        self._update_next_bell_display()
    
    def add_profile(self):
        name, ok = QInputDialog.getText(self.view, "New Profile", "Profile name:")
        if ok and name:
            self.app.schedule_manager.create_profile(name)
            self.load_profiles()
            self.add_log(f"Profile '{name}' created", "SUCCESS")
    
    def activate_profile(self):
        item = self.view.profile_list.currentItem()
        if not item:
            QMessageBox.warning(self.view, "Error", "Select a profile first")
            return
        profile_id = item.data(Qt.ItemDataRole.UserRole)
        if self.app.schedule_manager.set_active_profile(profile_id):
            self.app.reload_schedules()
            self.load_profiles()
            self._update_next_bell_display()
            self.add_log("Profile activated", "SUCCESS")
            
            try:
                from web.server import socketio
                socketio.emit('profile_activated', {'profile_id': profile_id})
                socketio.emit('schedules_updated')
                socketio.emit('profiles_updated')
            except Exception as e:
                self.add_log(f"Socket sync failed: {e}", "WARNING")
    
    def delete_profile(self):
        item = self.view.profile_list.currentItem()
        if not item:
            return
        profile_id = item.data(Qt.ItemDataRole.UserRole)
        active = self.app.schedule_manager.get_active_profile()
        if active and active.id == profile_id:
            QMessageBox.warning(self.view, "Error", "Cannot delete active profile")
            return
        if QMessageBox.question(self.view, "Delete", "Delete this profile?") == QMessageBox.StandardButton.Yes:
            self.app.schedule_manager.delete_profile(profile_id)
            self.load_profiles()
            self.add_log("Profile deleted", "WARNING")
    
    def add_schedule(self):
        if not self.current_profile_id:
            QMessageBox.warning(self.view, "Error", "Select a profile first")
            return
        dialog = ScheduleDialog(self.view)
        if dialog.exec():
            data = dialog.get_data()
            t = time(data['hour'], data['minute'])
            self.app.schedule_manager.add_schedule(
                profile_id=self.current_profile_id,
                name=data['name'],
                bell_time=t,
                days=data['days'],
                audio_file=data['audio_file']
            )
            self.app.reload_schedules()
            self.load_schedules()
            self._update_next_bell_display()
            self.add_log(f"Schedule '{data['name']}' added", "SUCCESS")
    
    def _get_schedule_from_selection(self):
        selected = self.view.table.selectedIndexes()
        if not selected:
            return None
        proxy_index = selected[0]
        
        if hasattr(self.view, 'proxy_model'):
            source_index = self.view.proxy_model.mapToSource(proxy_index)
        else:
            source_index = proxy_index
        
        row = source_index.row()
        if hasattr(self.view, 'table_model') and 0 <= row < len(self.view.table_model.schedules):
            return self.view.table_model.schedules[row]
        return None
    
    def edit_schedule(self):
        schedule = self._get_schedule_from_selection()
        if not schedule:
            return
        
        dialog = ScheduleDialog(self.view, schedule)
        if dialog.exec():
            data = dialog.get_data()
            t = time(data['hour'], data['minute'])
            self.app.schedule_manager.update_schedule(
                schedule.id,
                name=data['name'],
                bell_time=t,
                days_of_week=','.join(str(d) for d in data['days']),
                audio_file=data['audio_file']
            )
            self.app.reload_schedules()
            self.load_schedules()
            self._update_next_bell_display()
            self.add_log(f"Schedule '{data['name']}' updated", "INFO")
    
    def delete_schedule(self):
        schedule = self._get_schedule_from_selection()
        if not schedule:
            return
        if QMessageBox.question(self.view, "Delete", f"Delete '{schedule.name}'?") == QMessageBox.StandardButton.Yes:
            self.app.schedule_manager.delete_schedule(schedule.id)
            self.app.reload_schedules()
            self.load_schedules()
            self._update_next_bell_display()
            self.add_log(f"Schedule '{schedule.name}' deleted", "WARNING")
    
    def test_ring(self):
        schedule = self._get_schedule_from_selection()
        if not schedule:
            QMessageBox.information(self.view, "Info", "Select a schedule to test")
            return
        self.app.audio_manager.play(schedule.audio_file)
        
        active_profile = self.app.schedule_manager.get_active_profile()
        profile_name = active_profile.name if active_profile else "Unknown"
        
        self.app.schedule_manager.log_bell_event(
            schedule_name=schedule.name,
            audio_played=schedule.audio_file or "default",
            status="success",
            schedule_id=schedule.id,
            profile_name=profile_name
        )
        
        self.add_log(f"Test ring: {schedule.name}", "INFO")
        if hasattr(self.view, 'history_tab'):
            self.view.history_tab.load_history()
    
    def stop_test(self):
        self.app.audio_manager.stop()
        self.add_log("Test audio stopped", "INFO")
    
    def toggle_system(self):
        is_running = self.app.scheduler.get_scheduler_state_from_db() if hasattr(self.app.scheduler, 'get_scheduler_state_from_db') else self.app.scheduler.running
        
        if is_running:
            self.app.scheduler.stop()
            self.add_log("System STOPPED", "WARNING")
            self.view.superbar.set_running(False)
            self.view.toggle_btn.setText("▶ START SYSTEM")
            self.view.toggle_btn.setObjectName("start_btn")
        else:
            active_profile = self.app.schedule_manager.get_active_profile()
            if not active_profile:
                QMessageBox.warning(self.view, "Error", "No active profile found.\nPlease activate a profile first.")
                return
            
            schedules = self.app.schedule_manager.get_schedules_by_profile(active_profile.id, include_inactive=False)
            if not schedules:
                QMessageBox.warning(self.view, "Error", f"No schedules in profile '{active_profile.name}'.\nPlease add schedules first.")
                return
            
            result = self.app.scheduler.start()
            if result:
                self.add_log("System STARTED", "SUCCESS")
                self.view.superbar.set_running(True)
                self.view.toggle_btn.setText("⏹ STOP SYSTEM")
                self.view.toggle_btn.setObjectName("stop_btn")
            else:
                if self.app.scheduler.running:
                    self.add_log("System already running", "INFO")
                    self.view.superbar.set_running(True)
                    self.view.toggle_btn.setText("⏹ STOP SYSTEM")
                    self.view.toggle_btn.setObjectName("stop_btn")
                else:
                    self.add_log("System START failed", "ERROR")
        
        self.view.toggle_btn.style().unpolish(self.view.toggle_btn)
        self.view.toggle_btn.style().polish(self.view.toggle_btn)
    
    def reload_schedules(self):
        self.app.reload_schedules()
        self.load_schedules()
        self._update_next_bell_display()
        self.add_log("Schedules reloaded", "INFO")
    
    def update_system_status(self):
        status = self.app.get_status()
        is_running = status['scheduler']['running']
        
        self.view.superbar.set_running(is_running)
        
        if is_running:
            self.view.toggle_btn.setText("⏹ STOP SYSTEM")
            self.view.toggle_btn.setObjectName("stop_btn")
        else:
            self.view.toggle_btn.setText("▶ START SYSTEM")
            self.view.toggle_btn.setObjectName("start_btn")
        
        self.view.toggle_btn.style().unpolish(self.view.toggle_btn)
        self.view.toggle_btn.style().polish(self.view.toggle_btn)
        
        self._update_next_bell_display()
    
    def _find_next_schedule_today(self, schedules):
        now = datetime.now()
        candidates = []
        
        for s in schedules:
            if not s.is_active:
                continue
            days = s.get_days_list()
            if now.weekday() not in days:
                continue
            bell_dt = datetime(now.year, now.month, now.day, s.bell_time.hour, s.bell_time.minute)
            if bell_dt > now:
                candidates.append((bell_dt, s))
        
        if not candidates:
            return None, None, None
        
        candidates.sort(key=lambda x: x[0])
        bell_dt, sched = candidates[0]
        return bell_dt, sched.name, sched.id
    
    def _update_next_bell_display(self):
        if not self.current_profile_id:
            return
        
        schedules = self.app.schedule_manager.get_schedules_by_profile(self.current_profile_id)
        next_bell, next_name, new_next_id = self._find_next_schedule_today(schedules)
        
        if next_bell:
            self.view.superbar.update_next_bell(next_bell, next_name)
            if hasattr(self.view, 'table_model') and self.next_bell_id != new_next_id:
                self.next_bell_id = new_next_id
                self.view.table_model.next_bell_id = new_next_id
        else:
            self.view.superbar.update_next_bell(None, None)
            if self.next_bell_id is not None:
                self.next_bell_id = None
                if hasattr(self.view, 'table_model'):
                    self.view.table_model.next_bell_id = None
    
    def add_log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colors = {"INFO": "#39FF14", "WARNING": "#FFA500", "ERROR": "#F85149", "SUCCESS": "#1F6FEB"}
        color = colors.get(level, "#E6EDF3")
        
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'msg': msg,
            'html': f'<span style="color: #8B949E;">[{timestamp}]</span> <span style="color: {color};">[{level}]</span> {msg}<br>'
        }
        
        self._logs.append(log_entry)
        if len(self._logs) > 500:
            self._logs = self._logs[-500:]
        
        self._filter_logs()
    
    def _filter_logs(self):
        filter_text = self.view.log_filter_input.text().lower() if hasattr(self.view, 'log_filter_input') else ""
        
        self.view.log_console.clear()
        
        for log in self._logs:
            if filter_text:
                if filter_text in log['msg'].lower() or filter_text in log['level'].lower():
                    self.view.log_console.append(log['html'])
            else:
                self.view.log_console.append(log['html'])
        
        scrollbar = self.view.log_console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_logs(self):
        self._logs = []
        self.view.log_console.clear()
    
    def handle_close(self, event):
        if '--tray' in sys.argv:
            event.ignore()
            self.view.hide()
            self.add_log("Application minimized to tray", "INFO")
        else:
            reply = QMessageBox.question(
                self.view, "Exit", "Stop scheduler and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self.app.shutdown_all()
                except Exception as e:
                    QMessageBox.critical(self.view, "Shutdown Error", f"Error during shutdown:\n{str(e)}")
                event.accept()
            else:
                event.ignore()