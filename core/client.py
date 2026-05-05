# core/client.py
from typing import Optional

from core.repositories import get_repository
from core.services.scheduler import get_scheduler_service
from core.services.audio import get_audio_service
from core.runtime.state import get_state_manager
from core.runtime.events import get_event_bus
from core.ipc import get_ipc


class AppClient:
    """
    Single entry point for UI layer

    Responsibilities:
    - call scheduler service
    - read state
    - send IPC commands (optional)
    """

    def __init__(self):
        self.repo = get_repository()
        self.scheduler = get_scheduler_service()
        self.audio = get_audio_service()
        self.state = get_state_manager()
        self.events = get_event_bus()
        self.ipc = get_ipc()

        self._wire_events()

    # =========================
    # SCHEDULER CONTROL
    # =========================

    def start_scheduler(self):
        self.scheduler.start()

    def stop_scheduler(self):
        self.scheduler.stop()

    def reload_scheduler(self):
        self.scheduler.reload()

    def switch_profile(self, profile_id: int):
        self.scheduler.switch_profile(profile_id)
    
    # =========================
    # STATE READ
    # =========================

    def get_status(self):
        return self.state.snapshot()

    # =========================
    # PROFILE OPS
    # =========================

    def get_profiles(self):
        return self.repo.get_profiles()

    def get_active_profile(self):
        return self.repo.get_active_profile()

    # =========================
    # SCHEDULE OPS
    # =========================

    def get_schedules(self, profile_id: Optional[int] = None):
        return self.repo.get_schedules(profile_id)

    def add_schedule(self, profile_id, name, time, days, audio=None):
        return self.repo.add_schedule(profile_id, name, time, days, audio)

    # =========================
    # OPTIONAL IPC (MULTI PROCESS)
    # =========================

    def send_command(self, command: str, payload: dict = None):
        self.ipc.send(command, payload)

    def start_ipc(self):
        self.ipc.start_listener()

    def stop_ipc(self):
        self.ipc.stop()

    # =========================
    # EVENT WIRING (CORE FIX)
    # =========================

    def _wire_events(self):
        """
        Central event connections
        This replaces hidden dependencies
        """

        # Scheduler → Audio
        self.events.on("BELL_TRIGGERED", self._on_bell)

        # Scheduler → State update
        self.events.on("JOBS_UPDATED", self._on_jobs_updated)

        self.events.on("SYSTEM_STARTED", self._on_started)
        self.events.on("SYSTEM_STOPPED", self._on_stopped)

    # =========================
    # EVENT HANDLERS
    # =========================

    def _on_bell(self, data):
        schedule = data["schedule"]

        # 🔊 actual audio execution
        self.audio.play(schedule.audio_file)

        # optional state update
        self.state.set_next_bell(None)

    def _on_jobs_updated(self, count):
        self.state.set_jobs(count)

    def _on_started(self, _):
        self.state.set_running(True)

    def _on_stopped(self, _):
        self.state.set_running(False)
