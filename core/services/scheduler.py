# core/services/scheduler.py

import logging
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from core.config import get_config
from core.repositories import get_repository
from core.runtime.events import get_event_bus

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Event-driven Scheduler Service

    Rules:
    - NO direct audio call
    - NO state mutation
    - ONLY emit events
    """
    def __init__(self):
        self.repo = get_repository()
        self.config = get_config()
        self.events = get_event_bus()

        self._lock = threading.RLock()

        self.scheduler = self._create_scheduler()

        self.running = False

    def _create_scheduler(self):
        return BackgroundScheduler(
            timezone=ZoneInfo(self.config.get("timezone", "Asia/Jakarta")),
            job_defaults={
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 30,
            },
        )
    
    # =========================
    # CORE BELL TRIGGER
    # =========================

    def _ring_bell(self, schedule):
        profile = self.repo.get_active_profile()
        profile_name = profile.name if profile else "Unknown"

        now = datetime.now()

        logger.info(f"🔔 {schedule.name} @ {now.strftime('%H:%M:%S')}")

        # ONLY EVENT EMIT (NO DIRECT DEPENDENCY)
        self.events.emit("BELL_TRIGGERED", {
            "schedule": schedule,
            "profile": profile_name,
            "time": now,
        })

        self._publish_next_bell()

    def _publish_next_bell(self):
        jobs = self.scheduler.get_jobs()

        if not jobs:
            self.events.emit("NEXT_BELL_UPDATED", None)
            return

        nearest_job = None
        nearest_time = None

        for job in jobs:
            run_time = getattr(job, "next_run_time", None)
            if not run_time:
                continue

            if nearest_time is None or run_time < nearest_time:
                nearest_time = run_time
                nearest_job = job

        if nearest_job is None:
            self.events.emit("NEXT_BELL_UPDATED", None)
            return

        self.events.emit("NEXT_BELL_UPDATED", {
            "time": nearest_time,
            "name": nearest_job.name
        })
        
    # =========================
    # LOAD JOBS
    # =========================

    def load_jobs(self) -> int:
        with self._lock:
            try:
                self.scheduler.remove_all_jobs()
            except:
                pass

            profile = self.repo.get_active_profile()
            if not profile:
                logger.warning("No active profile")
                self.events.emit("JOBS_UPDATED", 0)
                self.events.emit("NEXT_BELL_UPDATED", None)
                return 0

            schedules = self.repo.get_schedules_by_profile(profile.id)
            if not schedules:
                logger.warning("No schedules")
                self.events.emit("JOBS_UPDATED", 0)
                self.events.emit("NEXT_BELL_UPDATED", None)
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

            self.events.emit("JOBS_UPDATED", count)
            self.events.emit("PROFILE_CHANGED", {
                "id": profile.id,
                "name": profile.name
            })

            logger.info(f"Loaded {count} jobs")
            return count

    # =========================
    # LIFECYCLE
    # =========================

    def start(self) -> bool:
        with self._lock:
            if self.running:
                return True

            # rebuild scheduler fresh if previously shutdown
            self.scheduler = self._create_scheduler()

            loaded = self.load_jobs()
            if loaded == 0:
                return False

            self.scheduler.start()
            self.running = True

            self._publish_next_bell()
            self.events.emit("SYSTEM_STARTED")
            return True

    def stop(self) -> bool:
        with self._lock:
            if not self.running:
                return False

            try:
                self.scheduler.shutdown(wait=False)
            except Exception as e:
                logger.warning(f"Scheduler shutdown warning: {e}")

            self.running = False

            self.events.emit("NEXT_BELL_UPDATED", None)
            self.events.emit("SYSTEM_STOPPED")
            return True

    def reload(self) -> bool:
        if not self.running:
            return False

        self.load_jobs()
        self._publish_next_bell()
        return True

    def switch_profile(self, profile_id: int) -> bool:
        ok = self.repo.set_active_profile(profile_id)
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


# =========================
# SINGLETON
# =========================

_scheduler = None
_lock = threading.Lock()


def get_scheduler_service():
    global _scheduler
    with _lock:
        if _scheduler is None:
            _scheduler = SchedulerService()
        return _scheduler