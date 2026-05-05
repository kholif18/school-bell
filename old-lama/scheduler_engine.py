# core/scheduler_engine.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from zoneinfo import ZoneInfo
import threading
import logging

from core.schedule_manager import get_schedule_manager
from core.audio_manager import get_audio_manager
from core.config_manager import get_config

logger = logging.getLogger(__name__)


class SchedulerEngine:
    """
    Clean School Bell Scheduler Engine
    - No runtime_state
    - No IPC dependency
    - No watchdog overengineering
    """

    def __init__(self):
        self.schedule_manager = get_schedule_manager()
        self.audio_manager = get_audio_manager()
        self.config = get_config()

        self.scheduler = BackgroundScheduler(
            timezone=ZoneInfo(self.config.get("scheduler.timezone", "Asia/Jakarta")),
            job_defaults={
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 30,
            },
        )

        self.running = False
        self._lock = threading.RLock()
        self.current_profile_id = None

    # =========================
    # CORE ACTION
    # =========================

    def _ring_bell(self, schedule):
        """Execute bell sound"""
        if not self.running:
            return

        profile = self.schedule_manager.get_active_profile()
        profile_name = profile.name if profile else "Unknown"

        logger.info(f"🔔 [{profile_name}] {schedule.name} - {datetime.now().strftime('%H:%M:%S')}")

        self.audio_manager.play(schedule.audio_file)

        # optional logging (keep simple)
        self.schedule_manager.log_bell_event(
            schedule_name=schedule.name,
            audio_played=schedule.audio_file or "default",
            status="success",
            schedule_id=schedule.id,
            profile_name=profile_name,
        )

    # =========================
    # LOAD SCHEDULES
    # =========================

    def load_jobs(self):
        """Load schedules from active profile"""
        with self._lock:
            self.scheduler.remove_all_jobs()

            profile = self.schedule_manager.get_active_profile()
            if not profile:
                logger.warning("No active profile")
                return 0

            schedules = self.schedule_manager.get_schedules_by_profile(profile.id)
            if not schedules:
                logger.warning("No schedules found")
                return 0

            count = 0

            for s in schedules:
                days = ",".join(map(str, s.get_days_list()))
                if not days:
                    continue

                trigger = CronTrigger(
                    day_of_week=days,
                    hour=s.bell_time.hour,
                    minute=s.bell_time.minute,
                )

                self.scheduler.add_job(
                    self._ring_bell,
                    trigger=trigger,
                    args=[s],
                    id=f"bell_{s.id}",
                    replace_existing=True,
                    name=s.name,
                )

                count += 1

            logger.info(f"Loaded {count} schedules from '{profile.name}'")
            return count

    # =========================
    # LIFECYCLE
    # =========================

    def start(self):
        with self._lock:
            if self.running:
                return True

            loaded = self.load_jobs()
            if loaded == 0:
                logger.warning("No schedules to run")
                return False

            self.scheduler.start()
            self.running = True

            logger.info(f"Scheduler started ({loaded} jobs)")
            return True

    def stop(self):
        with self._lock:
            if not self.running:
                return False

            self.scheduler.shutdown(wait=False)
            self.running = False

            # recreate clean instance
            self.scheduler = BackgroundScheduler(
                timezone=ZoneInfo(self.config.get("scheduler.timezone", "Asia/Jakarta")),
                job_defaults={
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": 30,
                },
            )

            logger.info("Scheduler stopped")
            return True

    def reload(self):
        """Hot reload schedules"""
        if not self.running:
            return False

        loaded = self.load_jobs()
        logger.info(f"Reloaded ({loaded} jobs)")
        return True

    def switch_profile(self, profile_id: int):
        """Switch active profile and reload"""
        ok = self.schedule_manager.set_active_profile(profile_id)
        if ok and self.running:
            self.reload()
        return ok

    # =========================
    # STATUS
    # =========================

    def get_jobs_count(self):
        if not self.running:
            return 0
        return len(self.scheduler.get_jobs())

    def get_next_bell(self):
        if not self.running:
            return None

        jobs = self.scheduler.get_jobs()
        next_run = None

        for j in jobs:
            if j.next_run_time:
                if not next_run or j.next_run_time < next_run:
                    next_run = j.next_run_time

        return next_run

    def get_status(self):
        profile = self.schedule_manager.get_active_profile()

        return {
            "running": self.running,
            "jobs": self.get_jobs_count(),
            "next_bell": self.get_next_bell(),
            "profile": profile.name if profile else None,
        }