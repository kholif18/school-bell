# core/runtime/state.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.runtime.events import get_event_bus


@dataclass
class AppState:
    running: bool = False

    active_profile_id: Optional[int] = None
    active_profile_name: Optional[str] = None

    active_jobs: int = 0
    next_bell: Optional[datetime] = None

    last_started: Optional[datetime] = None
    last_stopped: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StateManager:
    """
    Runtime state holder

    Rules:
    - in-memory only
    - no DB
    - updated via events
    """

    def __init__(self):
        self._state = AppState()
        self.events = get_event_bus()
        self._register_events()

    # =========================
    # EVENT WIRING
    # =========================

    def _register_events(self):
        self.events.on("SYSTEM_STARTED", self._on_start)
        self.events.on("SYSTEM_STOPPED", self._on_stop)
        self.events.on("PROFILE_CHANGED", self._on_profile)
        self.events.on("JOBS_UPDATED", self._on_jobs)
        self.events.on("NEXT_BELL_UPDATED", self._on_next_bell)

    # =========================
    # EVENT HANDLERS
    # =========================

    def _on_start(self, _=None):
        self._state.running = True
        self._state.last_started = datetime.now()
        self._state.updated_at = datetime.now()

    def _on_stop(self, _=None):
        self._state.running = False
        self._state.last_stopped = datetime.now()
        self._state.updated_at = datetime.now()

    def _on_profile(self, data):
        self._state.active_profile_id = data.get("id")
        self._state.active_profile_name = data.get("name")
        self._state.updated_at = datetime.now()

    def _on_jobs(self, count: int):
        self._state.active_jobs = count
        self._state.updated_at = datetime.now()

    def _on_next_bell(self, dt):
        self._state.next_bell = dt
        self._state.updated_at = datetime.now()

    # =========================
    # READ API
    # =========================

    def snapshot(self) -> dict:
        s = self._state
        return {
            "running": s.running,
            "active_profile_id": s.active_profile_id,
            "active_profile_name": s.active_profile_name,
            "active_jobs": s.active_jobs,
            "next_bell": s.next_bell,
            "last_started": s.last_started,
            "last_stopped": s.last_stopped,
            "updated_at": s.updated_at,
        }

    def get(self) -> AppState:
        return self._state


# =========================
# SINGLETON
# =========================

_state_manager = None


def get_state_manager():
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager