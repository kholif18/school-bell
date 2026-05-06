# core/app.py
import logging
from datetime import datetime

from core.config import get_config
from core.database import get_db_manager
from core.repositories import get_repository

from core.services.audio import get_audio_service
from core.services.scheduler import get_scheduler_service

from core.runtime.events import get_event_bus
from core.runtime.state import get_state_manager

logger = logging.getLogger(__name__)


class CoreApp:
    """
    CENTRAL BACKEND FACADE

    Responsibilities:
    - initialize backend services
    - orchestrate event flow
    - expose clean public API for UI bridge
    - handle graceful shutdown
    """

    def __init__(self):
        self.config = get_config()
        self.db = get_db_manager()
        self.repo = get_repository()

        self.audio = get_audio_service()
        self.scheduler = get_scheduler_service()

        self.events = get_event_bus()
        self.state = get_state_manager()

        self._wire_events()

    # =========================================================
    # INITIALIZE
    # =========================================================

    def initialize(self):
        logger.info("Initializing CoreApp...")

        self.db.create_tables()

        active = self.repo.get_active_profile()
        if active:
            self.events.emit("PROFILE_CHANGED", {
                "id": active.id,
                "name": active.name
            })

        logger.info("CoreApp initialized")

    # =========================================================
    # EVENT WIRING / ORCHESTRATION
    # =========================================================

    def _wire_events(self):
        self.events.on("BELL_TRIGGERED", self._handle_bell_trigger)

    def _handle_bell_trigger(self, payload):
        """
        Scheduler emits bell event -> CoreApp executes system actions
        """
        try:
            schedule = payload["schedule"]
            profile_name = payload["profile"]

            logger.info(f"Bell Triggered -> {schedule.name}")

            # play audio
            self.audio.play(schedule.audio_file)

            # history log
            self.repo.log_bell_event(
                schedule_id=schedule.id,
                schedule_name=schedule.name,
                audio_played=schedule.audio_file,
                status="SUCCESS",
                profile_name=profile_name
            )

        except Exception as e:
            logger.error(f"BELL_TRIGGERED handler error: {e}")

    # =========================================================
    # SYSTEM CONTROL API
    # =========================================================

    def start_system(self):
        return self.scheduler.start()

    def stop_system(self):
        return self.scheduler.stop()

    def reload_system(self):
        return self.scheduler.reload()

    def switch_profile(self, profile_id: int):
        return self.scheduler.switch_profile(profile_id)

    def is_running(self):
        return self.state.get().running

    # =========================================================
    # PROFILE API
    # =========================================================

    def get_profiles(self):
        return self.repo.get_profiles()

    def get_active_profile(self):
        return self.repo.get_active_profile()

    def create_profile(self, name, description=None, color="#4CAF50"):
        pid = self.repo.create_profile(name, description, color)

        if pid:
            logger.info(f"Profile created: {name}")

        return pid

    def delete_profile(self, profile_id: int):
        return self.repo.delete_profile(profile_id)

    # =========================================================
    # SCHEDULE API
    # =========================================================

    def get_schedules(self, profile_id: int):
        return self.repo.get_schedules_by_profile(profile_id)

    def get_schedule(self, schedule_id: int):
        return self.repo.get_schedule(schedule_id)

    def create_schedule(self, **kwargs):
        sid = self.repo.create_schedule(**kwargs)

        if sid and self.is_running():
            self.reload_system()

        return sid

    def update_schedule(self, schedule_id, **kwargs):
        """
        sementara update manual via SQLAlchemy object
        karena repo Anda belum ada method update_schedule
        """
        session = self.db.get_session()
        try:
            obj = session.get(type(self.repo.get_schedule(schedule_id)), schedule_id)
            if not obj:
                return False

            for k, v in kwargs.items():
                setattr(obj, k, v)

            session.commit()

            if self.is_running():
                self.reload_system()

            return True

        except Exception as e:
            session.rollback()
            logger.error(f"update_schedule error: {e}")
            return False
        finally:
            session.close()

    def delete_schedule(self, schedule_id: int):
        ok = self.repo.delete_schedule(schedule_id)

        if ok and self.is_running():
            self.reload_system()

        return ok

    # =========================================================
    # AUDIO API
    # =========================================================

    def test_audio(self, file=None):
        self.audio.play(file)

        self.repo.log_bell_event(
            schedule_name="Manual Test",
            audio_played=file,
            status="MANUAL_TEST",
            profile_name=self.state.get().active_profile_name
        )

    def stop_audio(self):
        self.audio.stop()

    def is_audio_busy(self):
        return self.audio.is_busy()

    def set_volume(self, volume: int):
        self.audio.set_volume(volume)
        self.config.set("volume", volume)

    # =========================================================
    # HISTORY API
    # =========================================================

    def get_history(self, limit=100):
        session = self.db.get_session()
        try:
            from core.models import BellHistory

            return session.query(BellHistory)\
                .order_by(BellHistory.rang_at.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()

    # =========================================================
    # STATE API
    # =========================================================

    def get_status(self):
        return self.state.snapshot()

    # =========================================================
    # SHUTDOWN
    # =========================================================

    def shutdown(self):
        logger.info("Shutting down CoreApp...")

        try:
            self.scheduler.stop()
        except Exception:
            pass

        try:
            self.audio.shutdown()
        except Exception:
            pass

        try:
            self.db.close()
        except Exception:
            pass

        logger.info("CoreApp shutdown complete")