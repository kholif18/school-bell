# apps/desktop/bridge/client_bridge.py

from typing import Optional
from datetime import time


class ClientBridge:
    """
    Single communication gate between Desktop UI and CoreApp

    GUI/controller MUST NEVER access core services directly.
    Everything goes through this bridge.
    """

    def __init__(self, core_app):
        self.core = core_app

    # =====================================================
    # CONFIG
    # =====================================================

    def get_config(self, key, default=None):
        return self.core.config.get(key, default)

    def set_config(self, key, value):
        self.core.config.set(key, value)

    # =====================================================
    # PROFILE API
    # =====================================================

    def get_profiles(self):
        return self.core.repo.get_profiles()

    def get_active_profile(self):
        return self.core.repo.get_active_profile()

    def create_profile(self, name):
        return self.core.repo.create_profile(name)

    def delete_profile(self, profile_id):
        return self.core.repo.delete_profile(profile_id)

    def activate_profile(self, profile_id):
        return self.core.scheduler.switch_profile(profile_id)

    # =====================================================
    # SCHEDULE API
    # =====================================================

    def get_schedules(self, profile_id):
        return self.core.repo.get_schedules_by_profile(profile_id)

    def get_schedule(self, schedule_id):
        return self.core.repo.get_schedule(schedule_id)

    def add_schedule(self, profile_id, name, bell_time: time, days, audio_file=None):
        result = self.core.repo.create_schedule(
            profile_id=profile_id,
            name=name,
            bell_time=bell_time,
            days=days,
            audio_file=audio_file
        )
        self.reload_jobs()
        return result

    def update_schedule(self, schedule_id, **kwargs):
        result = self.core.repo.update_schedule(schedule_id, **kwargs)
        self.reload_jobs()
        return result

    def delete_schedule(self, schedule_id):
        result = self.core.repo.delete_schedule(schedule_id)
        self.reload_jobs()
        return result

    # =====================================================
    # SYSTEM CONTROL
    # =====================================================

    def start_system(self):
        return self.core.scheduler.start()

    def stop_system(self):
        return self.core.scheduler.stop()

    def reload_jobs(self):
        return self.core.scheduler.reload()

    def is_running(self):
        return self.core.state.get().running

    # =====================================================
    # AUDIO
    # =====================================================

    def test_ring(self, file=None):
        self.core.audio.play(file)

    def stop_ring(self):
        self.core.audio.stop()

    # =====================================================
    # STATE
    # =====================================================

    def get_state(self):
        return self.core.state.snapshot()

    # =====================================================
    # EVENTS
    # =====================================================

    def events(self):
        return self.core.events

    # =====================================================
    # APP CLOSE
    # =====================================================

    def shutdown(self):
        self.core.shutdown()