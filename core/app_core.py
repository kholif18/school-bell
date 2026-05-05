# core/app_core.py
from core.ipc_bus import get_ipc_bus
from core.runtime_state import get_runtime_state
import threading
import time

class AppClient:
    """Client untuk GUI/Tray - komunikasi via IPC ke master"""
    
    def __init__(self):
        self.ipc = get_ipc_bus()
        self._listeners = []
        self._polling = False
        self._poll_thread = None
    
    def send_command(self, command: str, payload: dict = None):
        """Kirim command ke master process"""
        self.ipc.send(command, payload or {})
    
    def start_scheduler(self):
        self.send_command("START_SCHEDULER")
    
    def stop_scheduler(self):
        self.send_command("STOP_SCHEDULER")
    
    def reload_schedules(self):
        self.send_command("RELOAD_SCHEDULES")
    
    def switch_profile(self, profile_id: int):
        self.send_command("SWITCH_PROFILE", {"profile_id": profile_id})
    
    def get_status(self):
        """Baca status dari database (source of truth)"""
        state = get_runtime_state().get()
        return {
            'running': state.is_running if state else False,
            'active_jobs': state.active_jobs if state else 0,
            'next_bell': state.next_bell if state else None,
            'updated_at': state.updated_at if state else None
        }
    
    def start_polling(self, interval_seconds: float = 1.0, callback=None):
        """Polling status untuk real-time UI update"""
        self._polling = True
        
        def poll():
            while self._polling:
                try:
                    status = self.get_status()
                    if callback:
                        callback(status)
                except Exception as e:
                    print(f"Polling error: {e}")
                time.sleep(interval_seconds)
        
        self._poll_thread = threading.Thread(target=poll, daemon=True)
        self._poll_thread.start()
    
    def stop_polling(self):
        self._polling = False

# Singleton
_app_client = None

def get_app_client():
    global _app_client
    if _app_client is None:
        _app_client = AppClient()
    return _app_client